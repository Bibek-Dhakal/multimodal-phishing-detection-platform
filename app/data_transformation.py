import ipaddress
import json
import re
import socket
import urllib.request
from datetime import datetime
from urllib.parse import urlparse


class FeatureExtractor:
    """
    Automated Feature Extraction Engine.
    Parses raw URL strings natively via regular expressions, urllib,
    and heuristics to populate the 30 UCI structural features programmatically.
    """

    def __init__(self, url):
        self.url = url
        if not self.url.startswith('http://') and not self.url.startswith('https://'):
            self.url = 'http://' + self.url
        try:
            self.parsed_url = urlparse(self.url)
            self.domain = self.parsed_url.netloc.replace('www.', '').split(':')[0]
        except Exception:
            self.parsed_url = None
            self.domain = ""

        # NATIVE HTTPS RDAP IMPLEMENTATION (Bypasses Firewalls completely)
        self.rdap_data = None
        if self.domain:
            try:
                # We use the open redirect public bootstrap server rdap.org over port 443
                rdap_url = f"https://rdap.org/domain/{self.domain}"
                req = urllib.request.Request(rdap_url, headers={'User-Agent': 'Mozilla/5.0'})
                # Fast timeout so your dashboard doesn't lag
                with urllib.request.urlopen(req, timeout=3) as response:
                    self.rdap_data = json.loads(response.read().decode('utf-8'))
            except Exception:
                self.rdap_data = None

        # OPENPHISH LIVE THREAT FEED INTEGRATION
        self.openphish_feed = []
        try:
            # OpenPhish hosts a free, live public raw text feed of zero-day phishing links
            feed_url = "https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt"
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                # Read the clean list of active phishing URLs into memory
                raw_data = response.read().decode('utf-8')
                self.openphish_feed = [line.strip() for line in raw_data.splitlines() if line.strip()]
        except Exception:
            self.openphish_feed = []

        # Attempt to fetch HTML content for behavioral features
        self.html = None
        try:
            req = urllib.request.Request(self.url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                self.html = response.read().decode('utf-8', errors='ignore')
        except Exception:
            self.html = None

    def is_whitelisted(self):
        """
        Local High-Confidence Whitelist to prevent False Positives.
        If the domain is an exact match for highly-trusted platforms, bypass the ML model entirely.
        """
        trusted_domains = ["microsoft.com", "google.com", "amazon.com", "apple.com", "github.com", "linkedin.com"]
        for trusted in trusted_domains:
            if self.domain == trusted or self.domain.endswith('.' + trusted):
                return True
        return False

    def having_IP_Address(self):
        if not self.parsed_url: return 1
        try:
            domain = self.parsed_url.netloc.split(':')[0]
            ipaddress.ip_address(domain)
            return -1  # Phishing
        except ValueError:
            return 1  # Legitimate

    def URL_Length(self):
        if len(self.url) < 54:
            return 1
        elif 54 <= len(self.url) <= 75:
            return 0
        else:
            return -1

    def Shortining_Service(self):
        match = re.search(r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                          r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                          r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                          r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                          r'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                          r'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.com|'
                          r'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|'
                          r'tr\.im|link\.zip\.net',
                          self.url)
        return -1 if match else 1

    def having_At_Symbol(self):
        return -1 if '@' in self.url else 1

    def double_slash_redirecting(self):
        return -1 if self.url.rfind('//') > 7 else 1

    def Prefix_Suffix(self):
        if not self.parsed_url: return 1
        return -1 if '-' in self.parsed_url.netloc else 1

    def having_Sub_Domain(self):
        if not self.parsed_url: return 1
        dots = self.domain.count('.')
        if dots == 1:
            return 1
        elif dots == 2:
            return 0
        else:
            return -1

    def SSLfinal_State(self):
        if self.parsed_url and self.parsed_url.scheme == 'https': return 1
        return -1

    # --- FREE UPGRADES FOR RDAP FEATURES ---

    def Domain_registeration_length(self):
        """Feature 9: Phishing if domain expires within 1 year."""
        try:
            if self.rdap_data and 'events' in self.rdap_data:
                for event in self.rdap_data['events']:
                    if event.get('eventAction') == 'expiration':
                        date_str = event.get('eventDate')[:10]
                        exp = datetime.strptime(date_str, "%Y-%m-%d")
                        exp = exp.replace(tzinfo=None)
                        remaining_days = (exp - datetime.now()).days
                        return 1 if remaining_days > 365 else -1
        except Exception:
            return -1
        return -1  # If RDAP lookup fails or no data, highly suspicious

    def age_of_domain(self):
        """Feature 24: Phishing if domain is less than 6 months old."""
        try:
            if self.rdap_data and 'events' in self.rdap_data:
                for event in self.rdap_data['events']:
                    if event.get('eventAction') == 'registration':
                        date_str = event.get('eventDate')[:10]
                        creation = datetime.strptime(date_str, "%Y-%m-%d")
                        creation = creation.replace(tzinfo=None)
                        age_days = (datetime.now() - creation).days
                        return 1 if age_days >= 180 else -1
        except Exception:
            return -1
        return -1

    def DNSRecord(self):
        """Feature 25: Phishing if no identity resolution can be found via DNS lookup."""
        if not self.domain: return -1
        try:
            socket.gethostbyname(self.domain)
            return 1  # Record exists
        except socket.gaierror:
            return -1  # Host not found (Phishing)

    # --- FREE UPGRADES FOR TRAFFIC, GOOGLE INDEX, & EXTERNAL LINKS ---

    def web_traffic_and_pagerank(self):
        """Features 26 & 27 proxy check. 
        Checks if domain is globally recognized. If it doesn't match a tier 1 domain,
        phishing sites evaluate to -1.
        """
        top_brands = ["google", "facebook", "youtube", "microsoft", "apple", "amazon", "netflix", "linkedin", "github"]
        if any(brand in self.domain for brand in top_brands):
            return 1  # High traffic, real PageRank
        return 0  # Average or unknown (Suspicious/Phishing context)

    def Google_Index(self):
        """Feature 28: Verifies if the domain exists inside search index maps (via DuckDuckGo)."""
        if not self.domain:
            return -1
        try:
            from ddgs import DDGS
            results = list(DDGS().text(f"site:{self.domain}", max_results=3))
            if results:
                return 1
            else:
                return -1
        except ImportError:
            try:
                from duckduckgo_search import DDGS
                results = list(DDGS().text(f"site:{self.domain}", max_results=3))
                if results:
                    return 1
                else:
                    return -1
            except Exception:
                return 0
        except Exception:
            return 0

    def Links_pointing_to_page(self):
        """Feature 29: If unknown rank and unreachable HTML, assume zero backlinks (-1)."""
        if self.web_traffic_and_pagerank() == 1:
            return 1
        return -1 if self.html is None else 0

    def Statistical_report(self):
        """Feature 30: Threat Intelligence & Spam TLD check."""
        if not self.url or not self.domain:
            return 1

        # 1. Check for direct URL or domain match in the live OpenPhish ecosystem
        for malicious_url in self.openphish_feed:
            if self.url in malicious_url or self.domain in malicious_url:
                return -1  # Verified malicious inside active OpenPhish feed!

        # 2. Check Spam TLDs
        bad_tlds = ['.xyz', '.top', '.club', '.site', '.tk', '.one', '.vip', '.online', '.pw', '.cc', '.cn']
        if any(self.domain.endswith(tld) for tld in bad_tlds):
            return -1

        return 1  # Clean on current threat feed check

    # --- BEHAVIORAL & DOM METRICS ---
    def Favicon(self):
        return 1 if self.html and '<link rel="icon"' in self.html.lower() else (-1 if self.html is None else 0)

    def port(self):
        return -1 if self.parsed_url and self.parsed_url.port and self.parsed_url.port not in [80, 443] else 1

    def HTTPS_token(self):
        return -1 if self.parsed_url and 'https' in self.parsed_url.netloc else 1

    def Request_URL(self):
        return -1 if self.html is None else 1

    def URL_of_Anchor(self):
        return -1 if self.html is None else 1

    def Links_in_tags(self):
        return -1 if self.html is None else 1

    def SFH(self):
        return -1 if self.html is None else 1

    def Submitting_to_email(self):
        return -1 if self.html and 'mailto:' in self.html.lower() else (0 if self.html is None else 1)

    def Abnormal_URL(self):
        return -1 if not self.parsed_url or not self.parsed_url.hostname or self.parsed_url.hostname not in self.url else 1

    def Redirect(self):
        return 1 if self.url.count('//') > 1 else 0

    def on_mouseover(self):
        return -1 if self.html and 'window.status' in self.html.lower() else (0 if self.html is None else 1)

    def RightClick(self):
        return -1 if self.html and 'event.button==2' in self.html.lower() else (0 if self.html is None else 1)

    def popUpWidnow(self):
        return -1 if self.html and 'window.open' in self.html.lower() else (0 if self.html is None else 1)

    def Iframe(self):
        return -1 if self.html and '<iframe' in self.html.lower() else (0 if self.html is None else 1)

    def extract_features(self):
        # If the core domain matches exactly a trusted platform, bypass the model entirely
        # by returning a perfectly clean web profile vector according to the exact UCI schema.
        # Feature 19 (Redirect) is 0 for legitimate.
        if self.is_whitelisted():
            return [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        traffic_score = self.web_traffic_and_pagerank()

        features = [
            self.having_IP_Address(),  # 1
            self.URL_Length(),  # 2
            self.Shortining_Service(),  # 3
            self.having_At_Symbol(),  # 4
            self.double_slash_redirecting(),  # 5
            self.Prefix_Suffix(),  # 6
            self.having_Sub_Domain(),  # 7
            self.SSLfinal_State(),  # 8
            self.Domain_registeration_length(),  # 9 (RDAP HTTPS Engine)
            self.Favicon(),  # 10
            self.port(),  # 11
            self.HTTPS_token(),  # 12
            self.Request_URL(),  # 13
            self.URL_of_Anchor(),  # 14
            self.Links_in_tags(),  # 15
            self.SFH(),  # 16
            self.Submitting_to_email(),  # 17
            self.Abnormal_URL(),  # 18
            self.Redirect(),  # 19
            self.on_mouseover(),  # 20
            self.RightClick(),  # 21
            self.popUpWidnow(),  # 22
            self.Iframe(),  # 23
            self.age_of_domain(),  # 24 (RDAP HTTPS Engine)
            self.DNSRecord(),  # 25 (Socket DNS)
            traffic_score,  # 26 (Heuristic Traffic)
            traffic_score,  # 27 (Heuristic PageRank)
            self.Google_Index(),  # 28 (Google Direct Query)
            self.Links_pointing_to_page(),  # 29 (HTML/Traffic Heuristic)
            self.Statistical_report()  # 30 (OpenPhish + Spam TLD Checking)
        ]
        return features
