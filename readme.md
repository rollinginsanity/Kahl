[![Stories in Ready](https://badge.waffle.io/rollinginsanity/Kahl.png?label=ready&title=Ready)](https://waffle.io/rollinginsanity/Kahl)

[Go to the Site for Kahl](http://rollinginsanity.github.io/Kahl)

![Screenshot of Kahl](http://rollinginsanity.github.io/Kahl/images/screeny.png)

What is this?
=============

Currently this is a pre-pre-alpha build for a web based comic book reader using flask.

Read the requirements.txt file for the specific requirements for python modules, but in general, to get this thing going as fast as possible:
* Get a server, install python 3.4+ (or find one you already have.)
* Install libjpeg
* Install pip requirements
* Install redis.
* Run redis-server
* Run setup.sh to create some required directories (Yep, I know this is nasty...)
* run db_create and db_migrate.py
* Go to the root folder for the app, and run worker.py and run.py.
* Go to yourhostname:5000/upload and upload a comic.
* You will be redirected to /index, refresh the page until your comic appears (the processing is offloaded to a worker process, it can take a sec or two)
* Your comic should appear. Click on it. The is probably the most (and only) polished bit so far. Click on the right hand side of the screen to go forward a page, the left side to go back, the top to go back to /index.

Gotchas:

* The code is pretty hackneyed at the moment. Don't look through the git history, you will weep tears of immense sorrow as you see my n00bish mistakes.
* This thing looks about as ugly as some sick on the ground, use at your own peril.
* Again, pre-pre-pre-pre-pre-alpha, so I can't promise this will work too well.
* Also, only works with CBZs, also, I haven't set up functionality to pull comics from existing folders on the server, presumably there is a limit to the size of the file that can be uploaded...
* Enjoy.

Config file
===========

The config file takes a few values at this stage, and need to be in the structure:

```
[server]
ServerBindIP = 0.0.0.0
DebugMode = True
ListenPort = 5000
```

```
ServerBindIP = [The bind IP of the server. 127.0.0.1 to listen on localhost, 0.0.0.0 to listen to all requests.]
```

```
DebugMode = [True to display debug output for the app, False to show no output. Only set to true when developing Kahl.]
```

```
ListenPort = [The port you want this to listen on.]
```

High Level Architecture
=======================

The general layout is 3 components:

A server for reading comics
* Needs to pick up metadata
* Needs to be able to keep track of where a use got up to in the comic (page#) with the ability to resume or restart.
* Needs to list comics.

A task queue to process uploaded comics in asynch. (rq)

Where things are at:
====================
* Comic upload and unzipping works now.
* Using a database to store comics.
* Can read comics.
Todo
====
* Build comic download functionality? (Maybe just store a reference to the uploaded archive...)
* Main page selection
