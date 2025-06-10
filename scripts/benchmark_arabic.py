import yaml
import itertools
import os
import subprocess
import gzip
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

def load_data(source_file: str, target_file: str) -> list[tuple[str, str]]:
    with open(source_file, 'r', encoding='utf-8') as src_f, open(target_file, 'r', encoding='utf-8') as tgt_f:
        src_lines = [l.strip() for l in src_f]
        tgt_lines = [l.strip() for l in tgt_f]
    return list(zip(src_lines, tgt_lines))

def stringify_value(value):
    if isinstance(value, dict):
        return "_".join(f"{k}_{'_'.join(map(str, v)) if isinstance(v, list) else v}" for k, v in value.items())
    return str(value)

def generate_config(source_yaml: str, output_dir: str, filters, src_lang: str, tgt_lang: str, src_file_path: str, tgt_file_path: str):
    with open(source_yaml, 'r', encoding='utf-8') as f:
        base_config = yaml.safe_load(f)

    filter_items = [(name, values if isinstance(values, list) else [values])
                    for name, values in filters.items()]

    all_combinations = itertools.product(*[item[1] for item in filter_items])
    os.makedirs(output_dir, exist_ok=True)

    for combination in all_combinations:
        new_config = base_config.copy()
        new_config['steps'][0]['parameters']['inputs'] = [src_file_path, tgt_file_path]
        new_config['steps'][0]['parameters']['filters'] = []
        filter_name_parts = []

        for idx, (filter_type, _) in enumerate(filter_items):
            value = combination[idx]
            filter_name_parts.append(f"{filter_type}_{stringify_value(value)}")

            if filter_type == "LengthRatioFilter":
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {"threshold": value, "name": "word", "unit": "word"}
                })
            elif filter_type == "LengthFilter":
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {"min_length": value, "unit": "word"}
                })
            elif filter_type == "LanguageIDFilter" and value is not None:
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {
                        "languages": [src_lang, tgt_lang],
                        "id_method": "fasttext",
                        "thresholds": [0.7, 0.7],
                        "fasttext_model_path": "../models/lid.176.ftz"
                    }
                })
            elif filter_type == "CharacterScoreFilter":
                scripts = ["Latin", "Arabic"] if src_lang == "fr" else ["Arabic", "Arabic"]
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {
                        "scripts": scripts,
                        "thresholds": [value, value]
                    }
                })
            elif filter_type == "TerminalPunctuationFilter":
                new_config['steps'][0]['parameters']['filters'].append({
                    filter_type: {"languages": [src_lang, tgt_lang]}
                })

        filter_str = "_".join(filter_name_parts)
        new_config['steps'][0]['parameters']['outputs'] = [
            f"{src_lang}_{filter_str}.filtered.gz",
            f"{tgt_lang}_{filter_str}.filtered.gz"
        ]
        output_path = os.path.join(output_dir, f"config_{filter_str}.yaml")
        with open(output_path, "w", encoding='utf-8') as f_out:
            yaml.safe_dump(new_config, f_out)

        print(f"Fichier YAML généré : {output_path}")

