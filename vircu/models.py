"""
This module contains all the database objects used in the app. If it starts to get
too big, please consider splitting it in more cohesive modules.
Also, please respect the alphabetical order of the classes!
"""
import re
import hashlib
import random
import sqlalchemy
import time
import json
import urllib
from datetime import datetime, timedelta
from flask import url_for, current_app as app, g, _request_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.util import aliased


from vircu.dt import utc_mktime


# if you need db access use this sqlalchemy instance
#   from vircu.models import db
# never instantiate this yourself
db = SQLAlchemy()


