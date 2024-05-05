import json
import os
import threading
import time
import traceback

import yaml

from api import get_users, follow_users_v1
from web import get_spotify_tokens
from utils import split_list

disconnected = False
CHUNK_SIZE = 100
SAVE_CHECKPOINT = 100
queue = []
followed = []
processed = []

updating_tokens = False
access_token = None
sha = None

config = None
if os.path.isfile("env.yml"):
    with open('env.yml') as config_file:
        config = yaml.safe_load(config_file)
else:
    config = {"EMAIL": "email", "PASSWORD": "password"}
    with open('env.yml', 'w') as config_file:
        yaml.dump(config, config_file)
    raise Exception("The env.yml file has been generated. Please edit env.yml")

try:
    MAIL = config["EMAIL"]
    PASSWORD = config["PASSWORD"]
except:
    raise Exception("Invalid env file. Please update or regenerate it and try again.")





def update_tokens():
    global updating_tokens
    global access_token
    global sha
    if updating_tokens:
        return None
    updating_tokens = True

    access_token, sha = get_spotify_tokens(MAIL, PASSWORD)
    updating_tokens = False


def scrape_users():
    global queue
    count = 0
    while not disconnected:
        if len(followed) > 0 and not updating_tokens:
            for user_id in followed.copy():
                if disconnected:
                    break
                if user_id not in processed:
                    try:
                        mutuals = get_users(user_id, access_token)
                        print(f"[SCRAPER] Found more {len(mutuals)} users")
                        queue += mutuals
                    except:
                        traceback.print_exc()
                        update_tokens()
                    processed.append(user_id)
                    count += 1
                followed.remove(user_id)
                if count >= SAVE_CHECKPOINT:
                    save_progress()
                    count = 0
            time.sleep(10)
        else:
            time.sleep(5)


def save_progress():
    with open("progress.json", "w") as f:
        data = {"followed": followed, "processed": processed}
        json.dump(data, f, indent=4)


def load_progress():
    global processed
    global followed
    with open("progress.json", "r") as f:
        data = json.load(f)
        followed = data["followed"]
        processed = data["processed"]


def process_queue():
    global queue
    global access_token
    global followed
    while not disconnected:
        if len(queue) >= CHUNK_SIZE and not updating_tokens:
            print("[FOLLOWER] Found elements in queue! Processing...")
            split = split_list(queue, CHUNK_SIZE)
            for user_id in queue.copy():
                followed.append(user_id)
                queue.remove(user_id)
            for chunk in split:
                if disconnected:
                    break
                code, amount = follow_users_v1(chunk, access_token, sha)
                print(f"[FOLLOWER] Followed {amount} / {len(chunk)} users.")
                if code == 401:
                    update_tokens()
                time.sleep(2)
        else:
            time.sleep(10)


def start_threads():
    global disconnected
    update_tokens()
    q_proc = threading.Thread(target=process_queue)
    s_proc = threading.Thread(target=scrape_users)
    s_proc.start()
    q_proc.start()

    input("Press anything at any moment to stop execution.\n\n")
    print("Stopping execution... Please wait.")
    disconnected = True
    save_progress()


if __name__ == '__main__':
    print("What do you want to do?")
    try:
        a = int(input("1 - Start from a single username\n2 - Resume from saved files\n\n"))
        if a == 1:
            zero = input("Insert the username you want to start from: ")
            followed = [zero]
            save_progress()
        elif a == 2:
            load_progress()
    except:
        print("Invalid value inserted.")
    start_threads()

