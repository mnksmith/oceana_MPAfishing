import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from pyproj import Proj, transform
from rtree import index

#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/Natura2000_end2017_Shapefile/Natura2000_end2017_epsg3035.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/HELCOM_MPAs/HELCOM_MPAs.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/MPA/MPA.shp")]
polygons = [pol for pol in fiona.open("gases_habitats.shp")]

for i, poly in enumerate(polygons):
	print(poly['properties'])
	if i==0:
		break
print(len(polygons))