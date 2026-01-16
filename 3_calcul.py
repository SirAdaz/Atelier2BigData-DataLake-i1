"""Script de calcul : Moyennes des notes et chiffre d'affaires par produit"""
import pandas as pd
import os

os.makedirs("gold", exist_ok=True)

# Charger les données nettoyées
df_sales = pd.read_parquet("silver/sales_cleaned.parquet")
df_reviews = pd.read_parquet("silver/reviews_cleaned.parquet")

# Calculer le CA total par produit
ca_par_produit = df_sales.groupby('id_produit').agg(
    chiffre_affaires=('prix', 'sum'),
    nombre_ventes=('prix', 'count')
).reset_index()

# Calculer la moyenne des notes par produit
notes_par_produit = df_reviews.groupby('id_produit').agg(
    note_moyenne=('note', 'mean'),
    nombre_avis=('note', 'count')
).reset_index()

# Joindre les deux sources
df_performance = ca_par_produit.merge(notes_par_produit, on='id_produit', how='outer')
df_performance = df_performance.fillna(0)

# Sauvegarder en Gold
df_performance.to_parquet("gold/produits_performance.parquet", index=False)
df_performance.to_csv("gold/produits_performance.csv", index=False)

print("✅ Table de performance créée dans Gold:")
print(df_performance.to_string())
