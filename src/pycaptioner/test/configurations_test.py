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

def rural_configurations_test():
    """Test loading Vlad's urban gazetteer"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    reader = DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv')))
    for line in reader:
        if line['category'] == 'rural':
            point = geometry.Point(float(line['lon']), float(line['lat']))
            configurations = generate_configurations(point, gaz, 'rural')
            tools.assert_greater_equal(len(configurations), 0)
