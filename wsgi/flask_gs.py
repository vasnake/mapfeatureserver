#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r""" Global storage Flask extension.
In Flask, it's possible to store data across many requests.
But you must be aware of threading issues in that case.

Thanks to flask_sqlalchemy
https://github.com/mitsuhiko/flask-sqlalchemy/blob/master/flask_sqlalchemy.py

usage:
APP = Flask(__name__)
GS = flask_gs.VGlobalStorage(APP)
...
def getDataSource():
    conn = GS.getData('PGCONN') # Psycopg connection is thread-safe http://initd.org/psycopg/docs/usage.html#thread-safety
    if not conn:
        dsn = config.get('PGDSN')
        conn = postgis.PGConnection(dsn)
        GS.setData('PGCONN', conn)
    return conn


Copyright 2012-2013 Valentin Fedulov

This file is part of Mapfeatureserver.

Mapfeatureserver is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Mapfeatureserver is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Mapfeatureserver.  If not, see <http://www.gnu.org/licenses/>.
"""


from threading import Lock
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

EXTNAME = 'vglobalstorage'


class _VStorage(object):
    """ Storage dictionary
    """
    def __init__(self, app):
        self.app = app
        self.data = {}


class VGlobalStorage(object):
    """ Flask extension
    """

    def __init__(self, app=None):
        self._storage_lock = Lock()
        self.app = None
        if app is not None:
            self.app = app
            self.init_app(self.app)

    def init_app(self, app):
        """ Called from constructor, Flask need this.

        :param app: Flask app
        :type app: flask.Flask()
        """
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions[EXTNAME] = _VStorage(app)

    def getData(self, key):
        """ Getter, get stored data by key.

        :param key: any existed key for dictionary
        :type key: object
        """
        return self._get_data(self.get_app(), key)

    def setData(self, key, val):
        """ Setter, store data in dictionary.

        :param key: any key for dictionary
        :type key: object
        :param val: any value
        :type val: object
        """
        return self._set_data(self.get_app(), key, val)

    def _get_data(self, app, key):
        """ Internal getter.

        :param app: flask app
        :type app: flask.Flask()
        :param key: any dictionary key
        :type key: object
        """
        with self._storage_lock:
            stor = get_storage(app)
            return stor.data.get(key, None)

    def _set_data(self, app, key, val):
        """ Internal setter.

        :param app: flask app
        :type app: flask.Flask()
        :param key: any dictionary key
        :type key: object
        :param val: any value
        :type val: object
        """
        with self._storage_lock:
            stor = get_storage(app)
            stor.data[key] = val

    def get_app(self, reference_app=None):
        """ Return actual app object

        :param reference_app: flask app
        :type reference_app: flask.Flask()
        """
        if reference_app is not None:
            return reference_app
        if self.app is not None:
            return self.app
        ctx = stack.top
        if ctx is not None:
            return ctx.app
        raise RuntimeError('application not registered on gs '
            'instance and no application bound to current context')
#class VGlobalStorage(object):


def get_storage(app):
    """ Return storage object

    :param app: flask app
    :type app: flask.Flask()
    """
    return app.extensions[EXTNAME]
