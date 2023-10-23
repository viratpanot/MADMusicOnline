import os
from flask import Flask
from application import config
from application.config import LocalDevConfig
from application.database import db 

app = None

def generate_application():
    app = Flask (__name__ , template_folder= "templates")
    if os.getenv('ENV' , "development") == "production" :
        raise Exception("Curruntly running on local environment only, No production environment setup.")

    else:
        print("Turning on local development environment")
        app.config.from_object(LocalDevConfig)
    db.init_app(app)
    app.app_context().push()
    return app

app = generate_application()

from application.controllers import *


    

if __name__ =="__main__" :
    app.run(debug=True)

