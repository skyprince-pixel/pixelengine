#!/usr/bin/env python3
"""
YouTube Video Uploader using OAuth 2.0 (Google API)
Automatically uploads a generated video to YouTube!

REQUIREMENTS:
1. Install dependencies:
   pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

2. Setup Google Cloud Console for OAuth 2.0 (often requested as "Auth0" or OAuth):
   a. Go to https://console.cloud.google.com/
   b. Create a new Project.
   c. Enable the "YouTube Data API v3".
   d. Go to "OAuth consent screen", choose "External", and publish the app.
   e. Go to "Credentials" -> "Create Credentials" -> "OAuth client ID" -> "Desktop App".
   f. Download the JSON file, rename it to 'client_secrets.json', and place it in the same directory as this script.

3. Run the script:
   python youtube_uploader.py
"""

import os
import sys
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import glob

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application.
secret_files = glob.glob("client_secret*.json")
CLIENT_SECRETS_FILE = secret_files[0] if secret_files else "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
    """Authenticates the user and returns the YouTube API service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"ERROR: {CLIENT_SECRETS_FILE} not found!")
                print("Please download your OAuth 2.0 client secrets file from Google Cloud Console.")
                sys.exit(1)
                
            print("Starting new OAuth 2.0 authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def initialize_upload(youtube, options):
    """Uploads the video to YouTube."""
    tags = None
    if options.get("keywords"):
        tags = options["keywords"].split(',')

    body = {
        'snippet': {
            'title': options['title'],
            'description': options['description'],
            'tags': tags,
            'categoryId': options.get('category', '28') # 28 = Science & Technology
        },
        'status': {
            'privacyStatus': options.get('privacyStatus', 'private'),
            'selfDeclaredMadeForKids': False
        }
    }

    print(f"Loading media from {options['file']}...")
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
    )

    return resumable_upload(insert_request)

def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
                
            if response is not None:
                if 'id' in response:
                    video_id = response['id']
                    print("\n✅ Video was successfully uploaded!")
                    print(f"Video ID: {video_id}")
                    print(f"Video URL: https://youtu.be/{video_id}")
                    return True
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

if __name__ == '__main__':
    # Configuration for our V2 Wind Turbine Video
    video_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "wind_turbine_yt_short_v2.mp4"))
    
    if not os.path.exists(video_file):
        print(f"Error: Could not find video file at {video_file}")
        sys.exit(1)

    print("=== YouTube Video Uploader (OAuth 2.0) ===")
    
    # 1. Authenticate
    try:
        youtube = get_authenticated_service()
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    # 2. Upload Profile
    upload_options = {
        "file": video_file,
        "title": "Why Wind Turbines Only Have 3 Blades! #Physics #Engineering #Shorts",
        "description": "Discover the science and engineering behind wind turbines and the Goldilocks zone of 3 blades! Featuring aerodynamic wake effects and gyroscopic forces explained through a beautiful pixel art animation. #science #physics #engineering #STEM",
        "category": "28",
        "keywords": "wind turbine,physics,engineering,science,energy,renewables,animation,pixelart,shorts",
        "privacyStatus": "private" # Defaulting to private for safety until you review it
    }

    print(f"\nPreparing to upload: {upload_options['title']}")
    
    # 3. Execute
    try:
        initialize_upload(youtube, upload_options)
    except Exception as e:
        print(f"An error occurred during upload: {e}")
