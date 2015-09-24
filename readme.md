THE PROOF OF CONCEPT works

Todo: Make prettier
Better metadata
Better navigation
Ajax muchly



-------

Comic Book Library server
Requirements:

Redis
Flask
Python 3.4+
python-dev
libjpeg-dev
PIL

High Level Architecture
=======================

The general layout is 3 components:

A server for reading comics
-Needs to pick up metadata
-Needs to be able to keep track of where a use got up to in the comic (page#) with the ability to resume or restart.
-Needs to list comics.

A an area to upload comics
-Add metadata
-Upload .cbz file

A task queue to process uploaded comics in asynch. (rq)

Where things are at:
====================

* Comic upload and unzipping works now.
* Metafile containing comic title and list of pages matched to the image numbers is working.

Todo
====

* Build Library view with thumbnail images (GD or Imagemagik?) - Partial
* Build comic display logic.
* Build comic download functionality? (Maybe just store a reference to the uploaded archive...)
* Main page selection
