#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r""" Map Feature Server module.
PostGIS related functions.

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

import sys
import simplejson

import psycopg2
import psycopg2.extensions  # always unicode output
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

import esri
import mfslib
import layermeta

CP = 'UTF-8'

PGTEXT_LENGTH = 4000
# Field Length parameter for Postgres 'text' fields mapped to esriFieldTypeString
# maybe we should map 'text' to esriFieldTypeBlob

COLTYPESGEOM = (16912, 16397)
# Geometry columns type_code values

TYPECODE2ESRI = {23: u"esriFieldTypeInteger", 21: u"esriFieldTypeSmallInteger",
                 1043: u"esriFieldTypeString", 25: u"esriFieldTypeString",
                 1700: u"esriFieldTypeDouble", 1114: u"esriFieldTypeDate"}
# Map type_code to Esri types. esriFieldTypeOID == esriFieldTypeInteger
# 25 is PG 'text' type, maybe we should map 'text' to esriFieldTypeBlob

FIELDTYPENAME2ESRI = {'geography': u'esriFieldTypeGeometry', 'geometry': u'esriFieldTypeGeometry',
    'int4': u'esriFieldTypeInteger', 'int2': u'esriFieldTypeSmallInteger',
    'varchar': u'esriFieldTypeString', 'numeric': u'esriFieldTypeDouble',
    'text': u'esriFieldTypeString', 'timestamp': u'esriFieldTypeDate'}
# Map information_schema.columns.udt_name to Esri field type


class PGConnection(object):
    """ PostgreSQL connection wrapper """

    def __init__(self, dsn, app=None):
        self.app = app
        self.dsn = "host=vags101 port=5432 dbname=postgisdb user=mfs password=12345678 connect_timeout=10 client_encoding=utf8"
        if dsn:
            self.dsn = dsn
        self.conn = psycopg2.connect(self.dsn)
        self.conn.autocommit = True

        if self.app:
            self.app.logger.debug('PGConnection, PG connect open')
        print 'PGConnection, PG connect open'

    def __del__(self):
        self.conn.close()

        if self.app:
            self.app.logger.debug('PGConnection, PG connect close')
        print 'PGConnection, PG connect close'
#class PGConnection(object):


class DataSource(mfslib.IDataSource):
    """ Contain connection and connection.cursor for PostgreSQL.
    Cursor opens in constructor and closes in destructor.

    from flask_psycopg2 import Psycopg2
    conn = Psycopg2.connection
    """
    def __init__(self, conn):
        self.conn = conn
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        super(DataSource, self).__init__()

    def __del__(self):
        self.cursor.close()
#class DataSource(object):


def printCur(cur):
    """ Print cursor content """
    for rec in cur.description:
        print rec
    for rec in cur:
        map(lambda a: (sys.stdout.write((u"'%s', " % a).encode('utf8'))), rec)
        #[sys.stdout.write((u"'%s', " % x).encode(CP)) for x in rec]
        print


def postgisSRID(wkid):
    """ Return PostGIS SRID for Esri spatref WKID
    """
    if int(wkid) == 102100:
        return 3857
    return wkid


def layerRealExtent(ds, tabname, fname):
    """ PostGIS query.
    Extract layer extent in JSON format

    Args:
        ds: postgis.DataSource with db connection.cursor;
        tabname: db table name;
        fname: geometry field name.

    Returns:
        JSON text with 'extent' structure according ArcGIS spec
        http://resources.arcgis.com/en/help/rest/apiref/geometry.html#envelope
    """
    #if 0: ds = postgis.DataSource('')
    res = u"""
        "extent": {
          "xmin": %.15f,
          "ymin": %.15f,
          "xmax": %.15f,
          "ymax": %.15f,
          "spatialReference": {
           "wkid": %s,
           "latestWkid": %s
          }
         }
    """

    sql = '''SELECT st_xmin(ext) as xmin, st_ymin(ext) as ymin, st_xmax(ext) as xmax, st_ymax(ext) as ymax from
    (select ST_Extent(%s::geometry) as ext FROM %s) bbox;
    ''' % (fname, tabname)
    ds.cursor.execute(sql)
    xmin, ymin, xmax, ymax = ds.cursor.fetchone()

    sql = '''select st_srid(geom) as srid from
    (select %s::geometry as geom from %s fetch first row only) as rec;
    ''' % (fname, tabname)
    ds.cursor.execute(sql)
    srid, = ds.cursor.fetchone()

    res = res % (xmin, ymin, xmax, ymax, srid, srid)
    return res
