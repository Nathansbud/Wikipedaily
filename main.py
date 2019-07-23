#!/usr/local/bin/python3.7

import praw
import requests
import datetime
import os
import json

local_deploy = False

if local_deploy: #Very very bad practice, I just don't know how to do environment variables
    with open("creds.json") as jf:
        creds = json.load(jf)

        reddit = praw.Reddit(client_id = creds['client_id'],
                     client_secret = creds['client_secret'],
                     user_agent = creds['user_agent'],
                     username = creds['username'],
                     password = creds['password'])
else:
    reddit = praw.Reddit(
        client_id = os.environ['client_id'],
        client_secret = os.environ['client_secret'],
        user_agent = os.environ['user_agent'],
        username = os.environ['username'],
        password = os.environ['password']
    )


month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def get_page():
    passed = False
    page_id = ""
    page_title = ""

    while not passed:
        page = requests.get("https://en.wikipedia.org/w/api.php?format=json&action=query&generator=random&grnnamespace=0").json()
        article = page['query']['pages']

        page_title = ""
        page_id = ""

        for key in article:
            with open(os.path.join(os.path.dirname(__file__), "read_articles.txt"), "a+", True) as ra:
                lines = [line for line in ra]
                if key in lines:
                    break
                else:
                    page_id = key
                    page_title = article[key]['title']
                    ra.write(page_id + "\n")
                    passed = True

    return {"id": page_id, "title": page_title}

def make_daily_post():
    post_page = get_page()
    pd = datetime.datetime.now()
    subreddit = reddit.subreddit("Wikipedaily")

    subreddit.submit(title=month_names[pd.month - 1] + " " + str(pd.day) + ", " + str(pd.year) + ": " + post_page["title"] ,
                                           url="https://en.wikipedia.org/?curid="+post_page['id'])
    for post in subreddit.new(limit=1):
        submission = reddit.submission(post)

        submission.mod.flair(text="Daily Wikipedia")
        submission.mod.distinguish(how='yes', sticky=True)
        submission.reply(post_page["title"] + " is the Daily Wikipedia Thread for " + month_names[pd.month - 1] + " " + str(pd.day) + ", " + str(pd.year) + "! Leave a comment below, and start some discussion!")

        for comment in submission.comments:
            comment = reddit.comment(comment)
            comment.mod.distinguish(how="yes", sticky=True)
        print("Posted: " + post_page["title"])


if __name__ == "__main__":
    make_daily_post()
    pass