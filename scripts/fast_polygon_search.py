import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from pyproj import Proj, transform
from rtree import index

#read in shapefile
polygons = [pol for pol in fiona.open('reef_habitats.shp')]

#read in fishing points
gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/EUeez_allfishing_Mar18.csv")

#read in extra data
site_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/NATURA2000SITES.csv")
hab_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/HABITATS.csv")
vessel_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/EU_fleet_register.csv")

#index the polygons from the shapefile
idx = index.Index()
for pos, poly in enumerate(polygons):
	idx.insert(pos, shape(poly['geometry']).bounds)

#reef requirements
habitat_type = '1170'
bad_gears = pd.Series(['DRB',  # dredges
						'TBB', # trawls
						'OTB',
						'PTB',
						'OTT',
						'LHM', # hooks and lines
						'LHP',
						'LLD',
						'LLS',
						'FPO', # traps
						'FYK',
						'FPN',
						'GTR', # nets
						'GNS',
						'GND',
						'SSC', # seines
						'SDN',
						'SPR',
						'SB'])

#Functions

#coordinate transform and convert lat/lon into a Point
def get_point(lon, lat):
	inProj = Proj(init='epsg:4326')
	outProj = Proj(init='epsg:3035')
	x,y = transform(inProj, outProj, lon, lat)
	point = Point(x,y)
	return point

#ask if it's an incompatible gear type
def is_bad_gear(callsign, vessel_data):
	gear1 = 'FILL1'
	gear2 = 'FILL2'
	if callsign in vessel_data.IRCS.values:
		gear1 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Main Code'].values[0]
		gear2 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Sec Code'].values[0]
	if (gear1 in bad_gears.values) or (gear2 in bad_gears.values):
		return True
	else:
		return False
	
#ask if it's inside an MPA, get code, area, cover of MPA
def isin_MPA(idx, lon, lat):
	point= get_point(lon, lat)
	bool = False
	for j in idx.intersection(point.coords[0]):
		if point.within(shape(polygons[j]['geometry'])):
			bool = True
	return bool

#get gear types
def get_gear(callsign, vessel_data):
	gear1 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Main Code'].values[0]
	gear2 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Sec Code'].values[0]
	return gear1, gear2
	
#get habitat info
def get_hab_info(idx, lon, lat, site_data, hab_data):
	point= get_point(lon, lat)
	for j in idx.intersection(point.coords[0]):
		if point.within(shape(polygons[j]['geometry'])):
			sitecode = polygons[j]['properties']['SITECODE']
			areaseries = site_data.loc[site_data.SITECODE==sitecode]['AREAHA'].values
			area = areaseries[0]/100
			
			coverseries = hab_data.loc[(hab_data.SITECODE==sitecode) & (hab_data.HABITATCODE==habitat_type)]['COVER_HA'].values
			cover = coverseries[0]/100
			if(cover>area):
				cover = area
					
	return sitecode, area, cover

#Operations on the DataFrame

out_data = gfw_data

print('check 1')

#drop unwanted rows
out_data = out_data[out_data.apply(lambda row: is_bad_gear(row['callsign'], vessel_data), axis=1)]
print('check 2')
out_data = out_data[out_data.apply(lambda row: isin_MPA(idx, row['lon'], row['lat']), axis=1)]
print('check 3')
	
#add new columns
out_data[['Gear1', 'Gear2']] = out_data.apply(lambda row: get_gear(row['callsign'], vessel_data), axis=1)
print('check 4')
out_data[['MPA_Code', 'Area', 'Cover']] = out_data.apply(lambda row: get_hab_info(idx, row['lon'], row['lat'], site_data, hab_data), axis=1)
print('check 5')

print(out_data.head(2))

most_fished_MPAs = out_data.groupby('MPA_Code').fishing_hours.sum()
most_fished_MPAs_per_km2 = out_data.groupby(['MPA_Code', 'Area', 'Cover'],as_index=False).fishing_hours.sum()
most_fished_MPAs_per_km2['fishing_hours_per_km2'] = most_fished_MPAs_per_km2['fishing_hours']/most_fished_MPAs_per_km2['Area']
most_fished_MPAs_per_km2['fishing_hours_coverage'] = most_fished_MPAs_per_km2['fishing_hours']*most_fished_MPAs_per_km2['Cover']/most_fished_MPAs_per_km2['Area']
most_fished_countries = out_data.groupby('Country').fishing_hours.sum()
most_fished_vessels = out_data.groupby(['Vessel', 'Callsign', 'Gear1', 'Gear2']).fishing_hours.sum()

#print(most_fished_vessels.sort_values(ascending=False).head(10))

out_data.to_csv('reef_master_check.csv')
most_fished_MPAs.sort_values(ascending=False).to_csv('reef_MPAs_check.csv')
most_fished_MPAs_per_km2.sort_values(by='fishing_hours_per_km2', ascending=False).to_csv('reef_MPAs_per_km2_check.csv')
most_fished_countries.sort_values(ascending=False).to_csv('reef_countries_check.csv')
most_fished_vessels.sort_values(ascending=False).to_csv('reef_vessels_check.csv')

print('----Total Fishing Hours----')
print(total_fishing_hours)
print('----Most Fished MPAs----')
print(most_fished_MPAs.sort_values(ascending=False).head(10))
print('----Most Fished MPAs per km2----')
print(most_fished_MPAs_per_km2.sort_values(by='fishing_hours_per_km2', ascending=False).head(10))
print('----Most Fished MPAs per cover----')
print(most_fished_MPAs_per_km2.sort_values(by='fishing_hours_coverage', ascending=False).head(10))
print('----Biggest Culprits (Countries)----')
print(most_fished_countries.sort_values(ascending=False).head(10))
print('----Biggest Culprits (Vessels)----')
print(most_fished_vessels.sort_values(ascending=False).head(10))
	