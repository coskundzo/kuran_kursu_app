from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from config import config
import os
""" 
Bu dosya ekurs-flask kök paketini tanımlar. Uygulama factory fonksiyonu app/__init__.py'dedir.
"""
migrate = Migrate()
