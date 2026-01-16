"""Script d'ingestion : Simule l'arrivée de nouveaux fichiers dans Bronze"""
import os
import json
import csv
from datetime import datetime

# Créer le dossier Bronze s'il n'existe pas
os.makedirs("bronze", exist_ok=True)

# Générer des données de ventes (CSV)
sales_data = [
    {"id_produit": "P001", "prix": 299.99, "date": "2025-01-15", "client": "C001"},
    {"id_produit": "P002", "prix": 149.50, "date": "2025-01-15", "client": "C002"},
    {"id_produit": "P001", "prix": 299.99, "date": "2025-01-16", "client": "C003"},
    {"id_produit": "P003", "prix": 89.99, "date": "2025-01-16", "client": "C001"},
    {"id_produit": "P002", "prix": 149.50, "date": "2025-01-17", "client": "C004"},
    {"id_produit": "P001", "prix": 299.99, "date": "2025-01-17", "client": "C005"},
    {"id_produit": "P003", "prix": 89.99, "date": "2025-01-18", "client": "C002"},
    {"id_produit": "P002", "prix": 149.50, "date": "2025-01-18", "client": "C006"},
]

# Générer des avis clients (JSON)
reviews_data = [
    {"id_produit": "P001", "note": 5, "commentaire": "Excellent produit!"},
    {"id_produit": "P001", "note": 4, "commentaire": "Très bien"},
    {"id_produit": "P002", "note": 3, "commentaire": "Correct"},
    {"id_produit": "P002", "note": 2, "commentaire": "Déçu"},
    {"id_produit": "P003", "note": 5, "commentaire": "Parfait"},
    {"id_produit": "P003", "note": 4, "commentaire": "Bon rapport qualité-prix"},
]

# Sauvegarder en CSV
filename_sales = f"bronze/sales_data_{datetime.now().strftime('%Y_%m_%d')}.csv"
with open(filename_sales, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["id_produit", "prix", "date", "client"])
    writer.writeheader()
    writer.writerows(sales_data)

# Sauvegarder en JSON
filename_reviews = f"bronze/reviews_data_{datetime.now().strftime('%Y_%m_%d')}.json"
with open(filename_reviews, 'w', encoding='utf-8') as f:
    json.dump(reviews_data, f, ensure_ascii=False, indent=2)

print(f"✅ Données ingérées dans Bronze:")
print(f"   - {filename_sales}")
print(f"   - {filename_reviews}")
