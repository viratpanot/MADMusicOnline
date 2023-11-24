from flask import request, Flask, flash, session
from flask import render_template, url_for, redirect
from flask import current_app as app 
from application.models import *
from flask_basicauth import BasicAuth
from mutagen.mp3 import MP3


@app.route("/", methods = ['GET', 'POST'])
def home_page():
    if request.method == 'GET' :
        return render_template('home.html')
    if request.method == 'POST' :
        return url_for(registration)
    

basic_auth = BasicAuth(app)
@app.route("/admin", methods = ['GET', 'POST'])
@basic_auth.required
def admin_login():
    if request.method == 'GET' :
        return render_template('admn_login.html')
    if request.method == 'POST' :
        uname = request.form.get("username")
        pwd = request.form.get("password")
        print(request.form)
        if uname == 'virat'  and pwd == 'jain' : 
            app.logger.info(f"Login successful for {uname}")
            return render_template('admin_dashboard.html', key='ADMIN PAGE')
        else:
            flash('Invalid email or password. Please try again.')
            app.logger.warning(f"Login failed for {uname}")
            flash('Wrong admin password or username, please check with admin Virat for correct credentials')
            return redirect(url_for("home_page"))



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
       
        #email=request.form.get("email"),
        #print(db.session.query(User).filter_by(email=email).first())
        #if (email == db.session.query(User).filter_by(email=email).first().email):
            #db.session.close()
            #return render_template('registration_except.html')
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







@app.route("/user_login", methods = ['GET', 'POST'])
def user_login():
  

    if request.method == 'POST':
        email = request.form.get("email")
        user = db.session.query(User).filter_by(email=email).first()

        if user and (user.password == request.form.get("password")):
            app.logger.info(f"Login successful for {email}")
            session['user_email'] = user.email
            session['user_firstname'] = user.firstname
            session['user_password'] = user.password
            user_song = db.session.query(Song).filter_by(creater_id=user.id).all()
            return render_template('user_dashboard.html', key=user.firstname, user_songs = user_song)

        else:
            flash('Invalid email or password. Please try again. or register')
            app.logger.warning(f"Login failed for {email}")
            return redirect(url_for("user_login"))

    if  request.method == 'GET':
        return render_template('usr_login.html')

@app.route('/user_home')
def user_home():
    # Add logic to fetch user data or perform other actions if needed
    email= session['user_email']
    password= session['user_password']
    user = db.session.query(User).filter_by(email=email, password=password).first()
    # Render the user's home page template
    user_song = db.session.query(Song).filter_by(creater_id=user.id).all()
    return render_template('user_dashboard.html', key=user.firstname, user_songs = user_song)

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

                # Create a new album instance
                new_album = Album(name=album_name, genre=album_genre, artist=album_artist, creater_id= user.id)  # Set creater_id as needed

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
                    lyrics_file = lyrics_files[i]
                    song_file = song_files[i]
                    

                    # Save the uploaded files to the server (you might want to use a more secure method)
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
                        album_id=new_album.id  # Link the song to the newly created album
                    )

                    # Add the song to the database
                    db.session.add(new_song)
                    db.session.commit()
                app.logger.info(f"upload successful for {email}")
                flash('Album and songs uploaded successfully!', 'success')
                user_song = db.session.query(Song).filter_by(creater_id=user.id).all() #ignore creater spelling :)
                return render_template('user_dashboard.html', key=user.firstname, user_songs = user_song )
  

        except Exception as e:
            print(e)
            flash('Error uploading album and songs.', 'error')
            return redirect(url_for('upload'))

@app.route('/song/<int:song_id>',methods = ['GET', 'POST'] )
def song(song_id):
    email= session['user_email']
    user = db.session.query(User).filter_by(email=email).first()
    song = db.session.query(Song).filter_by(id=song_id).first()
    album=db.session.query(Album).filter_by(id=song.album_id).first()
    
    # Read the content of the text file
    lyrics_path = song.lyrics
    with open(lyrics_path, 'r') as file:
        lyrics_content = file.read()

    return render_template('song_detail.html', song=song, lyrics_content=lyrics_content, user=user , id =song.creater_id, album=album )
