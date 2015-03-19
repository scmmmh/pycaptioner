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
from pycaptioner.configurations import generate_configurations
from pycaptioner.generator import rural_caption, urban_caption
from pycaptioner.language import generate_caption


def rural_configurations():
    """Test generating a rural context captions"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    reader = DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv')))
    for line in reader:
        if line['category'] == 'rural':
            point = geometry.Point(float(line['lon']), float(line['lat']))
            configurations = generate_configurations(point, gaz, 'rural')
            configurations['subject'] = {'dc_title': line['subject']}
            caption = rural_caption(configurations)
            tools.assert_is_not_none(caption)
            caption = generate_caption(caption)
            tools.assert_is_not_none(caption)
            print(caption)
    tools.assert_is_not_none(None)

def urban_configurations_test():
    """Test generating urban context captions"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_urban.txt')))
    reader = DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv')))
    for line in reader:
        if line['category'] == 'urban':
            point = geometry.Point(float(line['lon']), float(line['lat']))
            configurations = generate_configurations(point, gaz, 'urban')
            configurations['subject'] = {'dc_title': line['subject']}
            caption = urban_caption(configurations)
            tools.assert_is_not_none(caption)
            caption = generate_caption(caption)
            tools.assert_is_not_none(caption)
            print(caption)
    tools.assert_is_not_none(None)
