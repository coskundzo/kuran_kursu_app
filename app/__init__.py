from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Lütfen giriş yapınız.'
    login_manager.login_message_category = 'warning'
    
    # Create upload folder if not exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes import auth, main, ogrenciler, egitmenler, dersler, aidat, siniflar
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(ogrenciler.bp)
    app.register_blueprint(egitmenler.bp)
    app.register_blueprint(dersler.bp)
    app.register_blueprint(aidat.bp)
    app.register_blueprint(siniflar.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters
    register_template_filters(app)
    
    # Shell context for flask cli
    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Ogrenci, Egitmen, Ders, Kurs, Sinif
        return {
            'db': db,
            'User': User,
            'Ogrenci': Ogrenci,
            'Egitmen': Egitmen,
            'Ders': Ders,
            'Kurs': Kurs,
            'Sinif': Sinif
        }
    
    return app


def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403


def register_template_filters(app):
    """Register custom template filters"""
    @app.template_filter('dbdate')
    def dbdate_filter(date_str):
        """Convert DD.MM.YYYY to YYYY-MM-DD"""
        if not date_str:
            return None
        parts = date_str.split('.')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return date_str
    
    @app.template_filter('displaydate')
    def displaydate_filter(date_obj):
        """Convert date object to DD.MM.YYYY"""
        if not date_obj:
            return ''
        return date_obj.strftime('%d.%m.%Y')
