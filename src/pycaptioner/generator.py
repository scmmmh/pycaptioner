# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@edgehill.ac.uk>
"""
from logging import getLogger
from osmgaz import OSMGaz, filters
from pyproj import Proj
from shapely.geometry import Point, MultiLineString, LineString, Polygon
from shapely import wkt

from pycaptioner import models

logger = getLogger('pycaptioner')

RURAL_TWO_POINT_MODELS = ['between.rural'] # Todo: Do something with these
URBAN_TWO_POINT_MODELS = ['between.urban']

MODELS = {'urban': [(model_name, models.load(model_name), excludes)
                    for model_name, excludes in [('at_corner.urban', ['at_corner.urban']),
                                                 ('on.universal', ['at_corner.urban',
                                                                   'on.universal']),
                                                 ('at.urban', ['at_corner.urban',
                                                               'on.universal',
                                                               'at.urban']),
                                                 ('next_to.universal', ['at_corner.urban',
                                                                        'on.universal',
                                                                        'at.urban',
                                                                        'next_to.universal']),
                                                 ('near.urban', ['at_corner.urban',
                                                                 'on.universal',
                                                                 'at.urban',
                                                                 'next_to.universal',
                                                                 'near.urban'])]],
          'rural': [(model_name, models.load(model_name), excludes)
                    for model_name, excludes in [('on.universal', ['on.universal']),
                                                 ('next_to.universal', ['on.universal',
                                                                        'next_to.universal']),
                                                 ('near.rural', ['on.universal',
                                                                 'next_to.universal',
                                                                 'near.rural',
                                                                 'east.rural',
                                                                 'north.rural',
                                                                 'west.rural',
                                                                 'south.rural']),
                                                 ('east.rural', ['on.universal',
                                                                 'next_to.universal',
                                                                 'near.rural',
                                                                 'east.rural',
                                                                 'west.rural']),
                                                 ('north.rural', ['on.universal',
                                                                  'next_to.universal',
                                                                  'near.rural',
                                                                  'north.rural',
                                                                  'south.rural']),
                                                 ('west.rural', ['on.universal',
                                                                 'next_to.universal',
                                                                 'near.rural',
                                                                 'east.rural',
                                                                 'west.rural']),
                                                 ('south.rural', ['on.universal',
                                                                  'next_to.universal',
                                                                  'near.rural',
                                                                  'north.rural',
                                                                  'south.rural'])]]}
PROJ = Proj(init='epsg:3857')
ROAD_WEIGHTS = {'dist': 1, 'error': 0, 'name': 0, 'type': 0, 'flickr': 0}
DISTANCE_WEIGHTS = {'rural': {'dist': 0.45, 'error': 0.15, 'name': 0.05, 'type': 0.05, 'flickr': 0.3},
                    'urban': {'dist': 0.55, 'error': 0.05, 'name': 0.05, 'type': 0.05, 'flickr': 0.3}}
SALIENCE_WEIGHTS = {'dist': 0.1, 'error': 0, 'name': 0.05, 'type': 0.05, 'flickr': 0.8}


def max_distance(point, other):
    """Calculate the maximum distance from the point to the other geometry. For
    things other than Points this will return the distance to the most distant
    control point."""
    if isinstance(other, Polygon):
        return max([point.distance(Point(c)) for c in other.exterior.coords])
    elif isinstance(other, LineString):
        return max([point.distance(Point(c)) for c in other.coords])
    elif isinstance(other, MultiLineString):
        return max([max_distance(point, part) for part in other])
    else:
        return point.distance(other)


def distance_limits(point, toponyms):
    """Calculate the maximum and miminum shortest and longest distances from the
    point to all toponyms."""
    distances = [point.distance(toponym['osm_geometry']) for toponym in toponyms]
    dist = (min(distances), max(distances) - min(distances))
    distances = [max_distance(point, toponym['osm_geometry']) for toponym in toponyms]
    error_dist = (min(distances), max(distances) - min(distances))
    return (dist, error_dist)


def flickr_normalisation(toponyms):
    """Calculate the minimum and maximum normalisation values for Flickr data."""
    if toponyms:
        counts = [toponym['osm_salience']['flickr'] if 'osm_salience' in toponym and 'flickr' in toponym['osm_salience'] else 0 for toponym in toponyms]
        return (min(counts), max(counts))
    else:
        return (0, 0)


def toponym_score(point, toponym, weights, dist=None, error_dist=None, flickr_norm=None, toponyms=None):
    """Calculate the score for the toponym given the weights. Must specify either
    dist and error_dist or toponyms. In the case of specifying toponyms, will autoamtically
    calculate dist and error_dist."""
    if toponyms:
        dist, error_dist = distance_limits(point, toponyms)
        flickr_norm = flickr_normalisation(toponyms)
    if dist[1] == 0:
        dist_score = 1
    else:
        dist_score = (1 - (point.distance(toponym['osm_geometry']) - dist[0]) / dist[1]) * weights['dist']
    if error_dist[1] == 0:
        error_score = 1
    else:
        error_score = (1 - (max_distance(point, toponym['osm_geometry']) - error_dist[0]) / error_dist[1]) * weights['error']
    if 'osm_salience' in toponym:
        if 'name' in toponym['osm_salience']:
            name_score = float(toponym['osm_salience']['name']) * weights['name']
        else:
            name_score = 0
        if 'type' in toponym['osm_salience']:
            type_score = float(toponym['osm_salience']['type']) * weights['type']
        else:
            type_score = 0
        if 'flickr' in toponym['osm_salience']:
            if flickr_norm[1] > 0:
                flickr_score = (float(toponym['osm_salience']['flickr'] - flickr_norm[0]) / flickr_norm[1]) * weights['flickr']
            else:
                flickr_score = float(toponym['osm_salience']['flickr']) * weights['flickr']
        else:
            flickr_score = 0
        score = dist_score + error_score + name_score + type_score + flickr_score
    else:
        score = dist_score + error_score
    return score


def sort_key(point, toponyms, weights):
    """Generates a function used to calculate sorting keys for sorting toponyms."""
    dist, error_dist = distance_limits(point, toponyms)
    flickr_norm = flickr_normalisation(toponyms)
    def score(toponym):
        return toponym_score(point, toponym, weights, dist=dist, error_dist=error_dist, flickr_norm=flickr_norm)
    return score


def filter_by_max_distance(point, toponyms, limit):
    """Filter all toponyms that are more than the limit max_distance from the point."""
    return [toponym for toponym in toponyms if max_distance(point, toponym['osm_geometry']) < limit]


def filter_by_min_distance(point, toponyms, limit):
    """Filter all toponyms that are less than the limit distance from the point."""
    return [toponym for toponym in toponyms if point.distance(toponym['osm_geometry']) >= limit]


def filter_by_score(point, toponyms, limit, weights):
    """Filter all toponyms that have a score lower than limit.""" 
    dist, error_dist = distance_limits(point, toponyms)
    flickr_norm = flickr_normalisation(toponyms)
    return [toponym for toponym in toponyms
            if toponym_score(point, toponym, weights, dist=dist, error_dist=error_dist, flickr_norm=flickr_norm) > limit]


def filter_by_names(toponyms, names):
    """Filter all toponyms that share an already-used name."""
    return [toponym for toponym in toponyms if toponym['dc_title'] not in names]


def filter_by_type(toponyms, dc_type):
    """Filter all toponyms that have the same type or a sub-type."""
    return [toponym for toponym in toponyms if not filters.type_match(toponym['dc_type'], dc_type)]


def sort(point, toponyms, weights):
    """Sort the given toponyms based on the sort_key."""
    if len(toponyms) > 1:
        toponyms.sort(key=sort_key(point, toponyms, weights),
                      reverse=True)
    return toponyms


def load_geodata(sqlalchemy_url, point, callback):
    """Load the geo-data from the gazetteer."""
    gaz = OSMGaz(sqlalchemy_url, callback=callback)
    geo_data = gaz(point)
    for toponym in geo_data['osm_proximal']:
        toponym['osm_geometry'] = wkt.loads(toponym['osm_geometry'])
    for toponym in geo_data['osm_containment']:
        toponym['osm_geometry'] = wkt.loads(toponym['osm_geometry'])
    return geo_data


def urban_rural(geo_data, point):
    """Determine whether the point is a rural or urban location."""
    for toponym in geo_data['osm_proximal']:
        if filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING']) and toponym['osm_geometry'].distance(point) < 400:
            return 'urban'
    return 'rural'


def closest_point(point, geom):
    """Return the closest point in geom with respect to point."""
    if isinstance(geom, LineString) or isinstance(geom, MultiLineString):
        geom = geom.interpolate(geom.project(point))
    elif isinstance(geom, Polygon):
        geom = LineString(geom.exterior)
        geom = geom.interpolate(geom.project(point))
    return geom


def add_road_element(point, toponyms, models):
    """Determine whether there is a road toponym to be added to the caption and return that."""
    for toponym in toponyms:
        if filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD']):
            geom = closest_point(point, toponym['osm_geometry'])
            for model_name, model, _ in models:
                if filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD', 'JUNCTION']):
                    if model_name.startswith('at_corner.'):
                        if model(point.x - geom.x, point.y - geom.y) > 0.6:
                            return {'dc_type': 'preposition',
                                    'preposition': model_name,
                                    'toponym': toponym}
                else:
                    if model_name.startswith('on.'):
                        if model(point.x - geom.x, point.y - geom.y) == 1:
                            return {'dc_type': 'preposition',
                                    'preposition': 'on.universal',
                                    'toponym': toponym}
    return None


def filter_models(models, filter_name):
    """Filter models, removing all models with the filter_name. filter_name can either
    be a single string or a list of strings."""
    if isinstance(filter_name, list):
        for name in filter_name:
            models = filter_models(models, name)
    else:
        models = [(name, model, excludes) for (name, model, excludes) in models if not name.startswith(filter_name)]
    return models


def add_toponym_element(point, toponyms, models):
    """Determine whether there is a toponym to be added to the caption and return that."""
    for toponym in toponyms:
        geom = closest_point(point, toponym['osm_geometry'])
        for model_name, model, _ in models:
            if model_name.startswith('on.') and not filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD']):
                continue
            elif model_name.startswith('at_corner.') and not filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD', 'JUNCTION']):
                continue
            elif model_name.startswith('at.') and not isinstance(toponym['osm_geometry'], Point):
                continue
            elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD']):
                continue
            score = model(point.x - geom.x, point.y - geom.y)
            if model_name.startswith('near.') and 'osm_salience' in toponym and 'flickr' in toponym['osm_salience'] and toponym['osm_salience']['flickr'] >= 1000:
                score_limit = 0.4
            else:
                score_limit = 0.66666
            if score >= score_limit:
                return {'dc_type': 'preposition',
                        'preposition': model_name,
                        'toponym': toponym}


def generate_caption(sqlalchemy_url, point, filter_names=None, callback=None):
    """Generate a caption for the given point."""
    if callback is not None:
        callback('Loading location data')
    geo_data = load_geodata(sqlalchemy_url, point, callback)
    point = Point(*PROJ(*point))
    caption = []
    spatial_error = max_distance(point, geo_data['osm_containment'][0]['osm_geometry'])
    if callback is not None:
        callback('Loading preposition models')
    models = MODELS[urban_rural(geo_data, point)]
    if callback is not None:
        callback('Generating a location description')
    names = [t['dc_title'] for t in geo_data['osm_containment']]
    if filter_names is not None:
        names.extend(filter_names)
    toponyms = sort(point,
                    filter_by_max_distance(point,
                                           filter_by_names(geo_data['osm_proximal'], names),
                                           spatial_error),
                    ROAD_WEIGHTS)
    road = add_road_element(point, toponyms, models)
    if road:
        names.append(road['toponym']['dc_title'])
        caption.append(road)
        spatial_error = max_distance(point, road['toponym']['osm_geometry'])
        models = filter_models(models, ['at_corner.', 'on.'])
    toponyms = filter_by_type(toponyms, ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD'])
    if filters.type_match(geo_data['osm_containment'][0]['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING']):
        if toponyms:
            toponyms = sort(point,
                            filter_by_score(point,
                                            filter_by_names(toponyms, names),
                                            toponym_score(point,
                                                          geo_data['osm_containment'][0],
                                                          SALIENCE_WEIGHTS,
                                                          toponyms=toponyms),
                                            SALIENCE_WEIGHTS),
                            SALIENCE_WEIGHTS)
        caption.append({'dc_type': 'preposition',
                        'preposition': 'in',
                        'toponym': geo_data['osm_containment'][0]})
        geo_data['osm_containment'] = geo_data['osm_containment'][1:]
    else:
        toponyms = sort(point,
                        filter_by_max_distance(point,
                                               filter_by_names(toponyms, names),
                                               spatial_error),
                        DISTANCE_WEIGHTS[urban_rural(geo_data, point)])
    while len(toponyms) > 0 and len(models) > 0:
        toponym = add_toponym_element(point, toponyms, models)
        if toponym:
            caption.append(toponym)
            
            models = filter_models(models, [excludes for model_name, _, excludes in models if model_name.startswith(toponym['preposition'])][0])
            toponyms = sort(point,
                            filter_by_min_distance(point,
                                                   filter_by_score(point,
                                                                   filter_by_names(toponyms, names),
                                                                   toponym_score(point,
                                                                                 caption[-1]['toponym'],
                                                                                 SALIENCE_WEIGHTS,
                                                                                 toponyms=toponyms),
                                                                   SALIENCE_WEIGHTS),
                                                   point.distance(caption[-1]['toponym']['osm_geometry'])),
                            SALIENCE_WEIGHTS)
        else:
            toponyms = []
    caption.extend([{'dc_type': 'preposition','preposition': 'in',
                     'toponym': toponym} for toponym in geo_data['osm_containment'][:-1]])
    return caption
