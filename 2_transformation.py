"""Script de transformation : Nettoie les données et convertit en Parquet"""
import pandas as pd
import os
from pathlib import Path

os.makedirs("silver", exist_ok=True)

# Lire les données brutes de Bronze
sales_files = list(Path("bronze").glob("sales_data_*.csv"))
reviews_files = list(Path("bronze").glob("reviews_data_*.json"))

# Traiter les ventes
dfs_sales = []
for file in sales_files:
    df = pd.read_csv(file)
    dfs_sales.append(df)

if dfs_sales:
    df_sales = pd.concat(dfs_sales, ignore_index=True)
    # Nettoyage : supprimer doublons, uniformiser dates
    df_sales = df_sales.drop_duplicates()
    df_sales['date'] = pd.to_datetime(df_sales['date'])
    df_sales = df_sales.dropna()
    # Sauvegarder en Parquet
    df_sales.to_parquet("silver/sales_cleaned.parquet", index=False)
    print(f"✅ Ventes nettoyées : {len(df_sales)} lignes → silver/sales_cleaned.parquet")

# Traiter les avis
dfs_reviews = []
for file in reviews_files:
    df = pd.read_json(file)
    dfs_reviews.append(df)

if dfs_reviews:
    df_reviews = pd.concat(dfs_reviews, ignore_index=True)
    # Nettoyage : supprimer doublons, valeurs nulles
    df_reviews = df_reviews.drop_duplicates()
    df_reviews = df_reviews.dropna()
    # Sauvegarder en Parquet
    df_reviews.to_parquet("silver/reviews_cleaned.parquet", index=False)
    print(f"✅ Avis nettoyés : {len(df_reviews)} lignes → silver/reviews_cleaned.parquet")
