# -*- coding:utf-8 -*-
"""
Generic neuron base classes
"""
from datetime import timedelta
import os


class ConfigBase(object):
    DEBUG = False
    TESTING = False
    USE_X_SENDFILE = False

    # DATABASE CONFIGURATION
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/project"
    SQLALCHEMY_ECHO = False
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = '$2a$12$iqP4vMXf60ih1NByMuFmy.'
    SECURITY_POST_LOGIN = '/'
    SECURITY_FLASH_MESSAGES = True
    CSRF_ENABLED = True
    SECRET_KEY = os.urandom(24)

    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # EMAIL CONFIGURATION
    MAIL_SERVER = "smtp.sendgrid.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEBUG = DEBUG
    MAIL_USERNAME = "rb-form-processor"
    MAIL_PASSWORD = "ff6845d6ac444bbb4c01e9df9a8666e6550c67f8e32bfe77'"
    DEFAULT_MAIL_SENDER = "nebula@rightbrain.com.mt"
    MAIL_RECIPIENTS = [
    ]

    BLUEPRINTS = [
    ]
    
    APIKEY = os.urandom(64).encode('hex')
    #SECURITY_LOGIN_USER_TEMPLATE = 'nebula/login.html'

    ERROR_TEMPLATES = {
        '404': 'nebula/error_404.html',
        '500': 'nebula/error_500.html',
        '403': 'nebula/error_403.html',
        '402': 'nebula/error_402.html'
    }

    ITEM_IMAGE_MAX_WIDTH = 400
    ITEM_IMAGE_MAX_HEIGHT = 400

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_POST_LOGIN_VIEW = '/dashboard'
    SECURITY_POST_REGISTER_VIEW = '/dashboard'


class ConfigDefault(ConfigBase):
    CLOUDFILES_ENABLED = False
    CACHE_TYPE = 'simple'
    LANG_DEFAULT = 'en'
    LANG_CODES = ['en','de']
    LANT_TITLES = {
        'en': "English",
        'de': "German"
    }
    BLUEPRINTS = [
    ]


class ConfigTest(ConfigBase):
    PROJECT_NAME = 'nebula'
    TESTING = True
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/nebula_test"
