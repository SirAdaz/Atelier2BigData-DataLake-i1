"""Script de calcul : Moyennes des notes et chiffre d'affaires par produit"""
import pandas as pd
import os

os.makedirs("gold", exist_ok=True)

df_sales = pd.read_parquet("silver/testFichierCSV.parquet")
df_reviews = pd.read_parquet("silver/testFichierJSON.parquet")
df_sales = df_sales.rename(columns={
    'id_prod': 'id_produit',
    'date_vente': 'date'
})
df_reviews = df_reviews.rename(columns={'id_prod': 'id_produit'})

# CALCULS SUR LES VENTES
ca_par_produit = df_sales.groupby('id_produit').agg(
    chiffre_affaires=('prix', 'sum'),
    nombre_ventes=('prix', 'count'),
    prix_moyen=('prix', 'mean'),
    prix_min=('prix', 'min'),
    prix_max=('prix', 'max')
).reset_index()

# Calculer le CA moyen par vente
ca_par_produit['ca_moyen_par_vente'] = ca_par_produit['chiffre_affaires'] / ca_par_produit['nombre_ventes']

# CALCULS SUR LES AVIS
notes_par_produit = df_reviews.groupby('id_produit').agg(
    note_moyenne=('note', 'mean'),
    nombre_avis=('note', 'count'),
    note_min=('note', 'min'),
    note_max=('note', 'max'),
    ecart_type_notes=('note', 'std')
).reset_index()

# CALCULS TEMPORELS
if 'date' in df_sales.columns:
    dates_par_produit = df_sales.groupby('id_produit').agg(
        date_premiere_vente=('date', 'min'),
        date_derniere_vente=('date', 'max')
    ).reset_index()
    
    # Calculer la durée d'activité en jours
    dates_par_produit['duree_activite_jours'] = (
        dates_par_produit['date_derniere_vente'] - 
        dates_par_produit['date_premiere_vente']
    ).dt.days + 1  # +1 pour inclure le premier jour
    
    # Calculer le nombre de ventes par jour
    ca_par_produit = ca_par_produit.merge(dates_par_produit, on='id_produit', how='left')
    ca_par_produit['ventes_par_jour'] = (
        ca_par_produit['nombre_ventes'] / ca_par_produit['duree_activite_jours']
    ).fillna(0)

# JOINTURE DES DEUX SOURCES
df_performance = ca_par_produit.merge(notes_par_produit, on='id_produit', how='outer')
df_performance = df_performance.fillna(0)

# MÉTRIQUES DÉRIVÉES
# Taux de réponse : % de clients qui ont laissé un avis
df_performance['taux_reponse'] = (
    df_performance['nombre_avis'] / df_performance['nombre_ventes'] * 100
).fillna(0)

# Score composite : combinaison CA et satisfaction (normalisé)
# Normaliser CA et notes entre 0 et 1
if df_performance['chiffre_affaires'].max() > 0:
    df_performance['ca_normalise'] = (
        df_performance['chiffre_affaires'] / df_performance['chiffre_affaires'].max()
    )
else:
    df_performance['ca_normalise'] = 0

df_performance['note_normalisee'] = df_performance['note_moyenne'] / 5.0

# Score composite (poids égal : 50% CA + 50% satisfaction)
df_performance['score_composite'] = (
    df_performance['ca_normalise'] * 0.5 + 
    df_performance['note_normalisee'] * 0.5
)

# Classement des produits
df_performance['classement_ca'] = df_performance['chiffre_affaires'].rank(ascending=False, method='dense')
df_performance['classement_note'] = df_performance['note_moyenne'].rank(ascending=False, method='dense')
df_performance['classement_composite'] = df_performance['score_composite'].rank(ascending=False, method='dense')

# STATISTIQUES GLOBALES
stats_globales = {
    'ca_total': df_performance['chiffre_affaires'].sum(),
    'ventes_total': df_performance['nombre_ventes'].sum(),
    'note_moyenne_globale': df_performance['note_moyenne'].mean(),
    'avis_total': df_performance['nombre_avis'].sum(),
    'produits_actifs': len(df_performance[df_performance['nombre_ventes'] > 0])
}

# SAUVEGARDE
# Réorganiser les colonnes pour une meilleure lisibilité
colonnes_ordre = [
    'id_produit',
    'chiffre_affaires',
    'nombre_ventes',
    'prix_moyen',
    'prix_min',
    'prix_max',
    'ca_moyen_par_vente',
    'note_moyenne',
    'nombre_avis',
    'note_min',
    'note_max',
    'ecart_type_notes',
    'taux_reponse',
    'score_composite',
    'classement_ca',
    'classement_note',
    'classement_composite'
]

# Ajouter les colonnes temporelles si elles existent
if 'date_premiere_vente' in df_performance.columns:
    colonnes_ordre.extend(['date_premiere_vente', 'date_derniere_vente', 
                          'duree_activite_jours', 'ventes_par_jour'])

# Sélectionner uniquement les colonnes qui existent
colonnes_finales = [col for col in colonnes_ordre if col in df_performance.columns]
df_performance = df_performance[colonnes_finales]

# Sauvegarder en Gold
df_performance.to_parquet("gold/produits_performance.parquet", index=False)
df_performance.to_csv("gold/produits_performance.csv", index=False)

# Sauvegarder les statistiques globales
import json
with open("gold/statistiques_globales.json", 'w', encoding='utf-8') as f:
    json.dump(stats_globales, f, indent=2, ensure_ascii=False, default=str)

# AFFICHAGE
print("=" * 80)
print("Table de performance creee dans Gold:")
print("=" * 80)
print(df_performance.to_string(index=False))
print("\n" + "=" * 80)
print("Statistiques globales:")
print("=" * 80)
for key, value in stats_globales.items():
    if isinstance(value, float):
        print(f"  {key}: {value:,.2f}")
    else:
        print(f"  {key}: {value}")
print("=" * 80)
