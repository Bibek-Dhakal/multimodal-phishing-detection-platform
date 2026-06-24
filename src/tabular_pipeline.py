import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split


def prepare_iscx_dataset(csv_path: str):
    """
    Safely loads, imputes, and standardizes the ISCX URL 2016 tabular dataset.
    Returns identically padded X and standardized binary y shapes.
    """
    df = pd.read_csv(csv_path, low_memory=False)

    target_col = 'URL_Type_obf_Type'

    if target_col in df.columns:
        # Convert ISCX multi-class (spam, malware, defacement, phishing) to Binary vs Benign
        df['target'] = df[target_col].apply(lambda x: 0 if str(x).strip().lower() == 'benign' else 1)
        X = df.drop(columns=[target_col, 'target'], errors='ignore')
        y = df['target']
    else:
        # Fallback processing logic
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1].apply(lambda x: 0 if str(x).strip().lower() == 'benign' else 1)

    # Filter to purely structural numerics and restrict/pad matrix boundary to exactly 79 features
    X = X.select_dtypes(include=[np.number])

    # Catch and replace Infinity values which crash sklearn's SimpleImputer
    X = X.replace([np.inf, -np.inf], np.nan)

    if X.shape[1] > 79:
        X = X.iloc[:, :79]
    elif X.shape[1] < 79:
        for i in range(X.shape[1], 79):
            X[f'pad_feature_{i}'] = 0.0

    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    return train_test_split(X_imputed, y, test_size=0.2, random_state=42)
