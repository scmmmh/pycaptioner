# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import logging
import numpy

from copy import deepcopy
from csv import DictReader
from io import TextIOWrapper
from pkg_resources import resource_stream
from re import match
from shapely import geometry, wkt

UNKNOWN = 'UNKNOWN'
POI = 'POI'
JUNCTION = 'JUNCTION'
POPULATED_PLACE = 'POPULATED_PLACE'
NATURAL_FEATURE = 'NATURAL_FEATURE'
AREA = 'AREA'

SCORE_MAPPINGS = {'LOW': 1,
                  'MEDIUM': 2,
                  'HIGH': 3}

TYPE_MAPPINGS = {}
reader = DictReader(TextIOWrapper(resource_stream('pycaptioner', 'data/gazetteer_type_mappings.csv')))
for line in reader:
    if line['source'].lower() not in TYPE_MAPPINGS:
        TYPE_MAPPINGS[line['source'].lower()] = {}
    if line['source_type'].lower() not in TYPE_MAPPINGS[line['source'].lower()]:
        TYPE_MAPPINGS[line['source'].lower()][line['source_type'].lower()] = {'main': line['target'],
                                                                              'sub': line['source_type'].lower(),
                                                                              'rural_score': SCORE_MAPPINGS[line['rural_score']],
                                                                              'urban_score': SCORE_MAPPINGS[line['urban_score']]}


class LocationType(object):
    
    def __init__(self, source, source_type):
        self.main_type = UNKNOWN
        self.sub_type = None
        self.rural_score = None
        self.urban_score = None
        if source:
            source = source.lower()
            if source_type:
                source_type = source_type.lower()
            else:
                source_type = ''
            if source in TYPE_MAPPINGS and source_type in TYPE_MAPPINGS[source]:
                self.main_type = TYPE_MAPPINGS[source][source_type]['main']
                self.sub_type = TYPE_MAPPINGS[source][source_type]['sub']
                self.rural_score = TYPE_MAPPINGS[source][source_type]['rural_score']
                self.urban_score = TYPE_MAPPINGS[source][source_type]['urban_score']
            else:
                logging.warning('Missing type %s:%s' % (source, source_type))
                self.rural_score = 0
                self.urban_score = 0

    def __repr__(self):
        return 'LocationType(main_type=%s, sub_type=%s, urban_score=%s, rural_score=%s)' % (self.main_type,
                                                                                            self.sub_type,
                                                                                            self.urban_score,
                                                                                            self.rural_score)


class Gazetteer(object):

    def _lookup(self, point, **options):
        return []

    def __call__(self, point, **options):
        features = []
        for feature in self._lookup(point, **options):
            feature['geo_type'] = LocationType(feature['dc_source'], feature['dc_type'])
            features.append(feature)
        if 'filter_urban_score' in options:
            features = [p for p in features if p['geo_type'].urban_score >= SCORE_MAPPINGS[options['filter_urban_score']]]
        if 'filter_rural_score' in options:
            features = [p for p in features if p['geo_type'].rural_score >= SCORE_MAPPINGS[options['filter_rural_score']]]
        return features


class VladGazetteer(Gazetteer):

    def __init__(self, source):
        self._gazetteer = {}
        for line in source:
            line = line.split('||')
            if line[3] == 'Unnamed':
                continue
            reference = '%f::%f' % (float(line[1]), float(line[0]))
            if reference not in self._gazetteer:
                self._gazetteer[reference] = {'poi': [], 'way': [], 'contain': []}
            if line[2] == 'Toponym':
                if 'OSM' not in line[5]:
                    continue
                line[8] = line[8].strip()[15:-1]
                topo = {'geo_lonlat': geometry.Point(float(line[8].split(',')[0]), float(line[8].split(',')[1])),
                        'dc_title': line[3],
                        'dc_type': line[4] if line[4] != 'null' else None,
                        'dc_source': line[5],
                        'tripod_score': int(line[7])}
                self._gazetteer[reference]['poi'].append(topo)
            elif line[2] == 'Ways':
                topo = {'geo_lonlat': wkt.loads(line[7]),
                        'dc_title': line[3],
                        'dc_type': line[4] if line[4] != 'null' else None,
                        'dc_source': line[5],
                        'tripod_score': int(line[6])}
                self._gazetteer[reference]['way'].append(topo)
            elif line[2] == 'Hierarchy':
                for part in line[3].strip()[1:-1].split(','):
                    m = match(r'([a-zA-Z ]+)\(([a-zA-Z -]+)\)', part.strip())
                    if m:
                        topo = {'geo_lonlat': None,
                                'dc_title': m.group(1).strip(),
                                'dc_type': m.group(2).strip(),
                                'dc_source': 'Vlad',
                                'tripod_score': 0}
                        self._gazetteer[reference]['contain'].append(topo)
        for key in self._gazetteer.keys():
            max_value = 0
            for feature in self._gazetteer[key]['poi']:
                max_value = max(max_value, feature['tripod_score'])
            if max_value > 0:
                max_value = float(max_value)
                for feature in self._gazetteer[key]['poi']:
                    feature['tripod_score'] = feature['tripod_score'] / max_value
            self._gazetteer[key]['contain'].reverse()

    def __len__(self):
        total = 0
        for categories in self._gazetteer.values():
            for points in categories.values():
                total = total + len(points)
        return total

    def _lookup(self, point, **options):
        reference = '%f::%f' % (point.x, point.y)
        if reference in self._gazetteer:
            if 'category' in options and options['category'] in self._gazetteer[reference]:
                return deepcopy(self._gazetteer[reference][options['category']])
            else:
                return []
        else:
            return []