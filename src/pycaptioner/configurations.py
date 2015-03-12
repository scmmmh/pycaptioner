# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import numpy

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
    return {'relative': configurations, 'contain': contain}
