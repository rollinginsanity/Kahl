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
        return '<User %r>' % self.title
