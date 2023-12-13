from flask import request, Flask, flash, session
from flask import render_template, url_for, redirect
from flask import current_app as app 
from application.models import *
from flask_basicauth import BasicAuth
from mutagen.mp3 import MP3
from sqlalchemy import or_ , desc, func
import os
from sqlalchemy.orm.exc import NoResultFound

@app.route("/", methods = ['GET', 'POST'])
def home_page():
    if request.method == 'GET' :
        return render_template('home.html')
    if request.method == 'POST' :
        return url_for(registration)

# Admin login route
basic_auth = BasicAuth(app)
@app.route("/admin", methods=['GET', 'POST'])
@basic_auth.required
def admin_login():
    if request.method == 'GET':
        return render_template('admn_login.html')

    if request.method == 'POST':
        uname = request.form.get("username")
        pwd = request.form.get("password")

        if uname == 'virat' and pwd == 'jain':
            app.logger.info(f"Login successful for {uname}")

            # Creating an admin session
            
            admin_session = AdminSession(admin_username='virat')
            admin_session.login_time = datetime.utcnow()
            db.session.add(admin_session)
            db.session.commit()

            # Storing admin session information in Flask session
            session['admin_logged_in'] = True
            session['admin_session_id'] = admin_session.id

            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            app.logger.warning(f"Login failed for {uname}")
            flash('Wrong admin password or username. Please check with admin Virat for correct credentials', 'error')
            return redirect(url_for("home_page"))

# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('You need to log in as an admin.', 'error')
        return redirect(url_for('admin_login'))

    # Retrieve admin session ID from the session
    admin_session_id = session['admin_session_id']

    # Fetch admin session from the database
    admin_session = AdminSession.query.get(admin_session_id)

    users = db.session.query(User).all()
    total_users = User.query.count()
    total_creators = User.query.filter_by(is_creator=True).count()
    total_albums = Album.query.count()
    total_songs = Song.query.count()
    total_playlist= Playlist.query.count()
    total_song_likes = db.session.query(func.sum(Song.likes)).scalar()
    total_playlist_likes = db.session.query(func.sum(Playlist.likes)).scalar()
    total_song_ratings = db.session.query(func.count(SongRating.id)).scalar()
    total_playlist_ratings = db.session.query(func.count(PlaylistRating.id)).scalar()
    most_creative_user = db.session.query(User).join(Song).group_by(User.id).order_by(func.count().desc()).first()
    count = db.session.query(func.count()).select_from(Song).filter_by(creater_id=most_creative_user.id).scalar()
    abusive_song = (db.session.query(Song).filter(Song.is_abusive == 1).all() )
    abusive_songs = (
                        db.session.query(Song, User)
                        .join(User, Song.creater_id == User.id)
                        .filter(Song.is_abusive == 1)
                        .all()
                    )

    return render_template('admin_dashboard.html', key='ADMIN PAGE', total_users=total_users, users=users,
                           total_creators=total_creators,
                           total_albums=total_albums,
                           total_songs=total_songs,
                           total_playlist=total_playlist,
                           total_song_likes=total_song_likes,
                           total_playlist_likes=total_playlist_likes,
                           total_song_ratings=total_song_ratings,
                           total_playlist_ratings=total_playlist_ratings,
                           most_creative_user=most_creative_user, count=count,
                           abusive_song=abusive_song,
                           abusive_songs=abusive_songs)

# Blacklist user route
@app.route('/blacklist/<int:user_id>')
def blacklist_user(user_id):
    if not session.get('admin_logged_in'):
        flash('You need to log in as an admin.', 'error')
        return redirect(url_for('admin_login'))

    admin_session_id = session['admin_session_id']
    user = db.session.query(User).filter_by(id=user_id).first()
    user.is_blacklisted = 1  
    db.session.commit()
    db.session.close()  
    flash('User blacklisted successfully!', 'success')

    return redirect(url_for('admin_dashboard'))

# Whitelist user route
@app.route('/whitelist/<int:user_id>')
def whitelist_user(user_id):
    if not session.get('admin_logged_in'):
        flash('You need to log in as an admin.', 'error')
        return redirect(url_for('admin_login'))

    user = db.session.query(User).filter_by(id=user_id).first()

    user.is_blacklisted = 0
    db.session.commit()
    db.session.close()
    flash('User whitelisted successfully!', 'success')

    return redirect(url_for('admin_dashboard'))



