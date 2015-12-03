import csv
import logging
import numpy

from pycaptioner import models, generator, language

logging.root.setLevel(logging.DEBUG)


def local_test():
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
        caption = generator.generate_caption(point)
        captions.append(language.generate_caption(caption))
    for c in captions:
        print(c)


def eval_test():
    captions = []
    with open('src/pycaptioner/test/data/points.csv') as in_f:
        reader = csv.DictReader(in_f)
        for line in reader:
            point = (float(line['lon']), float(line['lat']))
            print(point)
            caption = generator.generate_caption(point)
            caption.insert(0, {'dc_type': 'string', 'value': line['subject']})
            caption = language.generate_caption(caption)
            print(caption)
            captions.append(caption)
    for c in captions:
        print(c)


def main():
    local_test()
