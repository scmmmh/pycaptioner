# -*- coding: utf-8 -*-
"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""
import re

from osmgaz import filters


A_ROAD_PATTERN = re.compile('[ABC][0-9]+', re.IGNORECASE)


def needs_determiner(toponym):
    """A set of rules to determine whether the given toponym needs a definite article."""
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
        elif 'borough' in toponym['dc_title'].lower():
            return True
        elif toponym['dc_title'].lower().endswith('s'):
            if filters.type_match(toponym['dc_type'], ['AREA', 'ADMINISTRATIVE', '2']):
                return True
            elif filters.type_match(toponym['dc_type'], ['AREA', 'ADMINISTRATIVE', '4']):
                return True
        return False
    elif filters.type_match(toponym['dc_type'], ['AREA', 'CEREMONIAL']):
        return False
    elif filters.type_match(toponym['dc_type'], ['NATURAL FEATURE', 'WATER', 'FLOWING']):
        return True
    elif filters.type_match(toponym['dc_type'], ['NATURAL FEATURE']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'WATER WAY', 'STANDING WATER', 'RESERVOIR']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD']):
        if re.match(A_ROAD_PATTERN, toponym['dc_title']):
            return True
        else:
            return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING', 'COMMERCIAL']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING', 'EDUCATION']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING', 'TRANSPORT', 'AIR', 'TERMINAL']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING', 'TRANSPORT', 'RAILWAY', 'STATION']):
        return False
    elif filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'PARK']):
        return False
    elif 'osm_salience' in toponym and 'flickr' in toponym['osm_salience'] and toponym['osm_salience']['flickr'] > 1000:
        return False
    return True


CLASSIFY_TYPES = [['ARTIFICIAL FEATURE', 'TRANSPORT', 'PUBLIC', 'BUS STOP'],
                  ['ARTIFICIAL FEATURE', 'TRANSPORT', 'RAILWAY', 'STATION'],
                  ['ARTIFICIAL FEATURE', 'TRANSPORT', 'PARKING']]


def needs_toponym_type(toponym):
    """Test whether the toponym type should be added to the toponym."""
    for classify_type in CLASSIFY_TYPES:
        if filters.type_match(toponym['dc_type'], classify_type) and classify_type[-1].lower() not in toponym['dc_title'].lower():
            return classify_type[-1]
    return False


def generate_toponym(toponym):
    """Generate the toponym text, applying OSM-specific cleanups first."""
    if toponym['dc_title'].endswith(' CP'):
        toponym['dc_title'] = '%s Parish' % toponym['dc_title'][:-3]
    if toponym['dc_title'].endswith(', opp'):
        toponym['dc_title'] = toponym['dc_title'][:toponym['dc_title'].find(', opp')]
    if ' in ' in toponym['dc_title']:
        toponym['dc_title'] = toponym['dc_title'].replace(' in ', ', ')
    label = toponym['dc_title']
    if needs_toponym_type(toponym):
        label = '%s %s' % (label, needs_toponym_type(toponym).lower())
    if needs_determiner(toponym):
        label = 'the %s' % (label)
    return label


SUPPORT_TYPES = [['NATURAL FEATURE', 'WATER'],
                 ['NATURAL FEATURE', 'BEACH'],
                 ['ARTIFICIAL FEATURE', 'TRANSPORT', 'WATER WAY', 'FLOWING WATER', 'CANAL'],
                 ['ARTIFICIAL FEATURE', 'TRANSPORT', 'WATER WAY', 'FLOWING WATER', 'VIADUCT'],
                 ['ARTIFICIAL FEATURE', 'TRANSPORT', 'WATER WAY', 'STANDING WATER', 'DAM'],
                 ['ARTIFICIAL FEATURE', 'TRANSPORT', 'WATER WAY', 'STANDING WATER', 'RESERVOIR'],
                 ['ARTIFICIAL FEATURE', 'TRANSPORT', 'RAILWAY', 'BRIDGE'],
                 ['ARTIFICIAL FEATURE', 'TRANSPORT', 'ROAD'],
                 ['ARTIFICIAL FEATURE', 'TRANSPORT', 'PATH']]


def containment_support(toponym):
    """Returns either 'in' or 'on' depending on whether the toponym demands a containment preoposition
    or a support preposition."""
    for support_type in SUPPORT_TYPES:
        if filters.type_match(toponym['dc_type'], support_type):
            return 'on'
    if filters.type_match(toponym['dc_type'], ['ARTIFICIAL FEATURE', 'BUILDING']):
        return 'at'
    return 'in'


def generate_phrase(element, last_preposition):
    """Generate a single phrase as part of a larger caption."""
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
            preposition = containment_support(element['toponym'])
            if last_preposition == preposition:
                return preposition, ', %s' % (generate_toponym(element['toponym']))
            else:
                return preposition, ' %s %s' % (preposition, generate_toponym(element['toponym']))
        elif element['preposition'].startswith('on.'):
            return 'on', ' on %s' % (generate_toponym(element['toponym']))
    elif element['dc_type'] == 'string':
        return '', ' %s' % (element['value'])
    return '', ''


def generate_caption(elements):
    """Generate a full caption."""
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
