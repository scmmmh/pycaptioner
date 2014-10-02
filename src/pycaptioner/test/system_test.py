# -*- coding: utf-8 -*-
"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""

from csv import DictReader
from io import TextIOWrapper
from nose.tools import eq_
from pkg_resources import resource_stream

def full_test():
    reader = DictReader(TextIOWrapper(resource_stream('pycaptioner', 'test/data/points.csv')))
    for line in reader:
        print (line)