def run_opusfilter_on_configs(config_dir: str):
    for filename in os.listdir(config_dir):
        if filename.startswith("config_") and filename.endswith(".yaml") and "template" not in filename:
            config_path = os.path.join(config_dir, filename)
            print(f"Exécution : {config_path}")
            try:
                subprocess.run(["opusfilter", "--overwrite", config_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Erreur pendant OpusFilter : {e}")
    print("Toutes les configurations ont été traitées.")

def evaluate_filtered_data(original_pairs, filtered_dir, src_lang, tgt_lang, rejected_out_dir):
    resultats = []
    os.makedirs(rejected_out_dir, exist_ok=True)

    for filename in os.listdir(filtered_dir):
        if filename.endswith(".filtered.gz") and filename.startswith(f"{src_lang}_"):
            base_name = filename[len(src_lang)+1:-12]
            src_file = os.path.join(filtered_dir, f"{src_lang}_{base_name}.filtered.gz")
            tgt_file = os.path.join(filtered_dir, f"{tgt_lang}_{base_name}.filtered.gz")

            if not os.path.exists(src_file) or not os.path.exists(tgt_file):
                print(f"⛔ Fichiers manquants pour {base_name} – ignoré.")
                continue

            with gzip.open(src_file, 'rt', encoding='utf-8') as sf, gzip.open(tgt_file, 'rt', encoding='utf-8') as tf:
                s1 = [l.strip() for l in sf]
                s2 = [l.strip() for l in tf]
                filtered_pairs = list(zip(s1, s2))

            filtered_set = set(filtered_pairs)
            y_true = [1] * len(original_pairs)
            y_pred = [1 if pair in filtered_set else 0 for pair in original_pairs]

            VP = sum((yt == 1 and yp == 1) for yt, yp in zip(y_true, y_pred))
            FN = sum((yt == 1 and yp == 0) for yt, yp in zip(y_true, y_pred))
            FP = sum((yt == 0 and yp == 1) for yt, yp in zip(y_true, y_pred))
            VN = sum((yt == 0 and yp == 0) for yt, yp in zip(y_true, y_pred))

            resultats.append({
                "Filtres": base_name,
                "VP": VP, "FP": FP, "FN": FN, "VN": VN,
                "Précision": round(precision_score(y_true, y_pred, zero_division=0), 3),
                "Rappel": round(recall_score(y_true, y_pred, zero_division=0), 3),
                "F1": round(f1_score(y_true, y_pred, zero_division=0), 3)
            })

            output_path = os.path.join(rejected_out_dir, f"rejected_{base_name}.tsv")
            with open(output_path, "w", encoding='utf-8') as f:
                for src, tgt in original_pairs:
                    if (src, tgt) not in filtered_set:
                        f.write(f"{src}\t{tgt}\n")

    print("\nRésultats d’évaluation :")
    print(pd.DataFrame(resultats).to_markdown(index=False))

def benchmark_all():
    base_path = "/mnt/c/Users/soumia.daas/ar_fr_filter/filter-benchmark-align"
    config_yaml = os.path.join(base_path, "data/settings_yaml/config_template.yaml")
    settings_dir = os.path.join(base_path, "data/settings_yaml")
    filtered_dir = os.path.join(base_path, "data/filtered")

    benchmarks = [
        {
            "name": "fr_ar",
            "src_file": "data/aligned/arabe_fr/Tatoeba.ar-fr.fr",
            "tgt_file": "data/aligned/arabe_fr/Tatoeba.ar-fr.ar",
            "src_lang": "fr",
            "tgt_lang": "ar",
            "filters": {
                "LengthRatioFilter": [2.0],
                "TerminalPunctuationFilter": {"languages": ["fr", "ar"]},
                "CharacterScoreFilter": [0.6],
                "LanguageIDFilter": [None]
            }
        },
        {
            "name": "ar_ar_TN",
            "src_file": "data/aligned/arabe_tn/GNOME.ar-ar_TN.ar",
            "tgt_file": "data/aligned/arabe_tn/GNOME.ar-ar_TN.ar_TN",
            "src_lang": "ar",
            "tgt_lang": "ar_TN",
            "filters": {
                "LengthRatioFilter": [3.0],
                "TerminalPunctuationFilter": {"languages": ["ar", "ar_TN"]}
            }
        },
        {
            "name": "fr_ar_disaligned",
            "src_file": "data/none_aligned/arabe_fr/fr_disaligned.txt",
            "tgt_file": "data/none_aligned/arabe_fr/ar_disaligned.txt",
            "src_lang": "fr",
            "tgt_lang": "ar",
            "filters": {
                "LengthRatioFilter": [2.0],
                "TerminalPunctuationFilter": {"languages": ["fr", "ar"]},
                "CharacterScoreFilter": [0.6],
                "LanguageIDFilter": [None]
            }
        },
        {
            "name": "ar_ar_TN_disaligned",
            "src_file": "data/none_aligned/arabe_tn/ar.txt",
            "tgt_file": "data/none_aligned/arabe_tn/tun_disaligned.txt",
            "src_lang": "ar",
            "tgt_lang": "ar_TN",
            "filters": {
                "LengthRatioFilter": [3.0],
                "TerminalPunctuationFilter": {"languages": ["ar", "ar_TN"]}
            }
        }
    ]

    for bench in benchmarks:
        print(f"\n=== Benchmarking {bench['name']} ===")
        src_path = os.path.join(base_path, bench['src_file'])
        tgt_path = os.path.join(base_path, bench['tgt_file'])
        original_pairs = load_data(src_path, tgt_path)

        generate_config(
            source_yaml=config_yaml,
            output_dir=settings_dir,
            filters=bench['filters'],
            src_lang=bench['src_lang'],
            tgt_lang=bench['tgt_lang'],
            src_file_path=src_path,
            tgt_file_path=tgt_path
        )
        os.makedirs(filtered_dir, exist_ok=True)
        run_opusfilter_on_configs(settings_dir)
        evaluate_filtered_data(
            original_pairs,
            filtered_dir,
            bench['src_lang'],
            bench['tgt_lang'],
            os.path.join(base_path, f"rejected/{bench['name']}")
        )

if __name__ == "__main__":
    benchmark_all()
