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
from pycaptioner.generator import rural_caption

def rural_generator_test():
    """Test generating a rural context caption"""
    gaz = VladGazetteer(TextIOWrapper(resource_stream('pycaptioner', 'test/data/gazetteer_rural.txt')))
    reader = DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv')))
    line = next(reader)
    point = geometry.Point(float(line['lon']), float(line['lat']))
    configurations = generate_configurations(point, gaz, 'rural')
    caption = rural_caption(configurations)
    print(caption)
    tools.assert_is_not_none(caption)
    tools.eq_(len(caption), 3)

