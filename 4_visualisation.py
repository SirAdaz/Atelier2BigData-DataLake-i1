"""Script de visualisation : Corrélation entre ventes et notes"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger les données Gold
df = pd.read_parquet("gold/produits_performance.parquet")

# Créer le graphique
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Graphique 1 : CA vs Note moyenne
axes[0].scatter(df['note_moyenne'], df['chiffre_affaires'], s=100, alpha=0.6)
axes[0].set_xlabel('Note moyenne')
axes[0].set_ylabel('Chiffre d\'affaires (€)')
axes[0].set_title('Corrélation : CA vs Note moyenne')
axes[0].grid(True, alpha=0.3)

# Graphique 2 : Barres comparatives
x = range(len(df))
width = 0.35
axes[1].bar([i - width/2 for i in x], df['chiffre_affaires'], width, label='CA (€)', alpha=0.8)
ax2 = axes[1].twinx()
ax2.bar([i + width/2 for i in x], df['note_moyenne']*50, width, label='Note (x50)', color='orange', alpha=0.8)
axes[1].set_xlabel('Produits')
axes[1].set_ylabel('Chiffre d\'affaires (€)', color='blue')
ax2.set_ylabel('Note moyenne (x50)', color='orange')
axes[1].set_title('Performance par produit')
axes[1].set_xticks(x)
axes[1].set_xticklabels(df['id_produit'])
axes[1].legend(loc='upper left')
ax2.legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('gold/dashboard_performance.png', dpi=150, bbox_inches='tight')
print("✅ Dashboard sauvegardé : gold/dashboard_performance.png")

# Afficher la corrélation
correlation = df['note_moyenne'].corr(df['chiffre_affaires'])
print(f"\n📊 Corrélation entre Note moyenne et CA : {correlation:.3f}")
