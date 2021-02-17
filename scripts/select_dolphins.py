# -*- coding: utf-8 -*-
import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
from unidecode import unidecode

#select all MPAs that list Tursiops truncatus (bottlenose dolphin -- 1349) 
#    or Phocoena phocoena (harbor porpoise -- 1351) as a protected species


#read in shapefile
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/HELCOM_MPAs/HELCOM_MPAs.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/Natura2000_end2017_Shapefile/Natura2000_end2017_epsg3035.shp")]
#polygons = [pol for pol in fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/MPA/MPA.shp")]


#read in habitat code list
sp_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/SPECIES.csv")

#copy shapefile format
#with fiona.open("/Users/mnksmith/Documents/Oceana_MPA_data/Natura2000_end2017_Shapefile/Natura2000_end2017_epsg3035.shp", 'r') as source:
with fiona.open("natura2000_utf8.shp") as source:

	polygons = [pol for pol in source]
	with fiona.open('dolphin_habitats.shp', 'w', encoding='utf-8', **source.meta) as outfile:
	
		for i, poly in enumerate(polygons):
			sitecode = poly['properties']['SITECODE']
			sitetype = poly['properties']['SITETYPE']
			speciescodes = sp_data.loc[sp_data.SITECODE==sitecode]['SPECIESCODE']
			if ('1349' in speciescodes.values or '1351' in speciescodes.values) and (sitetype != 'A'):
				poly['properties']['SITENAME'] = 'PLACEHOLDER'
				outfile.write(poly)
				print(str(i) + ' Dolphin Site Code: ' + sitecode + str(speciescodes.values))
			if i%100==0:
				print(i)
	
	