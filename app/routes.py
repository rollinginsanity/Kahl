#Some of the logic for the server.
from app import app
import os
from flask import request, redirect, url_for
from werkzeug import secure_filename
from redis import Redis
from rq import Queue
from addf import extractcomic
import time
import zipfile
import hashlib
import re

UPLOAD_FOLDER = 'comics/unprocessed'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'cbz'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    output = "comics/processed/"+comic_name_hex
    zf = zipfile.ZipFile(comicfile)
    filenumber_rex = re.compile(r'[^\d]+')
    pages_in_comic = []
    for file in zf.namelist():
        filenumber = filenumber_rex.sub('',file)
        pages_in_comic.append("page"+filenumber.zfill(3)+":"+file+"\n")
        zf.extract(file, output)
    f = open(output+"/meta","w")
    f.write(comic_name+"\n")
    for page in pages_in_comic:
        f.write(page+"\n")
    f.close

@app.route('/')
@app.route('/index')
def index():
    return "Does it work?"

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
