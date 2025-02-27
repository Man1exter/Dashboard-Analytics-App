import os
from datetime import timedelta

class Config:
    """Podstawowa konfiguracja aplikacji"""
    # Ścieżka do katalogu głównego aplikacji
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # Konfiguracja tajnego klucza
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-secret-key-for-development'
    
    # Konfiguracja bazy danych
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfiguracja poczty
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@dashboard-analytics.com')
    
    # Konfiguracja JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Konfiguracja uploadów
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'txt'}
    
    # Konfiguracja cache
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minut
    
    # Konfiguracja kompresji
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    # Konfiguracja limitów API
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Konfiguracja systemu
    DASHBOARD_THEMES = ['light', 'dark', 'blue', 'green', 'orange', 'purple']
    DEFAULT_DASHBOARD_LAYOUT = 'grid'
    MAX_DASHBOARDS_PER_USER = 50  # Dla planu darmowego
    MAX_WIDGETS_PER_DASHBOARD = 20
    
    # Domyślne opcje wizualizacji
    DEFAULT_CHART_COLORS = [
        '#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52'
    ]
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Konfiguracja dla środowiska deweloperskiego"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(Config.BASEDIR, 'app-dev.db')
    
    # Dodatkowe opcje deweloperskie
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0  # Wyłączenie cache dla plików statycznych w trakcie rozwoju
    
    # Konfiguracja logowania
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Konfiguracja dla środowiska testowego"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(Config.BASEDIR, 'app-test.db')
    
    # Wyłączenie ochrony CSRF dla testów
    WTF_CSRF_ENABLED = False
    
    # Szybsza praca z hashowaniem haseł w testach
    BCRYPT_LOG_ROUNDS = 4
    
    # Konfiguracja dla testów
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Symulacja wysyłania e-maili
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    """Konfiguracja dla środowiska produkcyjnego"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/dashboard_analytics'
    
    # Konfiguracja bezpieczeństwa
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Konfiguracja cache
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Konfiguracja logowania
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Logowanie do pliku/syslog w produkcji
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler('logs/dashboard-analytics.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Dashboard Analytics startup')


class DockerConfig(ProductionConfig):
    """Konfiguracja dla środowiska Docker"""
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Przekierowanie logów do stdout dla Dockera
        import logging
        from logging import StreamHandler
        
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}