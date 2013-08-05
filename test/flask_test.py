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
import simplejson

pth = os.path.join(os.path.dirname(__file__), '../wsgi')
if pth not in sys.path:
    sys.path.insert(0, pth)

import mapfs_controller
import mfslib

FASTCHECK = False
DEVDSN = True
CP = 'UTF-8'


class MFSFlaskAppTestCase(unittest.TestCase):
    """ Tests for Flask app """

    def setUp(self):
        mapfs_controller.APP.config['TESTING'] = True
        self.app = mapfs_controller.APP.test_client()
        self.maxDiff = 300

    def tearDown(self):
        pass

    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
    def testRootPage(self):
        """ Check root page (/) output.
        """
        txt = u'''<a href="/0/query?outSR=102100&amp;geometryType=esriGeometryEnvelope&amp;geometry=%7B%22xmin%22%3A3907314.1268439%2C%22ymin%22%3A6927697.68990079%2C%22xmax%22%3A3996369.71947852%2C%22ymax%22%3A7001516.67745022%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D&amp;spatialRel=esriSpatialRelIntersects">Layer 0 data query by box</a>'''
        rv = self.app.get('/')
        self.assertIn(txt.encode(CP), rv.data)  # http://docs.python.org/2/library/unittest.html#assert-methods

    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
    def testLayerInfo(self):
        """ Check layer 0 metadata page (/0) output.
        """
        txt = u'''"id": 0,
 "name": "Ямочный ремонт",
 "type": "Feature Layer",
 "description": "Места установки заплаток на дорогах",'''
        rv = self.app.get('/0')
        self.assertIn(txt.encode(CP), rv.data)

    def testServicesList(self):
        """ Check services page (/services) output.
        """
        err = u'''"error": {'''
        txt = u'''"services": [
            {
              "name": "mfs",
              "type": "FeatureServer"
            } ]
        '''
        txt = u' '.join(txt.split())
        rv = self.app.get('''/services''')
        resdict = simplejson.loads(rv.data.decode(CP))
        restext = simplejson.dumps(resdict, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True, default=mfslib.jsonify)
        data = ' '.join(restext.split())
        self.assertNotIn(err, data)
        self.assertIn(txt, data)
#    def testServicesList(self):

    def testLayersList(self):
        """ Check FeatureServer page (/services/mfs/FeatureServer) output.
        """
        err = u'''"error": {'''
        txt = u'''"layers": [
            { "id":
        '''
        txt = u' '.join(txt.split())
        rv = self.app.get('''/services/mfs/FeatureServer''')
        data = ' '.join(rv.data.split())

        self.assertNotIn(err.encode(CP), data)
        self.assertIn(txt.encode(CP), data)
#    def testLayersList(self):

    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
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
        rv = self.app.get('''/0/query?geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&geometry={%22xmin%22%3A3907314.1268439%2C%22ymin%22%3A6927697.68990079%2C%22xmax%22%3A3996369.71947852%2C%22ymax%22%3A7001516.67745022%2C%22spatialReference%22%3A{%22wkid%22%3A102100}}&outSR=102100''')
        resdict = simplejson.loads(rv.data.decode(CP))
        restext = simplejson.dumps(resdict, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True, default=mfslib.jsonify)
        self.assertIn(txt, restext)
        err = u'''"error": {'''
        self.assertNotIn(err, restext)


    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
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
        rv = self.app.get('''/1/query?geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&geometry={"xmin"%3a6593024.93074047%2c"ymin"%3a10538006.415246%2c"xmax"%3a6641944.62884298%2c"ymax"%3a10569039.8487298%2c"spatialReference"%3a{"wkid"%3a102100}}&outSR=102100''')
        data = ' '.join(rv.data.split())
        self.assertNotIn(err.encode(CP), rv.data)
        self.assertIn(txt1.encode(CP), rv.data)
        self.assertIn(txt2.encode(CP), data)
#    def testLayer1Data(self):


    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
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
        rv = self.app.get('''/1/query?geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&geometry={%22xmin%22%3A3907314.1268439%2C%22ymin%22%3A6927697.68990079%2C%22xmax%22%3A3996369.71947852%2C%22ymax%22%3A7001516.67745022%2C%22spatialReference%22%3A{%22wkid%22%3A102100}}&outSR=102100''')
        resdict = simplejson.loads(rv.data.decode(CP))
        restext = simplejson.dumps(resdict, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True, default=mfslib.jsonify)
        data = ' '.join(restext.split())
        self.assertNotIn(err.encode(CP), rv.data)
        self.assertIn(txt.encode(CP), data)
