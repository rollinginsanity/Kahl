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

UPLOAD_FOLDER = 'comics/unprocessed'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'cbz'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#Extract Comic Books into a directory
def extractcomic(comicfile, comic_name):
	zf = zipfile.ZipFile(comicfile)
	for file in zf.namelist():
		output = "comics/processed/"+comic_name
		zf.extract(file, output)

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
