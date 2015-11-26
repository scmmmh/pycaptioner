import logging
import numpy

from pycaptioner import models, generator, language

logging.root.setLevel(logging.DEBUG)

def main():
    points = [
              (-2.63629, 53.39797), # Dakota Park
              (-1.88313, 53.38129), # Peak District
              (-3.43924, 51.88286), # Brecon Beacons
              (-3.17516, 51.50650), # Roath Park
              (-2.99141, 53.40111), # Liverpool
              (-2.04045, 53.34058), # Lyme Park
              (-2.47429, 53.3827),  # Lymm
              ]
    captions = []
    for point in points:
        print(point)
        caption = generator.generate_caption(point)
        captions.append(language.generate_caption(caption))
    for c in captions:
        print(c)

