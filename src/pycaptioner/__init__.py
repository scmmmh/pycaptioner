import csv
import json
import logging
import numpy

from argparse import ArgumentParser
from shapely import wkt
 
def local_test(args):
    """Run the set of local test points"""
    from pycaptioner import generator, language
    points = [
              (-2.63629, 53.39797),  # Dakota Park
              (-1.88313, 53.38129),  # Peak District
              (-3.43924, 51.88286),  # Brecon Beacons
              (-3.17516, 51.50650),  # Roath Park
              (-2.99141, 53.40111),  # Liverpool
              (-2.04045, 53.34058),  # Lyme Park
              (-2.47429, 53.3827),   # Lymm
              (-1.47876, 53.38033),  # Sheffield
              ]
    captions = []
    for point in points:
        print(point)
        caption = generator.generate_caption(args.sqlalchemy_url, point)
        captions.append(language.generate_caption(caption))
    for c in captions:
        print(c)


def eval_test(args):
    """Run the set of internal evaluation points"""
    from pycaptioner import generator, language
    captions = []
    with open('src/pycaptioner/test/data/points.csv') as in_f:
        reader = csv.DictReader(in_f)
        for line in reader:
            point = (float(line['lon']), float(line['lat']))
            print(point)
            caption = generator.generate_caption(args.sqlalchemy_url, point, filter_names=[line['subject']])
            caption.insert(0, {'dc_type': 'string', 'value': line['subject']})
            caption = language.generate_caption(caption)
            print(caption)
            captions.append(caption)
    for c in captions:
        print(c)


def point_caption(args):
    """Generate a caption for a single point"""
    from pycaptioner import generator, language
    point = (float(args.lon), float(args.lat))
    caption = generator.generate_caption(args.sqlalchemy_url, point, filter_names=[args.subject] if args.subject else None)
    if args.subject:
        caption.insert(0, {'dc_type': 'string', 'value': args.subject})
    rendered_caption = language.generate_caption(caption)
    if args.full:
        for element in caption:
            if 'toponym' in element and 'osm_geometry' in element['toponym']:
                element['toponym']['osm_geometry'] = wkt.dumps(element['toponym']['osm_geometry'])
        print(json.dumps({'caption': rendered_caption,
                          'source': caption}))
    else:
        print(rendered_caption)


def main():
    """Main application function."""
    parser = ArgumentParser()
    parser.add_argument('sqlalchemy_url', help='The SQLAlchemy connection URL')
    parser.add_argument('-v', action='store_true', help='Verbose logging (INFO level)')
    parser.add_argument('-vv', action='store_true', help='Very verbose logging (DEBUG level)')
    sub_parsers = parser.add_subparsers()
    sub_parser = sub_parsers.add_parser('local-test')
    sub_parser.set_defaults(func=local_test)
    sub_parser = sub_parsers.add_parser('eval-test')
    sub_parser.set_defaults(func=eval_test)
    sub_parser = sub_parsers.add_parser('point')
    sub_parser.set_defaults(func=point_caption)
    sub_parser.add_argument('lon', help='Point longitude')
    sub_parser.add_argument('lat', help='Point latitude')
    sub_parser.add_argument('--subject', help='Image subject')
    sub_parser.add_argument('--full', action='store_true', help='Output the full caption and source data')
    args = parser.parse_args()
    if args.v:
        logging.root.setLevel(logging.INFO)
    if args.vv:
        logging.root.setLevel(logging.DEBUG)
    args.func(args)
