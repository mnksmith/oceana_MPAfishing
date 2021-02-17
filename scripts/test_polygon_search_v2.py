import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from pyproj import Proj, transform
from rtree import index
import time

#read in shapefile
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/HELCOM_MPAs/HELCOM_MPAs.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/Natura2000_end2017_Shapefile/Natura2000_end2017_epsg3035.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/MPA/MPA.shp")]
polygons = [pol for pol in fiona.open('dolphin_habitats.shp')]

#read in fishing points
#gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/test_data.csv")
gfw_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/all_2017_0.csv")
#gfw_data = pd.read_csv('/Users/mnksmith/Documents/Oceana_MPA_data/EUeez_trawlers_Mar18.csv')
#gfw_data = gfw_data.drop(columns=['mmsi','flag_iso3','imo','eez_iso3'])

#read in site data
site_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/NATURA2000SITES_slim.csv")
'''site_data = site_data.drop(columns=['COUNTRY_CODE','SITENAME','SITETYPE','DATE_COMPILATION','DATE_UPDATE','DATE_SPA',
									'SPA_LEGAL_REFERENCE','DATE_PROP_SCI','DATE_CONF_SCI','DATE_SAC','SAC_LEGAL_REFERENCE',
									'EXPLANATIONS','LENGTHKM','MARINE_AREA_PERCENTAGE','LONGITUDE','LATITUDE','DOCUMENTATION',
									'QUALITY','DESIGNATION','OTHERCHARACT'])'''
hab_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/HABITATS_slim.csv")
'''hab_data = hab_data.drop(columns=['DESCRIPTION','HABITAT_PRIORITY','PRIORITY_FORM_HABITAT_TYPE','NON_PRESENCE_IN_SITE',
									'CAVES','REPRESENTATIVITY','RELSURFACE','CONSERVATION','GLOBAL_ASSESMENT','DATAQUALITY',
									'PERCENTAGE_COVER','INTRODUCTION_CANDIDATE'])'''
vessel_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/EU_fleet_register_slim.csv")
'''vessel_data = vessel_data.drop(columns=['Country Code','CFR','Event Code','Event Start Date','Event End Date','License Ind',
										'Registration Nbr','Ext Marking','Vessel Name','Port Code','Port Name','IRCS Code',
										'Vms Code','Loa','Lbp','Ton Ref','Ton Gt','Ton Oth','Ton Gts','Power Main',
										'Power Aux','Hull Material','Com Year','Com Month','Com Day','Segment','Exp Country',
										'Exp Type','Public Aid Code','Exp Type','Decision Date','Decision Seg Code',
										'Construction Year','Construction Place'])'''
										

#coordinate transformation
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:3035')

idx = index.Index()
for pos, poly in enumerate(polygons):
	idx.insert(pos, shape(poly['geometry']).bounds)


#reef requirements
'''habitat_type = '1170'
bad_gears = pd.Series(['DRB',  # dredges
						'TBB', # trawls
						'OTB',
						'PTB',
						'OTT',
						'LHM', # hooks and lines
						'LHP',
						'LLD', # longlines
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
						'SB']) '''
						
#cetaceans requirements
meh_gears = pd.Series(['OTB', # trawls
						'OTT',
						'PTB',
						'TBB',
						'OTM',
						'PTM',
						'LLD', # longlines
						'LLS',
						'SSC', # seines
						'SDN',
						'SPR'])
bad_gears = pd.Series(['GTR',  # nets
						'GNS',
						'GND',
						'PS',
						'GTN',
						'GNC',
						'SB']) # seines


total_fishing_hours = 0
fished_MPAs = pd.DataFrame(columns=['MPA_Code', 'Area', 'Cover', 'fishing_hours', 'Country', 'Vessel', 'Callsign', 'Gear1', 'Gear2'])
MPA_index = 0
begin = time.time()
for row in gfw_data.itertuples():
	x,y = transform(inProj, outProj, row.lon, row.lat)
#	x,y = row['lon'], row['lat']
	point = Point(x,y)
	fishing_hours = row.fishing_hours
	callsign = row.callsign
	gear1 = 'FILL1'
	gear2 = 'FILL2'
	if callsign in vessel_data.IRCS.values:
		gear1 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Main Code'].values[0]
		gear2 = vessel_data.loc[vessel_data.IRCS==callsign]['Gear Sec Code'].values[0]
		shipname = vessel_data.loc[vessel_data.IRCS==callsign]['Vessel Name'].values[0]
		
	if (gear1 in bad_gears.values) or (gear2 in bad_gears.values) or (gear1 in meh_gears.values) or (gear2 in meh_gears.values):

		for j in idx.intersection(point.coords[0]):
			if point.within(shape(polygons[j]['geometry'])):
				total_fishing_hours += fishing_hours
				sitecode = polygons[j]['properties']['SITECODE']
				areaseries = site_data.loc[site_data.SITECODE==sitecode]['AREAHA'].values
				area = areaseries[0]/100
				cover = area #for species
				'''coverseries = hab_data.loc[(hab_data.SITECODE==sitecode) & (hab_data.HABITATCODE==habitat_type)]['COVER_HA'].values
				cover = coverseries[0]/100
				if(cover>area):
					cover = area'''
			
			
				fished_MPAs.loc[MPA_index] = (sitecode, area, cover, fishing_hours, row.country_name, shipname, callsign, gear1, gear2) #Helcom,MPA: 'Name', Natura2000 'SITENAME'
				MPA_index+=1
	
	k = row.Index	
	if k%1000 == 0:
		print(k)
	if k%100000 == 0:
		end = time.time()
		print(end-begin)


most_fished_MPAs = fished_MPAs.groupby('MPA_Code').fishing_hours.sum()
most_fished_MPAs_per_km2 = fished_MPAs.groupby(['MPA_Code', 'Area', 'Cover'],as_index=False).fishing_hours.sum()
most_fished_MPAs_per_km2['fishing_hours_per_km2'] = most_fished_MPAs_per_km2['fishing_hours']/most_fished_MPAs_per_km2['Area']
most_fished_MPAs_per_km2['fishing_hours_coverage'] = most_fished_MPAs_per_km2['fishing_hours']*most_fished_MPAs_per_km2['Cover']/most_fished_MPAs_per_km2['Area']
most_fished_countries = fished_MPAs.groupby('Country').fishing_hours.sum()
most_fished_vessels = fished_MPAs.groupby(['Vessel', 'Callsign', 'Gear1', 'Gear2']).fishing_hours.sum()

fished_MPAs.to_csv('dolphin_master_temp.csv')
most_fished_MPAs.sort_values(ascending=False).to_csv('dolphin_MPAs_temp.csv')
most_fished_MPAs_per_km2.sort_values(by='fishing_hours_per_km2', ascending=False).to_csv('dolphin_MPAs_per_km2_temp.csv')
most_fished_countries.sort_values(ascending=False).to_csv('dolphin_countries_temp.csv')
most_fished_vessels.sort_values(ascending=False).to_csv('dolphin_vessels_temp.csv')

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
	