#!/usr/bin/env python3
# Copyright (c) 2026 Nardo. AGPL-3.0 — see LICENSE
"""Draft or post through X API v2 (OAuth 1.0a User Context).

Usage:
    python post_tweet.py "Draft text" --dry-run
    python post_tweet.py "Approved text" --confirm-post
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import tweepy
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parents[3] / "mcp"))
from lib import tweet_log

# Load env from DOTENV_PATH if set; otherwise rely on env vars already in environment
_dotenv_path = os.environ.get("DOTENV_PATH", "")
if _dotenv_path:
    load_dotenv(_dotenv_path)


def get_client() -> tweepy.Client:
    """Create authenticated X API v2 client."""
    return tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )


def get_api_v1() -> tweepy.API:
    """Create v1.1 API for media uploads (v2 doesn't support media upload)."""
    auth = tweepy.OAuth1UserHandler(
        os.environ["X_API_KEY"],
        os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"],
        os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    return tweepy.API(auth)


def upload_media(image_path: str) -> str:
    """Upload media and return media_id."""
    api = get_api_v1()
    media = api.media_upload(image_path)
    return media.media_id_string


def post_tweet(
    text: str,
    reply_to: Optional[str] = None,
    media_path: Optional[str] = None,
) -> dict:
    """Post a tweet. Returns tweet data."""
    client = get_client()

    kwargs: dict = {}

    if reply_to:
        kwargs["in_reply_to_tweet_id"] = reply_to

    if media_path:
        media_id = upload_media(media_path)
        kwargs["media_ids"] = [int(media_id)]

    response = client.create_tweet(text=text, **kwargs)

    tweet_id = response.data["id"]  # type: ignore[index]
    username = os.environ.get("SOCIAL_USERNAME", "me")
    url = f"https://x.com/{username}/status/{tweet_id}"

    tweet_log(tweet_id=str(tweet_id), text=text, url=url)

    return {
        "id": tweet_id,
        "text": text,
        "url": url,
    }


def send_notification(tweet_data: dict) -> None:
    """Send optional notification to a user-provided webhook."""
    import requests

    webhook_url = os.getenv("CONTENT_NOTIFY_WEBHOOK_URL", "")
    if not webhook_url:
        return

    requests.post(
        webhook_url,
        json={
            "event": "social_posted",
            "url": tweet_data["url"],
            "text": tweet_data["text"][:200],
        },
        timeout=10,
    )


def post_thread(
    tweets: list[str],
    media_path: Optional[str] = None,
) -> list[dict]:
    """Post a thread of tweets. First tweet gets optional media. Returns list of tweet data."""
    results = []
    reply_to = None

    for i, text in enumerate(tweets):
        media = media_path if i == 0 else None
        result = post_tweet(text, reply_to=reply_to, media_path=media)
        results.append(result)
        reply_to = str(result["id"])
        print(f"  [{i+1}/{len(tweets)}] {result['url']}")

        # Small delay between posts to avoid rate limiting
        if i < len(tweets) - 1:
            import time
            time.sleep(2)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Draft or post via X API")
    parser.add_argument("text", nargs="?", help="Tweet text (single tweet mode)")
    parser.add_argument("--reply-to", help="Tweet ID to reply to")
    parser.add_argument("--media", help="Path to image to attach")
    parser.add_argument("--dry-run", action="store_true", help="Print planned post without publishing")
    parser.add_argument("--confirm-post", action="store_true", help="Actually publish after separate approval")
    parser.add_argument("--no-alert", action="store_true", help="Skip notification webhook")
    parser.add_argument("--thread", help="Path to thread file (one tweet per section, separated by ---)")
    args = parser.parse_args()

    if not args.confirm_post:
        args.dry_run = True

    if args.thread:
        # Thread mode: read file, split on ---, post chain
        thread_path = Path(args.thread)
        if not thread_path.exists():
            print(f"Thread file not found: {args.thread}")
            sys.exit(1)
        content = thread_path.read_text().strip()
        tweets = [t.strip() for t in content.split("---") if t.strip()]
        if not tweets:
            print("No tweets found in thread file")
            sys.exit(1)

        if args.dry_run:
            print(json.dumps({"dry_run": True, "thread": tweets, "media": args.media}, indent=2))
            return

        print(f"Posting thread ({len(tweets)} tweets)...")
        results = post_thread(tweets, media_path=args.media)
        print(json.dumps(results, indent=2))

        if not args.no_alert:
            send_notification(results[0])
            print("notification sent.")
    else:
        if not args.text:
            parser.error("text is required in single tweet mode")

        if args.dry_run:
            print(json.dumps({
                "dry_run": True,
                "text": args.text,
                "reply_to": args.reply_to,
                "media": args.media,
            }, indent=2))
            return

        result = post_tweet(args.text, args.reply_to, args.media)
        print(json.dumps(result, indent=2))

        if not args.no_alert:
            send_notification(result)
            print("notification sent.")


if __name__ == "__main__":
    main()
