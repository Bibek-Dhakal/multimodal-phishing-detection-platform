# Dataset Information

## UCI Phishing Websites Dataset

The current implementation of the platform utilizes the *
*[UCI Phishing Websites Dataset](https://archive.ics.uci.edu/dataset/327/phishing+websites)**, a widely accepted
benchmark in cybersecurity research, developed by Rami Mohammad, Fadi Thabtah, and Lee McCluskey.

### Overview

* **Source**: [Official UCI Repository](https://archive.ics.uci.edu/dataset/327/phishing+websites)
* **Instances**: 11,055 records
* **Predictive Features**: 30 extracted features
* **Target Variable**: 1 (Result: Phishing or Legitimate)

### Feature Categories

The 30 features are broken down into distinct structural and behavioral categories:

1. **Address Bar Features**:
   Analyzes suspicious patterns directly within the URL string.
   *(e.g., having_IP_Address, URL_Length, having_At_Symbol, Prefix_Suffix, having_Sub_Domain)*

2. **Domain-Based Features**:
   Examines domain registration and external security properties.
   *(e.g., SSLfinal_State, Domain_registeration_length, HTTPS_token, age_of_domain, DNSRecord)*

3. **HTML and JavaScript Features**:
   Evaluates webpage structure and client-side code behaviors.
   *(e.g., Request_URL, Links_in_tags, Submitting_to_email, RightClick, Iframe)*

4. **External Context Features**:
   Incorporates information from ranking databases and statistical reports.
   *(e.g., Redirect, web_traffic, Page_Rank, Google_Index)*

### Original Target Variable Mapping

* `-1` : Phishing Website
* `1` : Legitimate Website

*(Note: During preprocessing, this is mapped to `1` (Phishing) and `0` (Legitimate) to align with standard deep learning
binary cross-entropy expectations).*