#User Registration
 
     
@app.route("/register", methods = ['GET', 'POST'])
def registration():
    if request.method == 'GET' :
        return render_template('usr_reg.html')
    if request.method == 'POST' :
        user = User(
            firstname =request.form["firstname"],
            lastname =request.form["lastname"],
            continent = request.form["continents"],
            email=request.form["email"],
            password =request.form["password"],
            )

    try:
        password =request.form["password"]
        confirmpassword =request.form["confirmpassword"]
        if (password==confirmpassword):
            db.session.add(user)
            db.session.commit()
            db.session.close()
            flash('You were successfully Registered, now login')
            return redirect(url_for("user_login"))
        
        else :
             return render_template('passwordvalidation.html')
        
    except:
        return render_template('registration_except.html')




#User Login


@app.route("/user_login", methods = ['GET', 'POST'])
def user_login():
  

    if request.method == 'POST':
        email = request.form.get("email")
        user = db.session.query(User).filter_by(email=email).first()

        if user and user.is_blacklisted == 1:
            flash(f'User {user.firstname} {user.lastname} ({user.email}) is Blacklisted by app admin. Contact admin Virat to come back in Whitelist', 'error')
            return redirect(url_for('home_page'))
        
        
        elif user and (user.password == request.form.get("password")):
            app.logger.info(f"Login successful for {email}")
            session['user_email'] = user.email
            session['user_firstname'] = user.firstname
            session['user_password'] = user.password
            user_songs = db.session.query(Song).filter_by(creater_id=user.id).all()
            all_songs = db.session.query(Song).all()
            recom_songs = db.session.query(Song).order_by(desc(Song.likes)).all()
            #user_playlists = db.session.query(users).filter_by(user_id=user.id).all()
            user_playlists = db.session.query(Playlist).join(users).filter(users.c.user_id == user.id).all()
            all_playlists = db.session.query(Playlist).join(users).all()
            user_albums = user.albums
            return render_template('user_dashboard.html', key=user.firstname,
                                    user_songs = user_songs, user_iscreator= user.is_creator, 
                                    recom_songs=recom_songs, genre_songs= all_songs, user_playlists = user_playlists, 
                                    all_playlists = all_playlists, user_albums=user_albums)

        else:
            flash('Invalid email or password. Please try again. or register')
            app.logger.warning(f"Login failed for {email}")
            return redirect(url_for("user_login"))

    if  request.method == 'GET':
        return render_template('usr_login.html')



#User HomePage

@app.route('/user_home', methods=['GET', 'POST'])
def user_home():
    if request.method == 'GET':
        email= session['user_email']
        password= session['user_password']
        user = db.session.query(User).filter_by(email=email, password=password).first()
        user_songs = db.session.query(Song).filter_by(creater_id=user.id).all()
        all_songs = db.session.query(Song).all()
        recom_songs = db.session.query(Song).order_by(desc(Song.likes)).all()
        #user_playlists = db.session.query(users).filter_by(user_id=user.id).all()
        #playlists= db.session.query(Playlist).all()
        user_playlists = db.session.query(Playlist).join(users).filter(users.c.user_id == user.id).all()
        all_playlists = db.session.query(Playlist).join(users).all()
        user_albums = user.albums
        return render_template('user_dashboard.html', key=user.firstname, user_songs = user_songs,
                                user_iscreator= user.is_creator, all_songs=all_songs, recom_songs=recom_songs,
                                  genre_songs= all_songs, user_playlists=user_playlists, 
                                  all_playlists=all_playlists, user_albums= user_albums)
    if request.method == 'POST':
        search_key = request.form.get('search_all')
        search_type = request.form.get('search_type')
        email = session['user_email']
        password = session['user_password']
        user = db.session.query(User).filter_by(email=email, password=password).first()
        genre_filter = request.form.get('genre')
        #user_playlists = db.session.query(users).filter_by(user_id=user.id).all()
        user_playlists = db.session.query(Playlist).join(users).filter(users.c.user_id == user.id).all()
        flash('Search Completed' )
        #Filter by Album Genre
        if genre_filter:  
            genre_songs = db.session.query(Song).join(Album).filter(Album.genre.ilike(f"%{genre_filter}%")).all()
            all_songs = db.session.query(Song).all()
            #user_playlists = db.session.query(users).filter_by(user_id=user.id).all()
            user_playlists = db.session.query(Playlist).join(users).filter(users.c.user_id == user.id).all()
            return render_template('user_dashboard.html', key=user.firstname,genre_songs= genre_songs , 
                                   genre_filter= genre_filter, all_songs=all_songs,user_playlists = user_playlists)
        
         #Search Functionality
        if search_type == 'song':
            user_songs = db.session.query(Song).filter(or_(Song.name.ilike(f"%{search_key}%"), Song.lyrics.ilike(f"%{search_key}%"), Song.avg_rating.ilike(f"%{search_key}%"))).all()
        elif search_type == 'album':
            user_songs = db.session.query(Song).join(Album).filter(or_(Album.name.ilike(f"%{search_key}%"))).all()
        elif search_type == 'artist':
            user_songs = db.session.query(Song).join(Album).filter(Album.artist.ilike(f"%{search_key}%")).all()
        return render_template('user_dashboard.html', key=user.firstname, user_songsearch = user_songs, search_key=search_key,user_playlists = user_playlists)
        


