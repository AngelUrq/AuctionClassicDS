import json
import requests
import datetime
import pyodbc
import time
import os
import math


def create_access_token(client_id, client_secret, region='us'):
    data = {'grant_type': 'client_credentials'}
    response = requests.post('https://%s.battle.net/oauth/token' %
                             region, data=data, auth=(client_id, client_secret))
    return response.json()


def retrieve_from_api(config):
    response = create_access_token(config['CLIENT_KEY'], config['SECRET_KEY'])
    token = response['access_token']
    print('Token created')

    response = requests.get('https://us.api.blizzard.com/data/wow/connected-realm/{}/auctions/{}?namespace=dynamic-classic-us&locale=en_US&access_token={}'.format(
        config['connected_realm_id'], config['auction_house_id'], token))

    print('Request done')

    return response.json()


def process_auction(auction):
    rand = None
    if 'rand' in auction['item'].keys():
        rand = str(auction['item']['rand'])

    seed = None
    if 'seed' in auction['item'].keys():
        seed = str(auction['item']['seed'])
    
    bid_gold = math.floor(auction['bid'] / 10000)
    bid_silver = math.floor(((auction['bid'] / 10000) - bid_gold) * 100)
    
    buyout_gold = math.floor(auction['buyout'] / 10000)
    buyout_silver = math.floor(((auction['buyout'] / 10000) - buyout_gold) * 100)

    return (auction['id'], auction['item']['id'], bid_gold, bid_silver, buyout_gold, buyout_silver, auction['quantity'], auction['time_left'], rand, seed)


def save_auctions(auctions, config):
    print('Loading auction data to the database')

    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          config['db_host'] + ';DATABASE='+config['db_name'] + ';UID='+config['db_user'] + ';PWD=' + config['db_password'])

    cursor = conn.cursor()

    sql = """
                DECLARE @AuctionId AS BIGINT;
                SET @AuctionId = ?;
                
                BEGIN TRY
                    INSERT INTO Auction
                    VALUES (@AuctionId, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
                    
                    INSERT INTO RecordedAuction
                    VALUES (@AuctionId, CURRENT_TIMESTAMP);
                END TRY
                BEGIN CATCH
                    INSERT INTO RecordedAuction
                    VALUES (@AuctionId, CURRENT_TIMESTAMP);
                END CATCH
            """

    start_time = time.time()
    cursor.executemany(sql, auctions)
    end_time = time.time()

    print('Elapsed time for auctions: ' + str((end_time - start_time)/60))

    conn.commit()

    cursor.close()
    conn.close()


def get_auction_data():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    with open(config_path) as json_data:
        config = json.load(json_data)

    data = retrieve_from_api(config)

    auctions = []

    for auction in data['auctions']:
        auctions.append(process_auction(auction))

    print(str(len(auctions)) + ' auctions processed.')

    save_auctions(auctions, config)


get_auction_data()
