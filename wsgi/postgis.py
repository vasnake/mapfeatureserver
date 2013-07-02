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

PGTIMESTAMP_LENGTH = 36  # 19 symbols "2013-05-29 18:09:00"; AGS shows: (type: esriFieldTypeDate, length: 36)
# timestamp [ (p) ] [ without time zone ] 8 bytes according to http://www.postgresql.org/docs/9.0/static/datatype-datetime.html

REGULAR_TYPES = []
# Postgres regular datatype codes
for typ in (psycopg2.STRING.values, psycopg2.DATETIME.values, psycopg2.BINARY.values,
            psycopg2.NUMBER.values, psycopg2.ROWID.values,
            psycopg2.extensions.UNICODE.values, psycopg2.extensions.DECIMAL.values,
            psycopg2.extensions.FLOAT.values, psycopg2.extensions.BOOLEAN.values,
            psycopg2.extensions.LONGINTEGER.values, psycopg2.extensions.INTEGER.values,
            psycopg2.extensions.DATE.values, psycopg2.extensions.TIME.values):
    for tc in typ:
        REGULAR_TYPES.append(tc)

TYPECODE2ESRI = {23: u"esriFieldTypeInteger", 21: u"esriFieldTypeSmallInteger",
                 1043: u"esriFieldTypeString", 25: u"esriFieldTypeString",
                 1700: u"esriFieldTypeDouble", 1114: u"esriFieldTypeDate"}
# Map type_code to Esri types. esriFieldTypeOID == esriFieldTypeInteger
# 25 is PG 'text' type, maybe we should map 'text' to esriFieldTypeBlob
# 1114 is timestamp [ (p) ] [ without time zone ]

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

    def filterLayerDataByGeom(self, lyrinfo, spatfilter):
        """ Answer for client query.
        Returns layer data from DB. Output formed as dictionary according to Esri spec.
        Features will be spatially filtered by spatfilter.geometry.

        specs:
            http://resources.arcgis.com/en/help/rest/apiref/fsquery.html
            http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#/Query_Feature_Service_Layer/02r3000000r1000000/

        query example:
            http://vags101.algis.com/arcgis/rest/services/PATHING/FeatureServer/0/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry={%22xmin%22%3a-7182265.21424325%2c%22ymin%22%3a-1567516.84684806%2c%22xmax%22%3a17864620.2142433%2c%22ymax%22%3a14321601.0968481%2c%22spatialReference%22%3a{%22wkid%22%3a102100}}&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson
            http://vdesk.algis.com:5000/3/query?returnGeometry=true&geometryType=esriGeometryPolygon&geometry=%7b%22spatialReference%22%3a%7b%22wkid%22%3a102100%7d%2c%22rings%22%3a%5b%5b%5b-3580921.90110393%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c15615167.6343221%5d%2c%5b20037508.3427892%2c15615167.6343221%5d%2c%5b20037508.3427892%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c-273950.309374072%5d%5d%2c%5b%5b-20037508.3427892%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c-273950.309374072%5d%5d%5d%7d&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=json&_ts=635056144548740692&

        Args:
            lyrinfo: layermeta.LayerInfo object with
                LayerInfo.tabname: layer table name;
                LayerInfo.geomfield: name for table field with geometry;
                LayerInfo.oidfield: name for field with OBJECTID;
            spatfilter: esri.OGCSpatialFilterParams with spatial filter parameters:
                outSR: integer from request, e.g. 'outSR=102100' which is srid for projecting DB geometry data to;
                inpGeomWKT: string, geometry in OGC WKT representation. Spatial filter will be
                    constructed from that geometry.
                inpGeomSR: integer, input geometry spatial reference WKID.
                spatRel: string, spatial relation for filter, one of (esriSpatialRelIntersects)
        """
        assert isinstance(spatfilter, esri.OGCSpatialFilterParams)
        assert isinstance(lyrinfo, layermeta.LayerInfo)

        if spatfilter.spatRel == esri.SpatialRelations.esriSpatialRelIntersects:
            pass
        else:
            raise TypeError("Layer data filter with '%s' not realized yet" % spatfilter.spatRel)

        queryRes = {"objectIdFieldName": lyrinfo.oidfield, "globalIdFieldName": "", "features": []}

        # srid for projecting data to
        outSrid = postgisSRID(spatfilter.outSR)
        # and from
        inSrid = postgisSRID(spatfilter.geomSR)

        # output "spatialReference": ...
        spatialReference = {"wkid": int(spatfilter.outSR), "latestWkid": outSrid}

        # sql query
        # TODO: sql builder must use 'outFields' query parameter
        sql = sqlSelectAllByWKTGeom(lyrinfo, outSrid, spatfilter.wktGeom, inSrid)
