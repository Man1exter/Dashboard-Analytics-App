import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_compress import Compress
from flask_assets import Environment

# Inicjalizacja rozszerzeń Flaska
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
cache = Cache()
compress = Compress()
assets = Environment()

def create_app(config_class="config.DevelopmentConfig"):
    """Fabryka aplikacji - tworzy i konfiguruje aplikację Flask"""
    app = Flask(__name__)
    
    # Ładowanie konfiguracji
    app.config.from_object(config_class)
    
    # Inicjalizacja rozszerzeń
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    compress.init_app(app)
    assets.init_app(app)
    
    # Konfiguracja CORS
    CORS(app)
    
    # Konfiguracja LoginManagera
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Proszę się zalogować, aby uzyskać dostęp do tej strony.'
    login_manager.login_message_category = 'info'
    
    # Rejestrowanie blueprintów
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from app.data import bp as data_bp
    app.register_blueprint(data_bp, url_prefix='/data')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Obsługa błędów
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    
    # Tworzenie folderów, jeśli nie istnieją
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'exports'), exist_ok=True)
    
    # Kompilacja assetów (CSS, JS)
    from app.assets import compile_assets
    compile_assets(assets)
    
    return app

# Import modeli aby były dostępne dla migracji
from app.auth.models import User
from app.dashboard.models import Dashboard, Widget, DataSource