from datetime import datetime, timedelta
import subprocess
from time import time, sleep
from random import randint
import urlparse
from flask.ext.script import Command, Option, Manager
from flask import current_app
from vircu import constants
from collections import namedtuple
from random import randint
from werkzeug.security import generate_password_hash
from sqlalchemy.sql.expression import func, distinct
import json
from vircu.common import simple_request_url, get_rounded_minute
from vircu.models import Exchange, ExchangeRate, ExchangeVolume
from vircu.config import config

manager = Manager()


class Versions(Command):
    @property
    def app(self):
        return current_app
    
    def run(self):
        self.build_version_file(self.get_versions())

    def local(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()

        if not err:
            err = None
        if not out:
            out = None

        return (out, err, p.poll())

    def get_versions(self):
        try:
            (out, err, returncode) = self.local('which git')
            if returncode > 0 or err is not None:
                raise Exception()
        except:
            raise Exception("can't use the `git` command")

        try:
            (out, err, returncode) = self.local('git log -1 --pretty="%H" .')
            if returncode > 0 or err is not None:
                raise Exception()
            else:
                MAIN_VERSION = out

            (out, err, returncode) = self.local('git log -1 --pretty="%H" ./vircu/static ./Gruntfile.js')
            if returncode > 0 or err is not None:
                raise Exception()
            else:
                STATIC_VERSION = out
        except:
            raise Exception("failed to get git versions")

        return {'main' : MAIN_VERSION[0:10], 'static' : STATIC_VERSION[0:10]}

    def build_version_file(self, versions = None):
        versions = versions or self.get_versions()
        self.local('echo "MAIN_VERSION=%s\nSTATIC_VERSION=%s" > ./VERSION' % (versions['main'], versions['static']))


manager.add_command("versions", Versions())
