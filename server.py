from flask import Flask, request, redirect
import webbrowser
import requests
from urllib.parse import urlencode

app = Flask(__name__)

# LinkedIn app credentials
CLIENT_ID = 'xxxxx'
CLIENT_SECRET = 'xxxxxx'
REDIRECT_URI = 'http://localhost:5000/callback'
AUTHORIZATION_URL = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
STREAMLIT_URL = 'http://localhost:8501'

def get_authorization_url():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid profile w_member_social email r_basicprofile'
    }
    return f"{AUTHORIZATION_URL}?{urlencode(params)}"

@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    if auth_code:
        access_token = exchange_code_for_access_token(auth_code)
        if access_token:
            return redirect(f"{STREAMLIT_URL}?access_token={access_token}")
        else:
            return "Failed to get access token."
    else:
        return "Authorization code not found."

def exchange_code_for_access_token(auth_code):
    response = requests.post(
        TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    if response.status_code == 200:
        response_data = response.json()
        return response_data.get('access_token')
    else:
        print("Error:", response.status_code, response.text)
        return None

if __name__ == '__main__':
    webbrowser.open(get_authorization_url())
    app.run(port=5000)
