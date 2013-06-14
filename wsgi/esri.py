#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# (c) Valik mailto:vasnake@gmail.com

r""" Map Feature Server module.
Esri related functions.

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

import simplejson

CP = 'UTF-8'

ESRI_FIELDS_WITH_LENGTH = (u"esriFieldTypeString", u"esriFieldTypeDate")
# Esri fields types with 'length' attribute
# from 10.0 fields of type (String, Date, GlobalID, GUID and XML) have an additional length property

GEOJSON_ESRI_GEOMTYPES = {u'Point': u'esriGeometryPoint',
                          u'MultiLineString': u'esriGeometryPolyline',
                          u'MultiPolygon': u'esriGeometryPolygon'}
# GeoJSON geometry types map to. ArcGIS geometry types


class GeometryTypes:
    """ Enum of names for ArcGIS geometry data types
    """
    esriGeometryEnvelope = u'esriGeometryEnvelope'
    esriGeometryPolygon = u'esriGeometryPolygon'

    def __init__(self):
        """placeholder"""
        pass
#class GeometryTypes:


class SpatialRelations:
    """ Enum of names for ArcGIS spatial relations types
    """
    esriSpatialRelIntersects = u'esriSpatialRelIntersects'

    def __init__(self):
        """placeholder"""
        pass
#class SpatialRelations:


class SpatialFilterParams(object):
    """ Parameters for spatial filter.
    Result SR, geometry, geometry type, spatial relation.
    """
    def __init__(self, outSR, agsGeom, geomType, spatRel):
        """ ArcGIS REST API specified spatial query parameters.

        Example: spfilter = esri.SpatialFilterParams(
                            102100,
                            '{"xmin":4103424.83887823,"ymin":7491699.58654681,"xmax":4494782.42369833,"ymax":7726819.88555201,"spatialReference":{"wkid":102100}}',
                            'esriGeometryEnvelope',
                            'esriSpatialRelIntersects')
        """
        self.outSR = outSR
        self.agsGeom = agsGeom
        self.geomType = geomType
        self.spatRel = spatRel
        if not self.spatRel:
            self.spatRel = SpatialRelations.esriSpatialRelIntersects

    def isAllSet(self):
        """ Check filter parameters
        """
        if not self.spatRel or not self.agsGeom or not self.geomType:
            return False
        return True
#class SpatialFilterParams(object)


class OGCSpatialFilterParams(SpatialFilterParams):
    """ Extended esri.SpatialFilterParams data structure
    """
    def __init__(self, esriSF, inpSR, geomWKT):
        """ Set esri.SpatialFilterParams members and set own InputGeomSpatialRef, InputGeomWKT data.
        """
        self.geomSR = inpSR
        self.wktGeom = geomWKT
        assert isinstance(esriSF, SpatialFilterParams)
        super(OGCSpatialFilterParams, self).__init__(esriSF.outSR, esriSF.agsGeom, esriSF.geomType, esriSF.spatRel)
#class OGCSpatialFilterParams(SpatialFilterParams):


class AGGeometryBox(object):
    """ ArcGIS geometry structure for Envelope or Box
    """
    def __init__(self, jsontext):
        """ jsontext is string like
        '{"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}'
        """
        box = simplejson.loads(jsontext)
        #координаты бокса,
        self.xmin = box['xmin']
        self.xmax = box['xmax']
        self.ymin = box['ymin']
        self.ymax = box['ymax']
        self.srWkid = box['spatialReference']['wkid']
#class AGGeometryBox(object):


class AGLayerOperation(object):
    """ Feature Server operations superclass.

    http://resources.arcgis.com/en/help/rest/apiref/fslayer.html
    """
    def __init__(self):
        pass
#class AGLayerOperation(object):


class AGLayerOpQuery(AGLayerOperation):
    """ Feature Server 'query' operation parameters.

    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html

    TODO: validate query parameters (SQL injections may be disaster).
    """
    def __init__(self, args):
        self.rawArgs = args
        super(AGLayerOpQuery, self).__init__()

    @property
    def outSR(self):
        """ Get outSR value from request params.
        Return spatref wkid or 0.
        For gmap/openstreet/bing outSR = 102100 or 3857
        """
        return int(self.rawArgs.get('outSR', 0))

    @property
    def spatRelation(self):
        """ Get spatialRel value from request params.
        Returns 'esriSpatialRelIntersects' or  ... or ''.
        """
        return self.rawArgs.get('spatialRel', '')

    @property
    def geomType(self):
        """ Get geometryType value from request params.
        Returns 'esriGeometryEnvelope' or 'esriGeometryPolygon' or ... or ''.
        """
        return self.rawArgs.get('geometryType', '')

    @property
    def geometry(self):
        """ Get geometry value from request params.
        Return json text or ''.

        Example:
            if geometryType=esriGeometryEnvelope
            geometry='{"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}'

            if geometryType=esriGeometryPolygon
            geometry='{
                "spatialReference":{"wkid":102100},
                "rings":[ [
                        [-3580921.90110393,-273950.309374072],
                        [-3580921.90110393,15615167.6343221],
                        [20037508.3427892,15615167.6343221],
                        [20037508.3427892,-273950.309374072],
                        [-3580921.90110393,-273950.309374072]
                    ], [
                        [-20037508.3427892,-273950.309374072],
                        [-20037508.3427892,15615167.6343221],
                        [-18609053.1581958,15615167.6343221],
                        [-18609053.1581958,-273950.309374072],
                        [-20037508.3427892,-273950.309374072]
                    ] ] }'
        """
        return self.rawArgs.get('geometry', '')
#    def geometry(self):
#class AGLayerOpQuery(AGLayerOperation):


def getLyrOperation(operation, reqargs):
    """ Parse request args dictionary and return AGLayerOperation with operation parameters.

    op = esri.getLyrOperation(operation, request.values)

    http://resources.arcgis.com/en/help/rest/apiref/fsquery.html
    """
    if operation == 'query':
        return AGLayerOpQuery(reqargs)
    return None
#def getLyrOperation(operation, reqargs):


def errorObject(message='Unable to complete operation.', details='Unsupported query or query parameters.'):
    """ Return dictionary with error data for json.dumps() to text,
    for sending error message as ArcGIS do
    """
    tmpl = u"""
        {
         "error": {
          "code": 400,
          "message": "Unable to complete operation.",
          "details": [
           "Operation without query criteria is not allowed."
          ]
         }
        }
    """
    err = simplejson.loads(tmpl)
    err['error']['message'] = message
    err['error']['details'] = (details,)
    return err
#def errorObject(message='Unable to complete operation.', details='Unsupported query or query parameters.'):


def geoJson2agJson(shape):
    """ Returns (geometryType, geometry) tuple
    where geometryType is string and geometry is dictionary according to
    ArcGIS spec http://resources.arcgis.com/en/help/rest/apiref/fsquery.html#response
    Convert GeoJSON style dictionary to ArcGIS JSON style.

    Args:
        shape: dictionary loaded from column 'shape'
        select *, st_asgeojson(1, st_transform(geom::geometry, srid)) shape ...

    geojson_dict_shape_sample = {u'type': u'MultiLineString', u'coordinates': [[[6608812.135620692, 10595529.37672699], [6609963.362158685, 10565901.99030698]]]}
    esriGeometryPolyline_json_geometry_sample =
    {
        "paths": [
         [
          [
           6619987.6538282307,
           10565389.9077409
          ],
          [
           6618262.3001932316,
           10614367.260334643
          ]
         ]
        ]
    }
    """
    geometryType = GEOJSON_ESRI_GEOMTYPES[shape['type']]
    geometry = {}

    if geometryType == u'esriGeometryPoint':
        geometry = {"x": shape['coordinates'][0], "y": shape['coordinates'][1]}
    elif geometryType == u'esriGeometryPolyline':
        geometry = {"paths": shape['coordinates']}
    elif geometryType == u'esriGeometryPolygon':
        if len(shape['coordinates']) == 1:
            geometry = {"rings": shape['coordinates'][0]}
        else:
            geometry = {"rings": shape['coordinates']}
            rings = []
            for ring in shape['coordinates']:
                for e in ring:
                    rings.append(e)
            geometry = {"rings": rings}
    else:
        raise ValueError("geoJson2agJson: unknown geometry type '%s'" % geometryType)

    return (geometryType, geometry)
#def geoJson2agJson(shape):


def AGGeoJSON2WKT(inpGeom, inpGeomType):
    """ Returns tuple (geomSR, geomWKT) that is OGC geometry SpatialReference WKID and geometry WKT
    converted from ArcGIS variation of GeoJSON.

    Args:
        inpGeom: json string, filter geometry object from request e.g.
            geometry={"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}
            or
            geometry={"spatialReference":{"wkid":102100}, "rings":[ [ [-3580921.90110393,-273950.309374072], [-3580921.90110393,15615167.6343221], [20037508.3427892,15615167.6343221], [20037508.3427892,-273950.309374072], [-3580921.90110393,-273950.309374072] ],[ [-20037508.3427892,-273950.309374072], [-20037508.3427892,15615167.6343221], [-18609053.1581958,15615167.6343221], [-18609053.1581958,-273950.309374072], [-20037508.3427892,-273950.309374072] ] ] }
        inpGeomType: string, input geometry type, one of (esriGeometryEnvelope, esriGeometryPolygon)
    """
    if inpGeomType == GeometryTypes.esriGeometryEnvelope:
        box = AGGeometryBox(inpGeom)
        geomSR = box.srWkid
        geomWKT = """POLYGON((%s %s, %s %s, %s %s, %s %s, %s %s))""" % (
                  box.xmin, box.ymin, box.xmax, box.ymin, box.xmax, box.ymax,
                  box.xmin, box.ymax, box.xmin, box.ymin)

    elif inpGeomType == GeometryTypes.esriGeometryPolygon:
        pgon = simplejson.loads(inpGeom)
        geomSR = pgon['spatialReference']['wkid']
        geomWKT = AGGeoJSONPolygon2WKT(pgon)

    else:
        raise TypeError("Geometry type '%s' haven't transformation yet" % inpGeomType)

#    print geomWKT
    return (geomSR, geomWKT)
#def AGGeoJSON2WKT(inpGeom, inpGeomType)


def AGGeoJSONPolygon2WKT(pgon):
    """ Returns OGC WKT multipolygon created from ArcGIS GeoJSON esriGeometryPolygon.

    Args:
        pgon: dictionary loaded from AGS GeoJSON, e.g.
        inpGeom = '{"spatialReference":{"wkid":102100}, "rings":[ [ [-3580921.90110393,-273950.309374072], [-3580921.90110393,15615167.6343221], [20037508.3427892,15615167.6343221], [20037508.3427892,-273950.309374072], [-3580921.90110393,-273950.309374072] ],[ [-20037508.3427892,-273950.309374072], [-20037508.3427892,15615167.6343221], [-18609053.1581958,15615167.6343221], [-18609053.1581958,-273950.309374072], [-20037508.3427892,-273950.309374072] ] ] }'
        pgon = simplejson.loads(inpGeom)
    """
    wktMPoly = ''
    for ring in pgon['rings']:
#            print "ring: '%s'" % ring
        wktPoly = ''
        for point in ring:
#                print "point: '%s'" % point
            xy = "%r %r" % (point[0], point[1])
            if wktPoly:
                wktPoly = ',\n'.join((wktPoly, xy))
            else:
                wktPoly = xy

        #~ print "wktPoly: '%s'" % wktPoly
        if wktMPoly:
            wktMPoly = '\n)), ((\n'.join((wktMPoly, wktPoly))
        else:
            wktMPoly = wktPoly

    if wktMPoly:
        wktMPoly = 'MULTIPOLYGON( ((\n' + wktMPoly + '\n)) )'
    return wktMPoly
#def AGGeoJSONPolygon2WKT(pgon):