#User as Creator 

@app.route("/creator", methods = ['GET', 'POST'])
def creator():
   # Check if the user is logged in as a creator
    if 'user_email' in session and 'user_password' in session:
        email = session['user_email']
        password = session['user_password']
        user = db.session.query(User).filter_by(email=email, password=password).first()
        user.is_creator = 1
        db.session.commit()
        
        if user:
            app.logger.info(f"Creator login for {email}")
            flash('You are a creator now')
            return render_template('creator_upload.html', key=user.firstname)
    
    # If not logged in as a creator, redirect to login
    flash('Please log in as a creator to access this page.')
    return redirect(url_for("user_login"))

#Song Upload

@app.route("/upload", methods = [ 'POST'])
def upload():

    # Check if the user is logged in
    if 'user_email' not in session:
        flash('Please log in to access this page.')
        email = request.form.get("email")
        user = db.session.query(User).filter_by(email=email).first()
        session['user_email'] = user.email
        session['user_firstname'] = user.firstname
        return redirect(url_for("creator"))

 
    if request.method == 'POST' :
        try:    
            
            if  session['user_email']: 
                email= session['user_email']
                user = db.session.query(User).filter_by(email=email).first()
                # Extract album information from the form
                album_name = request.form.get('albumName')
                album_genre = request.form.get('albumGenre')
                album_artist = request.form.get('albumArtist')


                # Check if the album already exists for the current user
                existing_album = Album.query.filter_by(name=album_name, creater_id=user.id).first()
                if existing_album:
                    flash('Album with the same name already exists.', 'error')
                    return redirect(url_for('upload'))

                # Create a new album instance
                new_album = Album(name=album_name, genre=album_genre, artist=album_artist, creater_id= user.id)  

                # Add the album to the database
                db.session.add(new_album)
                db.session.commit()

                # Extract song information from the form
                song_names = request.form.getlist('songName[]')
                lyrics_files = request.files.getlist('lyricsFile[]')
                song_files = request.files.getlist('songFile[]')
                #song_durations = request.form.getlist('songDuration[]')

                # Iterate over the songs and add them to the database
                for i in range(len(song_names)):
                    song_name = song_names[i]
                    
                    # Check if the song already exists in the album
                    existing_song = Song.query.filter_by(name=song_name, album_id=new_album.id).first()
                    if existing_song:
                        flash(f'Song "{song_name}" already exists in the album.', 'error')
                        # If a duplicate song is found, delete the newly created album to maintain data integrity
                        db.session.delete(new_album)
                        db.session.commit()
                        return redirect(url_for('upload'))
                    lyrics_file = lyrics_files[i]
                    song_file = song_files[i]
                    

                    # Save the uploaded files to the server 
                    lyrics_file.save(f'static/uploads/lyrics/{lyrics_file.filename}')
                    song_file.save(f'static/uploads/songs/{song_file.filename}')
                    
                    audio=f'static/uploads/songs/{song_file.filename}'
                    music = MP3(audio)
                    duration_in_seconds = int(music.info.length)
                    # Create a new song instance
                    new_song = Song(
                        name=song_name,
                        lyrics=f'static/uploads/lyrics/{lyrics_file.filename}',  # Store the file path in the database
                        audio=f'static/uploads/songs/{song_file.filename}' ,  # Store the file path in the database
                        creater_id= user.id,
                        created_on=datetime.utcnow(),
                        duration= duration_in_seconds,
                        album_id=new_album.id,  
                        
                    )



                    # Add the song to the database
                    db.session.add(new_song)
                    db.session.commit()
                app.logger.info(f"upload successful for {email}")
                flash('Album and songs uploaded successfully!', 'success')
                email= session['user_email']
                password= session['user_password']
                user = db.session.query(User).filter_by(email=email, password=password).first()
                return redirect(url_for("user_home"))
  

        except Exception as e:
            print(e)
            flash('Error uploading album and songs.', 'error')
            return redirect(url_for('upload'))


