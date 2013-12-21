import logging
import math
import numpy
import os

from ConfigParser import SafeConfigParser
from pkg_resources import resource_stream
from rpy2 import robjects

def load(field_name):
    config = SafeConfigParser()
    config.readfp(resource_stream('pycaptioner', 'models/%s.field' % (field_name)))
    field_type = config.get('Model', 'type')
    if field_type == 'spline':
        return SplineModel(config)
    elif field_type == 'kriging':
        return KrigingModel(config)
    else:
        return None

def dist(x, y):
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))

class SplineModel(object):
    
    def __init__(self, config):
        logging.debug('Instantiating SplineModel %s' % (config.get('Meta', 'name')))
        r = robjects.r
        points = [(int(p[0]), max(0, min(1, (float(p[1]) - 1) / 8))) for p in config.items('Data')]
        points.sort(key=lambda p: p[0])
        self.spline = r['splinefun'](robjects.IntVector([p[0] for p in points]),
                                     robjects.FloatVector([p[1] for p in points]),
                                     method=config.get('Model', 'method'))
        self.max_dist = config.getint('Extent', 'distance')
    
    def __call__(self, x, y):
        distance = dist(x, y)
        if distance > self.max_dist:
            return 0
        else:
            return max(0, min(1, self.spline(dist(x, y))[0]))

def point_in_lists(x, y, x_list, y_list):
    for idx in range(0, min(len(x_list), len(y_list))):
        if abs(x_list[idx] - x) < 0.01 and abs(y_list[idx] - y) < 0.01:
            return True
    return False

class KrigingModel(object):
    
    def __init__(self, config):
        logging.debug('Instantiating KrigingModel %s' % (config.get('Meta', 'name')))
        self.centre_x = float(config.getfloat('Extent', 'centre_x'))
        self.centre_y = float(config.getfloat('Extent', 'centre_y'))
        self.extent_x = config.getint('Extent', 'extent_x')
        self.extent_y = config.getint('Extent', 'extent_y')
        self.cell_size = config.getint('Extent', 'cell_size')
        if config.has_section('Post-process') and config.has_option('Post-process', 'filter'):
            self.filter = config.get('Post-process', 'filter')
        else:
            self.filter = None
        if os.path.exists('%s.ag' % (config.get('Meta', 'name'))):
            logging.debug('Loading KrigingModel from file %s.ag' % (config.get('Meta', 'name')))
            robjects.packages.importr('sp')
            krige = robjects.r['read.asciigrid']('%s.ag' % (config.get('Meta', 'name')))
        else:
            logging.debug('Calculating KrigingModel')
            x = []
            y = []
            confidence = []
            mirror = ''
            if config.has_section('Pre-process') and config.has_option('Pre-process', 'mirror'):
                mirror = config.get('Pre-process', 'mirror')
            for (_, data_line) in config.items('Data'):
                data_line = data_line.split(',')
                if not point_in_lists(float(data_line[0]), float(data_line[1]), x, y):
                    x.append(float(data_line[0]))
                    y.append(float(data_line[1]))
                    confidence.append(float(data_line[2]))
                if 'x' in mirror:
                    if not point_in_lists(self.centre_x - (float(data_line[0]) - self.centre_x), float(data_line[1]), x, y):
                        x.append(self.centre_x - (float(data_line[0]) - self.centre_x))
                        y.append(float(data_line[1]))
                        confidence.append(float(data_line[2]))
                if 'y' in mirror:
                    if not point_in_lists(float(data_line[0]), self.centre_y - (float(data_line[1]) - self.centre_y), x, y):
                        x.append(float(data_line[0]))
                        y.append(self.centre_y - (float(data_line[1]) - self.centre_y))
                        confidence.append(float(data_line[2]))
            data = robjects.DataFrame({'x': robjects.FloatVector(x), 'y': robjects.FloatVector(y), 'confidence': robjects.FloatVector(confidence)})
            robjects.packages.importr('sp')
            robjects.packages.importr('maptools')
            robjects.packages.importr('gstat')
            data2 = robjects.baseenv.get('coordinates<-')(data, robjects.Formula('~x+y'))
            cellcentre = robjects.FloatVector([self.centre_x - self.extent_x * (self.cell_size / 2.0), self.centre_y - self.extent_y * (self.cell_size / 2.0)])
            cellsize = robjects.FloatVector([self.cell_size, self.cell_size])
            cells = robjects.FloatVector([self.extent_x, self.extent_y])
            spatial_grid = robjects.r.SpatialGrid(robjects.r.GridTopology(**{'cellcentre.offset': cellcentre, 'cellsize': cellsize, 'cells.dim': cells}))
            fml = robjects.Formula('conf~1')
            fml.environment['conf'] = data[2]
            v = robjects.r.variogram(fml, data2)
            vgm = robjects.r.vgm(model=config.get('Model', 'name'),
                                 nugget=config.get('Model', 'nugget'),
                                 range=config.get('Model', 'range'),
                                 psill=config.get('Model', 'sill'))
            ovgm = robjects.r['fit.variogram'](v, vgm)
            krige = robjects.r.krige(robjects.Formula('conf~1'), data2, spatial_grid, model=ovgm)
            robjects.r['write.asciigrid'](krige, '%s.ag' % (config.get('Meta', 'name')))
            logging.debug('KrigingModel calculated')
        self.data = numpy.zeros(dtype='float', shape=(self.extent_x, self.extent_y))
        for idx, val in enumerate(krige.do_slot('data')[0]):
            dx = idx % self.extent_x
            dy = self.extent_y - 1 - (idx / self.extent_x)
            self.data[dx,dy] = max(1, min(9, val))
        self.data = (self.data - 1) / 9.0
    
    def __call__(self, x, y):
        if self.filter:
            if self.filter == 'north-plane' and y > 0:
                return 0
            elif self.filter == 'south-plane' and y < 0:
                return 0
            elif self.filter == 'east-plane' and x > 0:
                return 0
            elif self.filter == 'west-plane' and x < 0:
                return 0
        fx = self.extent_x / 2 + math.floor(x / self.cell_size)
        fy = self.extent_y / 2 + math.floor(y / self.cell_size)
        if fx >= 0 and fx < self.extent_x and fy >= 0 and fy < self.extent_y:
            return self.data[fx,fy]
        else:
            return 0
