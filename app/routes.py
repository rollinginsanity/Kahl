#Some of the logic for the server.
from app import app
import os
from flask import request, redirect, url_for, render_template
from werkzeug import secure_filename
from redis import Redis
from rq import Queue
from addf import extractcomic
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
    c.execute('''CREATE TABLE comics(id text, title text)''')
    c.execute('''CREATE TABLE pages(comic_id, page_number, page_file_name)''')
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
    print(natural_sort(zf.namelist))
    for file in zf.namelist():
        if "MACOSX" in file:
            continue
        filenumber = filenumber_rex.sub('',file)
        pages_in_comic.append(["page"+filenumber.zfill(3), file])
        zf.extract(file, output)

    conn = sqlite3.connect("comicdb")
    dbargs = (comic_name_hex, comic_name)
    c = conn.cursor()
    c.execute("INSERT INTO comics VALUES(?, ?)", dbargs)
    first_image_name = ""
    #This might solve the below issues: http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
    for page in pages_in_comic:
        if page[0] == "page001":
            first_image_name = page[1]
        dbargs = (comic_name_hex, page[0], page[1])
        c.execute("INSERT INTO pages VALUES(?,?,?)", dbargs)
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
    return render_template("index.html", comiclist=comics)

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
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type="file" name="file"/>
         <input type="text" name="comicname"/>
         <input type="submit" value="Upload"/>
    </form>
    '''
