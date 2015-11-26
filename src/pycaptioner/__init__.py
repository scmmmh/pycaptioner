import logging
import numpy

from osmgaz import OSMGaz, filters
from pyproj import Proj
from shapely.geometry import Point, LineString, Polygon
from shapely import wkt

from pycaptioner import models, language

logging.root.setLevel(logging.DEBUG)

RURAL_ONE_POINT_MODELS = ['on.universal', 'next_to.universal', 'near.rural', 'east.rural', 'north.rural', 'west.rural', 'south.rural']
URBAN_ONE_POINT_MODELS = ['on.universal', 'at_corner.urban', 'at.urban', 'next_to.universal', 'near.urban']
RURAL_TWO_POINT_MODELS = ['between.rural']
URBAN_TWO_POINT_MODELS = ['between.urban']


def distance(point, other):
    if isinstance(other, Polygon):
        return max([point.distance(Point(c)) for c in other.exterior.coords])
    elif isinstance(other, LineString):
        return max([point.distance(Point(c)) for c in other.coords])
    else:
        return point.distance(other)

def sort_key(point, toponyms, weights):
    distances = [point.distance(toponym['osm_geometry']) for toponym in toponyms]
    min_dist = min(distances)
    max_dist = max(distances) - min_dist
    distances = [distance(point, toponym['osm_geometry']) for toponym in toponyms]
    min_error_dist = min(distances)
    max_error_dist = max(distances) - min_error_dist
    def score(toponym):
        dist_score = (1 - (point.distance(toponym['osm_geometry']) - min_dist) / max_dist) * weights['dist']
        error_score = (1 - (distance(point, toponym['osm_geometry']) - min_error_dist) / max_error_dist) * weights['error']
        if 'osm_salience' in toponym:
            if 'name' in toponym['osm_salience']:
                name_score = toponym['osm_salience']['name'] * weights['name']
            else:
                name_score = 0
            if 'type' in toponym['osm_salience']:
                type_score = toponym['osm_salience']['type'] * weights['type']
            else:
                type_score = 0
            score = dist_score + error_score + name_score + type_score
        else:
            score = dist_score + error_score
        return score
    return score


def calculate_potentials(point, toponyms, spatial_error, weights):  # Should only filter by spatial error the first time. Then need to select higher scoring toponyms
    potentials = []
    for toponym in toponyms:
        if distance(point, toponym['osm_geometry']) < spatial_error:
            potentials.append(toponym)
    if len(potentials) > 1:
        potentials.sort(key=sort_key(point, potentials, weights), reverse=True)
    return potentials
    
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
    proj = Proj(init='epsg:3857')
    captions = []
    for point in points:
        print(point)
        geo_data = gaz(point)
        point = Point(*proj(*point))
        elements = []
        spatial_error = distance(point, wkt.loads(geo_data['osm_containment'][0]['osm_geometry']))
        urban_area = False
        for toponym in geo_data['osm_proximal']:
            toponym['osm_geometry'] = wkt.loads(toponym['osm_geometry'])
            print(toponym['dc_title'], point.distance(toponym['osm_geometry']))
            if filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING']) and toponym['osm_geometry'].distance(point) < 400:
                urban_area = True
        potentials = calculate_potentials(point, geo_data['osm_proximal'],
                                          spatial_error,
                                          {'dist': 0.4, 'error': 0.1, 'name': 0.3, 'type': 0.2})
        if urban_area:
            print('Urban')
            preposition_models = [(model_name, models.load(model_name)) for model_name in URBAN_ONE_POINT_MODELS]
        else:
            print('Rural')
            preposition_models = [(model_name, models.load(model_name)) for model_name in RURAL_ONE_POINT_MODELS]
        for toponym in potentials:
            added = False
            for model_name, model in preposition_models:
                geom = toponym['osm_geometry']
                if isinstance(geom, LineString):
                    geom = geom.interpolate(geom.project(point))
                elif isinstance(geom, Polygon):
                    geom = LineString(geom.exterior)
                    geom = geom.interpolate(geom.project(point))
                if model_name.startswith('at_corner.') and filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD', 'JUNCTION']):
                    pass
                elif model_name.startswith('on.') and filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD']):
                    if model(point.x - geom.x, point.y - geom.y) == 1:
                        elements.append({'dc_type': 'preposition',
                                         'preposition': 'on.universal',
                                         'toponym': {'dc_title': toponym['dc_title'],
                                                     'dc_type': toponym['dc_type']}})
                        spatial_error = distance(point, toponym['osm_geometry'])
                        added = True
                        break
            if added:
                break
        last_preposition_idx = 0
        while len(potentials) > 0:
            for toponym in potentials:
                geom = toponym['osm_geometry']
                if isinstance(geom, LineString):
                    geom = geom.interpolate(geom.project(point))
                elif isinstance(geom, Polygon):
                    geom = LineString(geom.exterior)
                    geom = geom.interpolate(geom.project(point))
                added = False
                for idx, (model_name, model) in enumerate(preposition_models[last_preposition_idx:]):
                    if model_name.startswith('at_corner.') and not filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD', 'JUNCTION']):
                        continue
                    elif model_name.startswith('on.') and not filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD']):
                        continue
                    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD']):
                        continue
                    score = model(point.x - geom.x, point.y - geom.y)
                    if score > 0.6:
                        elements.append({'dc_type': 'preposition',
                                         'preposition': model_name,
                                         'toponym': {'dc_title': toponym['dc_title'],
                                                     'dc_type': toponym['dc_type']}})
                        added = True
                        last_preposition_idx = last_preposition_idx + idx + 1
                        break
                if added:
                    break
            if not added:
                break
            print(distance(point, toponym['osm_geometry']))
            spatial_error = distance(point, toponym['osm_geometry'])
            potentials = calculate_potentials(point,
                                              potentials,
                                              spatial_error,
                                              {'dist': 0.1, 'error': 0.4, 'name': 0.4, 'type': 0.1})
        elements.extend([{'dc_type': 'preposition','preposition': 'in',
                          'toponym': {'dc_title': toponym['dc_title'],
                                      'dc_type': toponym['dc_type']}} for toponym in geo_data['osm_containment'][:-1]])
        captions.append(language.generate_caption(elements))
    for c in captions:
        print(c)

