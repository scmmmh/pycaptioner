import json

from argparse import ArgumentParser
from shapely import wkt

from pycaptioner import configurations, generator, language
from pycaptioner.gazetteer import *

logging.root.setLevel(logging.DEBUG)

RURAL_ONE_POINT_MODELS = ['near.rural', 'east.rural', 'north.rural', 'west.rural', 'south.rural']
URBAN_ONE_POINT_MODELS = ['at_corner.urban', 'at.urban', 'next_to.urban', 'near.urban']
RURAL_TWO_POINT_MODELS = ['between.rural']
URBAN_TWO_POINT_MODELS = ['between.urban']


def main():
    parser = ArgumentParser()
    parser.add_argument('lon', help='Point longitude')
    parser.add_argument('lat', help='Point latitude')
    parser.add_argument('gaz', help='File to load the gazetteer from')
    parser.add_argument('category', choices=['urban', 'rural'], help='Generate an urban or rural caption')
    parser.add_argument('--subject', help='Image subject')
    args = parser.parse_args()
    point = geometry.Point(float(args.lon), float(args.lat))
    with open(args.gaz) as in_f:
        gaz = VladGazetteer(in_f)
    configs = configurations.generate_configurations(point, gaz, args.category)
    if args.subject:
            configurations['subject'] = {'dc_title': args.subject}
    if args.category == 'rural':
        caption = generator.rural_caption(configs)
    else:
        caption = generator.rural_caption(configs)
    rendered_caption = language.generate_caption(caption)
    for element in caption:
        if 'feature' in element:
            if 'geo_type' in element['feature']:
                element['feature']['geo_type'] = {'main': element['feature']['geo_type'].main_type,
                                                  'sub': element['feature']['geo_type'].sub_type,
                                                  'urban_score': element['feature']['geo_type'].urban_score,
                                                  'rural_score': element['feature']['geo_type'].rural_score}
            if 'geo_lonlat' in element['feature'] and element['feature']['geo_lonlat']:
                element['feature']['geo_lonlat'] = wkt.dumps(element['feature']['geo_lonlat'])
    print(json.dumps({'caption': rendered_caption,
                      'source': caption}))
