import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from pyproj import Proj, transform
from rtree import index
import io
import csv
import time

#read in shapefile
polygons = [pol for pol in fiona.open('turtle_habitats.shp')]

#read in fishing points
gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/all_2017_8.csv")
										

#coordinate transformation
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:3035')

idx = index.Index()
for pos, poly in enumerate(polygons):
	idx.insert(pos, shape(poly['geometry']).bounds)

buffer = io.StringIO()
csv_writer = csv.writer(buffer)
csv_writer.writerow(['MPA_Code', 'timestamp', 'fishing_hours', 'Country', 'Callsign', 'GFW_gear'])
#fished_MPAs = pd.DataFrame(columns=['MPA_Code', 'timestamp', 'fishing_hours', 'Country', 'Callsign', 'GFW_gear'])
#MPA_index = 0
print('check 1')
begin = time.time()
for row in gfw_data.itertuples():
	x,y = transform(inProj, outProj, row.lon, row.lat)
	point = Point(x,y)
	
	for j in idx.intersection(point.coords[0]):
		if point.within(shape(polygons[j]['geometry'])):
			sitecode = polygons[j]['properties']['SITECODE']
				
#			fished_MPAs.loc[MPA_index] = (sitecode, row.timestamp, row.fishing_hours, row.country_name, row.callsign, row.gear) 
#			MPA_index+=1
			csv_writer.writerow([sitecode, row.timestamp, row.fishing_hours, row.country_name, row.callsign, row.gear])
	
	k = row.Index	
	if k%1000 == 0:
		print(k)
	if k%100000 == 0:
		end = time.time()
		print('time: ' + str(end-begin) + ' seconds')

buffer.seek(0)
fished_MPAs = pd.read_csv(buffer)
end = time.time()
print(end - begin)
buffer.close()
fished_MPAs.to_csv('turtle_master_complete_8.csv')

print('Complete!')
print(fished_MPAs.head(1))