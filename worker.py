import asyncio
import requests
import time
import os
from twscrape import API

CRM_ENDPOINT = "https://dhworpjdtpfnevqigwbe.supabase.co/functions/v1/ingest-tweet"

ACCOUNTS_TO_MONITOR = [
    "alexhormozi"
]

api = API()

async def init_account():
    acc = os.getenv("TWITTER_ACCOUNT")

    if acc:
        email, password, username = acc.split(":")
        await api.pool.add_account(username, password, email)
        await api.pool.login_all()

async def run():
    for username in ACCOUNTS_TO_MONITOR:
        threads = {}

        async for tweet in api.user_tweets(username, limit=20):

            if tweet.retweeted_tweet:
                continue

            cid = tweet.conversation_id

            if cid not in threads:
                threads[cid] = []

            threads[cid].append(tweet)

        for cid, thread in threads.items():
            thread = sorted(thread, key=lambda t: t.id)

            main = thread[0]
            rest = thread[1:]

            thread_content = "\n\n".join([t.full_text for t in rest]) if rest else None

            payload = {
                "username": main.user.username,
                "post_id": str(main.id),
                "content": main.full_text,
                "url": f"https://x.com/{main.user.username}/status/{main.id}",
                "media_urls": [],
                "thread_content": thread_content
            }

            print(payload)

            try:
                requests.post(CRM_ENDPOINT, json=payload)
            except Exception as e:
                print("Erreur:", e)

async def main():
    await init_account()
    while True:
        await run()
        time.sleep(600)

asyncio.run(main())
