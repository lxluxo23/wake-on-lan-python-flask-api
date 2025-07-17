from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from app.models import db
from config import config

migrate = Migrate()
bcrypt = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    CORS(app)
    
    from app.auth import auth
    from app.routes import main
    from app.api import api
    from app import commands
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(api)
    
    # Registrar comandos personalizados
    commands.init_app(app)
    
    return app