from app import db

class Comic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cb_hash = db.Column(db.String(256), index=True, unique=True)
    title = db.Column(db.String(256), index=True, unique=True)
    author = db.Column(db.String(256), index=False, unique=False)
    genre = db.Column(db.String(256), index=False, unique=False)
    series = db.Column(db.String(256), index=False, unique=False)
    franchise = db.Column(db.String(256), index=False, unique=False)
    issue_num = db.Column(db.Integer)
    volume_num = db.Column(db.Integer)

    def __repr__(self):
        return '<Comic %r>' % self.title

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cb_hash = db.Column(db.String(256), index=True, unique=False)
    page_num = db.Column(db.Integer)
    page_file = db.Column(db.String(2048), index=True, unique=False)

    def __repr__(self):
        return '<Page %r>' % self.page_num

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)

    def __repr__(self):
        return '<User %r>' % self.name

class UserReadInProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, index=True)
    cb_hash = db.Column(db.String(256), index=True, unique=False)
    page_num = db.Column(db.Integer)

    def __repr__(self):
        return '<PageRef %r>' % self.idsss
