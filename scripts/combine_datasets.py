import pandas as pd

out_df = pd.read_csv('/Users/mnksmith/Documents/Oceana_MPA_code/turtle_master_complete_0.csv')

for i in range(1,9):
	csv_name = '/Users/mnksmith/Documents/Oceana_MPA_code/turtle_master_complete_' + str(i) + '.csv'
	in_df = pd.read_csv(csv_name)
	out_df = out_df.append(in_df, ignore_index=True)
	
out_df.to_csv('turtle_master_complete_all.csv')
	
