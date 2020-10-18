import twitch_requests as f

user_login = 'ninja'



access_token = f.get_twitch_auth()


query = f.get_user_streams_query(user_login)
#query = twitch_requests.get_games_query()
response = f.get_response(query, access_token)

f.print_response(response)
