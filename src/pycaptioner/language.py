# -*- coding: utf-8 -*-
u"""

.. moduleauthor:: Mark Hall <mark.hall@mail.room3b.eu>
"""

def add_determiner(toponym):
    from pycaptioner import POI, JUNCTION, TOWN, COUNTRY
    
    if toponym['dc_type'] == POI:
        return 'the %s' % (toponym['dc_title'])
    elif toponym['dc_type'] == JUNCTION:
        return 'the %s' % (toponym['dc_title'])
    elif toponym['dc_type'] == TOWN:
        return toponym['dc_title']
    elif toponym['dc_type'] == COUNTRY:
        if toponym['dc_title'] in ['United Kingdom', 'United States of America', 'United States', 'Netherlands']:
            return 'the %s' % (toponym['dc_title'])
        else:
            return toponym['dc_title']
    else:
        return toponym['dc_title']

def generate_phrase(element, last_preposition):
    if element[0][0].startswith('at_corner.'):
        return 'at', ' at the corner of %s' % (element[1]['dc_title'])
    elif element[0][0].startswith('at.'):
        return 'at', ' at %s' % (add_determiner(element[1]))
    elif element[0][0].startswith('near.'):
        return 'near', ' near %s' % (add_determiner(element[1]))
    elif element[0][0].startswith('next_to.'):
        return 'next to', ' next to %s' % (add_determiner(element[1]))
    elif element[0][0].startswith('between.'):
        return 'between', ' between %s and %s' % (add_determiner(element[1]), add_determiner(element[2]))
    elif element[0][0].startswith('north.'):
        return 'north', ' north of %s' % (add_determiner(element[1]))
    elif element[0][0].startswith('east.'):
        return 'east', ' east of %s' % (add_determiner(element[1]))
    elif element[0][0].startswith('south.'):
        return 'south', ' south of %s' % (add_determiner(element[1]))
    elif element[0][0].startswith('west.'):
        return 'west', ' west of %s' % (add_determiner(element[1]))
    elif element[0][0] == 'in':
        if last_preposition == 'in':
            return 'in', ', %s' % (add_determiner(element[1]))
        else:
            return 'in', ' in %s' % (add_determiner(element[1]))
    return ''

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