#    def testLayer1EmptyRecset(self):


    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
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
        rv = self.app.get('''/1/query?geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&geometry={"xmin"%3a-7182265.21424325%2c"ymin"%3a-1567516.84684806%2c"xmax"%3a17864620.2142433%2c"ymax"%3a14321601.0968481%2c"spatialReference"%3a{"wkid"%3a102100}}&outSR=102100''')
        self.assertNotIn(err.encode(CP), rv.data)
        resdict = simplejson.loads(rv.data.decode(CP))
        restext = simplejson.dumps(resdict, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True, default=mfslib.jsonify)
        data = ' '.join(restext.split())
        self.assertIn(txt1, data)
        self.assertIn(txt2, data)
        self.assertEqual(1000, data.count('"geometry":'))
#    def testLayer1HugeRecset(self):


    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
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

        # dozen of records
        rv = self.app.get('''/2/query?geometryType=esriGeometryEnvelope&geometry=%7b%22xmin%22%3a4103424.83887823%2c%22ymin%22%3a7491699.58654681%2c%22xmax%22%3a4494782.42369833%2c%22ymax%22%3a7726819.88555201%2c%22spatialReference%22%3a%7b%22wkid%22%3a102100%7d%7d&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson''')
        data = ' '.join(rv.data.split())
        self.assertNotIn(err.encode(CP), rv.data)
        self.assertIn(txt1.encode(CP), rv.data)
        self.assertIn(txt2.encode(CP), data)
#    def testLayer2Data(self):


    @unittest.skipIf(DEVDSN, "need Gis-Lab DB DSN")
    def testLayer3DataByPolygon(self):
        """ Check layer 3 query by polygon result page (/3/query?...) output.
        """
        err = u'''"error": {'''
        txt1 = u'''"geo_accuracy": "до улицы"'''
        txt2 = u'''"geometry": {
            "x": 3471199.538874946,
            "y": 9661660.43442387
        }'''
        txt2 = u' '.join(txt2.split())

        # > 1000 recs
        rv = self.app.get('''/3/query?returnGeometry=true&geometryType=esriGeometryPolygon&geometry=%7b%22spatialReference%22%3a%7b%22wkid%22%3a102100%7d%2c%22rings%22%3a%5b%5b%5b-3580921.90110393%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c15615167.6343221%5d%2c%5b20037508.3427892%2c15615167.6343221%5d%2c%5b20037508.3427892%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c-273950.309374072%5d%5d%2c%5b%5b-20037508.3427892%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c-273950.309374072%5d%5d%5d%7d&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson''')
        data = ' '.join(rv.data.split())
        self.assertNotIn(err.encode(CP), rv.data)
        self.assertIn(txt1.encode(CP), rv.data)
        self.assertIn(txt2.encode(CP), data)

        # min set of parameters (geometryType, geometry))
        rv = self.app.get('''/3/query?geometryType=esriGeometryPolygon&geometry=%7b%22spatialReference%22%3a%7b%22wkid%22%3a102100%7d%2c%22rings%22%3a%5b%5b%5b-3580921.90110393%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c15615167.6343221%5d%2c%5b20037508.3427892%2c15615167.6343221%5d%2c%5b20037508.3427892%2c-273950.309374072%5d%2c%5b-3580921.90110393%2c-273950.309374072%5d%5d%2c%5b%5b-20037508.3427892%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c15615167.6343221%5d%2c%5b-18609053.1581958%2c-273950.309374072%5d%2c%5b-20037508.3427892%2c-273950.309374072%5d%5d%5d%7d&f=pjson''')
        data = ' '.join(rv.data.split())
        txt1 = u'''"name": "Школа-интернат"'''
        txt2 = u'''"geometry": {
            "x": 91.395959,
            "y": 56.169268 }
        '''
        txt3 = u'''"spatialReference": {
            "latestWkid": 4326,
            "wkid": 4326 }
        '''
        txt2 = u' '.join(txt2.split())
        txt3 = u' '.join(txt3.split())
        self.assertNotIn(err.encode(CP), rv.data)
        self.assertIn(txt1.encode(CP), rv.data)
        self.assertIn(txt2.encode(CP), data)
        self.assertIn(txt3.encode(CP), data)
