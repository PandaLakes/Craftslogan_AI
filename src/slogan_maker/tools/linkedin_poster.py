import requests
import json
import os
import time

class LinkedInPoster:
    CLIENT_ID = 'YOUR_CLIENT_ID'
    CLIENT_SECRET = 'YOUR_CLIENT_SECRET_ID'
    REDIRECT_URI = 'https://www.linkedin.com/developers/tools/oauth/redirect'
    AUTHORIZATION_CODE = 'YOUR_AUTHORIZATION_CODE'
    ACCESS_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    POST_IMAGE_URL = 'https://api.linkedin.com/v2/assets?action=registerUpload'
    POST_URL = 'https://api.linkedin.com/v2/ugcPosts'
    PERSON_ID = 'YOUR_PERSON_ID'
    TOKEN_FILE = 'linkedin_token.json'

    def get_access_token(self):
        """Exchange the authorization code for an access token."""
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'r') as file:
                token_data = json.load(file)
            if token_data.get('expires_at', 0) > time.time():
                return token_data['access_token']

        data = {
            'grant_type': 'authorization_code',
            'code': self.AUTHORIZATION_CODE,
            'redirect_uri': self.REDIRECT_URI,
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
        }
        response = requests.post(self.ACCESS_TOKEN_URL, data=data)
        response_data = response.json()
        if 'access_token' in response_data:
            response_data['expires_at'] = time.time() + response_data.get('expires_in', 0)
            with open(self.TOKEN_FILE, 'w') as file:
                json.dump(response_data, file)
            return response_data['access_token']
        else:
            raise Exception("Failed to obtain access token. Response:", response_data)

    def upload_image(self, access_token, image_path):
        """Upload an image to LinkedIn and return the asset ID."""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        request_body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": f"urn:li:person:{self.PERSON_ID}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        response = requests.post(self.POST_IMAGE_URL, headers=headers, json=request_body)
        response_data = response.json()
        upload_url = response_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = response_data['value']['asset']

        # Upload the actual image file
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        requests.put(upload_url, headers={'Authorization': f'Bearer {access_token}'}, data=image_data)
        
        return asset

    def post_content(self, access_token, asset, text):
        """Post content to LinkedIn with the uploaded image."""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        post_data = {
            "author": f"urn:li:person:{self.PERSON_ID}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Image Description"
                            },
                            "media": asset,
                            "title": {
                                "text": "Image Title"
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(self.POST_URL, headers=headers, json=post_data)
        print(response.json())

    def post_to_linkedin(self, text, image_path):
        try:
            access_token = self.get_access_token()
            asset = self.upload_image(access_token, image_path)
            self.post_content(access_token, asset, text)
        except Exception as e:
            print("An error occurred:", str(e))