"""Script de visualisation : Corrélation entre ventes et notes"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Configuration du style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 150

# Charger les données Gold
df = pd.read_parquet("gold/produits_performance.parquet")

# Calculer le nombre de produits
nb_produits = len(df)

# Adapter la taille de la figure selon le nombre de produits
if nb_produits <= 10:
    fig_width, fig_height = 18, 12
    font_size_labels = 11
    font_size_ticks = 10
elif nb_produits <= 30:
    fig_width, fig_height = 20, 14
    font_size_labels = 10
    font_size_ticks = 8
else:
    fig_width, fig_height = 24, 16
    font_size_labels = 9
    font_size_ticks = 7

# Créer un dashboard avec 6 graphiques
fig = plt.figure(figsize=(fig_width, fig_height))
gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.3)

# Générer une palette de couleurs dynamique
def get_color_palette(n):
    """Génère n couleurs distinctes"""
    if n <= 10:
        colors = sns.color_palette("husl", n)
    else:
        colors = sns.color_palette("Set3", n)
    return colors

# ========== GRAPHIQUE 1 : Corrélation avec ligne de tendance ==========
ax1 = fig.add_subplot(gs[0, :])
colors_scatter = ['#2ecc71' if note >= 4 else '#e74c3c' if note < 3 else '#f39c12' 
                  for note in df['note_moyenne']]

scatter = ax1.scatter(df['note_moyenne'], df['chiffre_affaires'], 
                     s=df['nombre_ventes']*150, c=colors_scatter, 
                     alpha=0.7, edgecolors='black', linewidth=2)

# Ajouter les labels des produits (seulement si pas trop nombreux)
if nb_produits <= 20:
    for idx, row in df.iterrows():
        ax1.annotate(str(row['id_produit']), 
                    (row['note_moyenne'], row['chiffre_affaires']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=max(8, font_size_labels - 1), fontweight='bold', alpha=0.8)
else:
    # Pour beaucoup de produits, afficher seulement les top/bottom
    top_ca = df.nlargest(3, 'chiffre_affaires')
    top_notes = df.nlargest(3, 'note_moyenne')
    to_annotate = pd.concat([top_ca, top_notes]).drop_duplicates()
    for idx, row in to_annotate.iterrows():
        ax1.annotate(str(row['id_produit']), 
                    (row['note_moyenne'], row['chiffre_affaires']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=font_size_labels, fontweight='bold', alpha=0.8)

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

# Si trop de produits, afficher seulement les top 20
if nb_produits > 20:
    df_ca_sorted = df.nlargest(20, 'chiffre_affaires').sort_values('chiffre_affaires', ascending=True)
    title_suffix = " (Top 20)"
else:
    df_ca_sorted = df.sort_values('chiffre_affaires', ascending=True)
    title_suffix = ""

colors_ca = get_color_palette(len(df_ca_sorted))
bars = ax2.barh(df_ca_sorted['id_produit'].astype(str), df_ca_sorted['chiffre_affaires'], 
              color=colors_ca, alpha=0.8, edgecolor='black', linewidth=0.5)

ax2.set_xlabel('Chiffre d\'affaires (€)', fontsize=font_size_labels, fontweight='bold')
ax2.set_title(f'Chiffre d\'affaires par Produit{title_suffix}', fontsize=font_size_labels+1, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# Rotation des labels si nécessaire
if nb_produits > 15:
    ax2.tick_params(axis='y', labelsize=font_size_ticks)
else:
    ax2.tick_params(axis='y', labelsize=font_size_labels)

# Ajouter les valeurs sur les barres (seulement si pas trop nombreux)
if len(df_ca_sorted) <= 15:
    for i, (bar, (idx, row)) in enumerate(zip(bars, df_ca_sorted.iterrows())):
        width = bar.get_width()
        ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                f'{width:.0f}€',
                ha='left', va='center', fontweight='bold', fontsize=font_size_ticks)

# ========== GRAPHIQUE 3 : Notes moyennes par produit ==========
ax3 = fig.add_subplot(gs[1, 1])

# Si trop de produits, afficher seulement les top 20 par note
if nb_produits > 20:
    df_notes_sorted = df.nlargest(20, 'note_moyenne').sort_values('note_moyenne', ascending=True)
    title_suffix = " (Top 20)"
else:
    df_notes_sorted = df.sort_values('note_moyenne', ascending=True)
    title_suffix = ""

# Couleurs selon la note
colors_notes = ['#e74c3c' if n < 3 else '#f39c12' if n < 4 else '#2ecc71' 
                for n in df_notes_sorted['note_moyenne']]

bars2 = ax3.barh(df_notes_sorted['id_produit'].astype(str), df_notes_sorted['note_moyenne'], 
               color=colors_notes, alpha=0.8, edgecolor='black', linewidth=0.5)

ax3.set_xlabel('Note moyenne (sur 5)', fontsize=font_size_labels, fontweight='bold')
ax3.set_title(f'Satisfaction Client par Produit{title_suffix}', fontsize=font_size_labels+1, fontweight='bold')
ax3.set_xlim([0, 5.5])
ax3.grid(True, alpha=0.3, axis='x')

# Rotation des labels si nécessaire
if nb_produits > 15:
    ax3.tick_params(axis='y', labelsize=font_size_ticks)
else:
    ax3.tick_params(axis='y', labelsize=font_size_labels)

# Ajouter les valeurs sur les barres (seulement si pas trop nombreux)
if len(df_notes_sorted) <= 15:
    for i, (bar, (idx, row)) in enumerate(zip(bars2, df_notes_sorted.iterrows())):
        width = bar.get_width()
        ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}/5',
                ha='left', va='center', fontweight='bold', fontsize=font_size_ticks)

# ========== GRAPHIQUE 4 : Comparaison multi-métriques ==========
ax4 = fig.add_subplot(gs[2, :])

# Limiter à 30 produits max pour la lisibilité
if nb_produits > 30:
    df_top = df.nlargest(30, 'chiffre_affaires')
    title_suffix = " (Top 30 par CA)"
else:
    df_top = df
    title_suffix = ""

x = np.arange(len(df_top))
width = 0.25

# Normaliser les données pour la comparaison (0-100)
ca_norm = (df_top['chiffre_affaires'] / df_top['chiffre_affaires'].max()) * 100
notes_norm = (df_top['note_moyenne'] / 5) * 100
ventes_norm = (df_top['nombre_ventes'] / df_top['nombre_ventes'].max()) * 100

bars1 = ax4.bar(x - width, ca_norm, width, label='CA (normalisé)', 
               color='#3498db', alpha=0.8, edgecolor='black', linewidth=0.5)
bars2 = ax4.bar(x, notes_norm, width, label='Note (normalisée)', 
               color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=0.5)
bars3 = ax4.bar(x + width, ventes_norm, width, label='Volume ventes (normalisé)', 
               color='#e67e22', alpha=0.8, edgecolor='black', linewidth=0.5)

ax4.set_ylabel('Valeur normalisée (%)', fontsize=font_size_labels, fontweight='bold')
ax4.set_title(f'Vue d\'ensemble : Performance Multi-Métriques par Produit{title_suffix}', 
             fontsize=font_size_labels+1, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(df_top['id_produit'].astype(str), fontsize=font_size_ticks, rotation=45 if len(df_top) > 15 else 0, ha='right' if len(df_top) > 15 else 'center')
ax4.legend(loc='upper right', fontsize=font_size_labels-1)
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_ylim([0, 110])

# Ajouter les valeurs réelles seulement si pas trop nombreux
if len(df_top) <= 20:
    for i, (idx, row) in enumerate(df_top.iterrows()):
        ax4.text(i - width, ca_norm.iloc[i] + 2, f'{row["chiffre_affaires"]:.0f}€',
                ha='center', va='bottom', fontsize=font_size_ticks-1, fontweight='bold', rotation=90 if len(df_top) > 15 else 0)
        ax4.text(i, notes_norm.iloc[i] + 2, f'{row["note_moyenne"]:.1f}/5',
                ha='center', va='bottom', fontsize=font_size_ticks-1, fontweight='bold', rotation=90 if len(df_top) > 15 else 0)
        ax4.text(i + width, ventes_norm.iloc[i] + 2, f'{int(row["nombre_ventes"])}',
                ha='center', va='bottom', fontsize=font_size_ticks-1, fontweight='bold', rotation=90 if len(df_top) > 15 else 0)

# ========== GRAPHIQUE 5 : Score Composite et Classements ==========
ax5 = fig.add_subplot(gs[3, 0])
if 'score_composite' in df.columns:
    # Limiter à 25 produits pour la lisibilité
    if nb_produits > 25:
        df_score = df.nlargest(25, 'score_composite').sort_values('score_composite', ascending=True)
        title_suffix = " (Top 25)"
    else:
        df_score = df.sort_values('score_composite', ascending=True)
        title_suffix = ""
    
    colors_score = ['#2ecc71' if s >= 0.7 else '#f39c12' if s >= 0.5 else '#e74c3c' 
                    for s in df_score['score_composite']]
    
    bars5 = ax5.barh(df_score['id_produit'].astype(str), df_score['score_composite'], 
                    color=colors_score, alpha=0.8, edgecolor='black', linewidth=0.5)
    ax5.set_xlabel('Score Composite (0-1)', fontsize=font_size_labels, fontweight='bold')
    ax5.set_title(f'Score Composite par Produit{title_suffix}\n(CA + Satisfaction)', 
                 fontsize=font_size_labels+1, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='x')
    ax5.set_xlim([0, 1.1])
    
    if nb_produits > 15:
        ax5.tick_params(axis='y', labelsize=font_size_ticks)
    else:
        ax5.tick_params(axis='y', labelsize=font_size_labels)
    
    # Ajouter les valeurs et classements seulement si pas trop nombreux
    if len(df_score) <= 20:
        for i, (bar, (idx, row)) in enumerate(zip(bars5, df_score.iterrows())):
            width = bar.get_width()
            classement = int(row['classement_composite']) if 'classement_composite' in row else ''
            ax5.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                    f'{width:.3f} (#{classement})',
                    ha='left', va='center', fontweight='bold', fontsize=font_size_ticks)

# ========== GRAPHIQUE 6 : Métriques avancées ==========
ax6 = fig.add_subplot(gs[3, 1])

# Limiter à 25 produits pour la lisibilité
if nb_produits > 25:
    df_metrics = df.nlargest(25, 'chiffre_affaires')
    title_suffix = " (Top 25)"
else:
    df_metrics = df
    title_suffix = ""

x = np.arange(len(df_metrics))
width = 0.2

# Préparer les données normalisées
metrics_data = {}
if 'taux_reponse' in df_metrics.columns:
    metrics_data['Taux réponse'] = df_metrics['taux_reponse'].values
if 'ventes_par_jour' in df_metrics.columns:
    max_ventes = df_metrics['ventes_par_jour'].max()
    if max_ventes > 0:
        metrics_data['Ventes/jour'] = (df_metrics['ventes_par_jour'] / max_ventes * 100).values
if 'ecart_type_notes' in df_metrics.columns:
    max_ecart = df_metrics['ecart_type_notes'].max()
    if max_ecart > 0:
        # Normaliser l'écart-type (plus c'est bas, mieux c'est, donc on inverse)
        ecart_norm = (1 - df_metrics['ecart_type_notes'] / max_ecart) * 100
        metrics_data['Stabilité notes'] = ecart_norm.values

colors_metrics = ['#3498db', '#9b59b6', '#16a085']
x_positions = [x - width, x, x + width][:len(metrics_data)]

for i, (label, values) in enumerate(metrics_data.items()):
    ax6.bar(x_positions[i], values, width, label=label, 
           color=colors_metrics[i], alpha=0.8, edgecolor='black', linewidth=0.5)

ax6.set_ylabel('Valeur normalisée (%)', fontsize=font_size_labels, fontweight='bold')
ax6.set_title(f'Métriques Avancées par Produit{title_suffix}', fontsize=font_size_labels+1, fontweight='bold')
ax6.set_xticks(x)
ax6.set_xticklabels(df_metrics['id_produit'].astype(str), fontsize=font_size_ticks, 
                   rotation=45 if len(df_metrics) > 15 else 0, ha='right' if len(df_metrics) > 15 else 'center')
ax6.legend(loc='upper right', fontsize=font_size_labels-1)
ax6.grid(True, alpha=0.3, axis='y')
ax6.set_ylim([0, 110])

# Ajouter les valeurs réelles pour le taux de réponse seulement si pas trop nombreux
if 'taux_reponse' in df_metrics.columns and len(df_metrics) <= 20:
    for i, (idx, row) in enumerate(df_metrics.iterrows()):
        ax6.text(i - width, df_metrics['taux_reponse'].iloc[i] + 3, 
                f'{row["taux_reponse"]:.1f}%',
                ha='center', va='bottom', fontsize=font_size_ticks-1, fontweight='bold',
                rotation=90 if len(df_metrics) > 15 else 0)

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
