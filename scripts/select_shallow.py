# -*- coding: utf-8 -*-
import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from unidecode import unidecode

#select all MPAs containing large shallow inlets and bays (1160)


#read in shapefile
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/HELCOM_MPAs/HELCOM_MPAs.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/Natura2000_end2017_Shapefile/Natura2000_end2017_epsg3035.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/MPA/MPA.shp")]


#read in habitat code list
hab_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/HABITATS.csv")

#copy shapefile format
#with fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/Natura2000_end2017_Shapefile/Natura2000_end2017_epsg3035.shp", 'r') as source:
with fiona.open("natura2000_utf8.shp") as source:

	polygons = [pol for pol in source]
	with fiona.open('shallow_habitats.shp', 'w', encoding='utf-8', **source.meta) as outfile:
	
		for i, poly in enumerate(polygons):
			sitecode = poly['properties']['SITECODE']
			sitetype = poly['properties']['SITETYPE']
			habitatcodes = hab_data.loc[hab_data.SITECODE==sitecode]['HABITATCODE']
#			print sitecode
#			print habitatcodes
			if ('1160' in habitatcodes.values) and (sitetype != 'A'):
				poly['properties']['SITENAME'] = 'PLACEHOLDER'
				outfile.write(poly)
				print(str(i) + ' Shallow Site Code: ' + sitecode)
			if i%100==0:
				print(i)
	
	