import shapefile
import fiona
from shapely.geometry import Point, shape
import pandas as pd
import matplotlib.pyplot as plt

polygons = [pol for pol in fiona.open('reef_habitats_temp.shp')]

site_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/NATURA2000SITES.csv")
hab_data = pd.read_csv("/Users/mnksmith/Documents/Oceana_MPA_data/PublicNatura2000End2017_csv/HABITATS.csv")

habitat_type = '1170'
cover_df = pd.DataFrame(columns=['MPA_Code', 'Area', 'Cover', 'Cover/Area'])

for i, poly in enumerate(polygons):
	sitecode = poly['properties']['SITECODE']
	areaseries = site_data.loc[site_data.SITECODE==sitecode]['AREAHA'].values
	area = areaseries[0]/100
	coverseries = hab_data.loc[(hab_data.SITECODE==sitecode) & (hab_data.HABITATCODE==habitat_type)]['COVER_HA'].values
	cover = coverseries[0]/100
	if((cover>0) & (cover<=area)):
		cover_df.loc[i] = (sitecode, area, cover, cover/area)

	if i%100 == 0:
		print(i)	
#cover_df = cover_df.sort_values(by='Cover/Area', ascending=False)

plt.hist(cover_df['Cover/Area'], density=True, bins=10)
plt.ylabel('Probability')
plt.xlabel('Cover/Area')
plt.axis([0,1,0,1])
plt.show()

cover_df.to_csv('reef_coverage.csv')
print(cover_df.head(20))

