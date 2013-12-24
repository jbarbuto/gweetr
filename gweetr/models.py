"""models.py"""

from gweetr import db


class Track(db.Model):

    """Track model."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    artist = db.Column(db.String)
    url = db.Column(db.Text, unique=True)

    def __init__(self, title, artist, url):
        self.title = title
        self.artist = artist
        self.url = url

    def __repr__(self):
        return "<Track %r>" % self.url


class Greeting(db.Model):

    """Greeting model."""

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String, unique=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    track = db.relationship(
        'Track',
        backref=db.backref('greetings', lazy='dynamic')
    )

    def __init__(self, phone, track):
        self.phone = phone
        self.track = track

    def __repr__(self):
        return "<Greeting %r>" % self.phone
