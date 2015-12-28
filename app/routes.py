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
import sqlite3
from PIL import Image

UPLOAD_FOLDER = 'app/static/comics/unprocessed'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'cbz'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#This bit of code is temporary until I figure out a nicer way to do it. It's the database.

if not os.path.isfile("comicdb"):
    conn = sqlite3.connect("comicdb")
    c = conn.cursor()
    ###PoC Datamodel
    ###Comics:
    ###     id - A hash of the filename
    ###     title - The name of the Comic
    ###     author - The author
    ###     Artist - The artist of the comic
    ###     genre - ie Sci Fi, Fantast...
    ###     series - The series the comic is in
    ###     franchise - Star Wars, Mass Effect, Marvel etc...
    ###     Issue_num - The issue of the comic within it's volume
    ###     volume_num - The volume of the comic.
    ###
    ###
    ###
    c.execute('''CREATE TABLE comics(id text, title text, author text, artist text, genre text, series text, franchise text, issue_num integer, volume_num integer)''')
    c.execute('''CREATE TABLE pages(comic_id text, page_number integer, page_file_name text)''')
    conn.commit()
    conn.close()

#From here: http://stackoverflow.com/a/4836734
#Used to sort the comic file list.
def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
        if "MACOSX" in file:
            continue

        pages_in_comic.append([i, file])

        zf.extract(file, output)
        i += 1

    conn = sqlite3.connect("comicdb")
    dbargs = (comic_name_hex, comic_name)
    c = conn.cursor()
    c.execute("INSERT INTO comics VALUES(?, ?, '', '', '', '', '', '', '')", dbargs)

    #SQLAlchemy Stuff (Yes, running side by side...)
    comic_sa = models.Comic(cb_hash=comic_name_hex, title=comic_name)
    db.session.add(comic_sa)

    first_image_name = ""
    #To change, once a file is uploaded, allow a user to set the proper first page. Still need to add that to the metadata, will come later.
    for page in pages_in_comic:
        if page[0] == 1:
            first_image_name = page[1]
        dbargs = (comic_name_hex, page[0], page[1])
        c.execute("INSERT INTO pages VALUES(?,?,?)", dbargs)
        #SQLAlchemy stuff again.
        page_sa = models.Page(cb_hash=comic_name_hex, page_num=page[0], page_file=page[1])
        print(page_sa)
        db.session.add(page_sa)
    db.session.commit()
    conn.commit()
    conn.close()
    img = Image.open("app/static/comics/processed/"+comic_name_hex+"/"+first_image_name)
    img.thumbnail((192, 192), Image.ANTIALIAS)
    img.save("app/static/thumbs/"+comic_name_hex+"_thumb.jpg", "JPEG")

@app.route('/')
@app.route('/index')
def index():
    conn = sqlite3.connect("comicdb")
    c = conn.cursor()
    rows = c.execute("SELECT * FROM comics")
    comics = []
    for row in rows:
        comics.append(row)
    print(comics)
    return render_template("index_main.html", comiclist=comics)

@app.route('/comiclist')
def index_comiclist():
    comics_sa = models.Comic.query.all()
    return render_template("index_comiclist.html", comiclist=comics_sa)

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

    conn = sqlite3.connect("comicdb")
    c = conn.cursor()
    dbargs = (comic_key, page_num)
    c.execute("SELECT * FROM pages WHERE comic_id = ? AND page_number = ?", dbargs)
    page = c.fetchone()

    if page is None:
        return redirect(url_for('index'))

    return render_template("viewcomic.html", comic_key=page[0], page_number=page[1], page_file=page[2])
