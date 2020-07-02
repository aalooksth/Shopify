import pandas as pd
import pathlib
# import sys.argv
# import os

# print(argv)

filename='Images-NPU-RAW.csv' # Must have Handle, Title and Images (Column Name doesnt matter/Order will be maintained, blanks will be ignored)
#base = r"D:\OneDrive - GrowByData\GrowByData - Alok\Rugs Done Right\RDR-2020\04.14.2020-RDR-Safavieh-NewRugs"
base = pathlib.Path().cwd()
print(base)

p_cols=['Handle','Title']

def runmain():
	print('Initialising . . .')
	base=pathlib.Path(base)
	df= pd.read_csv(base/filename)

	print("Processing . . .")
	df_new = df.set_index(p_cols).stack()
	df_new.index = df_new.index.set_names(p_cols+['del'])

	df_f = df_new.reset_index('del',drop=True).rename('Image Src').reset_index()

	print("Forming Alt text and removing Title from all but parent. . .")
	df_f['Image Alt Text'] = df_f['Handle'].str.replace("-"," ")
	df_f.loc[df_f['Title'].duplicated(),'Title']=''

	print("Exporting the Shopify CSV . . .")
	df_f.to_csv(base / 'Image-list-Shopifyformat.csv',header=True,index=False)
	print("Done.")

if __name__ == '__main__':
	runmain()