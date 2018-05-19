#circular states with geopandas

import math
import time
import os

import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import shapely
from shapely.geometry import Polygon, Point, mapping
from shapely.geometry.base import BaseGeometry


starting_dir = os.getcwd()
folder = '/cb_2017_us_state_5m'
file = 'cb_2017_us_state_5m.shp'

#roundness -> area of country in disk/max(area of country, area of disk)

def dist(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    

def circle_maker(radius, center, step = 0.01):

    domain = np.arange(0, 2 * math.pi, step)
    pts = [(radius * math.cos(t) + center[0], radius * math.sin(t) + center[1]) for t in domain]

    return Polygon(pts)

#country should be a Polygon already
def roundness(radius, center, state):

    disk = circle_maker(radius, center)
    intersect = BaseGeometry.intersection(disk.buffer(0), state.buffer(0))

    rnd = intersect.area / (max(disk.area, state.area))

    return rnd

#should return radius and roundness score
def max_roundness(state, center, steps = 100):
    state_pts = mapping(state)['coordinates']

    #need to find starting and ending points, format is slightly different for Polygon vs
    #MultiPolygon
    min_max_list = []
    try:
        assert type(state) == shapely.geometry.polygon.Polygon
        for index in range(len(state_pts)):
            current_list = [dist(center, pt) for pt in state_pts[index]]
            min_max_list.append(min(current_list))
            min_max_list.append(max(current_list))
    except AssertionError:
        for index in range(len(state_pts)):
            current_list = [dist(center, pt) for pt in state_pts[index][0]]
            min_max_list.append(min(current_list))
            min_max_list.append(max(current_list))
        
    init_radius = min(min_max_list)
    final_radius = max(min_max_list)
    step_size = (final_radius - init_radius) / steps
    
    top_score = [0, 0]    

    for step in range(steps):
        current_radius = init_radius + step * step_size
        
        round_score = roundness(current_radius, center, state)

        if round_score > top_score[0]:
            top_score[0] = round_score
            top_score[1] = current_radius
            
    return top_score

def plot_data(state_index):
    os.chdir(starting_dir + folder)

    states_data = gpd.read_file(file)

    vals = states_data.values[state_index]
    gpd_data = states_data[state_index: state_index + 1]

    state_name = vals[5]
    state_poly = vals[-1]
    state_center = state_poly.centroid.coords[0]

    score, radius = max_roundness(state_poly, state_center)

    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.axis('off')
    if state_name == 'Alaska':
        ax.set_xlim((-180,-130))
    
    gpd_data.plot(ax=ax, color = '0.66', edgecolor = 'black')
    circle = plt.Circle(state_center, radius, color = 'k', fill = False, clip_on = False)
    ax.add_artist(circle)

    file_name = state_name + ' ' + str(round(score, 3)) + '.png'
    os.chdir(starting_dir + '/Images')
    plt.savefig(file_name)
    plt.close()
    print('Created plot for ' + state_name)
    return

def main():
    start = time.time()
    for i in range(56):
        plot_data(i)
    end = time.time()
    print('Finished in '+ str(int(end-start)) + ' seconds')

if __name__=='__main__':
    if input('Create plots? (y/n) ') == 'y':
        main()
    
