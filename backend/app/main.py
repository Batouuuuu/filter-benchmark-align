from typing import Annotated, Tuple
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from pathlib import Path
from scripts.benchmark_filters_test import *
import re 

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_temporary_file(file_path: Path, content: bytes) -> Path:
    try:
        with open(file_path, "w", encoding='UTF-8') as f:
            f.write(content.decode('UTF-8'))
    except UnicodeDecodeError:
        raise
    return file_path
 
def remove_files(directory_path_filtered: str, directory_path_config_yaml : str) -> None :
    """"remove if files already are in filtered"""

    ## to clean the directory filtred
    folder_path = directory_path_filtered
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
             

    ## to clean the directory path but keep the config.yaml (very important we need it to generate other yaml)
    folder_path1 = directory_path_config_yaml
    pattern = r"^config\_.*\.yaml$"
    for filename in os.listdir(folder_path1):
        file_path = os.path.join(folder_path1, filename)
        if os.path.isfile(file_path) and re.match(pattern, filename) :
            os.remove(file_path) 
             

@app.post("/files")
async def create_files(file_src: Annotated[UploadFile, File()], file_target: Annotated[UploadFile, File()] ):
    """Read both files from the api, then create files in a temporaryDirectory for save their data"""

    remove_files("./data/filtered", "./data/settings_yaml")

    with tempfile.TemporaryDirectory() as tmp_dir: 
        content_src = await file_src.read()
        content_target = await file_target.read()
        files = [(Path(tmp_dir, "file1"), content_src),
                 (Path(tmp_dir, "file2"), content_target)]

        for path, content in files:
            create_temporary_file(path, content)


        original_pairs = load_data(str(files[0][0]), str(files[1][0]))
        base_dir = Path(__file__).resolve().parent.parent.parent
        source_yaml = base_dir / "data" / "settings_yaml" / "config.yaml"
        output_dir = base_dir / "data" / "settings_yaml"
        filtered_dir = base_dir / "data" / "filtered"

        generate_config(
            source_yaml=str(source_yaml),
            output_dir=str(output_dir),
            filters={"LengthRatioFilter": [1.8]}
        )

        run_opusfilter_on_configs(str(output_dir))

        # Compter les phrases avant/après filtrage
        initial_count = len(original_pairs)
        
        # Compter les phrases filtrées
        filtered_files = list(filtered_dir.glob("*.filtered.gz"))
        if filtered_files:
            with gzip.open(filtered_files[0], 'rt', encoding='utf-8') as f:
                filtered_count = sum(1 for _ in f)
        else:
            filtered_count = 0

        return {
            "status": "success",
            "initial_sentence_count": initial_count,
            "filtered_sentence_count": filtered_count,
            "rejected_count": initial_count - filtered_count,
            "filter_used": "LengthRatioFilter (1.8)"
        }
