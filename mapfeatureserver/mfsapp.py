#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r""" Flask web app for Map Feature Server.
Free featureserver implementation for Esri REST API
http://resources.arcgis.com/en/help/rest/apiref/index.html?featureserver.html

psycopg2 for Windows http://www.stickpeople.com/projects/python/win-psycopg/

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

import os
import re
from flask import (Flask, request, url_for, render_template, send_from_directory,
    make_response)
from flask.ext.sqlalchemy import SQLAlchemy
#~ import simplejson


CP = 'utf-8'
APP = Flask(__name__)
DB = SQLAlchemy(APP)


################################################################################


from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    """ CORS headers decorator
    http://flask.pocoo.org/snippets/56/

    usage example
        @APP.route('/<int:layerid>', methods=['GET', 'POST', 'OPTIONS'])
        @crossdomain(origin='*')
        def myroute(layerid=0): ...

    Javascript app settings according to https://developers.arcgis.com/en/javascript/jshelp/inside_esri_request.html
        require(["esri/config"], function(esriConfig) {
          esriConfig.defaults.io.corsEnabledServers.push("vdesk.algis.com:5000");
            esriConfig.defaults.io.corsEnabledServers.push("vdesk.algis.com");
        });
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods
        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


################################################################################


@APP.route('/')
def indexPage():
    """ List of all MFS endpoints, plus example urls. For demo purposes only.
    Also it's a pages/routes directory.
    """
    links = []
    for itm in ('indexPage', 'helpPage', 'favicon', 'clientaccesspolicy'):
        # static pages
        links.append((url_for(itm), ''))

    return render_template('servlets.html', lst=links)
#def indexPage():


@APP.route('/help')
def helpPage():
    """ Show info page about service
    """
    return render_template("help.html")
#def helpPage():


@APP.route('/favicon.ico')
def favicon():
    """ In debug mode, send favicon
    """
    return sendStatic('favicon.ico', 'image/vnd.microsoft.icon')


@APP.route('/clientaccesspolicy.xml')
def clientaccesspolicy():
    """ In debug mode, send clientaccesspolicy.xml
    """
    return sendStatic('clientaccesspolicy.xml', 'text/xml')


@APP.route('/services/mfs/FeatureServer/<int:layerid>')
@APP.route('/<int:layerid>', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*')
def layerMeta(layerid=0):
    """ Esri API, process requests to layer by Layer ID
    http://resources.arcgis.com/en/help/rest/apiref/fslayer.html

    Known requests example
    .../FeatureServer/0?f=pjson

    f=pjson by default
    """
    with open('c:/d/code/git/mapfeatureserver/t/testmeta.json') as fh:
        txt = fh.read().strip().decode(CP)
    return jsonRespFromText(txt)
#def layerMeta(layerid=0):


@APP.route('/services/mfs/FeatureServer/<int:layerid>/<operation>', methods=['GET', 'POST'])
@APP.route('/<int:layerid>/<operation>', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain(origin='*')
def layerOperations(layerid=0, operation='query'):
    """ Esri API, process all operations for layer by Layer ID and operation name.
    Only 'query' operation implemented by now.

    http://resources.arcgis.com/en/help/rest/apiref/fslayer.html
    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html#response

    Known request example
    .../FeatureServer/0/query?returnGeometry=true
        &geometryType=esriGeometryEnvelope
        &geometry={"xmin":-7182265.21424325,"ymin":-1567516.84684806,"xmax":17864620.2142433,"ymax":14321601.0968481,"spatialReference":{"wkid":102100}}
        &inSR=102100
        &spatialRel=esriSpatialRelIntersects
        &outSR=102100
        &outFields=*
        &f=pjson

    f=pjson by default
    """
    with open('c:/d/code/git/mapfeatureserver/t/testdata.json') as fh:
        txt = fh.read().strip().decode(CP)
    return jsonRespFromText(txt)
#def layerOperations(layerid=0, operation='query'):


################################################################################


def jsonRespFromText(txt):
    """ Return Flask response = make_response(txt)
    with custom headers and wrappers
    """
    # JSONP
    callback = request.args.get('callback', '')
    if callback:
        # Verify that the callback is secure
        if re.compile(r'^[a-zA-Z][\w.]*$').match(callback):
            txt = u'%s(%s);' % (callback, txt)

    resp = make_response(txt)
    # mime = 'text/javascript' if settings.DEBUG else 'application/json'
    resp.headers['Content-Type'] = 'text/plain;charset=utf-8'
    return resp
#def jsonRespFromText(txt):


def sendStatic(filename, mimetype):
    """ send file from app 'static' folder
    """
    return send_from_directory(os.path.join(APP.root_path, 'static'),
       filename, mimetype=mimetype)


def main():
    """ Flask app web server. TCP port 5000
    """
    APP.run(host='0.0.0.0', debug=True, threaded=True, use_reloader=False)
    APP.logger.debug('app started')
