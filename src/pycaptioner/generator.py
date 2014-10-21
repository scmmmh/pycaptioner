# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import numpy

from random import choice


def at_corner_configurations(configurations):
    max_value = 0
    max_config = None
    for configuration in filter(lambda d: d[0][0] == 'at_corner.urban', configurations):
        if configuration[0][1] > max_value:
            max_config = configuration
    return max_config


def at_corner_addons(configurations):
    max_value = 0.7
    max_config = None
    for configuration in configurations:
        if configuration[0][0] == 'next_to.urban' and configuration[0][1] >= max_value:
            max_config = configuration
    if max_config:
        return [max_config]
    max_value = 0.7
    max_config = None
    for configuration in configurations:
        if configuration[0][0] == 'near.urban' and configuration[0][1] >= max_value:
            max_config = configuration
    if max_config:
        return [max_config]
    return []


def weighted_score(configuration):
    return 0.98 * configuration['value'] + 0.02 * configuration['feature']['tripod_score']


def best_configuration(configurations):
    max_value = 0
    for configuration in configurations:
        if weighted_score(configuration) >= max_value:
            max_value = weighted_score(configuration)
    return choice([configuration for configuration in configurations if weighted_score(configuration) >= max_value])


def urban_caption(configurations):
    elements = []
    at_corner_element = at_corner_configurations(configurations)
    if at_corner_element:
        elements.append(at_corner_element)
        elements.extend(at_corner_addons(configurations))
    else:
        elements.append(best_configuration(configurations))
    elements.append((('in', 1), {'geo_lonlat': numpy.array((0, 0)), 'dc_title': 'Cardiff', 'dc_type': TOWN, 'tripod_score': 1}))
    elements.append((('in', 1), {'geo_lonlat': numpy.array((0, 0)), 'dc_title': 'Wales', 'dc_type': COUNTRY, 'tripod_score': 1}))
    elements.append((('in', 1), {'geo_lonlat': numpy.array((0, 0)), 'dc_title': 'United Kingdom', 'dc_type': COUNTRY, 'tripod_score': 1}))
    return elements


def top_near_captions(configurations):
    return [conf for conf in configurations if conf['type'] == 'preposition' and conf['model'] == 'near.rural' and weighted_score(conf) > 0.8]


def rural_caption(configurations):
    near_configurations = top_near_captions(configurations)
    if near_configurations:
        return [best_configuration(near_configurations)]
    return [best_configuration(configurations)]