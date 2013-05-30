#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

u""" Map Feature Server tests.

Flask app tests.
http://flask.pocoo.org/docs/testing/#testing
"""

import sys, os
import HTMLParser
import unittest
#from nose.plugins.skip import SkipTest

pth = os.path.join(os.path.dirname(__file__), '../wsgi')
if pth not in sys.path:
    sys.path.insert(0, pth)

import mapfs_controller

FASTCHECK = False
CP = 'UTF-8'

class MFSFlaskAppTestCase(unittest.TestCase):
    """ Tests for Flask app """

    def setUp(self):
        mapfs_controller.APP.config['TESTING'] = True
        self.app = mapfs_controller.APP.test_client()

    def tearDown(self):
        pass

    def testRootPage(self):
        """ Check root page (/) output.
        """
        txt = u'''<a href="/0/query?geometry=%7B%22xmin%22%3A3907314.1268439%2C%22ymin%22%3A6927697.68990079%2C%22xmax%22%3A3996369.71947852%2C%22ymax%22%3A7001516.67745022%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&amp;outSR=102100">/0/query?geometry=%7B%22xmin%22%3A3907314.1268439%2C%22ymin%22%3A6927697.68990079%2C%22xmax%22%3A3996369.71947852%2C%22ymax%22%3A7001516.67745022%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&amp;outSR=102100</a>'''
        rv = self.app.get('/')
        self.assertIn(txt.encode(CP), rv.data)  # http://docs.python.org/2/library/unittest.html#assert-methods

    def testLayerInfo(self):
        """ Check layer 0 metadata page (/0) output.
        """
        txt = u'''"id": 0,
 "name": "Ямочный ремонт",
 "type": "Feature Layer",
 "description": "Места установки заплаток на дорогах",'''
        rv = self.app.get('/0')
        self.assertIn(txt.encode(CP), rv.data)

    def testLayer0Data(self):
        """ Check layer 0 query result page (/0/query?...) output.
        """
        txt = u'''"ptchlenght": 500,
        "pthcdeptht": 8,
        "regdaterec": "2012/08/02",
        "regdaterep": "2012/09/15",
        "roadcarpet": "Асфальт",
        "testtimestamp": 1369850940000
      },
      "geometry": {
        "x": 3980475.9450405277,
        "y": 6976079.279805333'''
        #~ txt = txt.replace(',', ', ')
        rv = self.app.get('''/0/query?geometry={%22xmin%22%3A3907314.1268439%2C%22ymin%22%3A6927697.68990079%2C%22xmax%22%3A3996369.71947852%2C%22ymax%22%3A7001516.67745022%2C%22spatialReference%22%3A{%22wkid%22%3A102100}}&outSR=102100''')
        self.assertIn(txt.encode(CP), rv.data)
        err = u'''"error": {'''
        self.assertNotIn(err.encode(CP), rv.data)


    def testLayer1Data(self):
        """ Check layer 1 query result page (/1/query?...) output.
        """
        err = u'''"error": {'''
        txt1 = u'''"ship": "НИС ИСКАТЕЛЬ-2"'''
        txt2 = u'''"geometry": {
            "paths": [ [
                [ 6619987.653828225, 10565389.907740869 ],
                [ 6618262.300193224, 10614367.260334603 ]
                ] ] }'''
        txt2 = u' '.join(txt2.split())

        # dozen records
        rv = self.app.get('''/1/query?geometry={"xmin"%3a6593024.93074047%2c"ymin"%3a10538006.415246%2c"xmax"%3a6641944.62884298%2c"ymax"%3a10569039.8487298%2c"spatialReference"%3a{"wkid"%3a102100}}&outSR=102100''')
        data = ' '.join(rv.data.split())
        self.assertNotIn(err.encode(CP), rv.data)
        self.assertIn(txt1.encode(CP), rv.data)
        self.assertIn(txt2.encode(CP), data)
#    def testLayer1Data(self):


    def testLayer1EmptyRecset(self):
        """ Check layer 1 query result page (/1/query?...) for empty recordset.
        """
        err = u'''"error": {'''
        txt = u'''
            { "features": [],
            "globalIdFieldName": "",
            "objectIdFieldName": "gid" }'''
        txt = u' '.join(txt.split())
        # no features
        rv = self.app.get('''/1/query?geometry={%22xmin%22%3A3907314.1268439%2C%22ymin%22%3A6927697.68990079%2C%22xmax%22%3A3996369.71947852%2C%22ymax%22%3A7001516.67745022%2C%22spatialReference%22%3A{%22wkid%22%3A102100}}&outSR=102100''')
        data = ' '.join(rv.data.split())
        self.assertNotIn(err.encode(CP), rv.data)
        self.assertIn(txt.encode(CP), data)
