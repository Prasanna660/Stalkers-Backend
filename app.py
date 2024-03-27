import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from instasentiments import (
    getPublicProfileCaptions,
    getPrivateProfileCaptions,
    getSentiments,
    getPrivateProfileCommentsSentiments
)

# Initializing our application
app = Flask(__name__)
CORS(app)

# Function to fetch image from URL and encode it as base64
def fetch_and_encode_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Convert image to base64
            encoded_image = base64.b64encode(response.content).decode('utf-8')
            return encoded_image
    except Exception as e:
        print("Error fetching image:", e)
    return None

# Route that sends the JSON response to the client
@app.route('/requestjson', methods=['POST'])
def receiveSendJSON():
    if request.method == 'GET':
        return "<h1 style='color:red'> GET requests are not allowed, send some JSON data to this URL. </h1>"
    
    data = request.json

    response_data = {}

    if data['type'] == 'Public':
        login_id = data['login_id']
        result, profile_pic_url, full_name, posts_data = getPublicProfileCaptions(login_id)

    elif data['type'] == 'PrivateCombined':
        login_id = data['login_id']
        login_username = data['login_username']
        password = data['password']
    
        captions, profile_pic_url, full_name, captions_posts_data = getPrivateProfileCaptions(login_id, login_username, password)
        comments, _, _, comments_posts_data = getPrivateProfileCommentsSentiments(login_id, login_username, password)
        
        # Combine post data from captions and comments
        posts_data = captions_posts_data + comments_posts_data
    
        result = captions + comments  # Combine captions and comments

    if isinstance(result, str):
        response_data = {
            'Type': 'Fail',
            'Value': result
        }
    else:
        sentiments = getSentiments(result)
        if isinstance(sentiments, str):
            response_data = {
                'Type': 'Fail',
                'Value': sentiments,
            }
        else:
            # Fetch and encode profile picture
            encoded_profile_pic = fetch_and_encode_image(profile_pic_url)
            if encoded_profile_pic:
                response_data = {
                    'Type': 'Success',
                    'Value': sentiments,
                    'Picture': f"data:image/jpeg;base64,{encoded_profile_pic}",
                    'Name': full_name,
                    'PostData': []
                }

                # Fetch and encode images in post_data
                for post in posts_data:
                    encoded_post_image = fetch_and_encode_image(post['url'])
                    if encoded_post_image:
                        post_data_entry = {
                            'date': post['date'],
                            'likes': post['likes'],
                            'url': f"data:image/jpeg;base64,{encoded_post_image}"
                        }
                        response_data['PostData'].append(post_data_entry)
                    else:
                        print("Error fetching image for post:", post['url'])
            else:
                response_data = {
                    'Type': 'Fail',
                    'Value': 'Error fetching profile picture'
                }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=False, threaded=False)
