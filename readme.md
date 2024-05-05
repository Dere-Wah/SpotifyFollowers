# SpotifyFollowers

A python demonstration on how to scrape spotify user-ids and follow them.

## Installation

- Clone this repository and navigate into it ``git clone https://github.com/Dere-Wah/SpotifyFollowers``
- Install the requirements ``pip install -r requirements.txt``
- Open env.yml and fill in your spotify e-mail and password. I recommend not using your main spotify account for this demonstration.
- Run main.py ``python3 main.py``

## Overview

The bot operates through two main components: a scraper and a follower. These components function concurrently on separate threads.

### Login Procedure

To interact with the Spotify API, the bot initiates a login process to obtain necessary tokens. Utilizing Selenium, specifically the undetected version, it accesses a designated account via email and password. Following successful login, the bot extracts the required token from the HTML source of the page.

While the access token enables user identification, additional information is necessary to execute follow commands on Spotify. Specifically, the bot requires the persistentQuery sha256Hash for the followUser command. This code appears to be distinct from the login account and persists across different accounts and sessions. However, it remains uncertain whether this code is machine-dependent or a hardcoded value within Spotify's backend. Notably, distinct codes correspond to various operations, and mismatched codes result in erroneous responses or backend errors.

As sharing the sha256Hash code raises concerns, I devised a method for its automatic retrieval during login. Selenium initiates a mock follow request to a random account, and the bot captures the network traffic to extract the sha256Hash from the request.

Subsequently, the access token and the retrieved sha256Hash are utilized together to send follow requests to multiple users concurrently.

### Scraping Procedure

The scraping process is straightforward. Upon the initial run, the user must input a "patient-zero" account ID. The bot then identifies mutual connections of this account—essentially, accounts that follow or are followed by it. Each of these mutual connections is considered a valid account to follow and is queued for processing by the Follower component (explained below).

Once the Follower component completes the follow action on these accounts, the newly followed accounts are returned to the Scraper. The Scraper then proceeds to identify mutual connections of these newly followed accounts, eliminating duplicates, and repeats the process.

It's advisable to select accounts with a substantial number of mutual connections to start the scraping process effectively.

### Follower Procedure

The Follower component awaits new account IDs identified by the Scraper for follow actions. Upon receiving these IDs, it partitions them into manageable chunks (currently set at 100 but adjustable) and dispatches follow requests using the access token and sha256Hash.

Note: Spotify recently implemented a hardcoded rate limit on follow actions, which appears to restrict the number of accounts that can be followed within a specific timeframe. This limit is seemingly enforced regardless of whether this bot or the official WebAPI is used and approximates to around 100 follows per hour.

### Disclaimer

This project serves demonstration and educational purposes only. I disclaim any responsibility for the utilization of this script beyond these intentions.