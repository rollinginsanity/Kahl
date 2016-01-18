#Some of the logic for the server.
from app import app, models, db
import os
from flask import request, redirect, url_for, render_template
from werkzeug import secure_filename
from redis import Redis
from rq import Queue
import time
import zipfile
import hashlib
import re
from PIL import Image
import shutil

UPLOAD_FOLDER = 'app/static/comics/unprocessed'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'cbz'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#From here: http://stackoverflow.com/a/4836734
#Used to sort the comic file list.
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def deletecomic(comic_hash):
    shutil.rmtree("app/static/comics/processed/"+comic_hash, ignore_errors=True)


#Extract Comic Books into a directory
#The directory name is hashed
#Add a metadata file with the comic name and the pages.
def extractcomic(comicfile, comic_name):
    comic_name_pre_hash = comic_name
    comic_name_hashed = hashlib.sha1(comic_name_pre_hash.encode())
    comic_name_hex = comic_name_hashed.hexdigest()
    output = "app/static/comics/processed/"+comic_name_hex
    zf = zipfile.ZipFile(comicfile)
    filenumber_rex = re.compile(r'[^\d]+')

    pages_in_comic = []
    zipfiles = zf.namelist()
    files = natural_sort(zipfiles)
    i = 1
    for file in files:
        #Checking for mac junk
        if "MACOSX" in file:
            continue

        #Some CBZ files have nested folders. Checking for them and ignoring them.
        if file.endswith("/"):
            continue

        pages_in_comic.append([i, file])

        zf.extract(file, output)
        i += 1

    #SQLAlchemy Stuff (Yes, running side by side...)
    comic_sa = models.Comic(cb_hash=comic_name_hex, title=comic_name)
    db.session.add(comic_sa)

    first_image_name = ""
    #To change, once a file is uploaded, allow a user to set the proper first page. Still need to add that to the metadata, will come later.
    for page in pages_in_comic:
        if page[0] == 1:
            first_image_name = page[1]

        #SQLAlchemy stuff again.
        page_sa = models.Page(cb_hash=comic_name_hex, page_num=page[0], page_file=page[1])
        print(page_sa)
        db.session.add(page_sa)
    db.session.commit()
    img = Image.open("app/static/comics/processed/"+comic_name_hex+"/"+first_image_name)
    img.thumbnail((192, 192), Image.ANTIALIAS)
    img.save("app/static/thumbs/"+comic_name_hex+"_thumb.jpg", "JPEG")

@app.route('/')
@app.route('/index')
def index():

    return render_template("index_main.html")

@app.route('/comiclist')
def index_comiclist():
    comics = models.Comic.query.all()
    return render_template("index_comiclist.html", comiclist=comics)

#Takes an uploaded file and passes it off to an rq worker to be processed.
#The filename of the uploaded file is hashed before saving, and taken by the rq worker
#and extrated to a directory matching the name of the comic the user set (may hash this as well)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        comic_name = request.form['comicname']
        if file and allowed_file(file.filename):
            filename_pre_hash = secure_filename(file.filename)
            filename_hashed = hashlib.sha1(filename_pre_hash.encode())
            filename_hex = filename_hashed.hexdigest()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_hex))
            redis_conn = Redis()
            q = Queue(connection=redis_conn)  # no args implies the default queue
            job = q.enqueue(extractcomic, os.path.join(app.config['UPLOAD_FOLDER'], filename_hex), comic_name)
            return redirect(url_for('index'))
    return render_template("upload.html")

#View the pages in a comic book:
@app.route('/viewcomic/<comic_key>/page/<int:page_num>', methods=['GET'])
def view_comic(comic_key, page_num):

    page = models.Page.query.filter_by(cb_hash = comic_key).filter_by(page_num = page_num).first()

    if page is None:
        return redirect(url_for('index'))

    return render_template("viewcomic.html", comic_key=page.cb_hash, page_number=page.page_num, page_file=page.page_file)

#View the detail of a comic book.
@app.route('/detail/<comic_id>', methods=['GET'])
def comic_detail(comic_id):
    comic = models.Comic.query.filter_by(id = comic_id).first()
    comic_dict = dict((col, getattr(comic, col)) for col in comic.__table__.columns.keys())

    return render_template("comic_detail.html", comic_dict=comic_dict, comic=comic)

@app.route('/delete/<comic_key>', methods=['GET'])
def delete_comic(comic_key):
    redis_conn = Redis()
    q = Queue(connection=redis_conn)
    comic = models.Comic.query.filter_by(cb_hash = comic_key).first()
    job = q.enqueue(deletecomic, comic.cb_hash)
    db.session.delete(comic)
    db.session.commit()
    q = Queue(connection=redis_conn)  # no args implies the default queue

    return redirect(url_for('index'))
