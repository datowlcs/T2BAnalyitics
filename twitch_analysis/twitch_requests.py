import json
import requests
import psycopg2
import time


# API variables
BASE_URL = 'https://api.twitch.tv/helix/'
CLIENT_ID = 'ns8jo098eiow520zuf3ltf7x14erc0'
CLIENT_SECRET = '68wkijs855octdmp6mfzqk8ygztiqz'
INDENT = 2
AUTH_URL = 'https://id.twitch.tv/oauth2/token'


# Workflow for fetching data from Twitch API
# 1. Get auth token
# 2. Generate query url
# 3. Call Twitch API
# 4. Handle Response
# 5. Save to Database


def get_twitch_auth():
    params = {'client_id': CLIENT_ID,'client_secret': CLIENT_SECRET, 'grant_type': 'client_credentials'}
    response = requests.post(AUTH_URL, data=params)
    HEADERS = {
    "Client-ID": CLIENT_ID,
    "Authorization": "Bearer {}".format(response.json()["access_token"])
    }
    return response.json()["access_token"]

def get_response(query, token):
    url = BASE_URL + query
    HEADERS = {'client-id': CLIENT_ID, 'Authorization': 'Bearer ' + token}
    response = requests.get(url, headers=HEADERS)
    return response


# get the user's live stream info
# https://api.twitch.tv/helix/streams
def get_user_streams_query(user_login):
    return 'streams?user_login={0}'.format(user_login)

#get the user's live stream total
def get_user_total_info(user_login):
    return 'users?user_login={0}'.format(user_login)

def get_games_query():
    return 'games/top'

def handle_response(response):
    ret_vals = {}
    if len(response.json()["data"]) > 0:
        for k, v in response.json()["data"][0].items():
            if k == 'game_id' or k == 'viewer_count' or k == 'started_at' or k == 'language' or k == 'user_name':
                ret_vals[k] = v
    return ret_vals


def print_response(response):
    for k, v in response.json()["data"][0].items():
        print("{}: {}".format(k, v))


def writeLiveStreamDataToDB(user_login, user_name, game_id, viewer_count, started_at, language):
    # DB variables
    host = 't2banalyticsserver.postgres.database.azure.com'
    dbname = 'streamerliveanalytics'
    user = 'TannerTTV@t2banalyticsserver'
    password = 'AlexLinaNolan!'
    sslmode = 'require'
    table_name = user_login

    # connect to db
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)

    cursor = conn.cursor()

    # check if streamer table already exists
    stmt = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    cursor.execute(stmt)
    results = cursor.fetchall()
    exists = False
    for item in results:
        if item[0] == table_name.lower():
            exists = True
    

    # create table for streamer if none exist
    if not exists:
        create_table = """
        CREATE TABLE {} (
        timestamp INTEGER PRIMARY KEY,
        user_name VARCHAR(32) NOT NULL,
        game_id INTEGER NOT NULL,
        viewer_count INTEGER,
        started_at VARCHAR(32) NOT NULL,
        language VARCHAR(32) NOT NULL
        );""".format(table_name)

        cursor.execute(create_table)
    
    # write live stream data to table
    insert_data = ("INSERT INTO {} (timestamp, user_name, game_id, viewer_count, started_at, language) VALUES \
        ({}, '{}', {}, {}, '{}', '{}');").format(table_name, time.time(), user_name, game_id, viewer_count, started_at, language)

    cursor.execute(insert_data)

    conn.commit()
    cursor.close()
    conn.close()



if __name__ == "__main__":
    
    # users to fetch live stream data from
    user_logins = ['DansGaming', 'BobRoss', 'JoinTime', 'BeyondTheSummit', 'ESL_DOTA2', 
                    'RiotGames', 'Destroy', 'Monstercat', 'Whippy', 'marymaybe', 'Ponce']

    for user_login in user_logins:
        # obtain auth token
        access_token = get_twitch_auth()

        # # fetch stream data from api
        query = get_user_streams_query(user_login)
        response = get_response(query, access_token)

        # save data to azure db
        ret_vals = handle_response(response)
        if (len(ret_vals) > 0):
            writeLiveStreamDataToDB(user_login, ret_vals['user_name'], ret_vals['game_id'],
                                    ret_vals['viewer_count'], ret_vals['started_at'], ret_vals['language'])

    