# -*- coding: utf-8 -*-
"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""

from nose import tools

from pycaptioner.models import load


def rural_near_test():
    """Test loading the "near" rural model"""
    mdl = load('near.rural')
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, -1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, -1000))


def rural_north_test():
    mdl = load('north.rural')
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, -1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, -1000))
    tools.assert_equal(0, mdl(0, -1000))
    tools.assert_equal(0, mdl(-1000, -1000))
    tools.assert_equal(0, mdl(1000, -1000))


def rural_south_test():
    mdl = load('south.rural')
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, -1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, -1000))
    tools.assert_equal(0, mdl(0, 1000))
    tools.assert_equal(0, mdl(-1000, 1000))
    tools.assert_equal(0, mdl(1000, 1000))


def rural_east_test():
    mdl = load('east.rural')
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, -1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, -1000))
    tools.assert_equal(0, mdl(-1000, 0))
    tools.assert_equal(0, mdl(-1000, 1000))
    tools.assert_equal(0, mdl(-1000, -1000))


def rural_west_test():
    mdl = load('west.rural')
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, 1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(1000, -1000))
    tools.assert_greater_equal(mdl(0, 0), mdl(-1000, -1000))
    tools.assert_equal(0, mdl(1000, 0))
    tools.assert_equal(0, mdl(1000, 1000))
    tools.assert_equal(0, mdl(1000, -1000))
