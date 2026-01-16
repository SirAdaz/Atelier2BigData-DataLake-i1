"""Script de transformation : Nettoie les données et convertit en Parquet"""
import pandas as pd
import os
from pathlib import Path

os.makedirs("silver", exist_ok=True)

# =========================
# TRAITEMENT DES VENTES
# =========================

# Lister tous les fichiers CSV de ventes dans bronze
sales_files = Path("bronze").glob("sales_data_*.csv")

dfs_sales = []

for file in sales_files:
    df = pd.read_csv(file, header=None, names=["product_id", "price", "date", "client"])
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Nettoyage par fichier
    df = df.drop_duplicates()
    df["date_vente"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        format="%m-%d-%Y"
    )
    df = df.rename(columns={
        "product_id": "id_prod",
        "price": "prix",
        "client": "id_client"
    })
    df = df.dropna(subset=["id_prod", "prix", "date_vente"])
    df = df[["id_prod", "prix", "date_vente", "id_client"]]

    dfs_sales.append(df)

# Fusion de tous les fichiers
if len(dfs_sales) == 0:
    raise ValueError("Aucun fichier CSV de ventes trouve dans bronze/")
df_sales_final = pd.concat(dfs_sales, ignore_index=True)

# Suppression des doublons globaux
df_sales_final = df_sales_final.drop_duplicates()

# Sauvegarde en Parquet
df_sales_final.to_parquet("silver/testFichierCSV.parquet", index=False)

print(f"✅ {len(dfs_sales)} fichiers CSV fusionnés")
print(f"📦 {len(df_sales_final)} lignes finales")


review_files = Path("bronze").glob("review_data_*.json")

dfs_reviews = []

for file in review_files:
    df = pd.read_json(file)
    df = df.drop_duplicates()
    df = df.rename(columns={
        "product_id": "id_prod",
        "grade": "note"
    })
    df = df.dropna(subset=["id_prod", "note"])
    df = df[["id_prod", "note"]]
    dfs_reviews.append(df)

if len(dfs_reviews) == 0:
    raise ValueError("Aucun fichier JSON d'avis trouve dans bronze/")
df_reviews_final = pd.concat(dfs_reviews, ignore_index=True)
df_reviews_final = df_reviews_final.drop_duplicates()

df_reviews_final.to_parquet("silver/testFichierJSON.parquet", index=False)

print(f"✅ {len(dfs_reviews)} fichiers JSON fusionnés")