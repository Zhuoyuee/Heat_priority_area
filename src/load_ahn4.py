import laspy
import numpy as np

def thin_points (lidar_filepath, thinning_factor = 10):
    # Reading the las file
    lasfile = laspy.read(lidar_filepath)
    
    thinned_points = lasfile[::thinning_factor]
    
    return thinned_points, lasfile.classification






