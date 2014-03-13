# -*- coding:utf-8 -*-

"""
General neuron commands
"""
from flask.ext.script import Command, Option, prompt_bool
import sys
import os
import config


class CreateDB(Command):

    """
    Creates sqlalchemy database
    """

    def run(self):
        from ext.sys.database import db, create_all

        print "Tables binded :"
        for table in db.get_tables_for_bind() :
            print "#    %s" % table
        print "DB Engine :      %s" % db.get_engine( db.app )
        print "Creating Tables. Hang on.."
        print "Create all result :  %s" % create_all()
        print "==== all db created ====="

class CreateSqlliteDB(Command):

    """
    Creates sqlalchemy database
    """

    def run(self):
        from ext.sys.database import db, create_all

        print dir(db)
        return
        
        print "Tables binded :"
        for table in db.get_tables_for_bind() :
            print "#    %s" % table
        print "DB Engine :      %s" % db.get_engine( db.app )
        print "Creating Tables. Hang on.."
        print "Create all result :  %s" % create_all()
        print "==== all db created ====="

class CreateFlaskSecurityUser(Command):

    """
    Create a Flask Security User to pass require_login
    """

    def run(self):
        from ext.sys.database import db
        from flask import current_app
        from flask.ext.security.utils import encrypt_password

        current_app.security.datastore.create_user(
            email='email@email.com', 
            password=encrypt_password('password')
        )
        db.session.commit()


class DropDB(Command):

    """
    Drops sqlalchemy database
    """

    def run(self):
        from ext.sys.database import db, drop_all

        print "Tables binded :"
        for table in db.get_tables_for_bind() :
            print "#    %s" % table
        print "DB Engine :      %s" % db.get_engine( db.app )
        print "Dropping Tables. Hang on.."
        print "Drop all result :    %s" % drop_all()
        print "==== all db dropped ====="


class Test(Command):

    """
    Run tests
    """

    start_discovery_dir = "tests"

    def get_options(self):
        return [
            Option('--start_discover', '-s', dest='start_discovery',
                   help='Pattern to search for features',
                   default=self.start_discovery_dir),
        ]

    def run(self, start_discovery):
        import unittest

        if os.path.exists(start_discovery):
            argv = [config.project_name, "discover"]
            argv += ["-s", start_discovery]

            unittest.main(argv=argv)
        else:
            print("Directory '%s' was not found in project root." %
                  start_discovery)


class CreateSuperAdmin(Command):

    """
    Creates The SuperAdmin Account
    """

    def __init__(self):
        pass

    def run(self):
        from nebula.users.models import User
        from nebula.shops.models.shop import Shop, ShopCategory
        from hashlib import sha256
        from ext.sys.database import db

        print "Creating super admin account.."

        first_name = raw_input("First name: ")
        last_name = raw_input("Last name: ")
        email = raw_input("Email Address: ")
        _password = raw_input("Password: ")
        _password2 = raw_input("Confirm Password: ")


        if _password != _password2:
            print 'Passwords dont match'
            sys.exit(0)

        password = sha256(_password).hexdigest()

        user = User.query.filter( User.email == email ).filter( User.password == password ).first()
        if not user:
            user = User()
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.password = password

        shop = user.shops.first()
        if not shop:
            shop = Shop( {'name': 'Simple Shop'} )
            shop.user = user
            db.session.add( shop )

        category = shop.categories.first()
        if not category:
            category = ShopCategory({'name': 'Products'})
            category.shop = shop
            db.session.add( category )

        if user.permissions.count() == 0:
            from nebula.api import API
            user.permissions = API.init_resources()

        db.session.add( user )
        db.session.commit()

        print "Super Admin " + user.email + " created."


class SyncLocalFiles(Command):

    """
    Syncs local media files with database
    """

    def run(self):

        from flask import current_app
        self.app = current_app
        self.root_dir = self.app.config['ROOT_LOCATION']

        from ext.sys.database import db
        from explorer import File, create_path, get_files_list

        print 'Indexing Local Files'
        file_list = get_files_list(self.root_dir)

        # refactor file_list
        file_list_local = [f.replace(self.root_dir, '') for f in file_list]

        # get database entries that match the local_list
        db_list = db.session.query(File) \
            .filter(File.path.in_(file_list_local)).all()

        file_list_db = [f.path for f in db_list]
        final_list = [f for f in file_list_local if f not in file_list_db]

        for file in final_list:
            create_path(self.root_dir, os.path.join(
                self.app.config['MEDIA_LOCATION'], file))

        print 'Indexing Done'

