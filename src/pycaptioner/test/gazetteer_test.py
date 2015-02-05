# -*- coding: utf-8 -*-
"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""

from csv import DictReader
from io import TextIOWrapper
from nose import tools
from pkg_resources import resource_stream
from shapely import geometry

from pycaptioner.gazetteer import (VladGazetteer, LocationType, UNKNOWN, Gazetteer)


def gazetteer_base_test():
    gaz = Gazetteer()
    tools.eq_(len(gaz._lookup(geometry.Point(0, 0))), 0)


def gazetteer_mapping_test():
    lt = LocationType('', '')
    tools.eq_(lt.main_type, UNKNOWN)
    rural_gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    urban_gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_urban.txt')))
    for line in DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv'))):
        if line['category'] == 'rural':
            points = rural_gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='poi')
        elif line['category'] == 'urban':
            points = urban_gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='poi')
        for point in points:
            lt = LocationType(point['dc_source'], point['dc_type'])
            tools.assert_not_equal(lt.main_type, UNKNOWN)


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
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='poi')
            tools.assert_is_not_none(points)
            for feature in points:
                tools.assert_less_equal(feature['tripod_score'], 1)
                tools.assert_greater_equal(feature['tripod_score'], 0)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='way')
            tools.assert_is_not_none(points)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='contain')
            tools.assert_is_not_none(points)
            last_point = line
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), category='poi')
    tools.eq_(25, len(points))
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), category='way')
    tools.eq_(18, len(points))
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), category='contain')
    tools.eq_(7, len(points))


def filter_urban_test():
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_urban.txt')))
    for line in DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv'))):
        if line['category'] == 'urban':
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='poi', filter_urban_score='MEDIUM')
            for feature in points:
                lt = LocationType(feature['dc_source'], feature['dc_type'])
                tools.assert_greater_equal(lt.urban_score, 2)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='poi', filter_urban_score='HIGH')
            for feature in points:
                lt = LocationType(feature['dc_source'], feature['dc_type'])
                tools.assert_greater_equal(lt.urban_score, 3)


def vlad_rural_test():
    """Test loading Vlad's rural gazetteer"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    tools.eq_(3680, len(gaz))


def vlad_rural_lookup_test():
    """Test looking up the rural points in Vlad's rural gazetteer"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    for line in DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv'))):
        if line['category'] == 'rural':
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='poi')
            tools.assert_is_not_none(points)
            for feature in points:
                tools.assert_less_equal(feature['tripod_score'], 1)
                tools.assert_greater_equal(feature['tripod_score'], 0)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='way')
            tools.assert_is_not_none(points)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='contain')
            tools.assert_is_not_none(points)
            last_point = line
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), category='poi')
    tools.eq_(197, len(points))
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), category='way')
    tools.eq_(176, len(points))
    points = gaz(geometry.Point(float(last_point['lon']), float(last_point['lat'])), category='contain')
    tools.eq_(7, len(points))


def filter_rural_test():
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    for line in DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv'))):
        if line['category'] == 'rural':
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='poi', filter_rural_score='MEDIUM')
            for feature in points:
                lt = LocationType(feature['dc_source'], feature['dc_type'])
                tools.assert_greater_equal(lt.rural_score, 2)
            points = gaz(geometry.Point(float(line['lon']), float(line['lat'])), category='poi', filter_rural_score='HIGH')
            for feature in points:
                lt = LocationType(feature['dc_source'], feature['dc_type'])
                tools.assert_greater_equal(lt.rural_score, 3)
