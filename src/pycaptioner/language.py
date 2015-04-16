# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""

def add_determiner(toponym):
    from pycaptioner import POI, JUNCTION, POPULATED_PLACE, NATURAL_FEATURE

    if toponym['dc_type'] == POI:
        return 'the %s' % (toponym['dc_title'])
    elif toponym['dc_type'] == JUNCTION:
        return 'the %s' % (toponym['dc_title'])
    elif toponym['dc_type'] == POPULATED_PLACE:
        return toponym['dc_title']
    elif toponym['dc_type'] == NATURAL_FEATURE:
        return 'the %s' % (toponym['dc_title'])
    #elif toponym['dc_type'] == COUNTRY:
    #    if toponym['dc_title'] in ['United Kingdom', 'United States of America', 'United States', 'Netherlands']:
    #        return 'the %s' % (toponym['dc_title'])
    #    else:
    #        return toponym['dc_title']
    else:
        return toponym['dc_title']


def generate_phrase(element, last_preposition):
    if element['type'] == 'preposition':
        if element['model'].startswith('at_corner.'):
            return 'at', ' at the corner of %s and %s' % (element['feature'][0]['dc_title'], element['feature'][1]['dc_title'])
        elif element['model'].startswith('at.'):
            return 'at', ' at %s' % (add_determiner(element['feature']))
        elif element['model'].startswith('near.'):
            return 'near', ' near %s' % (add_determiner(element['feature']))
        elif element['model'].startswith('next_to.'):
            return 'next to', ' next to %s' % (add_determiner(element['feature']))
        elif element['model'].startswith('between.'):
            return 'between', ' between %s and %s' % (add_determiner(element['feature'][0]), add_determiner(element['feature'][1]))
        elif element['model'].startswith('north.'):
            return 'north', ' north of %s' % (add_determiner(element['feature']))
        elif element['model'].startswith('east.'):
            return 'east', ' east of %s' % (add_determiner(element['feature']))
        elif element['model'].startswith('south.'):
            return 'south', ' south of %s' % (add_determiner(element['feature']))
        elif element['model'].startswith('west.'):
            return 'west', ' west of %s' % (add_determiner(element['feature']))
        elif element['model'] == 'in':
            if last_preposition == 'in':
                return 'in', ', %s' % (add_determiner(element['feature']))
            else:
                return 'in', ' in %s' % (add_determiner(element['feature']))
        elif element['model'] == 'on':
            return 'on', ' on %s' % (add_determiner(element['feature']))
    elif element['type'] == 'string':
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
