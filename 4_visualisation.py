"""Script de visualisation : Corrélation entre Volume de ventes et Note moyenne"""
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

# Filtrer les produits avec au moins un avis pour la corrélation
df_with_reviews = df[df['nombre_avis'] > 0].copy()

# Calculer le nombre de produits
nb_produits = len(df)
nb_produits_with_reviews = len(df_with_reviews)

# Adapter la taille de la figure selon le nombre de produits
if nb_produits <= 10:
    fig_width, fig_height = 14, 10
    font_size_labels = 11
    font_size_ticks = 10
elif nb_produits <= 30:
    fig_width, fig_height = 16, 12
    font_size_labels = 10
    font_size_ticks = 8
else:
    fig_width, fig_height = 18, 14
    font_size_labels = 9
    font_size_ticks = 7

# Créer un dashboard avec 4 graphiques (1 grand en haut, 2 en bas)
fig = plt.figure(figsize=(fig_width, fig_height))
gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

# ========== GRAPHIQUE 1 : Corrélation Volume de ventes vs Note moyenne ==========
ax1 = fig.add_subplot(gs[0, :])

# Utiliser seulement les produits avec avis pour la corrélation
df_plot = df_with_reviews if len(df_with_reviews) > 0 else df

# Vérifier s'il y a de la variance dans les ventes
ventes_unique = df_plot['nombre_ventes'].nunique()
if ventes_unique == 1:
    # Si tous les produits ont le même nombre de ventes, utiliser le CA à la place
    x_data = df_plot['chiffre_affaires']
    x_label = 'Chiffre d\'affaires (€)'
    x_title = 'Corrélation entre Chiffre d\'Affaires et Note Moyenne'
else:
    x_data = df_plot['nombre_ventes']
    x_label = 'Volume de ventes (nombre)'
    x_title = 'Corrélation entre Volume de Ventes et Note Moyenne'

# Couleurs selon la note
colors_scatter = ['#2ecc71' if note >= 4 else '#e74c3c' if note < 3 else '#f39c12' 
                  for note in df_plot['note_moyenne']]

# Taille des points selon le CA
if df_plot['chiffre_affaires'].max() > 0:
    sizes = df_plot['chiffre_affaires'] / df_plot['chiffre_affaires'].max() * 300 + 50
else:
    sizes = 100

scatter = ax1.scatter(x_data, df_plot['note_moyenne'], 
                     s=sizes, c=colors_scatter, 
                     alpha=0.7, edgecolors='black', linewidth=1.5)

