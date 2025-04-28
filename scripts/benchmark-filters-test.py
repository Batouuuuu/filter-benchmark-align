"""Ce projet a pour but d'évaluer la pertinence de différents filtres d'OpusFilter sur un corpus 
de phrases supposément bien alignées (anglais/français).On cherche à identifier les filtres 
qui détectent le mieux les erreurs ou les mauvaises alignements sans altérer les bonnes paires."""

import yaml
import itertools
import os
from typing import Dict, List, Union, Optional
import subprocess
import gzip

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
    
    # Si la valeur est un dictionnaire
    if isinstance(value, dict):
        parts = []  # On stocke chaque morceau dans une liste
        for key, val in value.items():
            # Si la valeur associée est une liste (par exemple ["en", "fr"])
            if isinstance(val, list):
                val = "_".join(str(item) for item in val)  # On concatène tous les éléments de la liste avec "_"
            else:
                val = str(val)  # Sinon, on convertit simplement la valeur en string

            parts.append(f"{key}_{val}")  # On ajoute "clé_valeur" dans la liste parts
        
        return "_".join(parts)  # On concatène tous les morceaux ensemble avec "_"

    # Si ce n'est pas un dictionnaire (ex: juste un nombre, une string)
    else:
        return str(value)  # On le convertit directement en string




def generate_config(source_yaml : str, output_dir: str = "../data/settings_yaml/",
    filters: Optional[Dict[str, Union[List, Dict]]] = None
) -> None:
    """Génération automatique des fichiers yaml avec les filtres d'opusfilters que l'on souhaite
    
     Args:
        source_yaml (str): Chemin vers le fichier YAML de base.
        output_dir (str): Dossier de sortie pour les fichiers générés.
        filters (Dict[str, Union[List, Dict]], optional): Dictionnaire des filtres et de leurs paramètres.
    """

    if filters is None:
        filters = {} 
    
    ## charger la configuration de base (suit la structure d'un fichier yaml interprétable par opusfilter)
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


            ## cas particulier pour LengthRatioFilter
            if filter_type == "LengthRatioFilter":
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {
                        "threshold": value,
                        "name": "word",
                        "unit": "word"
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

    Args:
        original_pairs (list): Liste de tuples (source, transcription).
        filtered_dir (str): Dossier contenant les fichiers filtrés.
    """

    # Pour chaque fichier filtré généré
    for filename in os.listdir(filtered_dir):
        if filename.endswith(".filtered.gz") and filename.startswith("en_"):
            # Déduire le nom de base pour retrouver aussi le fichier français
            base_name = filename[3:-12]  # enlever "en_" et ".filtered.gz"
            fr_file = os.path.join(filtered_dir, f"fr_{base_name}.filtered.gz")
            en_file = os.path.join(filtered_dir, f"en_{base_name}.filtered.gz")

            # Lire les phrases filtrées
            with gzip.open(en_file, 'rt', encoding='utf-8') as en_f, \
                 gzip.open(fr_file, 'rt', encoding='utf-8') as fr_f:

                en_sentences = [l.strip() for l in en_f]
                fr_sentences = [l.strip() for l in fr_f]
                filtered_pairs = list(zip(en_sentences, fr_sentences))

            # Faire une évaluation simple : combien de paires originales restent ?
            original_set = set(original_pairs)
            filtered_set = set(filtered_pairs)

            surviving_pairs = filtered_set & original_set  # paires correctes conservées
            removed_pairs = original_set - filtered_set    # paires supprimées

            print(f"=== Évaluation pour filtre {base_name} ===")
            print(f"Nombre total de paires originales : {len(original_pairs)}")
            print(f"Nombre de paires après filtrage : {len(filtered_pairs)}")
            print(f"Paires originales conservées : {len(surviving_pairs)}")
            print(f"Paires originales supprimées : {len(removed_pairs)}")
            print("")

def main():

    original_pairs = load_data('../data/aligned/fr.txt', '../data/aligned/en.txt')
    generate_config(
    source_yaml="../data/settings_yaml/config.yaml",
    filters={
        "LengthRatioFilter": [0.5, 1.0],
        # "LanguageIdFilter": {"language": "en"},
        "TerminalPunctuationFilter": {"languages": ["en", "fr"]}
    }
)
    run_opusfilter_on_configs("../data/settings_yaml/")  
    evaluate_filtered_data(original_pairs, "../data/filtered/")
    
if __name__ == "__main__":
    main()






    


