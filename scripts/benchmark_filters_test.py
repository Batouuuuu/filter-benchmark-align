"""Ce projet a pour but d'évaluer la pertinence de différents filtres d'OpusFilter sur un corpus 
de phrases supposément bien alignées (anglais/français).On cherche à identifier les filtres 
qui détectent le mieux les erreurs ou les mauvaises alignements sans altérer les bonnes paires."""

import yaml
import itertools
import os
from typing import Dict, List, Union, Optional
import subprocess
import gzip
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score




def find_project_root(marker="data"):
    """Remonte l'arborescence jusqu'à trouver un dossier racine identifiable (ex: 'data/')"""
    path = os.path.abspath(__file__)
    while True:
        path = os.path.dirname(path)
        if os.path.isdir(os.path.join(path, marker)):
            return path
        if path == "/":
            raise RuntimeError(f"Impossible de trouver le dossier racine contenant '{marker}'")




def load_data(source_file: str, transcription_file: str) -> list[tuple[str, str]]:
    """on charge nos données"""

    with open(source_file, 'r') as source_f, open(transcription_file, 'r') as transcription_f :
        source_sentences = [l.strip() for l in source_f]
        transcription_sentences = [l.strip() for l in transcription_f]
    original_pairs = list(zip(source_sentences, transcription_sentences))

    return original_pairs


def stringify_value(value):
    """
    Transforme un seuil ou un dictionnaire en une string utilisable dans un nom de fichier.

    Exemples :
    - 0.5 -> "0.5"
    - {"language": "en"} -> "language_en"
    - {"languages": ["en", "fr"]} -> "languages_en_fr"
    """
    
    ## si la valeur est un dictionnaire
    if isinstance(value, dict):
        parts = []  
        for key, val in value.items():
            if isinstance(val, list):
                val = "_".join(str(item) for item in val)   
            else:
                val = str(val)  

            parts.append(f"{key}_{val}")  
        
        return "_".join(parts)  

    else:
        return str(value)  




def generate_config( source_yaml: str,output_dir: str = "./data/settings_yaml/",
                    filtered_dir: str = "./data/filtered",
                    filters: Optional[Dict[str, Union[List, Dict]]] = None) -> None:
    
    """Génération automatique des fichiers yaml avec les filtres d'opusfilters que l'on souhaite
    
     Args:
        source_yaml (str): Chemin vers le fichier YAML de base.
        output_dir (str): Dossier de sortie pour les fichiers générés.
        filters (Dict[str, Union[List, Dict]], optional): Dictionnaire des filtres et de leurs paramètres.
    """

    if filters is None:
        filters = {} 
    
    ## charge base configuration following a yaml syntax
    with open(source_yaml, 'r') as f:
        base_config = yaml.safe_load(f)

    filter_items = [(name, values if isinstance(values, list) else [values])
                    for name, values in filters.items()]
    
    all_combinations = itertools.product(*[item[1] for item in filter_items])

    os.makedirs(output_dir, exist_ok=True)

    for combination in all_combinations:
        new_config = base_config.copy()
        new_config['steps'][0]['parameters']['filters'] = []

        filter_name_parts = []

        for idx, (filter_type, _) in enumerate(filter_items):
            value = combination[idx]
            filter_name_parts.append(f"{filter_type}_{stringify_value(value)}")


            ## Lengths filters
            if filter_type == "LengthRatioFilter":
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {
                        "threshold": value,
                        "name": "word",
                        "unit": "word"
                    }
                })

            elif filter_type == "LengthFilter":
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {
                        "min_length": value,
                        "unit": "word",
                    }
                })

            ##Language ID filter

            elif filter_type == "LanguageIDFilter":
                 new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {
                        "languages": ["es", "fr"],       
                            "id_method": "fasttext", ## fasttext library required       
                            "thresholds": [0.7, 0.7], 
                            "fasttext_model_path": "../models/lid.176.ftz"  
                      
                    }
                })

            elif filter_type == "CharacterScoreFilter":
               new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {
                        "scripts": ["Latin", "Latin"],
                        "thresholds": [value, value]
                    }
               })
               
               
            elif filter_type == "WordAlignFilter":
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {
                        "src_threshold": value,
                        "tgt_threshold": value,
                        "src_tokenizer": ["moses", "fr"], 
                        "tgt_tokenizer": ["moses", "es"], 
                        "model": 3  ## eflomal
                    }
                })

               

            else:
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: value if isinstance(value, dict) else {"threshold": value}
                })

        
        filter_str = "_".join(filter_name_parts)

        new_config['steps'][0]['parameters']['outputs'] = [
            f"en_{filter_str}.filtered.gz",
            f"fr_{filter_str}.filtered.gz"
        ]

        output_path = os.path.join(output_dir, f"config_{filter_str}.yaml")
        new_config['common'] = {'output_directory': os.path.abspath(filtered_dir)}

        with open(output_path, "w", encoding="utf-8") as f_out:
            yaml.safe_dump(new_config, f_out, default_flow_style=False)

        print(f"Fichier généré : {output_path}")




