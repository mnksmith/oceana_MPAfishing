import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from pyproj import Proj, transform
from rtree import index

polygons = [pol for pol in fiona.open('gases_habitats.shp')]

site_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/NATURA2000SITES.csv")

factors = ['00', '10', '20', '30', '40', '45', '50', '55', '60', '65', '70', '75', '80', '85', '87', '89'] 

#coordinate transformation
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:3035')

idx = index.Index()
for pos, poly in enumerate(polygons):
	idx.insert(pos, shape(poly['geometry']).bounds)

factor_summary = pd.DataFrame(columns=['Factor', 'fishing_events', 'fishing_hours', 'fishing_hours_mpa'])

for i, factor in enumerate(factors):
	csv_name = '/Users/mnksmith/Documents/Oceana_MPA_data/factor' + factor + '.csv'
	gfw_data = pd.read_csv(csv_name)
	
	sum_fishing_all_hours = 0
	sum_fishing_mpa_hours = 0
	
	for k, row in gfw_data.iterrows():
		x,y = transform(inProj, outProj, row['lon'], row['lat'])
		point = Point(x,y)
		fishing_hours = row['fishing_hours']
		sum_fishing_all_hours += fishing_hours
		
		for j in idx.intersection(point.coords[0]):
			if point.within(shape(polygons[j]['geometry'])):
				sum_fishing_mpa_hours += fishing_hours
				
		if k%10000 == 0:
			print(k)
				
	print('Total fishing for factor ' + factor + ': ' + str(sum_fishing_all_hours))
	print('MPA fishing for factor ' + factor + ': ' + str(sum_fishing_mpa_hours))
	print('Proportion in MPA for factor ' + factor + ': %.2f%%\n' % (100*sum_fishing_mpa_hours/sum_fishing_all_hours))
	
	factor_summary.loc[i] = (factor, len(gfw_data.index), sum_fishing_all_hours, sum_fishing_mpa_hours)
	
factor_summary.to_csv('gases_factor_summary.csv')

