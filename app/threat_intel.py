import time
import urllib.request

OPENPHISH_URL = "https://openphish.com/feed.txt"
_openphish_feed = set()
_last_feed_update = 0


def update_threat_feed():
    """
    1-Hour TTL Background Caching to prevent network latency.
    Designed to be run in a threadpool to prevent async loop blocking.
    """
    global _openphish_feed, _last_feed_update
    if time.time() - _last_feed_update > 3600:
        try:
            req = urllib.request.Request(OPENPHISH_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_data = response.read().decode('utf-8')
                new_feed = {line.strip() for line in raw_data.splitlines() if line.strip()}
                if new_feed:
                    _openphish_feed = new_feed
                    _last_feed_update = time.time()
        except Exception as e:
            print(f"[-] Background threat feed update failed: {e}")


def get_threat_feed():
    """Returns the globally cached OpenPhish feed dataset."""
    return _openphish_feed
