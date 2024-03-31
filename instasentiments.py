import instaloader
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
from instaloader import Profile

def getPublicProfileCaptions(profile_id):
    loader = instaloader.Instaloader()
    profile = Profile.from_username(loader.context, profile_id)
    profile_pic = profile.get_profile_pic_url()
    full_name = profile.full_name

    posts = profile.get_posts()
    captions = []
    posts_data = []  # Initialize the list outside the loop
    for post in posts:
        if post.caption:
            captions.append(post.caption)
            posts_data.append({
                'url': post.url,
                'likes': post.likes,
                'date': post.date,
            })
    
    loader.close()
    
    if len(captions) < 1:
        return "No captions found! Are you sure this profile is public and has posted?", "Empty", "Empty"
    else:
        captions_or_comments = captions
        return captions_or_comments, profile_pic, full_name, posts_data

def getPrivateProfileCaptions(profile_id, login, password):
    loader = instaloader.Instaloader()
    
    try:
        loader.login(login, password)
    except:
        return "Failed to login!", "Empty", "Empty", None

    profile = Profile.from_username(loader.context, profile_id)
    posts = profile.get_posts()
    profile_pic = profile.get_profile_pic_url()
    full_name = profile.full_name
    captions = []
    posts_data = []  # Initialize the list outside the loop
    for post in posts:
        if post.caption:
            captions.append(post.caption)
            posts_data.append({
                'url': post.url,
                'likes': post.likes,
                'date': post.date,
            })
    
    loader.close()
    
    if len(captions) < 1:
        return "No captions found! Are you sure this profile has posted?", "Empty", "Empty", None
    else:
        captions_or_comments = captions
        return captions_or_comments, profile_pic, full_name, posts_data


def getPublicProfileCommentsSentiments(profile_id):
    loader = instaloader.Instaloader()
    profile = Profile.from_username(loader.context, profile_id)
    profile_pic = profile.get_profile_pic_url()
    full_name = profile.full_name

    posts = profile.get_posts()

    comments = []
    posts_data = []  # Initialize the list outside the loop
    for post in posts:
        for comment in post.get_comments():
            comments.append(comment.text)
            posts_data.append({
                'url': post.url,
                'likes': post.likes,
                'date': post.date,
            })

    loader.close()

    if len(comments) < 1:
        return "No comments found for this public profile.", "Empty", "Empty"
    else:
        captions_or_comments = comments
        return captions_or_comments, profile_pic, full_name, posts_data
    
def getPrivateProfileCommentsSentiments(profile_id, login, password):
    loader = instaloader.Instaloader()

    try:
        loader.login(login, password)
    except:
        return "Failed to login!", "Empty", "Empty"

    profile = Profile.from_username(loader.context, profile_id)
    posts = profile.get_posts()
    profile_pic = profile.get_profile_pic_url()
    full_name = profile.full_name

    comments = []
    posts_data = []  # Initialize the list outside the loop
    for post in posts:
        for comment in post.get_comments():
            comments.append(comment.text)
            posts_data.append({
                'url': post.url,
                'likes': post.likes,
                'date': post.date,
            })

    loader.close()

    if len(comments) < 1:
        return "No comments found for this private profile.", "Empty", "Empty"
    else:
        captions_or_comments = comments
        return captions_or_comments, profile_pic, full_name, posts_data


def getSentiments(captions_or_comments):
    if len(captions_or_comments) > 0 and isinstance(captions_or_comments, list):
        analyser = SentimentIntensityAnalyzer()
        neutral = []
        positive = []
        negative = []
        compound = []

        for text in captions_or_comments:
            scores = analyser.polarity_scores(text)
            neutral.append(scores['neu'])
            positive.append(scores['pos'])
            negative.append(scores['neg'])
            compound.append(scores['compound'])

        neutral = np.array(neutral)
        positive = np.array(positive)
        negative = np.array(negative)
        compound = np.array(compound)

        return {
            'Neutral': round(neutral.mean(), 2) * 100.0,
            'Positive': round(positive.mean(), 2) * 100.0,
            'Negative': round(negative.mean(), 2) * 100.0,
            'Overall': round(compound.mean(), 2) * 100.0
        }
    else:
        return captions_or_comments