#def layerRealExtent():


def tableFields4esri(ds, tabname, oidfname):
    """ PostGIS query.
    Extract fields spec in JSON format.

    Args:
        ds: postgis.DataSource with db connection.cursor;
        tabname: db table name;
        oidfname: OBJECTID field name.

    Returns:
        JSON text with 'fields' structure according ArcGIS spec
        http://resources.arcgis.com/en/help/rest/apiref/fslayer.html
        Plus, objectIdField layer property.
    """
    #if 0: ds = DataSource('')
    assert isinstance(ds, DataSource)
    cur = ds.cursor

    sql = """select column_name, is_nullable, data_type, udt_name, character_maximum_length,
        numeric_precision, numeric_scale
        from information_schema.columns where table_name like '%s';""" % tabname
    cur.execute(sql)

    nullable = {'YES': True, 'NO': False}

    data = []
    for rec in cur:
#        print rec # (u'testtext', u'YES', u'text', u'text', None, None, None) # esriFieldTypeString or esriFieldTypeBlob?
        # (u'shotspacin', u'YES', u'numeric', u'numeric', None, None, None) # esriFieldTypeDouble
        # (u'geom', u'YES', u'USER-DEFINED', u'geometry', None, None, None)
        ftype = FIELDTYPENAME2ESRI[rec[3]]
        if ftype == u'esriFieldTypeGeometry':
            continue

        obj = {u'name': rec[0], u'type': ftype, u'alias': rec[0].upper(), u'domain': None,
            u'editable': False, u'nullable': nullable[rec[1]]}

        if obj[u'type'] == u'esriFieldTypeString':
            obj[u'length'] = rec[4]
            if rec[3] == u'text':  # maybe we should use esriFieldTypeBlob
                obj[u'length'] = PGTEXT_LENGTH

        if oidfname.lower() == obj[u'name'].lower():
            obj = {u'name': rec[0], u'type': u'esriFieldTypeOID', u'alias': u'OBJECTID',
            u'domain': None, u'editable': False, u'nullable': False}

        data.append(obj)

    return simplejson.dumps({'objectIdField': oidfname, 'fields': data},
                      ensure_ascii=False, sort_keys=True, indent=2)
#def tableFields4esri(cur, tabname):


def sqlSelectAllByBox(lyrinfo, outSrid, box):
    """ Return SQL text for 'select *, shape ...' query with spatial filter.
    Field 'shape' is st_asgeojson text for geometry field.

        Args:
            lyrinfo: DBLayerInfo object with
                LayerInfo.tabname: layer table name;
                LayerInfo.geomfield: name for table field with geometry;
                LayerInfo.oidfield: name for field with OBJECTID;
            outSrid: integer, PostGIS srid for output projection;
            box: AGGeometryBox with xmin, xmax, ymin, ymax, srWkid attributes;

    # intersect
    sql = "select *, st_asgeojson(1, st_transform(%s::geometry, %s)) shape
        from %s where %s::geometry && ST_transform(
        ST_GeomFromText('POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))', %s)
        , st_srid(%s::geometry) )
        order by %s limit 1000;
        " % (lyrinfo.geomfield, outSrid, lyrinfo.tabname, lyrinfo.geomfield,
            box.xmin, box.ymin, box.xmax, box.ymin, box.xmax, box.ymax, box.xmin, box.ymax, box.xmin, box.ymin,
            box.pgSrid, lyrinfo.geomfield, lyrinfo.oidfield)
    """
    assert isinstance(lyrinfo, layermeta.DBLayerInfo)
    box.pgSrid = postgisSRID(box.srWkid)
    # contain
    sql = """select *, st_asgeojson(1, st_transform(%s::geometry, %s)) shape
        from %s
        where not st_disjoint(
            %s::geometry
            , ST_transform(
                ST_GeomFromText('POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))', %s)
                , st_srid(%s::geometry) )
        ) order by %s limit 1000;
        """ % (lyrinfo.geomfield, outSrid, lyrinfo.tabname, lyrinfo.geomfield,
            box.xmin, box.ymin, box.xmax, box.ymin, box.xmax, box.ymax, box.xmin, box.ymax, box.xmin, box.ymin,
            box.pgSrid, lyrinfo.geomfield, lyrinfo.oidfield)
    return sql
