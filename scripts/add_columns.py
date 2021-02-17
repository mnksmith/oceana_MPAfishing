import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd

#read in fishing points
gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_code/reef_master_complete_0.csv")

#read in extra data
site_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/NATURA2000SITES.csv")
hab_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/HABITATS.csv")
vessel_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/EU_fleet_register.csv")


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
	return bool,

#get gear types
def get_gear(callsign, vessel_data):
	gear1 = 'FILL1'
	gear2 = 'FILL2'
	if callsign in vessel_data.IRCS.values:
		gear1 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Main Code'].values[0]
		gear2 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Sec Code'].values[0]
	return gear1, gear2
	
#get habitat info
def get_hab_info(sitecode, sitedata, hab_data):
	areaseries = site_data.loc[site_data.SITECODE==sitecode]['AREAHA'].values
	area = areaseries[0]/100
			
	coverseries = hab_data.loc[(hab_data.SITECODE==sitecode) & (hab_data.HABITATCODE==habitat_type)]['COVER_HA'].values
	cover = coverseries[0]/100
	if(cover>area):
		cover = area
					
	return area, cover

#Operations on the DataFrame

out_data = gfw_data


#drop unwanted rows
'''out_data = out_data[out_data.apply(lambda row: is_bad_gear(row['callsign'], vessel_data), axis=1)]
print('check 2')
out_data = out_data[out_data.apply(lambda row: isin_MPA(idx, row['lon'], row['lat']), axis=1)]
print('check 3')'''
	
#add new columns
out_data['Gear1'], out_data['Gear2'] = out_data.apply(lambda row: get_gear(row['Callsign'], vessel_data), axis=1)
print('check 1')
out_data['Area'], out_data['Cover'] = out_data.apply(lambda row: get_hab_info(row['MPA_Code'], site_data, hab_data), axis=1)


print(out_data.head(2))
