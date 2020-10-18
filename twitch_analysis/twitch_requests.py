import json
import requests

BASE_URL = 'https://api.twitch.tv/helix/'
CLIENT_ID = 'ns8jo098eiow520zuf3ltf7x14erc0'
CLIENT_SECRET = '68wkijs855octdmp6mfzqk8ygztiqz'
#HEADERS = {'client-id': CLIENT_ID, 'Authorization': 'Bearer ' + ACCESS_TOKEN}
INDENT = 2
AUTH_URL = 'https://id.twitch.tv/oauth2/token'


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

if __name__ == "__main__":
    get_twitch_auth()

    user_login = 'sodapoppin'

    access_token = get_twitch_auth()

    query = get_user_streams_query(user_login)
    #query = twitch_requests.get_games_query()
    response = get_response(query, access_token)

    print_response(response)