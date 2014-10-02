# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import numpy

from re import match
from shapely import geometry, wkt

POI = 'POI'
JUNCTION = 'JUNCTION'
TOWN = 'TOWN'
COUNTRY = 'COUNTRY'

GAZETTEER = [{'geo_lonlat': numpy.array((-2.6001763343811035, 53.38953524087438)),
              'dc_title': 'Warrington Town Hall',
              'dc_type': POI,
              'tripod_score': 1},
             {'geo_lonlat': numpy.array((-2.600938081741333, 53.38832593138862)),
              'dc_title': 'Baptist Church',
              'dc_type': POI,
              'tripod_score': 0.8},
             {'geo_lonlat': numpy.array((-2.600712776184082, 53.38865225638026)),
              'dc_title': 'Sankey Street and Arpley Street',
              'dc_type': JUNCTION,
              'tripod_score': 1}]


class VladGazetteer(object):

    def __init__(self, source):
        self._gazetteer = {}
        for line in source:
            line = line.split('||')
            reference = '%f::%f' % (float(line[1]), float(line[0]))
            if reference not in self._gazetteer:
                self._gazetteer[reference] = {'poi': [], 'way': [], 'contain': []}
            if line[2] == 'Toponym':
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
                                'dc_title': m.group(1),
                                'dc_type': m.group(2),
                                'dc_source': None,
                                'tripod_score': 0}
                        self._gazetteer[reference]['contain'].append(topo)

    def __len__(self):
        total = 0
        for categories in self._gazetteer.values():
            for points in categories.values():
                total = total + len(points)
        return total

    def __call__(self, point, category):
        reference = '%f::%f' % (point.x, point.y)
        if reference in self._gazetteer and category in self._gazetteer[reference]:
            return self._gazetteer[reference][category]
        else:
            return None