# Ligne de tendance seulement si on a assez de points et de variance
if len(df_plot) > 2 and x_data.nunique() > 1:
    try:
        z = np.polyfit(x_data, df_plot['note_moyenne'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(x_data.min(), x_data.max(), 100)
        ax1.plot(x_trend, p(x_trend), "r--", alpha=0.6, linewidth=2, label='Tendance')
    except (ValueError, np.linalg.LinAlgError):
        pass

# Ajouter les labels des produits (seulement si pas trop nombreux)
if nb_produits_with_reviews <= 20 and nb_produits_with_reviews > 0:
    for idx, row in df_plot.iterrows():
        ax1.annotate(str(row['id_produit']), 
                    (x_data.loc[idx], row['note_moyenne']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=max(8, font_size_labels - 1), fontweight='bold', alpha=0.8)
elif nb_produits_with_reviews > 20:
    # Pour beaucoup de produits, afficher seulement les top/bottom
    top_ventes = df_plot.nlargest(3, 'nombre_ventes' if ventes_unique > 1 else 'chiffre_affaires')
    top_notes = df_plot.nlargest(3, 'note_moyenne')
    to_annotate = pd.concat([top_ventes, top_notes]).drop_duplicates()
    for idx, row in to_annotate.iterrows():
        ax1.annotate(str(row['id_produit']), 
                    (x_data.loc[idx], row['note_moyenne']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=font_size_labels, fontweight='bold', alpha=0.8)

ax1.set_xlabel(x_label, fontsize=font_size_labels, fontweight='bold')
ax1.set_ylabel('Note moyenne (sur 5)', fontsize=font_size_labels, fontweight='bold')
ax1.set_title(x_title, 
             fontsize=font_size_labels+2, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3)
if len(df_plot) > 2 and x_data.nunique() > 1:
    ax1.legend()
ax1.set_ylim([0, 5.5])

# Calculer et afficher la corrélation
if len(df_plot) > 1 and x_data.nunique() > 1:
    correlation = x_data.corr(df_plot['note_moyenne'])
    if not np.isnan(correlation):
        ax1.text(0.02, 0.98, f'Corrélation : {correlation:.3f}\nProduits avec avis : {nb_produits_with_reviews}/{nb_produits}', 
                transform=ax1.transAxes, fontsize=font_size_labels,
                verticalalignment='top', bbox={'boxstyle': 'round', 
                'facecolor': 'wheat', 'alpha': 0.7})
    else:
        ax1.text(0.02, 0.98, f'Corrélation : N/A\nProduits avec avis : {nb_produits_with_reviews}/{nb_produits}', 
                transform=ax1.transAxes, fontsize=font_size_labels,
                verticalalignment='top', bbox={'boxstyle': 'round', 
                'facecolor': 'wheat', 'alpha': 0.7})
else:
    ax1.text(0.02, 0.98, f'Pas assez de données pour calculer la corrélation\nProduits avec avis : {nb_produits_with_reviews}/{nb_produits}', 
            transform=ax1.transAxes, fontsize=font_size_labels,
            verticalalignment='top', bbox={'boxstyle': 'round', 
            'facecolor': 'lightcoral', 'alpha': 0.7})

# ========== GRAPHIQUE 2 : Chiffre d'affaires par produit ==========
ax2 = fig.add_subplot(gs[1, 0])

# Si trop de produits, afficher seulement les top 20 par CA
if nb_produits > 20:
    df_ca_sorted = df.nlargest(20, 'chiffre_affaires').sort_values('chiffre_affaires', ascending=True)
    title_suffix = " (Top 20)"
else:
    df_ca_sorted = df.sort_values('chiffre_affaires', ascending=True)
    title_suffix = ""

colors_ca = sns.color_palette("Blues", len(df_ca_sorted))
bars = ax2.barh(df_ca_sorted['id_produit'].astype(str), df_ca_sorted['chiffre_affaires'], 
              color=colors_ca, alpha=0.8, edgecolor='black', linewidth=0.5)

ax2.set_xlabel('Chiffre d\'affaires (€)', fontsize=font_size_labels, fontweight='bold')
ax2.set_title(f'Chiffre d\'Affaires par Produit{title_suffix}', fontsize=font_size_labels+1, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

if nb_produits > 15:
    ax2.tick_params(axis='y', labelsize=font_size_ticks)
else:
    ax2.tick_params(axis='y', labelsize=font_size_labels)

# Ajouter les valeurs sur les barres
if len(df_ca_sorted) <= 15:
    for i, (bar, (idx, row)) in enumerate(zip(bars, df_ca_sorted.iterrows())):
        width = bar.get_width()
        ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                f'{width:.0f}€',
                ha='left', va='center', fontweight='bold', fontsize=font_size_ticks)

# ========== GRAPHIQUE 3 : Note moyenne par produit ==========
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
ax3.set_title(f'Note Moyenne par Produit{title_suffix}', fontsize=font_size_labels+1, fontweight='bold')
ax3.set_xlim([0, 5.5])
ax3.grid(True, alpha=0.3, axis='x')

if nb_produits > 15:
    ax3.tick_params(axis='y', labelsize=font_size_ticks)
else:
    ax3.tick_params(axis='y', labelsize=font_size_labels)

# Ajouter les valeurs sur les barres
if len(df_notes_sorted) <= 15:
    for i, (bar, (idx, row)) in enumerate(zip(bars2, df_notes_sorted.iterrows())):
        width = bar.get_width()
        ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}/5',
                ha='left', va='center', fontweight='bold', fontsize=font_size_ticks)

# ========== GRAPHIQUE 4 : Comparaison directe Volume vs Note (barres groupées) ==========
ax4 = fig.add_subplot(gs[0, 1])
ax4.remove()  # On garde seulement 3 graphiques : 1 grand en haut, 2 en bas

# Titre général du dashboard
fig.suptitle('Dashboard : Corrélation Volume de Ventes et Note Moyenne', 
            fontsize=font_size_labels+3, fontweight='bold', y=0.98)

plt.savefig('gold/dashboard_performance.png', dpi=150, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
print("Dashboard sauvegarde : gold/dashboard_performance.png")

# Afficher la corrélation dans la console
if len(df_with_reviews) > 1:
    if df_with_reviews['nombre_ventes'].nunique() > 1:
        correlation = df_with_reviews['nombre_ventes'].corr(df_with_reviews['note_moyenne'])
    else:
        # Si tous ont le même nombre de ventes, utiliser le CA
        correlation = df_with_reviews['chiffre_affaires'].corr(df_with_reviews['note_moyenne'])
    
    if not np.isnan(correlation):
        print(f"\nCorrelation entre Volume de ventes et Note moyenne : {correlation:.3f}")
        
        # Interprétation
        if correlation > 0.5:
            interpretation = "Correlation positive forte : Les produits les plus vendus ont tendance a avoir de meilleures notes"
        elif correlation > 0.2:
            interpretation = "Correlation positive moderee : Leger lien entre volume de ventes et satisfaction"
        elif correlation > -0.2:
            interpretation = "Pas de correlation significative : Pas de lien evident entre volume et satisfaction"
        else:
            interpretation = "Correlation negative : Les produits les plus vendus ont tendance a avoir de moins bonnes notes"
        
        print(f"Interpretation : {interpretation}")
    else:
        print("\nImpossible de calculer la correlation (pas assez de variance dans les donnees)")
else:
    print(f"\nPas assez de produits avec avis pour calculer la correlation ({nb_produits_with_reviews} produits avec avis sur {nb_produits} total)")

print("\n" + "=" * 80)
print("RESUME :")
print("=" * 80)
colonnes_afficher = ['id_produit', 'nombre_ventes', 'note_moyenne']
colonnes_disponibles = [col for col in colonnes_afficher if col in df.columns]
print(df[colonnes_disponibles].to_string(index=False))
