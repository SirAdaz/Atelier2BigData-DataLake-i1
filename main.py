"""Script principal : Exécute tout le pipeline Data Lake"""
import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("🚀 DÉMARRAGE DU PIPELINE DATA LAKE")
    print("=" * 60)
    
    # Créer les dossiers de l'architecture Médaillon
    print("\n📁 Création de l'architecture...")
    os.makedirs("bronze", exist_ok=True)
    os.makedirs("silver", exist_ok=True)
    os.makedirs("gold", exist_ok=True)
    print("   ✅ Bronze, Silver, Gold créés")
    
    # Étape 1 : Ingestion
    print("\n" + "=" * 60)
    print("ÉTAPE 1 : INGESTION → Bronze")
    print("=" * 60)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("ingestion", "1_ingestion.py")
        ingestion = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ingestion)
    except Exception as e:
        print(f"❌ Erreur lors de l'ingestion : {e}")
        sys.exit(1)
    
    # Étape 2 : Transformation
    print("\n" + "=" * 60)
    print("ÉTAPE 2 : TRANSFORMATION → Silver")
    print("=" * 60)
    try:
        spec = importlib.util.spec_from_file_location("transformation", "2_transformation.py")
        transformation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(transformation)
    except Exception as e:
        print(f"❌ Erreur lors de la transformation : {e}")
        sys.exit(1)
    
    # Étape 3 : Calcul
    print("\n" + "=" * 60)
    print("ÉTAPE 3 : CALCUL → Gold")
    print("=" * 60)
    try:
        spec = importlib.util.spec_from_file_location("calcul", "3_calcul.py")
        calcul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(calcul)
    except Exception as e:
        print(f"❌ Erreur lors du calcul : {e}")
        sys.exit(1)
    
    # Étape 4 : Visualisation
    print("\n" + "=" * 60)
    print("ÉTAPE 4 : VISUALISATION")
    print("=" * 60)
    try:
        spec = importlib.util.spec_from_file_location("visualisation", "4_visualisation.py")
        visualisation = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(visualisation)
    except Exception as e:
        print(f"❌ Erreur lors de la visualisation : {e}")
        sys.exit(1)
    
    # Résumé final
    print("\n" + "=" * 60)
    print("✅ PIPELINE TERMINÉ AVEC SUCCÈS !")
    print("=" * 60)
    print("\n📊 Fichiers générés :")
    
    # Lister les fichiers créés
    bronze_files = list(Path("bronze").glob("*"))
    silver_files = list(Path("silver").glob("*"))
    gold_files = list(Path("gold").glob("*"))
    
    print(f"\n   Bronze ({len(bronze_files)} fichiers) :")
    for f in bronze_files:
        print(f"      - {f.name}")
    
    print(f"\n   Silver ({len(silver_files)} fichiers) :")
    for f in silver_files:
        print(f"      - {f.name}")
    
    print(f"\n   Gold ({len(gold_files)} fichiers) :")
    for f in gold_files:
        print(f"      - {f.name}")
    
    print("\n🎯 Question analysée :")
    print("   'Est-ce que les produits les plus vendus sont aussi")
    print("    ceux qui ont les meilleures notes ?'")
    print("\n   → Consultez gold/dashboard_performance.png pour la réponse !")

if __name__ == "__main__":
    main()
