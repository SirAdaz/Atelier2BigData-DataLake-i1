# Data Lake - Analyse Performance Ventes et Avis Clients

## Architecture Médaillon

- **Bronze** : Données brutes (CSV, JSON)
- **Silver** : Données nettoyées (Parquet)
- **Gold** : Données agrégées prêtes à l'analyse

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Méthode rapide
```bash
python main.py
```
Exécute tout le pipeline automatiquement et crée les dossiers Bronze/Silver/Gold.

### Méthode étape par étape
1. **Ingestion** : `python 1_ingestion.py`
2. **Transformation** : `python 2_transformation.py`
3. **Calcul** : `python 3_calcul.py`
4. **Visualisation** : `python 4_visualisation.py`

## Question analysée

"Est-ce que les produits les plus vendus sont aussi ceux qui ont les meilleures notes ?"