#        print sql
        cur = self.cursor
        cur.execute(sql)
        if not cur.rowcount is None and cur.rowcount > 0:
            #output "fields": [ { "name": "descr",   "alias": "Описание",   "type": "esriFieldTypeString",   "length": 100 },...
            #  из описания курсора «for rec in cur.description:»
            fields = attrFieldsFromDescr(cur, lyrinfo)

            #"geometryType": "esriGeometryPoint",   - из первой же записи выборки, поле «shape»
            #"features": [   { "attributes": {...,   "geometry": {...   - из результатов запроса.
#            geometryType, features = featuresFromCursor(cur)
            geometryType, features = featuresFromCursor(cur, lyrinfo)

            queryRes.update({"geometryType": geometryType, "spatialReference": spatialReference,
                        "fields": fields, "features": features})
            if cur.rowcount >= 1000:
                queryRes["exceededTransferLimit"] = True

        return queryRes
#    def filterLayerDataByGeom(self, lyrinfo, outSR, inpGeomWKT, inpGeomSR, spatRel):
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
#        print rec  # (u'testtimestamp', u'YES', u'timestamp without time zone', u'timestamp', None, None, None)
        # (u'testtext', u'YES', u'text', u'text', None, None, None) # esriFieldTypeString or esriFieldTypeBlob?
        # (u'shotspacin', u'YES', u'numeric', u'numeric', None, None, None) # esriFieldTypeDouble
        # (u'geom', u'YES', u'USER-DEFINED', u'geometry', None, None, None)
        ftype = FIELDTYPENAME2ESRI[rec[3]]
        if ftype == u'esriFieldTypeGeometry':
            continue

        obj = {u'name': rec[0], u'type': ftype, u'alias': rec[0].upper(), u'domain': None,
            u'editable': False, u'nullable': nullable[rec[1]]}

        if obj[u'type'] in esri.ESRI_FIELDS_WITH_LENGTH:
            obj[u'length'] = rec[4]
            if rec[3] == u'text':  # maybe we should use esriFieldTypeBlob
                obj[u'length'] = PGTEXT_LENGTH
            elif rec[3] == u'timestamp':
                obj[u'length'] = PGTIMESTAMP_LENGTH

        if oidfname.lower() == obj[u'name'].lower():
            obj = {u'name': rec[0], u'type': u'esriFieldTypeOID', u'alias': u'OBJECTID',
            u'domain': None, u'editable': False, u'nullable': False}

        data.append(obj)

    return simplejson.dumps({'objectIdField': oidfname, 'fields': data},
                      ensure_ascii=False, sort_keys=True, indent=2)
#def tableFields4esri(cur, tabname):


def  sqlSelectAllByWKTGeom(lyrinfo, outSrid, wktGeom, inSrid):
    """ Return SQL text for 'select *, shape ... limit 1000' query with 'intersect' spatial filter.
    Field 'shape' is st_asgeojson text for geometry field.

    Args:
        lyrinfo: DBLayerInfo object with
            LayerInfo.tabname: layer table name;
            LayerInfo.geomfield: name for table field with geometry;
            LayerInfo.oidfield: name for field with OBJECTID;
        outSrid: integer, PostGIS srid for output projection;
        wktGeom: OGC WKT geometry for spatial filter;
    """
    assert isinstance(lyrinfo, layermeta.DBLayerInfo)
#    assert isinstance(lyrinfo, layermeta.LayerInfo)

    sql = """select *, st_asgeojson(1, st_transform({gcol}::geometry, {outsrid})) as shape
        from {table} where not st_disjoint(
            {gcol}::geometry,
            ST_transform(
                ST_GeomFromText('{wkt}', {insrid})
                , st_srid({gcol}::geometry) )
        ) order by {pk} limit 1000;
        """.format(gcol=lyrinfo.geomfield, outsrid=outSrid, table=lyrinfo.tabname,
            wkt=wktGeom, insrid=inSrid, pk=lyrinfo.oidfield)

    return sql
#def  sqlSelectAllByWKTGeom(lyrinfo, outSrid, inpGeomWKT, inSrid)


