#!/usr/bin/python
# -*- coding:utf-8 -*-
from ext.sys.config import ConfigBase
import os

project_name = "well-done"

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)+"/.."))
module_name = os.path.basename(os.path.dirname(__file__))
project_blueprint = module_name + '.project'

class Config(ConfigBase):
    PROJECT_NAME = project_name
    SITE_URL = 'http://localhost:5000'
    # SERVER_NAME = 'localhost'

    DEFAULT_GEOLOCATION = '35.897093411089784,14.511051302978558'

    BLUEPRINTS = [
        ( project_blueprint )
    ]

    TEMPLATE_DIRS = [
        os.path.dirname(__file__) + '/views',
    ]

    ROOT_LOCATION = os.path.dirname(__file__)

    CLOUDFILES_ENABLED = False
    CLOUDFILES_URI = 'http://d48a8df41bc0fa1e04e4-a0659a64b343eb265f1787aac259c325.r57.cf3.rackcdn.com'
    CLOUDFILES_CONTAINER = 'test'
    APIKEY = os.urandom(32).encode('hex')
    SECURITY_POST_LOGIN = '/'

    MEDIA_LOCATION = os.path.join(ROOT_LOCATION, 'media')
    STATIC_LOCATION = os.path.join(ROOT_LOCATION, 'static')

class Dev(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    CLOUDFILES_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/%s?charset=utf8&use_unicode=0" % project_name
    MAIL_RECIPIENTS = [
        "rouvenherzog@newstartprogramming.com"
    ]


class Production(Config):
    DEBUG = True
    SITE_URL = "http://welldone.rightbrain-nodes.com"
    SERVER_NAME = "welldone.rightbrain-nodes.com"
    TEMPLATE_DIRS = [
        '/var/www/well-done/app/views'
    ]
    MAIL_RECIPIENTS = [
        "rouvenherzog@newstartprogramming.com"
    ]

    ROOT_LOCATION = '/var/www/well-done/app'

    SQLALCHEMY_DATABASE_URI = "mysql://rouven:*(HH4SEdZaUewAAeDz)!@localhost/%s?charset=utf8&use_unicode=0" % "well-done"
    MEDIA_LOCATION = os.path.join(ROOT_LOCATION, 'media')
    STATIC_LOCATION = os.path.join(ROOT_LOCATION, 'static')


class Testing(Config):
    TESTING = True
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/%s" % project_name
    SQLALCHEMY_ECHO = False
