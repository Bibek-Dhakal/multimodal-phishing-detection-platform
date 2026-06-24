# Detailed Data Registry & Provenance Logs

This document acts as the Single Source of Truth (SSoT) for all dataset schemas utilized across the Tabular, NLP, and
future Vision branches.

## 1. ISCX URL Dataset (Active Core Production Tabular & ANN Data)

* **Official Data Provenance Location:
  ** [UNB Canadian Institute for Cybersecurity - URL Dataset 2016](https://www.unb.ca/cic/datasets/url-2016.html)
* **Dataset Shape Metrics:** 35,000+ data rows, 79 structural feature metrics, 1 categorical multi-class label string
  column (`All.csv`).
* **Extraction Processing:** Extracted completely offline from raw URL text strings without making slow external network
  calls.
* **Role in Project:** Used exclusively by `train_tabular.py` to train classical Machine Learning classifiers. It is *
  *never** passed to NLP transformers.
* **Complete 79-Feature Column Registry:**
  `Querylength`, `domain_token_count`, `path_token_count`, `avgdomaintokenlen`, `longdomaintokenlen`, `avgpathtokenlen`,
  `tld`, `charcompvowels`, `charcompace`, `ldl_url`, `ldl_domain`, `ldl_path`, `ldl_filename`, `ldl_getArg`, `dld_url`,
  `dld_domain`, `dld_path`, `dld_filename`, `dld_getArg`, `urlLen`, `domainlength`, `pathLength`, `subDirLen`,
  `fileNameLen`, `this.fileExtLen`, `ArgLen`, `pathurlRatio`, `ArgUrlRatio`, `argDomanRatio`, `domainUrlRatio`,
  `pathDomainRatio`, `argPathRatio`, `executable`, `isPortEighty`, `NumberofDotsinURL`, `ISIpAddressInDomainName`,
  `CharacterContinuityRate`, `LongestVariableValue`, `URL_DigitCount`, `host_DigitCount`, `Directory_DigitCount`,
  `File_name_DigitCount`, `Extension_DigitCount`, `Query_DigitCount`, `URL_Letter_Count`, `host_letter_count`,
  `Directory_LetterCount`, `Filename_LetterCount`, `Extension_LetterCount`, `Query_LetterCount`,
  `LongestPathTokenLength`, `Domain_LongestWordLength`, `Path_LongestWordLength`, `sub-Directory_LongestWordLength`,
  `Arguments_LongestWordLength`, `URL_sensitiveWord`, `URLQueries_variable`, `spcharUrl`, `delimeter_Domain`,
  `delimeter_path`, `delimeter_Count`, `NumberRate_URL`, `NumberRate_Domain`, `NumberRate_DirectoryName`,
  `NumberRate_FileName`, `NumberRate_Extension`, `NumberRate_AfterPath`, `SymbolCount_URL`, `SymbolCount_Domain`,
  `SymbolCount_Directoryname`, `SymbolCount_FileName`, `SymbolCount_Extension`, `SymbolCount_Afterpath`, `Entropy_URL`,
  `Entropy_Domain`, `Entropy_DirectoryName`, `Entropy_Filename`, `Entropy_Extension`, `Entropy_Afterpath`.

## 2. PhiUSIIL Phishing URL Dataset (Active NLP Model Core Data)

* **Official Data Provenance Location:
  ** [Kaggle - Phishing URL Websites Dataset (PhiUSIIL)](https://www.kaggle.com/datasets/kaggleprollc/phishing-url-websites-dataset-phiusiil)
* **Dataset Shape Metrics:** 235,795 data rows containing raw text URL entries mapping to a clean binary target index.
* **Role in Project:** Sourced to provide the raw text sequence layouts required for training the NLP transformer
  branch (`train_nlp.py`).
* **Explicit System Classification Target Vector:** `label` (Integer binary target vector tracking: `1` for Verified
  Phishing, `0` for Verified Benign).

## 3. UCI Phishing Websites Dataset (Historical Baseline)

* **Official Data Provenance Location:
  ** [UCI Machine Learning Repository - Dataset ID 327](https://archive.ics.uci.edu/dataset/327/phishing+websites)
* **Dataset Shape Metrics:** 11,055 data rows, 30 categorical/discrete columns, 1 binary target class mapping vector.
* **Role in Project:** Serves strictly as a historical tabular baseline comparison file. Has been deprecated from the
  active production model.

---
