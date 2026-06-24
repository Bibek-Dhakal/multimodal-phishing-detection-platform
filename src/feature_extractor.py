import math
import re
import urllib.parse
import numpy as np

class FeatureExtractor:
    """
    Exhaustive Offline Feature Extractor targeting all 79 dimensions of the ISCX URL 2016 dataset.
    """
    def __init__(self, url: str):
        self.url = url
        self.parsed = urllib.parse.urlparse(url if url.startswith('http') else f"http://{url}")
        self.domain = self.parsed.netloc.replace('www.', '').split(':')[0].lower()
        self.path = self.parsed.path
        self.query = self.parsed.query
        
        # Isolate directory, filename, and extension
        path_parts = self.path.split('/')
        self.filename = path_parts[-1] if '.' in path_parts[-1] else ""
        self.extension = self.filename.split('.')[-1] if '.' in self.filename else ""
        self.directory = "/".join(path_parts[:-1]) if len(path_parts) > 1 else ""

    def is_whitelisted(self) -> bool:
        """Enterprise Tracking & Top-Tier Domain Whitelist to prevent False Positives."""
        trusted = [
            "google.com", "microsoft.com", "amazon.com", "apple.com", 
            "github.com", "linkedin.com", "paypal.com", "youtube.com", 
            "facebook.com", "netflix.com", "chase.com", "instagram.com"
        ]
        return any(self.domain == t or self.domain.endswith('.' + t) for t in trusted)

    # --- Helper Mathematical Functions ---
    def _entropy(self, text: str) -> float:
        if not text: return 0.0
        entropy = 0.0
        for x in set(text):
            p_x = float(text.count(x)) / len(text)
            entropy += - p_x * math.log2(p_x)
        return float(entropy)

    def _safe_div(self, n, d):
        return 0.0 if d == 0 else float(n) / float(d)

    def _ldl(self, text): return len(re.findall(r'[a-zA-Z][0-9][a-zA-Z]', text))
    def _dld(self, text): return len(re.findall(r'[0-9][a-zA-Z][0-9]', text))
    
    def _vowels(self, text): return len(re.findall(r'[aeiouAEIOU]', text))
    def _digits(self, text): return sum(c.isdigit() for c in text)
    def _letters(self, text): return sum(c.isalpha() for c in text)
    def _symbols(self, text): return len(re.findall(r'[^a-zA-Z0-9]', text))
    
    def _avg_len(self, tokens): return float(np.mean([len(t) for t in tokens])) if tokens else 0.0
    def _max_len(self, tokens): return float(np.max([len(t) for t in tokens])) if tokens else 0.0
    def _tokens(self, text, sep): return [t for t in text.split(sep) if t]

    def extract(self) -> np.ndarray:
        """Generates exactly 79 structural features mapping to the ISCX dataset schema."""
        vector = np.zeros(79, dtype=np.float32)
        if self.is_whitelisted():
            return vector
            
        f = []
        domain_toks = self._tokens(self.domain, '.')
        path_toks = self._tokens(self.path, '/')
        
        # 1-9: Tokens and Basic Lengths
        f.append(len(self.query))                                         # 1. Querylength
        f.append(len(domain_toks))                                        # 2. domain_token_count
        f.append(len(path_toks))                                          # 3. path_token_count
        f.append(self._avg_len(domain_toks))                              # 4. avgdomaintokenlen
        f.append(self._max_len(domain_toks))                              # 5. longdomaintokenlen
        f.append(self._avg_len(path_toks))                                # 6. avgpathtokenlen
        f.append(len(domain_toks[-1]) if domain_toks else 0)              # 7. tld
        f.append(self._vowels(self.url))                                  # 8. charcompvowels
        f.append(len(re.findall(r'[aceACE]', self.url)))                  # 9. charcompace

        # 10-19: LDL and DLD Transitions
        f.extend([self._ldl(x) for x in [self.url, self.domain, self.path, self.filename, self.query]]) # 10-14 ldl
        f.extend([self._dld(x) for x in [self.url, self.domain, self.path, self.filename, self.query]]) # 15-19 dld
        
        # 20-26: Component Lengths
        f.append(len(self.url))                                           # 20. urlLen
        f.append(len(self.domain))                                        # 21. domainlength
        f.append(len(self.path))                                          # 22. pathLength
        f.append(len(self.directory))                                     # 23. subDirLen
        f.append(len(self.filename))                                      # 24. fileNameLen
        f.append(len(self.extension))                                     # 25. this.fileExtLen
        f.append(len(self.query))                                         # 26. ArgLen
        
        # 27-32: Length Ratios
        f.append(self._safe_div(len(self.path), len(self.url)))           # 27. pathurlRatio
        f.append(self._safe_div(len(self.query), len(self.url)))          # 28. ArgUrlRatio
        f.append(self._safe_div(len(self.query), len(self.domain)))       # 29. argDomanRatio
        f.append(self._safe_div(len(self.domain), len(self.url)))         # 30. domainUrlRatio
        f.append(self._safe_div(len(self.path), len(self.domain)))        # 31. pathDomainRatio
        f.append(self._safe_div(len(self.query), len(self.path)))         # 32. argPathRatio
        
        # 33-38: Executables, IP, Continuity
        f.append(1 if self.extension.lower() in ['exe', 'php', 'js', 'apk'] else 0) # 33. executable
        f.append(1 if ':80' in self.parsed.netloc else 0)                 # 34. isPortEighty
        f.append(self.url.count('.'))                                     # 35. NumberofDotsinURL
        f.append(1 if re.search(r'\d+\.\d+\.\d+\.\d+', self.domain) else 0) # 36. ISIpAddressInDomainName
        f.append(max([len(x) for x in re.findall(r'[a-zA-Z]+', self.url)] + [0])) # 37. CharacterContinuityRate
        f.append(self._max_len(self._tokens(self.query, '&')))            # 38. LongestVariableValue
        
        # 39-50: Digit and Letter Counts
        parts = [self.url, self.domain, self.directory, self.filename, self.extension, self.query]
        f.extend([self._digits(x) for x in parts])                        # 39-44. DigitCounts
        f.extend([self._letters(x) for x in parts])                       # 45-50. LetterCounts
        
        # 51-55: Longest Words
        f.append(self._max_len(path_toks))                                # 51. LongestPathTokenLength
        f.append(self._max_len(re.findall(r'[a-zA-Z]+', self.domain)))    # 52. Domain_LongestWordLength
        f.append(self._max_len(re.findall(r'[a-zA-Z]+', self.path)))      # 53. Path_LongestWordLength
        f.append(self._max_len(re.findall(r'[a-zA-Z]+', self.directory))) # 54. sub-Directory_LongestWordLength
        f.append(self._max_len(re.findall(r'[a-zA-Z]+', self.query)))     # 55. Arguments_LongestWordLength
        
        # 56-61: Sensitive words and Delimiters
        sensitive = ['secure', 'account', 'webscr', 'login', 'ebay', 'banking', 'confirm']
        f.append(sum(self.url.lower().count(w) for w in sensitive))       # 56. URL_sensitiveWord
        f.append(len(self._tokens(self.query, '&')))                      # 57. URLQueries_variable
        f.append(self._symbols(self.url))                                 # 58. spcharUrl
        f.append(self._symbols(self.domain))                              # 59. delimeter_Domain
        f.append(self._symbols(self.path))                                # 60. delimeter_path
        f.append(self._symbols(self.url))                                 # 61. delimeter_Count
        
        # 62-67: Number Rates
        f.extend([self._safe_div(self._digits(x), len(x)) for x in parts])# 62-67. NumberRates
        
        # 68-73: Symbol Counts
        f.extend([self._symbols(x) for x in parts])                       # 68-73. SymbolCounts
        
        # 74-79: Entropies
        f.extend([self._entropy(x) for x in parts])                       # 74-79. Entropies

        # Ensure exact match with 79 dimension architecture
        return np.array(f, dtype=np.float32)[:79]