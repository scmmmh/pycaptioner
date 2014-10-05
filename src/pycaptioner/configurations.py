# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import numpy

from pyproj import Proj

from pycaptioner import models

MODELS = {'rural': {'one_poi': ['near.rural', 'east.rural', 'north.rural', 'west.rural', 'south.rural'],
                    'two_poi': ['between.rural']},
          'urban': {'one_poi': ['at_corner.urban', 'at.urban', 'next_to.urban', 'near.urban'],
                    'two_poi': []}}


def generate_configurations(reference, gaz, context):
    pois = gaz(reference, 'poi')
    proj = Proj(init='epsg:32630')
    reference = numpy.array(proj(reference.x, reference.y))
    for feature in pois:
        feature['geo_lonlat'] = numpy.array(proj(feature['geo_lonlat'].x, feature['geo_lonlat'].y))
    configurations = []
    for model_name in MODELS[context]['one_poi']:
        model = models.load(model_name)
        for feature in pois:
            value = model(*(reference - feature['geo_lonlat']))
            if model_name != 'near.rural':
                value = value * 0.9 # TODO: This is a hack that needs to be addressed
            if value >= 0.6:
                configurations.append(((model_name, value), feature))
    return configurations