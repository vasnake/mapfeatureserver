#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

u""" Map Feature Server tests.

Data model tests.
"""

import sys, os
import unittest
import simplejson
#from nose.plugins.skip import SkipTest

pth = os.path.join(os.path.dirname(__file__), '../wsgi')
if pth not in sys.path:
    sys.path.insert(0, pth)

CP = 'UTF-8'

NODB = False
DSN = "host=vags101 port=5432 dbname=postgisdb user=mfs password=12345678 connect_timeout=10 client_encoding=utf8"
CONN = None
import psycopg2
import psycopg2.extensions  # always unicode output
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
try:
    CONN = psycopg2.connect(DSN)
except:
    NODB = True
#    raise


class LayerDataTests(unittest.TestCase):
    """ Tests for layerdata module """

    def setUp(self):
        self.conn = CONN
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self.maxDiff = None
    #def setUp(self):

    def tearDown(self):
        self.cur.close()


    @unittest.skipIf(NODB, "haven't DB connection")
    def testLayerExtent(self):
        """ postgis.layerRealExtent(ds, tabname, fname) returns "extent" JSON
        """
        import postgis
        ds = postgis.DataSource(self.conn)
        tabname = 'patching'
        fname = 'geog'
        txt1 = u'ymax": 52.99648148'
        txt2 = u'wkid": 4326'
        res = postgis.layerRealExtent(ds, tabname, fname)
        self.assertIn(txt1, res)
        self.assertIn(txt2, res)

        tabname = 'seisprof'
        fname = 'geom'
        txt1 = u'ymax": 81.59710856'
        txt2 = u'wkid": 4326'
        res = postgis.layerRealExtent(ds, tabname, fname)
        self.assertIn(txt1, res)
        self.assertIn(txt2, res)

        tabname = 'flyzone'
        fname = 'geom'
        txt1 = u'"xmax": 158.29704000000001'
        txt2 = u'wkid": 4326'
        res = postgis.layerRealExtent(ds, tabname, fname)
        self.assertIn(txt1, res)
        self.assertIn(txt2, res)
#    def testLayerExtent(self):


    @unittest.skipIf(NODB, "haven't DB connection")
    def testLayerFields(self):
        """ postgis.tableFields4esri(ds, tabname, oidfname) returns "fields" JSON
        """
        import postgis
        ds = postgis.DataSource(self.conn)
        tabname = 'patching'
        oidfname = 'gid'
        res = postgis.tableFields4esri(ds, tabname, oidfname)
        self.assertIn('type": "esriFieldTypeOID', res)
        self.assertIn('name": "ptchlenght', res)

        tabname = 'seisprof'
        oidfname = 'gid'
        res = postgis.tableFields4esri(ds, tabname, oidfname)
        self.assertIn('type": "esriFieldTypeOID', res)

        tabname = 'flyzone'
        oidfname = 'gid'
        res = postgis.tableFields4esri(ds, tabname, oidfname)
        self.assertIn('type": "esriFieldTypeOID', res)
        self.assertIn('"objectIdField": "gid"', res)
#    def testLayerFields(self):


    @unittest.skipIf(NODB, "haven't DB connection")
    def testLayerDataSpatialFilter(self):
        """ function layerdata.layerDataFilterByGeom returns filtered layer data
        as dictionary according to
        http://resources.arcgis.com/en/help/rest/apiref/fslayer.html
        http://resources.arcgis.com/en/help/rest/apiref/fsquery.html

        example:
        http://vags101.algis.com/arcgis/rest/services/PATHING/FeatureServer/0/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry={%22xmin%22%3a-7182265.21424325%2c%22ymin%22%3a-1567516.84684806%2c%22xmax%22%3a17864620.2142433%2c%22ymax%22%3a14321601.0968481%2c%22spatialReference%22%3a{%22wkid%22%3a102100}}&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson
        http://vags101.algis.com/arcgis/rest/services/flyzone/FeatureServer/3/query?returnGeometry=true&geometryType=esriGeometryPolygon&geometry=%7b%22spatialReference%22%3a%7b%22wkid%22%3a102100%7d%2c%22rings%22%3a%5b%5b%5b-3580921.90110393%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c15615167.6343221%5d%2c%5b20037508.3427892%2c15615167.6343221%5d%2c%5b20037508.3427892%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c-273950.309374072%5d%5d%2c%5b%5b-20037508.3427892%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c-273950.309374072%5d%5d%5d%7d&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson

        TODO: replace QueryByBox tests; add query by polygon
        """
        import layerdata, esri, mapfs_controller, postgis, mfslib

        ds = postgis.DataSource(self.conn)
        lyrinf = mapfs_controller.getLayerConfig('0')
        spfilter = esri.SpatialFilterParams(102100,
                                            '{"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}',
                                             'esriGeometryEnvelope',
                                             'esriSpatialRelIntersects')
        res = layerdata.layerDataFilterByGeom(ds, lyrinf, spfilter)
        txt = simplejson.dumps(res, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True, default=mfslib.jsonify)
#        with open('layerdata.test1.json', 'wb') as fh:
#            fh.write(txt.encode(CP))
        res = simplejson.loads(txt, use_decimal=True)
        with open('layerdata.test1.json') as fh:
            txt = fh.read().strip().decode(CP)
            dct = simplejson.loads(txt, use_decimal=True)
        self.assertDictEqual(dct, res)
