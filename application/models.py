from application.database import db
from datetime import datetime

class Song(db.Model):
    __tablename__ = 'songs'
    __table_args__ = {'extend_existing': True}
    song_id = db.Column(db.Integer, autoincrement = True, primary_key = True )
    name = db.Column(db.String(100), nullable = False, unique = True )
    lyrics = db.Column(db.String(10000), nullable= False)
    created_on =db.Column(db.DateTime(timezone=True), default =datetime.utcnow())
    duration= db.Column(db.Integer, default = 0)
    rating = db.Column(db.Integer)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id'), nullable= False)
    playlists = db.relationship('Playlist', backref = 'playlist', lazy = True)
    creater_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable= False)
    is_abusive = db.Column(db.Boolean, default = 0)



class Album(db.Model):
    __tablename__ = 'albums'
    __table_args__ = {'extend_existing': True}
    album_id = db.Column(db.Integer, autoincrement = True, primary_key = True )
    name = db.Column(db.String(50), nullable = False, unique = True )
    genre = db.Column(db.String(20), default = "not available")
    artist =db.Column(db.String(50), default = "not available")
    rating = db.Column(db.Integer, default= 0)
    album_songs = db.relationship('Song', backref = 'song', lazy = True)



class Playlist(db.Model):
    __tablename__ = 'playlists'
    __table_args__ = {'extend_existing': True}
    playlist_id = db.Column(db.Integer, autoincrement = True, primary_key = True )
    name = db.Column(db.String(50), nullable = False, unique = True )
    rating = db.Column(db.Integer, default= 0)
    playlist_songs = db.relationship('Song', backref = 'song', lazy = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable= False)



class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, autoincrement = True, primary_key = True )
    firstname = db.Column(db.String(20), nullable = False, )
    lastname = db.Column(db.String(20), nullable = False, )
    continent= db.Column(db.String(20), nullable = False, )
    email = db.Column(db.String(50), nullable = False, unique = True )
    password = db.Column(db.String(12), nullable = False,)
    is_creator = db.Column(db.Boolean, default = 0)
    is_admin = db.Column(db.Boolean, default = 0)
    playlists = db.relationship('Playlist', backref = 'user', lazy = True)

    

