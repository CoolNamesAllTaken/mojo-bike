import requests
from pprint import pprint

# Access token docs
# http://developers.strava.com/docs/authentication/

# Uploading to Strava docs
# http://developers.strava.com/docs/uploads/
# http://developers.strava.com/docs/reference/#api-Uploads-createUpload

# Authentication redirect. If you want to grant the app access to your strava account,
# click this link then click 'Authorize'. The URL it redirects you to contains the access code.
# https://www.strava.com/oauth/authorize?client_id=32742&response_type=code&redirect_uri=http://bensprojects.com&approval_prompt=force&scope=activity:write

# Callback format. Once the user clicks authorize, it redirects them to the
# callback domain (bensprojects.com) with the access code. Using that and the
# client secret, we can generate a short lived API key to actually upload stuff.
# http://bensprojects.com/?state=&code=4b33bd68832db37bb1870a035a80f8ef15b72053&scope=read,activity:write

# GPX format documentation
# https://en.wikipedia.org/wiki/GPS_Exchange_Format

# Get a temporary user access token
r = requests.post('https://www.strava.com/oauth/token', data={
	'client_id': 32742,
	'client_secret': '<GET THIS FROM THE API CONSOLE>',
	'code': '5f7bbec36c2593d64d5960f31b437ec808db0703', # This is Ben's access code use the procedure above to generate your own
	'grant_type': 'authorization_code'
})

access_token = r.json()['access_token']

# Initiate the upload (Asynchronous)
r = requests.post('https://www.strava.com/api/v3/uploads', data={
	'access_token': access_token,
	'data_type': 'gpx',
	'name': 'MOJO upload'
}, files={
	# An example GPX file, stolen from Wikipedia
	'file': open('path.gpx', 'rb')
})

print(r.status_code)
pprint(r.json())

