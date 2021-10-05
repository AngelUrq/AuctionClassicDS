import pandas as pd
import json
import pyodbc
import pickle

from etl.load_data import get_auction_data

def get_data(sql, config):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + config['db_host'] +';DATABASE=' + config['db_name'] +';UID='+config['db_user'] +';PWD='+ config['db_password'] )
    cursor = conn.cursor()

    cursor.execute(sql)

    result = cursor.fetchall()

    headers = [column[0] for column in cursor.description]
    
    cursor.close()
    conn.close()
    
    return result, headers


print('Starting prediction engine!')
print('Loading configuration files...')

with open('etl/config.json') as json_data:
    config = json.load(json_data)

with open("sql/get_data.sql", "r") as f:
    sql = f.read()
    

print('Loading machine learning model...')
filename = 'model.sav'
reg = pickle.load(open(filename, 'rb'))

print('Loading DB auction historical data...')
result, headers = get_data(sql, config)

df_historical = pd.DataFrame.from_records(result, columns=headers)
df_historical = df_historical[df_historical['BuyoutGold'] > 0]
df_historical = df_historical[df_historical['TimeLeft'] == 'VERY_LONG']
df_historical.loc[:,'Sold'] = df_historical['TimesSeen'] <= 12
df_historical['UnitPrice'] = df_historical['BuyoutGold'] / df_historical['Quantity']
df_historical = df_historical[df_historical['Sold'] == True]

with open("sql/get_items.sql", "r") as f:
    sql_items = f.read()
    
print('Loading DB items data...')
result, headers = get_data(sql_items, config)

items = pd.DataFrame.from_records(result, columns=headers)
items['ItemId'] = items['Id']
items['SellPrice'] = items['SellPriceGold'] + items['SellPriceSilver'] / 100.0

print('Loading actual auction house data...')
auctions = get_auction_data(save=False)

df_actual = pd.DataFrame.from_records(auctions, columns=['Id', 'ItemId', 'BidGold', 'BidSilver', 'BuyoutGold', 'BuyoutSilver', 'Quantity', 'TimeLeft', 'Rand', 'Seed'])
df_actual['BuyoutGold'] = df_actual['BuyoutGold'] + (df_actual['BuyoutSilver'] / 100.0)
df_actual['UnitPrice'] = df_actual['BuyoutGold'] / df_actual['Quantity']
df_actual = df_actual[df_actual['BuyoutGold'] > 0]

historical_price = df_historical.groupby(by=['ItemId'])['UnitPrice'].median().reset_index(name='HistoricalPrice')
median_competitor_price = df_actual.groupby(by=['ItemId'])['UnitPrice'].median().reset_index(name='MedianCompetitorPrice')
lowest_competitor_price = df_actual[df_actual['UnitPrice'] > 0].groupby(by=['ItemId'])['UnitPrice'].min().reset_index(name='LowestCompetitorPrice')

print('Prediction engine ready!')

while True:
    item_id = int(input('Item id:'))
    quantity = int(input('Quantity:'))
    
    predict = pd.DataFrame()
    predict['ItemId'] = [item_id]
    predict['Quantity'] = [quantity]
    
    df_merged = pd.merge(predict, historical_price, on=['ItemId'], how='left')
    df_merged = pd.merge(df_merged, median_competitor_price, on=['ItemId'], how='left')
    df_merged = pd.merge(df_merged, lowest_competitor_price, on=['ItemId'], how='left')
    df_merged = pd.merge(df_merged, items[['ItemId', 'Name', 'Quality', 'ItemClass']], on=['ItemId'], how='left')
    
    df_merged['HistoricalPrice'] = df_merged['HistoricalPrice'].fillna(0)
    df_merged['MedianCompetitorPrice'] = df_merged['MedianCompetitorPrice'].fillna(0)
    df_merged['LowestCompetitorPrice'] = df_merged['LowestCompetitorPrice'].fillna(0)
    
    predictions = reg.predict(df_merged[['Quantity', 'HistoricalPrice', 'MedianCompetitorPrice', 'LowestCompetitorPrice']]) * quantity
 
    df_merged['RecommendedPrice'] = predictions
    
    print(df_merged.head())