class CacheItems(Command):
    def run(self):
        from nebula.shops.models.shop import Item
        from nebula.cache import rediscache

        result = []
        items = Item.query.all()
        for item in items:
            result.append(item)
        rediscache.set('items', result)

class CompareCache(Command):
    def run(self):
        from nebula.shops.models.shop import Item
        from nebula.cache import rediscache
        from datetime import datetime
        from sqlalchemy import or_
        import re

        query = "WORLD"

        start = datetime.now()
        items = Item.query.filter(or_(
            Item.name.like('%{0}%'.format(query)),
            Item.description.like('%{0}%'.format(query))
            )).all()
        end_sql  = (datetime.now()-start).microseconds

        result = []
        items = Item.query.all()
        for item in items:
            _i = item.serialize
            _i["body"] = "{0} {1}".format(item.name, item.description)
            result.append(_i)
        rediscache.set('items', result)

        start = datetime.now()
        items = rediscache.get('items')
        result = [ item for item in items if re.match(query, item['body']) ]
        end_cache = (datetime.now()-start).microseconds

        print "SQL TOOK", end_sql, "MS"
        print "CACHE TOOK", end_cache, "MS"
        print "CACHE IS", float(end_sql)/float(end_cache), "TIMES FASTER"


class GeneratePreviews(Command):

    """
    Generate image previews for admin use
    """

    root_dir = None
    parent_loc = None

    def run(self):
        from explorer import File, make_preview
        from ext.sys.database import db
        from flask import current_app as app
        self.root_dir = app.config['MEDIA_LOCATION']

        img_types = ['jpg', 'bmp', 'gif', 'png', 'jpeg']
        previews_path = os.path.join(self.root_dir, '_previews')
        if not os.path.exists(previews_path):
            os.mkdir(previews_path)

        parent = False
        if self.parent_loc is not None:
            if not isinstance(self.parent_loc, File):
                parent = self.parent_loc
            else:
                parent = file_exists_in_db(self.parent_loc)

        query = db.session.query(File) \
            .filter(File.dir == False) \
            .filter(File.hidden == False) \
            .filter(File.local == True) \
            .filter(File.has_preview == False) \
            .filter(File.ext.in_(img_types))

        if parent != False:
            query.filter(File.parent_id == parent.id)

        files = query.all()
        for file in files:
            full_path = self.root_dir + file.path
            # try:
            make_preview(self.root_dir, file, full_path, previews_path)
            file.has_preview = True
            db.session.add(file)
            print "Generating Preview For %s" % (full_path)
            # except:
            #	print 'Error In Generating Preview For %s' % full_path

        db.session.commit()


class SyncCloudFiles(Command):

    """
    Syncs local media with rackspace cloudfiles
    """

    cloudfiles_container = None
    delete_local = False

    root_dir = None

    def run(self):
        from flask import current_app as app
        from utils.cloud import cloudfiles
        from ext.sys.database import db
        from explorer import File
        session = db.session

        self.root_dir = app.config['ROOT_LOCATION']
        container = cloudfiles.container

        CLOUDFILES = []
        # get online file list from container, those matched from cloud should
        # be marked as not local in db
        marker = ""

        while True:
            batch = container.list_objects(marker=marker)
            if len(batch) > 0:
                CLOUDFILES += batch
                marker = CLOUDFILES[-1]
            else:
                break

        print 'Total Files in Cloud: %s' % str(len(CLOUDFILES))

        c_files = ["/%s" % f for f in CLOUDFILES]
        res = session.query(File).filter(File.path.in_(c_files)) \
            .filter(File.local == True) \
            .update({'local': False}, synchronize_session=False)

        print '%s Files Were set as Non Local' % str(res)
        print '-'

        files = session.query(File) \
            .filter(File.local == True) \
            .filter(File.path != '/').all()

        for file in files:
            cloud_file = file.path[1:len(file.path)]
            local_path = self.root_dir + file.path
            try:
                obj = container.create_object(cloud_file)
                if file.dir:
                    obj.content_type = 'application/directory'
                    obj.sync_metadata()
                    obj.write()
                else:
                    obj.load_from_filename(local_path)
                    if self.delete_local:
                        os.rm(local_path)
                        print 'Removed local file: %s' % local_path

                file.local = False
                session.add(file)
                session.commit()
                print 'Uploaded: %s' % local_path
            except:
                print 'Failed To Upload: %s' % local_path


class BuildStatic(Command):

    def run(self):
        from flask import current_app as app
        import os
        static_folders = []

        for key in app.blueprints:
            bl = app.blueprints[key]
            static_folders.append(bl.static_folder)
