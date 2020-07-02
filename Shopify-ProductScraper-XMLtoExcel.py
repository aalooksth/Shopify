import requests, json
import xmltodict
import time
import ctypes
import pandas as pd

# Author: aalooksth@gmail.com

start_time = time.time() #script start time
today = time.strftime('%m.%d.%Y') #today's date

URL = open("URL.txt", 'r').read().splitlines() #read url from file
print("Reading product URLs from file...")

#process urls
count = 0
df = pd.DataFrame()
for url in URL:
    print("Loading XML data for " + url)
    data = requests.get(url + ".xml").content
    
    print("Parsing XML into JSON data.")
    d_dict = xmltodict.parse(data, xml_attribs =False)
    jdata=json.loads(json.dumps(d_dict))['hash'] #loads parsed data in json format

    #backup data within data
    variants = jdata['variants']['variant'] #Variation (Option Combinations)
    options = jdata['options']['option'] #Option Name
    images = jdata['images']['image']
    image = jdata['image']
    
    # clean original json data
    try:
        del jdata['options']
        del jdata['variants']
        del jdata['images']
        del jdata['image']
    except:
        pass

    # extract Option Names
    try:
        options = [option['name'] for option in options]
    except: 
        options = [options['name']]
    
    len_o = len(options)
    
    options+=[None]*(3-len_o) #Normalise Option in 3
        
    # Create df of image and variants
    df_p = pd.DataFrame([jdata.values()],columns=jdata.keys())
    df_o = pd.DataFrame([options],columns=['Option1 Name', 'Option2 Name','Option3 Name'])
    df_v = pd.DataFrame.from_dict(variants).add_prefix('Variant ')
    df_i = pd.DataFrame.from_dict(images).add_prefix('Image ')
    
    print(len_o,"options.")
    print(df_v.shape[0],"variant combinations.")
    print(df_i.shape[0],'images.')


    df_v = df_v.join(df_i[['Image src','Image id']].set_index('Image id'),on='Variant image-id').rename(columns={'Image src':'Variant Image'})
    
    df_i.columns = [x.title() for x in df_i.columns]
    df_i.rename(columns={'Image Alt':'Image Alt Text'}, inplace=True)
    df_v.columns = [x.title().replace('-',' ') for x in df_v.columns]
    df_v.rename(columns={
        'Variant Sku':'Variant SKU', 'Variant Inventory Management': 'Variant Inventory Tracker',
        'Variant Option1':'Option1 Value', 'Variant Option2':'Option2 Value',
        'Variant Option3':'Option3 Value', 'Variant Inventory Quantity':'Variant Inventory Qty'
    }, inplace=True)
    df_p.columns = [x.title() for x in df_p.columns]
    df_p.rename(columns={
        'Body-Html':'Body (HTML)', 'Product-Type':'Type', 'Published-Scope':'Published'
    }, inplace=True)


    #Clean
    df_p.loc[df_p['Published']=='web','Published']=True
    df_v.loc[df_v['Variant Compare At Price'].isnull(),'Variant Compare At Price']=0
    df_v.loc[:,['Variant Requires Shipping','Variant Taxable']]=df_v.loc[:,['Variant Requires Shipping','Variant Taxable']].replace('true',True)

    #Temporary Fix
    if 'Variant Inventory Policy' not in df_v.columns:
       print('VIP and VIQ not present, setting default value to None.')
       df_v['Variant Inventory Policy']=None
       df_v['Variant Inventory Qty']=None

    df_v['Variant Tax Code'], df_v['Cost per item'] = None, None

    order = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type','Tags', 
            'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name',
            'Option2 Value', 'Option3 Name','Option3 Value', 'Variant SKU',
            'Variant Grams', 'Variant Inventory Tracker','Variant Inventory Qty',
            'Variant Inventory Policy', 'Variant Fulfillment Service',
            'Variant Price','Variant Compare At Price',
            'Variant Requires Shipping', 'Variant Taxable','Variant Barcode',
            'Image Src','Image Position', 'Image Alt Text',
    # Gift Card   SEO Title     SEO Description      Google Shopping / Google Product Category Google Shopping / Gender    Google Shopping / Age Group Google Shopping / MPN       Google Shopping / AdWords Grouping Google Shopping / AdWords Labels   Google Shopping / Condition Google Shopping / Custom Product   Google Shopping / Custom Label 0   Google Shopping / Custom Label 1   Google Shopping / Custom Label 2   Google Shopping / Custom Label 3   Google Shopping / Custom Label 4         
            'Variant Image', 'Variant Weight Unit',
            'Variant Tax Code', 'Cost per item'
           ]

    res = df_p.join(df_o, how='outer').join(df_v, how='outer').join(df_i,how='outer')[order]

    res['Handle']= res['Handle'].ffill()
    res

    df = df.append(res[order], ignore_index=True)
    
    # try:
    #     existing = pd.read_excel("Parsed_Data_"+today+".xlsx")
    #     final = existing.append(res[order], ignore_index=True)
    # except:
    #     final = res
    # final.to_excel("Parsed_Data_"+today+".xlsx",index=False)
    # print("Saved parsed data to output file.")
    count +=1
    print("URL processed: " + str(count) +" of "+ str(len(URL)))
df.to_excel("Parsed_Data_"+today+"--.xlsx",index=False)
    
#calculate time taken to run script
time_taken = int(time.time() - start_time)
time_taken_minutes = int(time_taken / 60)
time_taken_seconds = time_taken - (time_taken_minutes * 60)
ctypes.windll.user32.MessageBoxW(0, "Completed in: " + str(time_taken_minutes) + " minutes and " + str(time_taken_seconds)\
    + " seconds.\n\nTotal URLs in file: "+ str(len(URL)) + "\n\nURLs processed: " + str(count), "Time Elapsed", 0)
