import fiona
from shapely.geometry import MultiPoint, Point, Polygon, shape
from shapely.geometry.polygon import Polygon
import pandas as pd

#gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/EUeez_allfishing_Mar18.csv")
gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/test_data.csv")

multipol = fiona.open(r"/Users/mnksmith/Documents/Oceana_MPA_data/HELCOM_MPAs/HELCOM_MPAs.shp")
multi = next(iter(multipol))
#print multi
for index, row in gfw_data.iterrows():
	point = Point(row['lat'],row['lon'])
	if point.within(shape(multi['geometry'])):
		print point
	if index%10000 == 0:
		print index