def run_opusfilter_on_configs(config_dir: str):
    """Exécute opusfilter filter pour tous les fichiers de configuration dans config_dir."""
    for filename in os.listdir(config_dir):
        if filename.startswith("config_") and filename.endswith(".yaml"):
            config_path = os.path.join(config_dir, filename)
            print(f"Running opusfilter on {config_path}...")
            
            try:
                subprocess.run(["opusfilter", config_path], check=True)

            except subprocess.CalledProcessError as e:
                print(f"Erreur en exécutant OpusFilter sur {config_path} : {e}")
    
    print("Tous les fichiers ont été traités (même s'il y a eu des erreurs).")




def evaluate_filtered_data(original_pairs: list[tuple[str, str]], filtered_dir: str):
    """
    Évalue les performances des filtres en comparant les données originales aux données filtrées.
    Calcule les métriques classiques : VP, FP, FN, VN, précision, rappel, F1.
    """
    resultats = []

    for filename in os.listdir(filtered_dir):
        if filename.endswith(".filtered.gz") and filename.startswith("en_"):
            base_name = filename[3:-12]
            fr_file = os.path.join(filtered_dir, f"fr_{base_name}.filtered.gz")
            en_file = os.path.join(filtered_dir, f"en_{base_name}.filtered.gz")

            with gzip.open(en_file, 'rt', encoding='utf-8') as en_f, \
                 gzip.open(fr_file, 'rt', encoding='utf-8') as fr_f:
                en_sentences = [l.strip() for l in en_f]
                fr_sentences = [l.strip() for l in fr_f]
                filtered_pairs = list(zip(fr_sentences, en_sentences))

           
            filtered_set = set(filtered_pairs)

            y_true = []  
            y_pred = [] 

            for pair in original_pairs:
                y_true.append(1)  
                y_pred.append(1 if pair in filtered_set else 0)

            VP = sum((yt == 1 and yp == 1) for yt, yp in zip(y_true, y_pred))
            FP = sum((yt == 0 and yp == 1) for yt, yp in zip(y_true, y_pred)) 
            FN = sum((yt == 1 and yp == 0) for yt, yp in zip(y_true, y_pred))
            VN = sum((yt == 0 and yp == 0) for yt, yp in zip(y_true, y_pred)) 

            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)

            resultats.append({
                "Combinaison de filtres": base_name,
                "VP": VP,
                "FP": FP,
                "FN": FN,
                "VN": VN,
                "Précision": round(precision, 3),
                "Rappel": round(recall, 3),
                "F1-score": round(f1, 3),
            })
            log_rejected_pairs(original_pairs, filtered_pairs, base_name, filtered_dir)

    
    df = pd.DataFrame(resultats)
    print(df.to_markdown(index=False))



def log_rejected_pairs(original_pairs, filtered_pairs, base_name, output_dir, max_display=10):
    """
    Affiche et enregistre les paires rejetées par les filtres OpusFilter.
    """

    filtered_set = set(filtered_pairs)
    rejected_pairs = [pair for pair in original_pairs if pair not in filtered_set]

    print(f"\n--- Paires rejetées pour la config : {base_name} ---")
    for i, (src, tgt) in enumerate(rejected_pairs[:max_display]):
        print(f"[{i+1}] FR: {src} | ES: {tgt}")
    print(f"Total rejetées : {len(rejected_pairs)}")

   
    rejected_file = os.path.join(output_dir, f"../rejected/spanish/rejected_{base_name}.tsv")
    with open(rejected_file, "w", encoding="utf-8") as rej_f:
        for src, tgt in rejected_pairs:
            rej_f.write(f"{src}\t{tgt}\n")



def main():
    PROJECT_ROOT = find_project_root()
    es_path = os.path.join(PROJECT_ROOT, "data", "aligned", "spanish", "es.txt")
    fr_path = os.path.join(PROJECT_ROOT, "data", "aligned", "spanish", "fr.txt")
    source_yaml = os.path.join(PROJECT_ROOT, "data", "settings_yaml", "config.yaml")
    settings_dir = os.path.join(PROJECT_ROOT, "data", "settings_yaml")
    filtered_dir = os.path.join(PROJECT_ROOT, "data", "filtered")


    original_pairs = load_data(es_path, fr_path)
    filters_to_test = {
        # "LengthRatioFilter": [1.8, 2.0],
        "CharacterScoreFilter": [0.9, 1.2, 1.4],
        "TerminalPunctuationFilter": {"languages": ["es", "fr"]},
        # "LengthFilter": [2],
        # "LanguageIdFilter": ["es", "fr"]
    }

    generate_config(source_yaml=source_yaml,output_dir=settings_dir,filtered_dir=filtered_dir,filters=filters_to_test)
    run_opusfilter_on_configs(settings_dir)
    evaluate_filtered_data(original_pairs, filtered_dir)



if __name__ == "__main__":
    main()
