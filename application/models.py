from application.database import db
from datetime import datetime
class Album(db.Model):
    __tablename__ = 'album'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement = True, primary_key = True )
    name = db.Column(db.String(50), nullable = False, unique = True )
    genre = db.Column(db.String(20), default = "not available")
    artist =db.Column(db.String(50), default = "not available")
    rating = db.Column(db.Integer, default= 0)
    creater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)
    creator=db.relationship('User', backref = 'albums_created')
    album_songs = db.relationship('Song', backref = 'associated_songs', lazy = True)

songs = db.Table(
    'songs',
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True),
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    extend_existing=True
)

users = db.Table(
    'users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    extend_existing=True
)
class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement = True, primary_key = True )
    firstname = db.Column(db.String(20), nullable = False, )
    lastname = db.Column(db.String(20), nullable = False, )
    continent= db.Column(db.String(20), nullable = False, )
    email = db.Column(db.String(50), nullable = False, unique = True )
    password = db.Column(db.String(12), nullable = False,)
    is_creator = db.Column(db.Boolean, default = 0)
    is_admin = db.Column(db.Boolean, default = 0)
    playlists = db.relationship('Playlist',
                                secondary = users,  backref = db.backref('associated_users', lazy = True))
    albums = db.relationship('Album', 
                              backref = db.backref('associated_albums', lazy = True))
    
    def __repr__(self):
        return f'<User {self.firstname} {self.email}>'


class Song(db.Model):
    __tablename__ = 'song'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement = True, primary_key = True )
    name = db.Column(db.String(100), nullable = False, unique = True )
    lyrics = db.Column(db.String(10000), nullable= False)
    audio = db.Column(db.String(10000), nullable= False)
    creater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)
    created_on =db.Column(db.DateTime(timezone=True), default =datetime.utcnow())
    duration= db.Column(db.Integer, default = 0)
    rating = db.Column(db.Integer)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable= False)
    is_abusive = db.Column(db.Boolean, default = 0)
    playlists = db.relationship(
        'Playlist',
        secondary=songs,
        primaryjoin='Song.id == songs.c.song_id',
        secondaryjoin='Playlist.id == songs.c.playlist_id',
        backref=db.backref('associated_songs', lazy=True)
    )



class Playlist(db.Model):
    __tablename__ = 'playlist'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement = True, primary_key = True )
    name = db.Column(db.String(50), nullable = False, unique = True )
    rating = db.Column(db.Integer, default= 0)
    songs = db.relationship(
        'Song',
        secondary=songs,
        primaryjoin='Playlist.id == songs.c.playlist_id',
        secondaryjoin='Song.id == songs.c.song_id',
        backref=db.backref('associated_playlists', lazy=True)
    )
    users = db.relationship('User', secondary = users, lazy='subquery',
            backref=db.backref('associated_playlists', lazy=True))






