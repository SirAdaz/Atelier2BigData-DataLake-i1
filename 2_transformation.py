"""Script de transformation : Nettoie les données et convertit en Parquet"""
import pandas as pd
import os
from pathlib import Path

os.makedirs("silver", exist_ok=True)

# =========================
# TRAITEMENT DES VENTES
# =========================

# Lister tous les fichiers CSV de ventes
sales_files = Path(".").glob("sales_data_*.csv")

dfs_sales = []

for file in sales_files:
    df = pd.read_csv(file)

    # Nettoyage par fichier
    df = df.drop_duplicates()

    df["date_vente"] = pd.to_datetime(
        df["date_vente"],
        errors="coerce",
        dayfirst=True
    )

    df = df.dropna(subset=["id_prod", "prix", "date_vente"])

    df = df[["id_prod", "prix", "date_vente", "id_client"]]

    dfs_sales.append(df)

# Fusion de tous les fichiers
df_sales_final = pd.concat(dfs_sales, ignore_index=True)

# Suppression des doublons globaux
df_sales_final = df_sales_final.drop_duplicates()

# Sauvegarde en Parquet
df_sales_final.to_parquet("silver/testFichierCSV.parquet", index=False)

print(f"✅ {len(dfs_sales)} fichiers CSV fusionnés")
print(f"📦 {len(df_sales_final)} lignes finales")


review_files = Path(".").glob("review_data_*.json")

dfs_reviews = []

for file in review_files:
    df = pd.read_json(file)
    df = df.drop_duplicates()
    df = df.dropna(subset=["id_prod", "note"])
    df = df[["id_prod", "note"]]
    dfs_reviews.append(df)

df_reviews_final = pd.concat(dfs_reviews, ignore_index=True)
df_reviews_final = df_reviews_final.drop_duplicates()

df_reviews_final.to_parquet("silver/testFichierJSON.parquet", index=False)

print(f"✅ {len(dfs_reviews)} fichiers JSON fusionnés")