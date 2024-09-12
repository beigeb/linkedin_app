import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs

# LinkedIn app credentials
CLIENT_ID = '77hz82ojukwrzf'
CLIENT_SECRET = 'LcWS9J8M5ExeZtQT'
REDIRECT_URI = 'http://localhost:5000/callback'
AUTHORIZATION_URL = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
POST_URL = 'https://api.linkedin.com/v2/ugcPosts'

def get_authorization_url():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'r_liteprofile w_member_social email'
    }
    return f"{AUTHORIZATION_URL}?{requests.compat.urlencode(params)}"

def get_access_token_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('access_token', [None])[0]

def get_user_urn(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
    response_data = response.json()
    return response_data.get('id', '')


def post_linkedin_status(access_token, message):
    user_urn = get_user_urn(access_token)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    post_data = {
        "author": f"urn:li:person:{user_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareMediaCategory": "NONE",
                "shareCommentary": {
                    "text": message
                }
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(POST_URL, headers=headers, json=post_data)
    return response.status_code, response.json()

st.title("LinkedIn OAuth 2.0 Integration")

# Display a message
st.write("1. You are being redirected to LinkedIn for authorization.")

# Extract access token from URL if present
url_params = st.experimental_get_query_params()
access_token = url_params.get('access_token', [None])[0]

if access_token:
    st.success("Access Token Obtained Successfully:")
    st.code(access_token)

    # Add functionality to post a LinkedIn status
    st.subheader("Post a LinkedIn Status")

    message = st.text_area("Enter your status message here:")

    if st.button("Post Status"):
        if message:
            status_code, response_data = post_linkedin_status(access_token, message)
            if status_code == 201:
                st.success("Status posted successfully!")
            else:
                st.error(f"Failed to post status: {response_data}")
        else:
            st.warning("Please enter a status message.")
else:
    st.write("Waiting for authorization...")

