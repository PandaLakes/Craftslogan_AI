import tweepy

# Replace these values with your actual credentials
CONSUMER_KEY = 'jIWXLRiwm224v8rLiX8sLx3zP'
CONSUMER_SECRET = 'LCShW4NrMwd7UC3lLikvbC3n9hKz8HyIXHUK5enUmI0uOcqdNf'
ACCESS_TOKEN = '1623441977650958340-Y66CjTSxSVbg9hznMjWl8bqNqtPO27'
ACCESS_TOKEN_SECRET = 'gvKxvZER3x1xTbrGaTirsoe16EktPtK6EEYvEK1eTA8dm'

def post_tweet_with_image(text, image_path):
    # Authenticate to Twitter
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    try:
        # Verify credentials
        api.verify_credentials()
        print("Authentication OK")

        # Upload image
        media = api.media_upload(image_path)

        # Post tweet with image
        api.update_status(status=text, media_ids=[media.media_id])
        print("Tweet posted successfully!")
    except tweepy.TweepyException as e:
        print("Error posting tweet:", e.response.text)

if __name__ == "__main__":
    text = "YWoven with Heritage, Adorned with Elegance."
    image_path = "C:/Users/isach/slogan_maker/generated_image_20240524_125522.png"  # Replace with the path to your image
    post_tweet_with_image(text, image_path)