#    def testLayer1EmptyRecset(self):


    @unittest.skipIf(FASTCHECK, 'huge and slow recordset processing')
    def testLayer1HugeRecset(self):
        """ Check layer 1 query result page (/1/query?...) for features > 1000 recordset.
        """
        err = u'''"error": {'''
        txt1 = u'''{ "exceededTransferLimit": true,
            "features": [
            { "attributes": {'''
        txt2 = u''' "geometryType": "esriGeometryPolyline",
            "globalIdFieldName": "",
            "objectIdFieldName": "gid",
            "spatialReference": {
            "latestWkid": 3857,
            "wkid": 102100 } }'''
        txt1 = u' '.join(txt1.split())
        txt2 = u' '.join(txt2.split())
        # features > 1000
        rv = self.app.get('''/1/query?geometry={"xmin"%3a-7182265.21424325%2c"ymin"%3a-1567516.84684806%2c"xmax"%3a17864620.2142433%2c"ymax"%3a14321601.0968481%2c"spatialReference"%3a{"wkid"%3a102100}}&outSR=102100''')
        self.assertNotIn(err.encode(CP), rv.data)
        data = ' '.join(rv.data.split())
        self.assertIn(txt1.encode(CP), data)
        self.assertIn(txt2.encode(CP), data)
        self.assertEqual(1000, data.count('"geometry":'))
#    def testLayer1HugeRecset(self):


    def testLayer2Data(self):
        """ Check layer 2 query result page (/2/query?...) output.
        Record "recid": 143
        """
        err = u'''"error": {'''
        txt1 = u'''"boundary": "564124с  0375800в  далее  по  дуге  по  часовой  стрелке'''
        txt2 = u'''"geometry": {
        "rings": [ [ [
              4279602.386113361,
              7520773.048816763
            ], [
              4279572.070031156,
              7520668.786903687
            ], [
              4279455.184565822,
              7520710.387695587
            ], [
              4279602.386113361,
              7520773.048816763
            ] ], [ [
              4208589.216875655,
              7569584.6493480615
            ],'''
        txt2 = u' '.join(txt2.split())

        # dozen records
        rv = self.app.get('''/2/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry=%7b%22xmin%22%3a4103424.83887823%2c%22ymin%22%3a7491699.58654681%2c%22xmax%22%3a4494782.42369833%2c%22ymax%22%3a7726819.88555201%2c%22spatialReference%22%3a%7b%22wkid%22%3a102100%7d%7d&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson''')
        data = ' '.join(rv.data.split())
        self.assertNotIn(err.encode(CP), rv.data)
        self.assertIn(txt1.encode(CP), rv.data)
        self.assertIn(txt2.encode(CP), data)
#    def testLayer2Data(self):


    def testExtractMetaFromDB(self):
        """ Check admin page output for SQL error, layers meta from DB.
        """
        hp = HTMLParser.HTMLParser()
        err1 = u'''SQL error'''
        err2 = u"n/a"
        txt1 = u'''"spatialReference": {
            "wkid": 4326,
            "latestWkid": 4326'''
        txt1 = u' '.join(txt1.split())
        txt2 = u'''"alias": "OBJECTID",
            "domain": null,
            "editable": false,
            "name": "gid",
            "nullable": false,
            "type": "esriFieldTypeOID"'''
        txt2 = u' '.join(txt2.split())
        txt3 = u'"objectIdField": "gid"'

        rv = self.app.get('/admin/dsn/seisprof?oidfield=gid&geomfield=geom')
        self.assertNotIn(err1.encode(CP), rv.data)
        self.assertNotIn(err2.encode(CP), rv.data)

        rv = self.app.get('/admin/dsn/patching?oidfield=gid&geomfield=geog')
        self.assertNotIn(err1.encode(CP), rv.data)
        self.assertNotIn(err2.encode(CP), rv.data)
        data = hp.unescape(rv.data.decode(CP))
        data = ' '.join(data.split())
        self.assertIn(txt1, data)
        self.assertIn(txt2, data)

        rv = self.app.get('/admin/dsn/flyzone?oidfield=gid&geomfield=geom')
        self.assertNotIn(err1.encode(CP), rv.data)
        self.assertNotIn(err2.encode(CP), rv.data)
        data = hp.unescape(rv.data.decode(CP))
        data = ' '.join(data.split())
        self.assertIn(txt1, data)
        self.assertIn(txt2, data)
        self.assertIn(txt3, data)
#class MFSFlaskAppTestCase(unittest.TestCase):


if __name__ == '__main__':
    unittest.main(verbosity=3)