#    def testLayerDataSpatialFilter(self):


    @unittest.skipIf(NODB, "haven't DB connection")
    def testLayerQueryByBox(self):
        """ Obsolete.
        function layerdata.layerDataInBox return layer data as dictionary
        prepared for JSONify
        according to http://resources.arcgis.com/en/help/rest/apiref/fslayer.html
        http://resources.arcgis.com/en/help/rest/apiref/fsquery.html

        example
        http://vags101.algis.com/arcgis/rest/services/PATHING/FeatureServer/0/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry={%22xmin%22%3a-7182265.21424325%2c%22ymin%22%3a-1567516.84684806%2c%22xmax%22%3a17864620.2142433%2c%22ymax%22%3a14321601.0968481%2c%22spatialReference%22%3a{%22wkid%22%3a102100}}&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson

        Args:
            cur: connection.cursor for PostGIS DB
        Hardcoded args:
            query parameters:
                returnGeometry=true
                &geometryType=esriGeometryEnvelope
                &geometry={"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}
                &inSR=102100
                &spatialRel=esriSpatialRelIntersects
                &outSR=102100
                &outFields=*&f=json
            ini Layer config:
                layer.table = patching
                layer.geomfield = geog
                layer.oidfield = gid
        """
        import layermeta, layerdata, mfslib

        # sample recordset for patching
        #имя таблицы - from ini
        #имя поля геометрии - from ini
        #"objectIdFieldName": "objectid",   - из ини файла «oidname = ini.get(lyrid, 'layer.oidfield')»
        lyrinf = layermeta.DBLayerInfo('patching', 'geog', 'gid')
        #"spatialReference": { "wkid": 102100, "latestWkid": 3857 },    - из параметра «outSR=102100» запроса. 102100 = 3857
        outSR = '102100'
        inpBox = '{"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}'
        res = layerdata.layerDataInBox(self.cur, lyrinf, outSR, inpBox)
        # compare patching data

        txt = simplejson.dumps(res, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True, default=mfslib.jsonify)
#        with open('layerdata.test1.json', 'wb') as fh:
#            fh.write(txt.encode(CP))
        res = simplejson.loads(txt, use_decimal=True)
        with open('layerdata.test1.json') as fh:
            txt = fh.read().strip().decode(CP)
            dct = simplejson.loads(txt, use_decimal=True)
        # compare dictionaries
        self.assertDictEqual(dct, res)

        # empty recordset for seismoprofiles
        lyrinf = layermeta.DBLayerInfo('seisprof', 'geom', 'gid')
        outSR = '102100'
        inpBox = '{"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}'
        res = layerdata.layerDataInBox(self.cur, lyrinf, outSR, inpBox)
        dct = {"objectIdFieldName": lyrinf.oidfield, "globalIdFieldName": "", "features": []}
        self.assertDictEqual(dct, res)

        # sample recordset for seismoprofiles
        # http://vags101.algis.com/arcgis/rest/services/seisprofiles/FeatureServer/1/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry={"xmin":6593024.93074047,"ymin":10538006.415246,"xmax":6641944.62884298,"ymax":10569039.8487298,"spatialReference":{"wkid":102100}}&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson
        lyrinf = layermeta.DBLayerInfo('seisprof', 'geom', 'gid')
        outSR = '102100'
        inpBox = '{"xmin":6593024.93074047,"ymin":10538006.415246,"xmax":6641944.62884298,"ymax":10569039.8487298,"spatialReference":{"wkid":102100}}'
        res = layerdata.layerDataInBox(self.cur, lyrinf, outSR, inpBox)
        # compare
        txt = simplejson.dumps(res, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True)
#        with open('layerdata.test2.json', 'wb') as fh:
#            fh.write(txt.encode(CP))
        res = simplejson.loads(txt, use_decimal=True)
        with open('layerdata.test2.json') as fh:
            txt = fh.read().strip().decode(CP)
            dct = simplejson.loads(txt, use_decimal=True)
        # compare dictionaries
        self.assertDictEqual(dct, res)

        # sample recordset for flyzone
        # http://vags101.algis.com/arcgis/rest/services/flyzone/FeatureServer/2/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry=%7b%22xmin%22%3a4103424.83887823%2c%22ymin%22%3a7491699.58654681%2c%22xmax%22%3a4494782.42369833%2c%22ymax%22%3a7726819.88555201%2c%22spatialReference%22%3a%7b%22wkid%22%3a102100%7d%7d&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson
        lyrinf = layermeta.DBLayerInfo('flyzone', 'geom', 'gid')
        outSR = '102100'
        inpBox = '{"xmin":4103424.83887823,"ymin":7491699.58654681,"xmax":4494782.42369833,"ymax":7726819.88555201,"spatialReference":{"wkid":102100}}'
        res = layerdata.layerDataInBox(self.cur, lyrinf, outSR, inpBox)
        # compare
        txt = simplejson.dumps(res, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True)
#        with open('layerdata.test3.json', 'wb') as fh:
#            fh.write(txt.encode(CP))
        res = simplejson.loads(txt, use_decimal=True)
        with open('layerdata.test3.json') as fh:
            txt = fh.read().strip().decode(CP)
            dct = simplejson.loads(txt, use_decimal=True)
        # compare dictionaries
        self.assertDictEqual(dct, res)
    #def testLayerQueryByBox(self):


if __name__ == '__main__':
    unittest.main(verbosity=3, exit=False)
