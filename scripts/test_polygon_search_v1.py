import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from pyproj import Proj, transform
from rtree import index

#read in shapefile
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/HELCOM_MPAs/HELCOM_MPAs.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/Natura2000_end2017_Shapefile/Natura2000_end2017_epsg3035.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/MPA/MPA.shp")]
polygons = [pol for pol in fiona.open('reef_habitats.shp')]

#read in fishing points
#gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/test_data.csv")
gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/EUeez_allfishing_Mar18.csv")
#gfw_data = pd.read_csv('/Users/mnksmith/Documents/Oceana_MPA_data/EUeez_trawlers_Mar18.csv')

#read in site data
site_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/NATURA2000SITES.csv")
hab_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/HABITATS.csv")
vessel_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/EU_fleet_register.csv")

#coordinate transformation
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:3035')

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


total_fishing_hours = 0
fished_MPAs = pd.DataFrame(columns=['MPA_Code', 'Area', 'Cover', 'fishing_hours', 'Country', 'Vessel', 'Callsign', 'Gear1', 'Gear2'])
MPA_index = 0

for k, row in gfw_data.iterrows():
	x,y = transform(inProj, outProj, row['lon'], row['lat'])
#	x,y = row['lon'], row['lat']
	point = Point(x,y)
	fishing_hours = row['fishing_hours']
	callsign = row['callsign']
	gear1 = 'FILL1'
	gear2 = 'FILL2'
	if callsign in vessel_data.IRCS.values:
		gear1 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Main Code'].values[0]
		gear2 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Sec Code'].values[0]
		
	if (gear1 in bad_gears.values) or (gear2 in bad_gears.values):

		for j in idx.intersection(point.coords[0]):
			if point.within(shape(polygons[j]['geometry'])):
				total_fishing_hours += fishing_hours
				sitecode = polygons[j]['properties']['SITECODE']
				areaseries = site_data.loc[site_data.SITECODE==sitecode]['AREAHA'].values
				area = areaseries[0]/100
			
				coverseries = hab_data.loc[(hab_data.SITECODE==sitecode) & (hab_data.HABITATCODE==habitat_type)]['COVER_HA'].values
				cover = coverseries[0]/100
				if(cover>area):
					cover = area
			
			
			fished_MPAs.loc[MPA_index] = (sitecode, area, cover, fishing_hours, row['country_name'], row['shipname'], callsign, gear1, gear2) #Helcom,MPA: 'Name', Natura2000 'SITENAME'
			MPA_index+=1
			
	if k%1000 == 0:
		print(k)
	if k%10000 == 0:
		print(total_fishing_hours)


most_fished_MPAs = fished_MPAs.groupby('MPA_Code').fishing_hours.sum()
most_fished_MPAs_per_km2 = fished_MPAs.groupby(['MPA_Code', 'Area', 'Cover'],as_index=False).fishing_hours.sum()
most_fished_MPAs_per_km2['fishing_hours_per_km2'] = most_fished_MPAs_per_km2['fishing_hours']/most_fished_MPAs_per_km2['Area']
most_fished_MPAs_per_km2['fishing_hours_coverage'] = most_fished_MPAs_per_km2['fishing_hours']*most_fished_MPAs_per_km2['Cover']/most_fished_MPAs_per_km2['Area']
most_fished_countries = fished_MPAs.groupby('Country').fishing_hours.sum()
most_fished_vessels = fished_MPAs.groupby(['Vessel', 'Callsign', 'Gear1', 'Gear2']).fishing_hours.sum()

fished_MPAs.to_csv('reef_master.csv')
most_fished_MPAs.sort_values(ascending=False).to_csv('reef_MPAs.csv')
most_fished_MPAs_per_km2.sort_values(by='fishing_hours_per_km2', ascending=False).to_csv('reef_MPAs_per_km2.csv')
most_fished_countries.sort_values(ascending=False).to_csv('reef_countries.csv')
most_fished_vessels.sort_values(ascending=False).to_csv('reef_vessels.csv')

print('----Total Fishing Hours----')
print(total_fishing_hours)
print('----Most Fished MPAs----')
print(most_fished_MPAs.sort_values(ascending=False).head(10))
print('----Most Fished MPAs per km2----')
print(most_fished_MPAs_per_km2.sort_values(by='fishing_hours_per_km2', ascending=False).head(10))
print('----Biggest Culprits (Countries)----')
print(most_fished_countries.sort_values(ascending=False).head(10))
print('----Biggest Culprits (Vessels)----')
print(most_fished_vessels.sort_values(ascending=False).head(10))	
	