#View Song

@app.route('/song/<int:song_id>',methods = ['GET', 'POST'] )
def songs(song_id):
    email= session['user_email']
    user = db.session.query(User).filter_by(email=email).first()
    song = db.session.query(Song).filter_by(id=song_id).first()
    
    album=db.session.query(Album).filter_by(id=song.album_id).first()
    
    # Read the content of the text file
    lyrics_path = song.lyrics
    with open(lyrics_path, 'r') as file:
        lyrics_content = file.read()

    return render_template('song_detail.html', song=song, lyrics_content=lyrics_content, user=user , id =song.creater_id, album=album, user_iscreator= user.is_creator )

#Assign Album to Song


@app.route('/assign_album_to/<int:song_id>',methods = ['GET', 'POST'] )
def assign_album(song_id):

    if request.method == 'GET':
        email= session['user_email']
        password= session['user_password']
        user = db.session.query(User).filter_by(email=email, password=password).first()
        song = db.session.query(Song).filter_by(id=song_id).first()
        key=user.firstname
        user_albums = user.albums
        return render_template('assign_album.html', user=user , song =song, key=key, user_albums=user_albums)



    if request.method == 'POST':
            email= session['user_email']
            user = db.session.query(User).filter_by(email=email).first()
            song = db.session.query(Song).filter_by(id=song_id).first()
            album= request.form.get('albumName')
            album = db.session.query(Album).filter_by(id=album).first()

            # Assign the song to the album
            if song and album:
                song.album_id = album.id
                db.session.commit()
                flash('Song assigned to the album successfully!', 'success')
            else:
                flash('Song or album not found.', 'error')
            
    return redirect(url_for('user_home'))




#Delete Album