#    def testLayer3DataByPolygon(self):


    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
    def testPostQuery(self):
        """ Check query output for POST verb
        """
        err1 = u'''Method Not Allowed'''
        txt1 = u'''
            "geometryType": "esriGeometryPolygon",
            "globalIdFieldName": "",
            "objectIdFieldName": "gid",
            "spatialReference": {
              "latestWkid": 3857,
              "wkid": 102100
        '''
        txt1 = u' '.join(txt1.split())
        txt2 = u'"gid": 111'
        data = {
            'returnGeometry': 'true',
            'geometryType': 'esriGeometryEnvelope',
            'geometry': '{"xmin":-7416226.23234093,"ymin":-1565430.33928041,"xmax":17630659.1961456,"ymax":14323687.6044157,"spatialReference":{"wkid":102100}}',
            'inSR': 102100,
            'spatialRel': 'esriSpatialRelIntersects',
            'where': 'gid NOT IN (85,86,87,88,111,115,120,12,40,41,71,72,73,74,75,76,77,78,79,80,81,82,83,84,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,105,106,107,108,109,110,112,113,114,116,117,119,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,298,299,302,304,305,306,307,308,309,310,311,313,314,315,319,322,324,325,326,327,328,329,330,331,332,333,334,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,386,387,388,390,391,392,393,394,395,400,401,402,403,404,405,406,407,408,409,410)',
            'outSR': 102100,
            'outFields': '*'}
        rv = self.app.post('/2/query', data=data)
        resdict = simplejson.loads(rv.data.decode(CP))
        restext = simplejson.dumps(resdict, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True, default=mfslib.jsonify)
        res = ' '.join(restext.split())
        self.assertNotIn(err1, res)
        self.assertIn(txt1, res)
        self.assertNotIn(txt2, res, "I found a records which must be filtered out (gid: 111)")
#    def testPostQuery(self):


    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
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


    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
    def testNoGeometryFilter(self):
        """ Check 'where' w/o geometry filter (/0/query?where...).
        """
        txt = u'''"regdaterec": "2012/08/02",
        "regdaterep": "2012/09/15",
        "roadcarpet": "Асфальт",
        "testtimestamp": 1369850940000'''
        txt = u' '.join(txt.split())
        rv = self.app.get('''/0/query?returnGeometry=false&spatialRel=esriSpatialRelIntersects&where=1%3D1&outFields=gid%2Cptchlenght%2Cpthcdeptht%2Cdescr%2Cregdaterec%2Cregdaterep%2Croadcarpet%2Ctesttimestamp&f=pjson''')
        data = u' '.join(rv.data.decode(CP).split())
        self.assertIn(txt, data)
        err = u'''"error": {'''
        self.assertNotIn(err, data)


    @unittest.skipIf(not DEVDSN, "need developer DB DSN")
    def testGidFirst(self):
        """ Check attributes order (oid first)
        """
        txt = u'''"attributes": {
            "gid":'''
        err = u'''"error": {'''
        txt = u' '.join(txt.split())
        rv = self.app.get('''/0/query?where=1%3D1&f=pjson''')
        def checkRes():
            data = u' '.join(rv.data.decode(CP).split())
            self.assertNotIn(err, data)
            fcount = data.count(txt)
            res = simplejson.loads(data)
            self.assertEqual(fcount, len(res['features']))
        checkRes()
        rv = self.app.get('''/0/query?returnGeometry=true&geometryType=esriGeometryEnvelope&geometry={%22xmin%22%3a-7182265.21424325%2c%22ymin%22%3a-1567516.84684806%2c%22xmax%22%3a17864620.2142433%2c%22ymax%22%3a14321601.0968481%2c%22spatialReference%22%3a{%22wkid%22%3a102100}}&inSR=102100&spatialRel=esriSpatialRelIntersects&outSR=102100&outFields=*&f=pjson''')
        checkRes()


#class MFSFlaskAppTestCase(unittest.TestCase):


if __name__ == '__main__':
    unittest.main(verbosity=3)