def sqlSelectAllByBox(lyrinfo, outSrid, box):
    """ Obsolete.
    Return SQL text for 'select *, shape ...' query with spatial filter.
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


def fieldFromDescr(col, lyrinfo):
    """ Return field description as dictionary in form that Esri require
    {name, alias, type, length if type is string or date}.
    Return None if field contains geometry.
    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html

    Args:
        col: Pg cursor.description[n]
        lyrinfo: layermeta.LayerInfo object with fields metadata

    Result example:
        {
          "alias": "DESCR",
          "length": 100,
          "name": "descr",
          "type": "esriFieldTypeString"
        }
    """
#    debug info
#    print col  # Column(name='geometry', type_code=1441608681, display_size=None, internal_size=1107452, precision=None, scale=None, null_ok=None)
    # PG field type 'timestamp':
    # Column(name='testtimestamp', type_code=1114, display_size=None, internal_size=8, precision=None, scale=None, null_ok=None)
    # PG field type 'text':
    # Column(name='testtext', type_code=25, display_size=None, internal_size=-1, precision=None, scale=None, null_ok=None)
    # Column(name='shape', type_code=25, display_size=None, internal_size=-1, precision=None, scale=None, null_ok=None)
    assert isinstance(lyrinfo, layermeta.LayerInfo)

    # if field is geometry or not in known list
    fldname = unicode(col.name).lower()
    if fldname == u'shape' or fldname == lyrinfo.geomfield:
        return None

    # TODO: this check is not really needed in case sql query builded from list of fields instead of 'select * from ...'
    if not fldname in lyrinfo.fields:
        print "fieldFromDescr: field '{fldname}' not in layer metadata".format(**locals())
        return None

    fldmeta = lyrinfo.fields[fldname]
    fld = {'name': fldmeta['name'], 'alias': fldmeta['alias'], 'type': fldmeta['type']}
    if 'length' in fldmeta:
        fld['length'] = fldmeta['length']

    return fld
#def fieldFromDescr(col, oidfield):


def attrFieldsFromDescr(cur, lyrinfo):
    """ Return array of fields descriptions as described in ArcGIS spec.
    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html

    Args:
        cur: Pg connection.cursor with cur.description tuple
        lyrinfo: layermeta.LayerInfo object with
            LayerInfo.oidfield: name for field with OBJECTID
    """
    assert isinstance(lyrinfo, layermeta.LayerInfo)
    fields = []
    for col in cur.description:
        #~ print "name: '%s', alias: '%s', type: '%s', length '%s'" % (col.name, col.name, col.type_code, col.internal_size)
        fld = fieldFromDescr(col, lyrinfo)
        if fld:
            fields.append(fld)
    return fields
#def attrFieldsFromDescr(cur):


def featuresFromCursor(cur, lyrinfo):
    """ Parse cursor records and return (geometryType, features) tuple
    where geometryType is string and features is array according to
    ArcGIS spec http://resources.arcgis.com/en/help/rest/apiref/fsquery.html#response

    "geometryType": "esriGeometryPoint",
    "features": [ { "attributes": {..., "geometry": {...

    Args:
        cur: Pg connection.cursor with dataset
        lyrinfo: layermeta.LayerInfo object with layer metadata (layer fields specs)
    """
    assert isinstance(lyrinfo, layermeta.LayerInfo)
    columns = lambda a: (zip(range(len(a)), a))
    ufields = {}
    #"geometryType": "esriGeometryPoint",   - из первой же записи выборки, поле «shape»
    geometryType = ''
    #"features": [   { "attributes": {...,   "geometry": {...   - из результатов запроса.
    features = []
    for rec in cur:
#        print rec
        fitem = {}  # feature attributes, geometry
        attributes = {}
        geometry = {}

        for colnum, col in columns(cur.description):
#            print col  # Column(name='testtimestamp', type_code=1114, display_size=None, internal_size=8, precision=None, scale=None, null_ok=None)
            fldname = unicode(col.name).lower()
            if fldname == u'shape':  # geometry
                shape = simplejson.loads(rec[colnum])
                geometryType, geometry = esri.geoJson2agJson(shape)
                continue

            # TODO: this check not needed in case sql query builded properly
            if fldname == lyrinfo.geomfield:
                continue

            if fldname not in lyrinfo.fields:  # unknown field
                ufields[fldname] = ''
                continue

            attributes[lyrinfo.fields[fldname]['name']] = rec[colnum]

        fitem["attributes"] = attributes
        fitem["geometry"] = geometry
        features.append(fitem)

    if len(ufields.keys()):
        print "featuresFromCursor: fields '{lst}' not in layer metadata".format(lst=ufields.keys())
    return (geometryType, features)
#def featuresFromCursor(cur):
