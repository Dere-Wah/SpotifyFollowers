import time
import traceback
import requests
from utils import extract_user_ids, merge_lists_without_duplicates


def get_users(username: str, access_token: str):
    user_ids = None
    following_url = f"https://spclient.wg.spotify.com/user-profile-view/v3/profile/{username}/following"
    followers_url = f"https://spclient.wg.spotify.com/user-profile-view/v3/profile/{username}/followers"
    querystring = {"market": "from_token"}
    payload = ""
    headers = {
        "authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = requests.request("GET", following_url, data=payload, headers=headers, params=querystring)
    if not response.ok:
        if response.status_code != 429:
            raise Exception(f"INVALID TOKEN: {response.text} {response.status_code}")
        else:
            print("[SCRAPER] Rate limited. Waiting...")
            time.sleep(10)
    try:
        profiles = response.json()["profiles"]
        following_user_ids = extract_user_ids(profiles)
    except:
        following_user_ids = []

    response = requests.request("GET", followers_url, data=payload, headers=headers, params=querystring)

    if not response.ok:
        if response.status_code != 429:
            raise Exception(f"INVALID TOKEN: {response.text} {response.status_code}")
        else:
            print("[SCRAPER] Rate limited. Waiting...")
            time.sleep(10)
    try:
        profiles = response.json()["profiles"]
        followers_user_ids = extract_user_ids(profiles)
    except:
        followers_user_ids = []

    return merge_lists_without_duplicates(following_user_ids, followers_user_ids)


def follow_users_v1(chunk, access_token, sha):
    url = "https://api-partner.spotify.com/pathfinder/v1/query"

    payload = {
        "variables": {"usernames": chunk},
        "operationName": "followUsers",
        "extensions": {"persistedQuery": {
            "version": 1,
            "sha256Hash": sha
        }}
    }
    headers = {
        "authorization": f"Bearer {access_token}",
        "content-type": "application/json;charset=UTF-8"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.ok:
        failed = 0
        try:
            data = response.json()["data"]["followUsers"]["responses"]
            for r in data:
                if r["__typename"] == "GenericError":
                    failed += 1
            return response.status_code, len(chunk) - failed
        except:
            traceback.print_exc()
    return response.status_code, len(chunk)
