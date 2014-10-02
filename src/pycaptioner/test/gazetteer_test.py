# -*- coding: utf-8 -*-
"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""

from csv import DictReader
from io import TextIOWrapper
from nose import tools
from pkg_resources import resource_stream
from shapely import geometry

from pycaptioner.gazetteer import VladGazetteer


def vlad_urban_load_test():
    """Test loading Vlad's urban gazetteer"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_urban.txt')))
    tools.eq_(671, len(gaz))


def vlad_urban_lookup_test():
    """Test looking up the urban points in Vlad's urban gazetteer"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_urban.txt')))
    last_point = None
    for line in DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv'))):
        if line['category'] == 'urban':
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), 'poi')
            tools.assert_is_not_none(points)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), 'way')
            tools.assert_is_not_none(points)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), 'contain')
            tools.assert_is_not_none(points)
            last_point = line
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), 'poi')
    tools.eq_(25, len(points))
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), 'way')
    tools.eq_(18, len(points))
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), 'contain')
    tools.eq_(7, len(points))


def vlad_rural_test():
    """Test loading Vlad's rural gazetteer"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    tools.eq_(3680, len(gaz))


def vlad_rural_lookup_test():
    """Test looking up the rural points in Vlad's rural gazetteer"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    for line in DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv'))):
        if line['category'] == 'rural':
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), 'poi')
            tools.assert_is_not_none(points)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), 'way')
            tools.assert_is_not_none(points)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), 'contain')
            tools.assert_is_not_none(points)
            last_point = line
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), 'poi')
    tools.eq_(197, len(points))
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), 'way')
    tools.eq_(176, len(points))
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), 'contain')
    tools.eq_(7, len(points))
