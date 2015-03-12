# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import numpy
import math

from pyproj import Proj

from pycaptioner import models

MODELS = {'rural': {'one_poi': ['at.rural', 'near.rural', 'east.rural', 'north.rural', 'west.rural', 'south.rural'],
                    'two_poi': ['between.rural']},
          'urban': {'one_poi': ['at_corner.urban', 'at.urban', 'next_to.urban', 'near.urban'],
                    'two_poi': ['between.urban']}}


def generate_configurations(reference, gaz, context):
    if context == 'rural':
        pois = gaz(reference, category='poi', filter_rural_score='MEDIUM')
        contain = gaz(reference, category='contain', filter_rural_score='MEDIUM')
    elif context == 'urban':
        pois = gaz(reference, category='poi', filter_urban_score='MEDIUM')
        contain = gaz(reference, category='contain', filter_urban_score='MEDIUM')
    proj = Proj(init='epsg:32630')
    reference = numpy.array(proj(reference.x, reference.y))
    for feature in pois:
        feature['geo_lonlat'] = numpy.array(proj(feature['geo_lonlat'].x, feature['geo_lonlat'].y))
    configurations = []
    for model_name in MODELS[context]['one_poi']:
        model = models.load(model_name)
        for feature in pois:
            value = model(*(reference - feature['geo_lonlat']))
            if value >= 0.4:
                configurations.append({'type': 'preposition', 'model': model_name, 'value': value, 'feature': feature})
    for model_name in MODELS[context]['two_poi']:
        model = models.load(model_name)
        for idx in range(1, len(pois)):
            start = pois[idx]
            for idx2 in range(0, idx):
                end = pois[idx2]
                if context == 'rural':
                    if start['dc_title'] != end['dc_title'] and start['geo_type'].main_type == end['geo_type'].main_type and start['geo_type'].main_type != 'POI':
                        d = math.sqrt(math.pow(end['geo_lonlat'][0] - start['geo_lonlat'][0], 2) +
                                      math.pow(end['geo_lonlat'][1] - start['geo_lonlat'][1], 2))
                        if 5000 > d > 0:
                            params = list((end['geo_lonlat'] - start['geo_lonlat'])) + list((reference - start['geo_lonlat']))
                            value = model(*(params))
                            if value >= 0.6:
                                configurations.append({'type': 'preposition', 'model': model_name, 'value': value, 'feature': [start, end]})
    return {'relative': configurations, 'contain': contain}
