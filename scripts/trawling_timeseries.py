import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from pyproj import Proj, transform
from rtree import index

polygons = [pol for pol in fiona.open('reef_habitats.shp')]

site_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/NATURA2000SITES.csv")

months = ['May18', 'Apr18', 'Mar18']#, 'Feb18', 'Jan18', 
#		'Dec17', 'Nov17', 'Oct17', 'Sep17', 'Aug17', 'Jul17', 'Jun17', 'May17', 'Apr17', 'Mar17', 'Feb17', 'Jan17',
#		'Dec16', 'Nov16', 'Oct16', 'Sep16', 'Aug16', 'Jul16', 'Jun16']

#coordinate transformation
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:3035')

idx = index.Index()
for pos, poly in enumerate(polygons):
	idx.insert(pos, shape(poly['geometry']).bounds)

fishing_summary = pd.DataFrame(columns=['Month', 'MPA_Code', 'Area', 'fishing_hours', 'fishing_hours_per_km2'])

fished_MPAs = pd.DataFrame(columns=['Month', 'MPA_Code', 'Area', 'fishing_hours', 'Country', 'Vessel'])

for i, month in enumerate(months):
	csv_name = '/Users/mnksmith/Documents/Oceana_MPA_data/EUeez_trawlers_' + month + '.csv'
	gfw_data = pd.read_csv(csv_name)
	
	sum_fishing_hours = 0
	fished_MPAs = fished_MPAs.iloc[0:0]
	MPA_index = 0
	
	for k, row in gfw_data.iterrows():
		x,y = transform(inProj, outProj, row['lon'], row['lat'])
		point = Point(x,y)
		fishing_hours = row['fishing_hours']
		
		for j in idx.intersection(point.coords[0]):
			if point.within(shape(polygons[j]['geometry'])):
				sum_fishing_hours += fishing_hours
				sitecode = polygons[j]['properties']['SITECODE']
				areaseries = site_data.loc[site_data.SITECODE==sitecode]['AREAHA'].values
				area = areaseries[0]/100
				fished_MPAs.loc[MPA_index] = (month, sitecode, area, fishing_hours, row['country_name'], row['shipname'])
				MPA_index+=1
		
		if k%100000 == 0:
			print(k)
				
	print('Total fishing in ' + month + ': ' + str(sum_fishing_hours))
	
	most_fished_MPAs_per_km2 = fished_MPAs.groupby(['Month', 'MPA_Code', 'Area'],as_index=False).fishing_hours.sum()
	most_fished_MPAs_per_km2['fishing_hours_per_km2'] = most_fished_MPAs_per_km2['fishing_hours']/most_fished_MPAs_per_km2['Area']
	most_fishedMPAs_per_km2 = most_fished_MPAs_per_km2.sort_values(by='fishing_hours_per_km2', ascending=False)
	fishing_summary = fishing_summary.append(most_fished_MPAs_per_km2, ignore_index=True)
	
#	print(most_fished_MPAs_per_km2.head(10))
#	print(fishing_summary.head(10))
	
		
	
fishing_summary.to_csv('reef_fishing_timeseries.csv')

