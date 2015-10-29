import logging
import numpy

from osmgaz import OSMGaz
from pyproj import Proj

from pycaptioner import models, language, generator
from pycaptioner.gazetteer import *

logging.root.setLevel(logging.DEBUG)

RURAL_ONE_POINT_MODELS = ['near.rural', 'east.rural', 'north.rural', 'west.rural', 'south.rural']
URBAN_ONE_POINT_MODELS = ['at_corner.urban', 'at.urban', 'next_to.urban', 'near.urban']
RURAL_TWO_POINT_MODELS = ['between.rural']
URBAN_TWO_POINT_MODELS = ['between.urban']


def main():
    points = [
              (-2.63629, 53.39797), # Dakota Park
              (-1.88313, 53.38129), # Peak District
              (-3.43924, 51.88286), # Brecon Beacons
              (-3.17516, 51.50650), # Roath Park
              (-2.99141, 53.40111), # Liverpool
              (-2.04045, 53.34058), # Lyme Park
              (-2.47429, 53.3827),  # Lymm
              ]
    gaz = OSMGaz('postgresql+psycopg2://osm:osmPWD@localhost:4321/osm')
    for point in points:
        print(point)
        geo_data = gaz(point)
        print(language.generate_caption([{'dc_type': 'preposition',
                                          'preposition': 'in',
                                          'toponym': {'dc_title': toponym['dc_title'],
                                                      'dc_type': toponym['dc_type']}} for toponym in geo_data['osm_containment'][:-1]]))
    '''
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
    '''
