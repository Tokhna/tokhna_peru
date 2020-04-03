import pandas as pd
import json

def sunat_catalog(file):
    sunat_file = pd.read_excel(file, None)
    sunat_catalog = sunat_file['Catálogos']
    null_rows = list(sunat_catalog[sunat_catalog.isnull().all(axis=1)].index)
    list_of_dataframes = []
    for i in range(len(null_rows) - 1):
        list_of_dataframes.append(sunat_catalog.iloc[null_rows[i]+1:null_rows[i+1],:])
    cleaned_tables = []
    for _df in list_of_dataframes:
        cleaned_tables.append(_df.dropna(axis=1, how='all'))
    sunat_dict = {}
    for df in cleaned_tables:
        if len(df.columns) == 2:
            df.columns = ['value', 'key']
        elif len(df.columns) == 3:
            df.columns = ['value', 'key', 'val1']
        elif len(df.columns) == 4:
            df.columns = ['value', 'key', 'val1', 'val2']
        index = df.index[0]
        sunat_dict[df['key'][index + 1]] = {}
        for ind in df.index:
            if ind > (index + 2):
                sunat_dict[df['key'][index + 1]][df['key'][ind]] = df['value'][ind]
    with open('sunat.json', 'w') as fp:
        json.dump(sunat_dict, fp)