@app.route('/delete_album/<int:album_id>', methods=['GET'])
def delete_album(album_id):
    email = session['user_email']
    user = db.session.query(User).filter_by(email=email).first()

    try:
        album = db.session.query(Album).filter_by(id=album_id, creater_id=user.id).one()
    except NoResultFound:
        flash('Album not found or does not belong to the logged-in user.', 'error')
        return redirect(url_for('user_home'))

    try:
        # Remove the album from the user's albums
        user.albums.remove(album)

        # Explicitly set creater_id to None before deleting
        album.creater_id = None

        # Update songs associated with the album
        for song in album.album_songs:
            song.album_id = None

        db.session.commit()

        # Now delete the album
        db.session.delete(album)
        db.session.commit()

        flash('Album removed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        print(album)
        flash(f'Error removing album: {str(e)}', 'error')

    return redirect(url_for('user_home'))

#Delete Song


@app.route('/delete_song/<int:song_id>', methods=['GET'])
def delete_song(song_id):
    email = session['user_email']
    user = db.session.query(User).filter_by(email=email).first()
    song = db.session.query(Song).filter_by(id=song_id).first()

    if song:
        try:
            # Check if the song belongs to the logged-in user
            if user and song in user.songs:
                # Remove the song from the user's songs
                user.songs.remove(song)

                # Also, remove the song from all playlists associated with it
                for playlist in song.playlists:
                    playlist.pl_songs.remove(song)

                db.session.commit()
                flash('Song removed successfully!', 'success')
            else:
                flash('Song not found or does not belong to the logged-in user.', 'error')

        except Exception as e:
            db.session.rollback()
            print(song)
            flash(f'Error removing song: {str(e)}', 'error')

    return redirect(url_for('user_home'))

#playlist CRUD

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    
    if request.method == 'GET':
        email= session['user_email']
        password= session['user_password']
        user = db.session.query(User).filter_by(email=email, password=password).first()
        user_songs = db.session.query(Song).filter_by(creater_id=user.id).all()
        all_songs = db.session.query(Song).all() 
    
    
    
    if request.method == 'POST':
        playlist_name = request.form.get('playlist_name')
        selected_song_ids = request.form.getlist('songs[]')

        try:

            if not playlist_name or not selected_song_ids:
                flash('Playlist name and at least one song are required.', 'error')
                return redirect(url_for('user_home'))  

            
            email = session['user_email']
            user = db.session.query(User).filter_by(email=email).first()
            user_songs = db.session.query(Song).filter_by(creater_id=user.id).all()
            all_songs = db.session.query(Song).all()

            # Create playlist and store it to 'songs' table in DB
            playlist = Playlist(name=playlist_name)
            playlist.pl_songs = Song.query.filter(Song.id.in_(selected_song_ids)).all()
            

            # Add the playlist to the user's playlists
            user.playlists.append(playlist)

            # Commit all songs to playlist and  playlist to user in DB
            db.session.commit()
            # Fetch the updated list of playlists after committing
            user_playlists = db.session.query(Playlist).join(users).filter(users.c.user_id == user.id).all()
            flash('Playlist created successfully!', 'success')
            return redirect(url_for('user_home'))  # Replace with the actual route

        except Exception as e:
                db.session.rollback()
                flash(f'Error Creating playlist, try changing the playlist name : {str(e)}', 'error')
                return redirect(url_for('user_home'))


        

    return render_template('create_playlist.html', key=user.firstname, user_songs=user_songs, user_iscreator=user.is_creator, all_songs=all_songs, genre_songs=all_songs)



@app.route('/edit_song/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    song = db.session.query(Song).get(song_id)
    email = session['user_email']
    user = db.session.query(User).filter_by(email=email).first()
    album=db.session.query(Album).filter_by(id=song.album_id).first()
   
    if request.method == 'GET':
        # Read the content of the text file
        lyrics_path = song.lyrics
        with open(lyrics_path, 'r') as file:
            lyrics_content = file.read()


        return render_template('edit_song.html', song=song, song_lyrics_content=lyrics_content, user=user,)

    if request.method == 'POST':
        # Update song details based on the form data
        song = db.session.query(Song).get(song_id)
        song.name = request.form.get('song_name')
        album.artist = request.form.get('artist')

        # Update the content of the text file
        updated_lyrics_content = request.form.get('song_lyrics')
        lyrics_path = song.lyrics
        with open(lyrics_path, 'w') as file:
            file.write(updated_lyrics_content)

        # Handle file upload
        new_lyrics_file = request.files['new_lyrics_file']
        if new_lyrics_file:
            new_lyrics_path = os.path.join('static/uploads/lyrics', f'lyrics_{song.id}.txt')
            new_lyrics_file.save(new_lyrics_path)
            song.lyrics = new_lyrics_path

        db.session.commit()
        flash('Song updated successfully!', 'success')
        return redirect(url_for('user_home')) 
    
#Playlist Details Page

@app.route('/playlist/<int:playlist_id>')
def playlist_details(playlist_id):
    # Fetch the playlist based on the provided playlist_id
    playlist = Playlist.query.get(playlist_id)
    
    email = session['user_email']
    user = db.session.query(User).filter_by(email=email).first()
    all_songs = db.session.query(Song).all() 
   


    # Check if the playlist exists
    if not playlist:
        flash('Playlist not found.', 'error')
        return redirect(url_for('user_home'))  # Replace with the actual route

    # Render the playlist details template with the fetched playlist
    return render_template('playlist_detail.html', playlist=playlist, user=user, all_songs=all_songs)


    
# Edit Playlist
@app.route('/edit_playlist/<int:playlist_id>', methods=['GET', 'POST'])
def edit_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)

    if request.method == 'GET':
        all_songs = Song.query.all()  # Fetch all songs to display in the form
        return render_template('edit_playlist.html', playlist=playlist,all_songs= all_songs)
    
    if request.method == 'POST':
            try:    
                         
                    playlist = Playlist.query.get(playlist_id)        
                    selected_song_id = request.form.get('selected_song_id')
                    selected_song = Song.query.get(selected_song_id)
                    # Add the selected song to the playlist
                    playlist.pl_songs.append(selected_song)
                    db.session.commit()
                    flash('Song added to playlist successfully!', 'success')
                    return redirect(url_for('playlist_details', playlist_id=playlist_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error editing playlist: {str(e)}', 'error')
            return redirect(url_for('user_home'))



@app.route('/remove_song/<int:song_id>/<int:playlist_id>', methods=['GET'])
def remove_song(song_id, playlist_id):
    try:
        # Get the song by ID
        song = db.session.query(Song).filter_by(id=song_id).first()

        # Get the playlist by ID
        playlist = db.session.query(Playlist).filter_by(id=playlist_id).first()

        if song and playlist:
            # Check if the song is in the playlist
            if song in playlist.pl_songs:
                # Remove the song from the playlist
                playlist.pl_songs.remove(song)

                # Commit changes to the database
                db.session.commit()
                flash('Song removed from the playlist successfully!', 'success')
            else:
                flash('Song not found in the playlist.', 'error')
        else:
            flash('Song or playlist not found.', 'error')

    except Exception as e:
        db.session.rollback()
        flash(f'Error removing/adding song: {str(e)}', 'error')

    return redirect(url_for('user_home'))


#Likes of Songs

@app.route('/like_song/<int:song_id>', methods=['POST'])
def like_song(song_id):
    song = db.session.query(Song).filter_by(id=song_id).first()

    if song:
        try:
            # Increment the likes count
            song.likes += 1
            db.session.commit()
            flash('Song liked successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error liking song: {str(e)}', 'error')

    return redirect(url_for('songs', song_id=song_id))


#Rating a song


@app.route('/rate_song/<int:song_id>', methods=['POST'])
def rate_song(song_id):
    song = db.session.query(Song).filter_by(id=song_id).first()
    email = session['user_email']
    user = db.session.query(User).filter_by(email=email).first()

    if song:
        try:
            # Get the rating from the form data
            rating = int(request.form.get('rating'))
            
            # Create a new rating entry
            song_rating = SongRating(user_id=user.id, song_id=song.id, rating=rating)
            
            # Update the average rating
            song.ratings.append(song_rating)
            song.avg_rating = db.session.query(func.avg(SongRating.rating)).scalar()
            db.session.commit()
            flash('Song rated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error rating song: {str(e)}', 'error')

    return redirect(url_for('songs', song_id=song_id))      


#Likes of playlists

@app.route('/like_playlist/<int:playlist_id>', methods=['POST'])
def like_playlist(playlist_id):
    playlist = db.session.query(Playlist).filter_by(id=playlist_id).first()

    if playlist:
        try:
            # Increment the likes count
            playlist.likes += 1
            db.session.commit()
            flash('playlist liked successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error liking playlist: {str(e)}', 'error')

    return redirect(url_for('playlist_details', playlist_id=playlist_id))

#Rating a playlist


@app.route('/rate_playlist/<int:playlist_id>', methods=['POST'])
def rate_playlist(playlist_id):
    playlist = db.session.query(Playlist).filter_by(id=playlist_id).first()
    email = session['user_email']
    user = db.session.query(User).filter_by(email=email).first()

    if playlist:
        try:
            # Get the rating from the form data
            rating = int(request.form.get('rating'))
            
            # Create a new rating entry
            playlist_rating = PlaylistRating(user_id=user.id, playlist_id=playlist.id, rating=rating)
            
            # Update the average rating
            playlist.ratings.append(playlist_rating)
            playlist.avg_rating = db.session.query(func.avg(PlaylistRating.rating)).scalar()
            db.session.commit()
            flash('Playlist rated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error rating Playlist: {str(e)}', 'error')

    return redirect(url_for('playlist_details', playlist_id=playlist_id))

#Report Abusive Song
@app.route('/abusive_song/<int:song_id>', methods=['POST'])
def abusive_song(song_id):
    song = db.session.query(Song).filter_by(id=song_id).first()

    if song:
        try:
            # Increment the likes count
            song.is_abusive= 1
            db.session.commit()
            flash('Song reported abusive to admin!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error liking song: {str(e)}', 'error')

    return redirect(url_for('songs', song_id=song_id))

