# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import numpy

from itertools import product
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
    scored = []
    for configuration in configurations:
        if isinstance(configuration, list) or isinstance(configuration, tuple):
            score = sum([weighted_score(c) for c in configuration])
        else:
            score = weighted_score(configuration)
        scored.append((score, configuration))
        if score >= max_value:
            max_value = score
    return choice([configuration for (score, configuration) in scored if score >= max_value])


def filter_duplicates(configurations):
    filtered = []
    for config in configurations:
        found = False
        for idx in range(0, len(config)):
            for idx2 in range(idx + 1, len(config)):
                if config[idx]['feature']['dc_title'] == config[idx2]['feature']['dc_title']:
                    found = True
                    break
        if not found:
            filtered.append(config)
    return filtered


def filter_configurations(configurations, model, limit):
    return [conf for conf in configurations if conf['type'] == 'preposition' and conf['model'] == model and weighted_score(conf) > limit]


def filter_feature(configurations, feature):
    return [config for config in configurations if config['feature']['dc_title'] != feature]


def rural_best_relative(configurations):
    at_configurations = filter_configurations(configurations, 'at.rural', 0.6)
    if at_configurations:
        return [best_configuration(at_configurations)]
    else:
        at_configurations = filter_configurations(configurations, 'at.rural', 0.4)
        if at_configurations:
            other_configs = filter_configurations(configurations, 'near.rural', 0.8) + \
                filter_configurations(configurations, 'north.rural', 0.8) + \
                filter_configurations(configurations, 'east.rural', 0.8) + \
                filter_configurations(configurations, 'south.rural', 0.8) + \
                filter_configurations(configurations, 'west.rural', 0.8)
            combined_configs = filter_duplicates([list(p) for p in product(at_configurations, other_configs)])
            if combined_configs:
                return best_configuration(combined_configs)
            else:
                near_configurations = filter_configurations(configurations, 'near.rural', 0.8)
                if near_configurations:
                    return [best_configuration(near_configurations)]
                else:
                    return [best_configuration(configurations)]
        else:
            near_configurations = filter_configurations(configurations, 'near.rural', 0.8)
            if near_configurations:
                return [best_configuration(near_configurations)]
            else:
                return [best_configuration(configurations)]


def rural_caption(configurations):
    caption = []
    if 'subject' in configurations:
        filter_feature(configurations['relative'], configurations['subject']['dc_title'])
        caption.append({'type': 'string', 'value': configurations['subject']['dc_title']})
    caption.extend(rural_best_relative(configurations['relative']))
    if 'contain' in configurations and configurations['contain']:
        admin_area = False
        for config in configurations['contain']:
            if config['geo_type']:
                if config['geo_type'].main_type == 'ADMIN_1' or config['geo_type'].main_type == 'ADMIN_2' or config['geo_type'].main_type == 'ADMIN_3':
                    if not admin_area:
                        caption.append({'type': 'preposition', 'model': 'in', 'feature': config})
                        admin_area = True
                else:
                    caption.append({'type': 'preposition', 'model': 'in', 'feature': config})
    return caption


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


