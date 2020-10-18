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
    print(response.json()["access_token"])
    #response_valid = requests.post("https://id.twitch.tv/oauth2/validate", headers=HEADERS)

    print(response.json())
    print(HEADERS)

    nowApiTest = requests.get("https://api.twitch.tv/helix/games/top", headers=HEADERS)
    print(nowApiTest.json()["data"][0]["name"])

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

def print_response(response):
    print(response.json()["data"][0]["viewer_count"])


def writeLiveStreamDataToDB(user_login, game_id, viewer_count, started_at, language):
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
    cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (table_name,))

    # create table for streamer if none exist
    if not bool(cursor.rowcount):
        create_table = """
        CREATE TABLE {} (
        timestamp INTEGER PRIMARY KEY,
        game_id INTEGER NOT NULL,
        viewer_count INTEGER,
        started_at INTEGER NOT NULL,
        language VARCHAR(32) NOT NULL
        );""".format(table_name)

        cursor.execute(create_table)
    
    # write live stream data to table
    insert_data = """
    INSERT INTO {} (timestamp, game_id, viewer_count, started_at, language) VALUES
    ({}, {}, {}, {}, {});""".format(time.time, game_id, viewer_count, started_at, language)

    cursor.execute(insert_data)

    conn.commit()
    cursor.close()
    conn.close()



if __name__ == "__main__":
    
    # users to fetch live stream data from
    user_login = 'Sykkuno'

    # obtain auth token
    access_token = get_twitch_auth()

    # fetch stream data from api
    query = get_user_streams_query(user_login)
    response = get_response(query, access_token)

    #print_response(response)

    # TODO: Parse response to obtain stream data values

    # stream data
    game_id = 0
    viewer_count = 0
    started_at = 0
    language = ""

    writeLiveStreamDataToDB(user_login, game_id, viewer_count, started_at, language)

    