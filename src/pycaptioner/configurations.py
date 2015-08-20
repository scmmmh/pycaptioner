# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import logging
import numpy

from copy import deepcopy
from itertools import permutations
from pyproj import Proj
from shapely import geometry

from pycaptioner import models

MODELS = {'rural': {'one_poi': ['at.rural', 'near.rural', 'east.rural', 'north.rural', 'west.rural', 'south.rural'],
                    'two_poi': []},
          'urban': {'one_poi': ['at.urban', 'next_to.urban', 'near.urban'],
                    'two_poi': ['between.urban']}}


class Projector(object):

    def __init__(self, init):
        self.proj = Proj(init=init)

    def __call__(self, geom):
        if isinstance(geom, geometry.Point):
            return geometry.Point(*self.proj(geom.x, geom.y))
        elif isinstance(geom, geometry.LineString):
            coords = []
            for coord in geom.coords:
                coords.append(self.proj(coord[0], coord[1]))
            return geometry.LineString(coords)
        elif isinstance(geom, list):
            return [self(item) for item in geom]
        elif isinstance(geom, dict):
            if 'geo_lonlat' in geom:
                result = deepcopy(geom)
                result['geo_lonlat'] = self(geom['geo_lonlat'])
                return result
            else:
                logging.warning('No geo_lonlat to project')
                return None
        else:
            logging.warning('Trying to project an unknown type %s' % (geom.__class__))
            return None


def generate_contain_configurations(reference, gaz, context, projector):
    if context == 'rural':
        return gaz(reference, category='contain', filter_rural_score='MEDIUM')
    elif context == 'urban':
        return gaz(reference, category='contain', filter_urban_score='MEDIUM')
    else:
        return None


def generate_relative_configurations(reference, gaz, context, projector):
    if context == 'rural':
        pois = projector(gaz(reference, category='poi', filter_rural_score='MEDIUM'))
    elif context == 'urban':
        pois = projector(gaz(reference, category='poi', filter_urban_score='MEDIUM'))
        roads = projector(gaz(reference, category='way', filter_urban_score='LOW'))

    proj_reference = projector(reference)
    configurations = []
    for model_name in MODELS[context]['one_poi']:
        model = models.load(model_name)
        for feature in pois:
            value = model(*(numpy.array(proj_reference) - numpy.array(feature['geo_lonlat'])))
            if value >= 0.4:
                configurations.append({'type': 'preposition', 'model': model_name, 'value': value, 'feature': feature})
    if context == 'rural':
        for model_name in MODELS[context]['two_poi']:
            model = models.load(model_name)
            for idx in range(1, len(pois)):
                start = pois[idx]
                for idx2 in range(0, idx):
                    end = pois[idx2]
                    if start['dc_title'] != end['dc_title'] and start['geo_type'].main_type == end['geo_type'].main_type and start['geo_type'].main_type != 'POI':
                        d = start['geo_lonlat'].distance(end['geo_lonlat'])
                        if 5000 > d > 0:
                            params = list((numpy.array(end['geo_lonlat']) - numpy.array(start['geo_lonlat']))) + list((numpy.array(proj_reference) - numpy.array(start['geo_lonlat'])))
                            value = model(*(params))
                            if value >= 0.6:
                                configurations.append({'type': 'preposition', 'model': model_name, 'value': value, 'feature': [start, end]})
    elif context == 'urban':
        for model_name in MODELS[context]['two_poi']:
            model = models.load(model_name)
            for road in roads:
                if road['geo_lonlat'].distance(proj_reference) <= 10:
                    if model_name == 'between.urban':
                        intersections = []
                        for poi in pois:
                            d = road['geo_lonlat'].distance(poi['geo_lonlat'])
                            if d <= 10:
                                intersections.append(poi)
                        for road2 in roads:
                            if road['dc_title'] != road2['dc_title'] and road['geo_lonlat'].intersects(road2['geo_lonlat']):
                                intersection = road['geo_lonlat'].intersection(road2['geo_lonlat'])
                                if isinstance(intersection, geometry.Point):
                                    poi = deepcopy(road2)
                                    poi['geo_lonlat'] = intersection
                                    intersections.append(poi)
                        for pairs in permutations(intersections, 2):
                            dist_1 = road['geo_lonlat'].project(pairs[0]['geo_lonlat'])
                            dist_2 = road['geo_lonlat'].project(proj_reference)
                            dist_3 = road['geo_lonlat'].project(pairs[1]['geo_lonlat'])
                            if dist_1 < dist_2 < dist_3:
                                value = model(dist_2 - dist_1) / (dist_3 - dist_1)
                                if value >= 0.6:
                                    configurations.append({'type': 'preposition', 'model': model_name, 'value': value, 'feature': [pairs[0], pairs[1]]})
    return configurations


def generate_road_configurations(reference, gaz, context, projector):
    if context == 'rural':
        roads = projector(gaz(reference, category='way', filter_rural_score='LOW'))
    elif context == 'urban':
        roads = projector(gaz(reference, category='way', filter_urban_score='LOW'))

    proj_reference = projector(reference)
    configurations = []
    for road in roads:
        d = road['geo_lonlat'].distance(proj_reference)
        if d <= 10:
            configurations.append({'type': 'preposition', 'model': 'on', 'value': 1, 'feature': road})
        if context == 'urban':
            model = models.load('at_corner.urban')
            for road2 in roads:
                if road['dc_title'] != road2['dc_title'] and road['geo_lonlat'].intersects(road2['geo_lonlat']):
                    intersection = road['geo_lonlat'].intersection(road2['geo_lonlat'])
                    if isinstance(intersection, geometry.Point):
                        params = list(numpy.array(proj_reference) - numpy.array(intersection))
                        value = model(*params)
                        if value >= 0.6:
                            configurations.append({'type': 'preposition', 'model': 'at_corner.urban', 'value': value, 'feature': [road, road2]})
    return configurations


def generate_configurations(reference, gaz, context):
    projector = Projector(init='EPSG:32630')
    configurations = {}
    contain_config = generate_contain_configurations(reference, gaz, context, projector)
    if contain_config:
        configurations['contain'] = contain_config
    rel_configs = generate_relative_configurations(reference, gaz, context, projector)
    if rel_configs:
        configurations['relative'] = rel_configs
    road_config = generate_road_configurations(reference, gaz, context, projector)
    if road_config:
        configurations['support'] = road_config
    return configurations
