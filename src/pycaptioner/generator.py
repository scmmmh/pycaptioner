# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import numpy

from itertools import product
from jellyfish import jaro_winkler
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
    if isinstance(configuration['feature'], list):
        return 0.98 * configuration['value'] + 0.02 * (sum([f['tripod_score'] for f in configuration['feature']]) / float(len(configuration['feature'])))
    else:
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
    if scored:
        return choice([configuration for (score, configuration) in scored if score >= max_value])
    else:
        return None


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
    filtered = []
    for config in configurations:
        if isinstance(config['feature'], list):
            found = False
            for sub_feature in config['feature']:
                if jaro_winkler(sub_feature['dc_title'].lower(), feature.lower()) > 0.95:
                    found = True
                    break
            if not found:
                filtered.append(config)
        elif jaro_winkler(config['feature']['dc_title'].lower(), feature.lower()) <= 0.95:
            filtered.append(config)
    return filtered


def rural_best_relative(configurations):
    at_configurations = filter_configurations(configurations, 'at.rural', 0.6)
    if at_configurations:
        return [best_configuration(at_configurations)]
    else:
        between_configurations = filter_configurations(configurations, 'between.rural', 0.8)
        if between_configurations:
            between_config = best_configuration(between_configurations)
            near_config = best_configuration(filter_feature(filter_feature(filter_configurations(configurations,
                                                                                                 'near.rural',
                                                                                                 0.8),
                                                                           between_config['feature'][0]['dc_title']),
                                                            between_config['feature'][1]['dc_title']))
            if near_config:
                return [between_config, near_config]
            else:
                return [between_config]
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
    near_configurations = filter_configurations(configurations, 'near.rural', 0.8)
    if near_configurations:
        return [best_configuration(near_configurations)]
    else:
        return [best_configuration(configurations)]


def rural_caption(configurations):
    caption = []
    if 'subject' in configurations:
        if 'relative' in configurations:
            filter_feature(configurations['relative'], configurations['subject']['dc_title'])
        caption.append({'type': 'string', 'value': configurations['subject']['dc_title']})
    if 'relative' in configurations:
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
    caption = []
    if 'subject' in configurations:
        if 'relative' in configurations:
            filter_feature(configurations['relative'], configurations['subject']['dc_title'])
        caption.append({'type': 'string', 'value': configurations['subject']['dc_title']})
    if 'contain' in configurations and configurations['contain']:
        area_added = False
        for config in configurations['contain']:
            if config['geo_type']:
                if config['geo_type'].main_type == 'DISTRICT':
                    pass
                elif config['geo_type'].main_type in ['ADMIN_1', 'ADMIN_2', 'ADMIN_3', 'POPULATED_PLACE']:
                    if not area_added:
                        caption.append({'type': 'preposition', 'model': 'in', 'feature': config})
                        area_added = True
                else:
                    caption.append({'type': 'preposition', 'model': 'in', 'feature': config})
    return caption
