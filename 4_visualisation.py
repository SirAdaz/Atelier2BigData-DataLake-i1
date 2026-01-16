"""Script de visualisation : Corrélation entre ventes et notes"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuration du style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 150

# Charger les données Gold
df = pd.read_parquet("gold/produits_performance.parquet")

# Créer un dashboard avec 6 graphiques
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.3)

# ========== GRAPHIQUE 1 : Corrélation avec ligne de tendance ==========
ax1 = fig.add_subplot(gs[0, :])
colors_scatter = ['#2ecc71' if note >= 4 else '#e74c3c' if note < 3 else '#f39c12' 
                  for note in df['note_moyenne']]

scatter = ax1.scatter(df['note_moyenne'], df['chiffre_affaires'], 
                     s=df['nombre_ventes']*150, c=colors_scatter, 
                     alpha=0.7, edgecolors='black', linewidth=2)

# Ajouter les labels des produits
for idx, row in df.iterrows():
    ax1.annotate(row['id_produit'], 
                (row['note_moyenne'], row['chiffre_affaires']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=11, fontweight='bold')

# Ligne de tendance
z = np.polyfit(df['note_moyenne'], df['chiffre_affaires'], 1)
p = np.poly1d(z)
ax1.plot(df['note_moyenne'], p(df['note_moyenne']), 
        "r--", alpha=0.5, linewidth=2, label='Tendance')

ax1.set_xlabel('Note moyenne (sur 5)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Chiffre d\'affaires (€)', fontsize=12, fontweight='bold')
ax1.set_title('Corrélation entre Satisfaction Client et Performance Commerciale', 
             fontsize=14, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.set_xlim([2, 5.5])

# Calculer et afficher la corrélation
correlation = df['note_moyenne'].corr(df['chiffre_affaires'])
ax1.text(0.02, 0.98, f'Corrélation : {correlation:.3f}', 
        transform=ax1.transAxes, fontsize=11,
        verticalalignment='top', bbox={'boxstyle': 'round', 
        'facecolor': 'wheat', 'alpha': 0.5})

# ========== GRAPHIQUE 2 : Barres comparatives CA par produit ==========
ax2 = fig.add_subplot(gs[1, 0])
bars = ax2.bar(df['id_produit'], df['chiffre_affaires'], 
              color=['#3498db', '#9b59b6', '#16a085'], alpha=0.8, edgecolor='black')
ax2.set_ylabel('Chiffre d\'affaires (€)', fontsize=11, fontweight='bold')
ax2.set_title('Chiffre d\'affaires par Produit', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# Ajouter les valeurs sur les barres
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}€',
            ha='center', va='bottom', fontweight='bold')

# ========== GRAPHIQUE 3 : Notes moyennes par produit ==========
ax3 = fig.add_subplot(gs[1, 1])
bars2 = ax3.bar(df['id_produit'], df['note_moyenne'], 
               color=['#e74c3c' if n < 3 else '#f39c12' if n < 4 else '#2ecc71' 
                      for n in df['note_moyenne']], 
               alpha=0.8, edgecolor='black')
ax3.set_ylabel('Note moyenne (sur 5)', fontsize=11, fontweight='bold')
ax3.set_title('Satisfaction Client par Produit', fontsize=12, fontweight='bold')
ax3.set_ylim([0, 5.5])
ax3.grid(True, alpha=0.3, axis='y')

# Ajouter les valeurs sur les barres
for bar in bars2:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}/5',
            ha='center', va='bottom', fontweight='bold')

# ========== GRAPHIQUE 4 : Comparaison multi-métriques ==========
ax4 = fig.add_subplot(gs[2, :])
x = np.arange(len(df))
width = 0.25

# Normaliser les données pour la comparaison (0-100)
ca_norm = (df['chiffre_affaires'] / df['chiffre_affaires'].max()) * 100
notes_norm = (df['note_moyenne'] / 5) * 100
ventes_norm = (df['nombre_ventes'] / df['nombre_ventes'].max()) * 100

bars1 = ax4.bar(x - width, ca_norm, width, label='CA (normalisé)', 
               color='#3498db', alpha=0.8, edgecolor='black')
bars2 = ax4.bar(x, notes_norm, width, label='Note (normalisée)', 
               color='#2ecc71', alpha=0.8, edgecolor='black')
bars3 = ax4.bar(x + width, ventes_norm, width, label='Volume ventes (normalisé)', 
               color='#e67e22', alpha=0.8, edgecolor='black')

ax4.set_ylabel('Valeur normalisée (%)', fontsize=11, fontweight='bold')
ax4.set_title('Vue d\'ensemble : Performance Multi-Métriques par Produit', 
             fontsize=12, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(df['id_produit'], fontsize=11)
ax4.legend(loc='upper right', fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_ylim([0, 110])

# Ajouter les valeurs réelles
for i, (idx, row) in enumerate(df.iterrows()):
    ax4.text(i - width, ca_norm.iloc[i] + 2, f'{row["chiffre_affaires"]:.0f}€',
            ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax4.text(i, notes_norm.iloc[i] + 2, f'{row["note_moyenne"]:.1f}/5',
            ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax4.text(i + width, ventes_norm.iloc[i] + 2, f'{int(row["nombre_ventes"])}',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

# ========== GRAPHIQUE 5 : Score Composite et Classements ==========
ax5 = fig.add_subplot(gs[3, 0])
if 'score_composite' in df.columns:
    bars5 = ax5.barh(df['id_produit'], df['score_composite'], 
                    color=['#2ecc71' if s >= 0.7 else '#f39c12' if s >= 0.5 else '#e74c3c' 
                           for s in df['score_composite']],
                    alpha=0.8, edgecolor='black')
    ax5.set_xlabel('Score Composite (0-1)', fontsize=11, fontweight='bold')
    ax5.set_title('Score Composite par Produit\n(CA + Satisfaction)', 
                 fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    ax5.set_xlim([0, 1.1])
    
    # Ajouter les valeurs et classements
    for i, (bar, (idx, row)) in enumerate(zip(bars5, df.iterrows())):
        width = bar.get_width()
        classement = int(row['classement_composite']) if 'classement_composite' in row else ''
        ax5.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                f'{width:.3f} (#{classement})',
                ha='left', va='center', fontweight='bold', fontsize=10)

# ========== GRAPHIQUE 6 : Métriques avancées ==========
ax6 = fig.add_subplot(gs[3, 1])
x = np.arange(len(df))
width = 0.2

# Préparer les données normalisées
metrics_data = {}
if 'taux_reponse' in df.columns:
    metrics_data['Taux réponse'] = df['taux_reponse'].values
if 'ventes_par_jour' in df.columns:
    metrics_data['Ventes/jour'] = (df['ventes_par_jour'] / df['ventes_par_jour'].max() * 100).values
if 'ecart_type_notes' in df.columns:
    # Normaliser l'écart-type (plus c'est bas, mieux c'est, donc on inverse)
    ecart_norm = (1 - df['ecart_type_notes'] / df['ecart_type_notes'].max()) * 100
    metrics_data['Stabilité notes'] = ecart_norm.values

colors_metrics = ['#3498db', '#9b59b6', '#16a085']
x_positions = [x - width, x, x + width][:len(metrics_data)]

for i, (label, values) in enumerate(metrics_data.items()):
    ax6.bar(x_positions[i], values, width, label=label, 
           color=colors_metrics[i], alpha=0.8, edgecolor='black')

ax6.set_ylabel('Valeur normalisée (%)', fontsize=11, fontweight='bold')
ax6.set_title('Métriques Avancées par Produit', fontsize=12, fontweight='bold')
ax6.set_xticks(x)
ax6.set_xticklabels(df['id_produit'], fontsize=11)
ax6.legend(loc='upper right', fontsize=9)
ax6.grid(True, alpha=0.3, axis='y')
ax6.set_ylim([0, 110])

# Ajouter les valeurs réelles pour le taux de réponse
if 'taux_reponse' in df.columns:
    for i, (idx, row) in enumerate(df.iterrows()):
        ax6.text(i - width, df['taux_reponse'].iloc[i] + 3, 
                f'{row["taux_reponse"]:.1f}%',
                ha='center', va='bottom', fontsize=8, fontweight='bold')

# Titre général du dashboard
fig.suptitle('Dashboard : Analyse Performance Ventes et Avis Clients (Enrichi)', 
            fontsize=16, fontweight='bold', y=0.995)

plt.savefig('gold/dashboard_performance.png', dpi=150, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
print("Dashboard sauvegarde : gold/dashboard_performance.png")

# Afficher la corrélation dans la console
correlation = df['note_moyenne'].corr(df['chiffre_affaires'])
print(f"\nCorrelation entre Note moyenne et CA : {correlation:.3f}")

# Afficher les métriques clés
print("\n" + "=" * 80)
print("METRIQUES CLES PAR PRODUIT :")
print("=" * 80)
for idx, row in df.iterrows():
    print(f"\n{row['id_produit']}:")
    print(f"  - CA: {row['chiffre_affaires']:.2f}€ ({int(row['nombre_ventes'])} ventes)")
    print(f"  - Note moyenne: {row['note_moyenne']:.1f}/5 ({int(row['nombre_avis'])} avis)")
    if 'score_composite' in row:
        print(f"  - Score composite: {row['score_composite']:.3f} (Classement: #{int(row['classement_composite'])})")
    if 'taux_reponse' in row:
        print(f"  - Taux de reponse: {row['taux_reponse']:.1f}%")
    if 'ventes_par_jour' in row:
        print(f"  - Ventes par jour: {row['ventes_par_jour']:.2f}")
    if 'ecart_type_notes' in row:
        print(f"  - Ecart-type notes: {row['ecart_type_notes']:.2f} (variabilite)")

print("\n" + "=" * 80)
print("RESUME COMPLET :")
print("=" * 80)
# Afficher seulement les colonnes principales pour la lisibilité
colonnes_afficher = ['id_produit', 'chiffre_affaires', 'nombre_ventes', 'note_moyenne', 
                     'nombre_avis', 'score_composite', 'taux_reponse']
colonnes_disponibles = [col for col in colonnes_afficher if col in df.columns]
print(df[colonnes_disponibles].to_string(index=False))
