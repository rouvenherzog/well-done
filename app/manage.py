# -*- coding:utf-8 -*-
import sys
import os
from flask.ext import script
from ext.sys import commands

if __name__ == "__main__":
    from ext.sys.main import app_factory
    import config
    manager = script.Manager(app_factory)
    manager.add_option(
        "-c", "--config", dest="config", required=False, default=config.Dev)
    manager.add_command("test", commands.Test())
    manager.add_command("create_db", commands.CreateDB())
    manager.add_command("drop_db", commands.DropDB())
    manager.add_command('create_super_admin', commands.CreateSuperAdmin())
    manager.add_command('cache_items', commands.CacheItems())
    manager.add_command('compare_cache', commands.CompareCache())
    manager.add_command('create_sqllite_db', commands.CreateSqlliteDB())
    manager.add_command('create_flask_security_user', commands.CreateFlaskSecurityUser())
    manager.run()
