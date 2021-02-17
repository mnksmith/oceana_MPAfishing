import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from pyproj import Proj, transform
from rtree import index

polygons = [pol for pol in fiona.open('dolphin_habitats.shp')]

site_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/NATURA2000SITES.csv")
 

#coordinate transformation
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:3035')

idx = index.Index()
for pos, poly in enumerate(polygons):
	idx.insert(pos, shape(poly['geometry']).bounds)

csv_name = '/Users/mnksmith/Documents/Oceana_MPA_data/EUeez_allfishing_Mar18.csv'
gfw_data = pd.read_csv(csv_name)
	
#sum_fishing_all_hours = 0
sum_fishing_mpa_hours = 0
	
for k, row in gfw_data.iterrows():
	x,y = transform(inProj, outProj, row['lon'], row['lat'])
	point = Point(x,y)
	fishing_hours = row['fishing_hours']
#	sum_fishing_all_hours += fishing_hours
		
	for j in idx.intersection(point.coords[0]):
		if point.within(shape(polygons[j]['geometry'])):
			sum_fishing_mpa_hours += fishing_hours
				
	if k%10000 == 0:
		print(k)
				
#print('Total fishing: ' + str(sum_fishing_all_hours))
print('MPA fishing: ' + str(sum_fishing_mpa_hours))
#print('Proportion in MPA: %.2f%%\n' % (100*sum_fishing_mpa_hours/sum_fishing_all_hours))
	
