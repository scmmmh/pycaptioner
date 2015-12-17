# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
from osmgaz import filters


def needs_determiner(toponym):
    if toponym['dc_title'].lower().startswith('the'):
        return False
    elif filters.type_match(toponym['dc_type'], ['PLACE']):
        return False
    elif filters.type_match(toponym['dc_type'], ['AREA', 'ADMINISTRATIVE']):
        if 'kingdom' in toponym['dc_title'].lower():
            return True
        elif 'states' in toponym['dc_title'].lower():
            return True
        elif 'republic' in toponym['dc_title'].lower():
            return True
        elif toponym['dc_title'].lower().endswith('s'):
            return True
        return False
    elif filters.type_match(toponym['dc_type'], ['AREA', 'CEREMONIAL']):
        return False
    elif filters.type_match(toponym['dc_type'], ['NATURAL FEATURE', 'WATER', 'FLOWING WATER']):
        return False
    elif filters.type_match(toponym['dc_type'], ['NATURAL FEATURE']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING', 'COMMERCIAL']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING', 'EDUCATION']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'PARK']):
        return False
    return True


def add_determiner(toponym):
    if needs_determiner(toponym):
        return 'the %s' % toponym['dc_title']
    else:
        return toponym['dc_title']


def generate_toponym(toponym):
    if toponym['dc_title'].endswith(' CP'):
        toponym['dc_title'] = '%s Parish' % toponym['dc_title'][:-3]
    if ' in ' in toponym['dc_title']:
        toponym['dc_title'] = toponym['dc_title'].replace(' in ', ', ')
    return add_determiner(toponym)

def generate_phrase(element, last_preposition):
    if element['dc_type'] == 'preposition':
        if element['preposition'].startswith('at_corner.'):
            return 'at', ' at the corner of %s' % (element['toponym']['dc_title'])
        elif element['preposition'].startswith('at.'):
            return 'at', ' at %s' % (generate_toponym(element['toponym']))
        elif element['preposition'].startswith('near.'):
            return 'near', ' near %s' % (generate_toponym(element['toponym']))
        elif element['preposition'].startswith('next_to.'):
            return 'next to', ' next to %s' % (generate_toponym(element['toponym']))
        elif element['preposition'].startswith('between.'):
            return 'between', ' between %s and %s' % (generate_toponym(element['toponym'][0]), generate_toponym(element['toponym'][1]))
        elif element['preposition'].startswith('north.'):
            return 'north', ' north of %s' % (generate_toponym(element['toponym']))
        elif element['preposition'].startswith('east.'):
            return 'east', ' east of %s' % (generate_toponym(element['toponym']))
        elif element['preposition'].startswith('south.'):
            return 'south', ' south of %s' % (generate_toponym(element['toponym']))
        elif element['preposition'].startswith('west.'):
            return 'west', ' west of %s' % (generate_toponym(element['toponym']))
        elif element['preposition'] == 'in':
            if last_preposition == 'in':
                return 'in', ', %s' % (generate_toponym(element['toponym']))
            else:
                return 'in', ' in %s' % (generate_toponym(element['toponym']))
        elif element['preposition'].startswith('on.'):
            return 'on', ' on %s' % (generate_toponym(element['toponym']))
    elif element['dc_type'] == 'string':
        return '', ' %s' % (element['value'])
    return '', ''


def generate_caption(elements):
    phrases = []
    last_preposition = None
    for element in elements:
        last_preposition, phrase = generate_phrase(element, last_preposition)
        phrases.append(phrase)
    caption = ''.join(phrases).strip()
    if caption:
        return caption[0].upper() + caption[1:]
    else:
        return ''
