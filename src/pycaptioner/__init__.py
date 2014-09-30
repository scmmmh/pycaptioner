import logging
import numpy

from pyproj import Proj

from pycaptioner import models, language, generator
from pycaptioner.gazetteer import *

logging.root.setLevel(logging.DEBUG)

RURAL_ONE_POINT_MODELS = ['near.rural', 'east.rural', 'north.rural', 'west.rural', 'south.rural']
URBAN_ONE_POINT_MODELS = ['at_corner.urban', 'at.urban', 'next_to.urban', 'near.urban']
RURAL_TWO_POINT_MODELS = ['between.rural']
URBAN_TWO_POINT_MODELS = ['between.urban']


def main():
    proj = Proj(init='epsg:32630')
    for feature in GAZETTEER:
        feature['geo_lonlat'] = numpy.array(proj(*feature['geo_lonlat']))
    #point = numpy.array(proj(*(-2.5901763343811035, 53.38953524087438)))
    #point = numpy.array(proj(*(-2.6008307933807373, 53.388645857875055, )))
    #point = numpy.array(proj(*(-2.5901763343811035, 53.38953524087438)))
    point = numpy.array(proj(*(-2.6004, 53.3887))) # Between point
    configurations = []
    """
    for model_name in RURAL_ONE_POINT_MODELS:
        model = models.load(model_name)
        for feature in GAZETTEER:
            if model_name in ['at.urban', 'near.urban', 'next_to.urban', 'east.rural', 'north.rural', 'west.rural', 'south.rural', 'near.rural'] and feature['dc_type'] == POI:
                value = model(*(point - feature['geo_lonlat']))
            elif model_name == 'at_corner.urban' and feature['dc_type'] == JUNCTION:
                value = model(*(point - feature['geo_lonlat']))
            else:
                value = None
            if value and value >= 0.6:
                print model_name, value
                configurations.append(((model_name, value), feature))
    """
    for model_name in RURAL_TWO_POINT_MODELS:
        model = models.load(model_name)
        for feature1 in GAZETTEER:
            for feature2 in GAZETTEER:
                if feature1['dc_type'] != JUNCTION and feature2['dc_type'] != JUNCTION and feature1['dc_title'] != feature2['dc_title']:
                    baseline = feature2['geo_lonlat'] - feature1['geo_lonlat']
                    pos = point - feature1['geo_lonlat']
                    print(baseline, pos)
                    configurations.append((('between.rural', 1), feature1, feature2))
    print(language.generate_caption(generator.urban_caption(configurations)))

