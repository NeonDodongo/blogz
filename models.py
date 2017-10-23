from app import db
from math import ceil
from hashutils import make_pw_hash
from datetime import datetime

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String(175))
    post_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.LargeBinary)


    def __init__(self, title, content, owner, post_date=None):
        self.title = title
        self.content = content
        self.owner = owner

        if post_date is None:
            post_date = datetime.now()

        self.post_date = post_date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    pw_hash = db.Column(db.String(120))
    blog = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)