#def sqlSelectAllByBox(lyrinfo, outSrid, box):


def fieldFromDescr(col, oidfield):
    """ Return field description as dictionary in form that Esri require
    {name, alias, type, length if type is string or date}.
    Return None if field contains geometry.
    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html

    Args:
        col: Pg cursor.description[n]
        oidfield: OBJECTID field name

    TODO: rewrite function, field parameters must be parsed from layer metadata from layer config.
    Field alias and type actually.
    """
#    print col
    # PG field type 'text':
    # Column(name='testtext', type_code=25, display_size=None, internal_size=-1, precision=None, scale=None, null_ok=None)
    # Column(name='shape', type_code=25, display_size=None, internal_size=-1, precision=None, scale=None, null_ok=None)
    if col.type_code in COLTYPESGEOM or unicode(col.name) == u'shape':
        return None

    ftype = TYPECODE2ESRI[col.type_code]
    falias = col.name
    if falias.lower() == oidfield.lower():
        falias = u'OBJECTID'
        ftype = u'esriFieldTypeOID'

    fld = {'name': col.name, 'alias': falias.upper(), 'type': ftype}
    if ftype in esri.ESRI_FIELDS_WITH_LENGTH:
        fld['length'] = col.internal_size
        if col.internal_size == -1:  # 'text' field type, actually it's a blob
            fld['length'] = PGTEXT_LENGTH

    return fld
#def fieldFromDescr(col, oidfield):


def attrFieldsFromDescr(cur, lyrinfo):
    """ Return array of fields descriptions as described in ArcGIS spec.
    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html

    Args:
        cur: Pg connection.cursor with cur.description tuple
        lyrinfo: DBLayerInfo object with
            LayerInfo.oidfield: name for field with OBJECTID
    """
    fields = []
    for col in cur.description:
        #~ print "name: '%s', alias: '%s', type: '%s', length '%s'" % (col.name, col.name, col.type_code, col.internal_size)
        fld = fieldFromDescr(col, lyrinfo.oidfield)
        if fld:
            fields.append(fld)
    return fields
#def attrFieldsFromDescr(cur):


def featuresFromCursor(cur):
    """ Parse cursor records and return (geometryType, features) tuple
    where geometryType is string and features is array according to
    ArcGIS spec http://resources.arcgis.com/en/help/rest/apiref/fsquery.html#response

    "geometryType": "esriGeometryPoint",
    "features": [ { "attributes": {..., "geometry": {...

    Args:
        cur: Pg connection.cursor with dataset

    TODO: rewrite function, fields must be parsed according layer metadata from layer config.
    No extra attributes like shape_leng
    """
    #"geometryType": "esriGeometryPoint",   - из первой же записи выборки, поле «shape»
    geometryType = ''
    #"features": [   { "attributes": {...,   "geometry": {...   - из результатов запроса.
    features = []
    for rec in cur:
#        print rec
        fitem = {}  # feature attributes, geometry
        attributes = {}
        geometry = {}

        columns = lambda a: (zip(range(len(a)), a))
        for colnum, col in columns(cur.description):
#            print col
            if unicode(col.name) == u'shape':  # geometry
                shape = simplejson.loads(rec[colnum])
                geometryType, geometry = esri.geoJson2agJson(shape)
                continue
            if col.type_code in COLTYPESGEOM:
                continue
            attributes[col.name] = rec[colnum]

        fitem["attributes"] = attributes
        fitem["geometry"] = geometry
        features.append(fitem)
    return (geometryType, features)
#def featuresFromCursor(cur):
