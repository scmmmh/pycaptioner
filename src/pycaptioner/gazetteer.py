# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import numpy

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
