import difflib
import math


def calculate_entropy(text):
    """Calculates the mathematical randomness (Shannon Entropy) of the string."""
    if not text: return 0
    entropy = 0
    for x in set(text):
        p_x = float(text.count(x)) / len(text)
        entropy += - p_x * math.log2(p_x)
    return entropy


def is_whitelisted(domain):
    """Local High-Confidence Apex Whitelist to prevent False Positives."""
    trusted = ["microsoft.com", "google.com", "amazon.com", "apple.com", "github.com", "linkedin.com", "paypal.com"]
    return any(domain == t or domain.endswith('.' + t) for t in trusted)


def check_brand_spoofing(domain):
    """
    Advanced Typosquatting Heuristic:
    Uses Substring checks + Fuzzy String Matching (Levenshtein distance).
    If a domain is highly similar to a trusted brand (>80% ratio) or contains the 
    brand string natively, but is not the exact official apex domain, it is highly malicious.
    """
    trusted_brands = {
        "microsoft": "microsoft.com",
        "google": "google.com",
        "amazon": "amazon.com",
        "apple": "apple.com",
        "github": "github.com",
        "linkedin": "linkedin.com",
        "paypal": "paypal.com",
        "chase": "chase.com",
        "netflix": "netflix.com",
        "facebook": "facebook.com",
        "instagram": "instagram.com"
    }
    if not domain:
        return 0.0

    domain_lower = domain.lower()
    # Isolate the core string without TLD for fuzzy matching
    domain_name_only = domain_lower.split('.')[0] if '.' in domain_lower else domain_lower

    for brand, true_domain in trusted_brands.items():
        # Condition 1: Substring match (e.g. secure-paypal-login.com)
        substring_match = brand in domain_lower

        # Condition 2: Fuzzy match for misspellings (e.g. paypdals.com)
        similarity = difflib.SequenceMatcher(None, brand, domain_name_only).ratio()
        fuzzy_match = similarity >= 0.80

        if substring_match or fuzzy_match:
            if domain_lower != true_domain and not domain_lower.endswith('.' + true_domain):
                return 1.5  # Massive logit penalty for brand spoofing/typosquatting
    return 0.0


def calibrate_risk(base_risk, penalty):
    """
    Scales structural penalties into a calibrated logistic function layer
    to bound the consensus space consistently between 0 and 1.
    """
    eps = 1e-5
    clipped = max(eps, min(1 - eps, base_risk))
    # Convert to log-odds (logit)
    logit = math.log(clipped / (1 - clipped))

    # Scale the continuous penalty up so it impacts the logit gradient 
    scaled_penalty = penalty * 5.0
    new_logit = logit + scaled_penalty

    # Convert back to probability bounds via sigmoid
    calibrated_prob = 1 / (1 + math.exp(-new_logit))
    return calibrated_prob
