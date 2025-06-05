from typing import Annotated, Tuple
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from pathlib import Path
from scripts.benchmark_filters_test import *


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
 
    

@app.post("/files")
async def create_files(file_src: Annotated[UploadFile, File()], file_target: Annotated[UploadFile, File()] ):
    """Read both files from the api, then create files in a temporaryDirectory for save their data"""
    with tempfile.TemporaryDirectory() as tmp_dir: 
        content_src = await file_src.read()
        content_target = await file_target.read()
        files = [(Path(tmp_dir, "file1"), content_src),
                 (Path(tmp_dir, "file2"), content_target)]

        for path, content in files:
            create_temporary_file(path, content)


        original_pairs = load_data(str(files[0][0]), str(files[1][0]))

       
        generate_config(
            source_yaml="../data/settings_yaml/config.yaml",
            filters={"WordAlignFilter": [0.2]}
        )

        run_opusfilter_on_configs("../data/settings_yaml/")

        # evaluate_filtered_data(original_pairs, "../data/filtered/")

        return {"status": "Traitement terminé"}
       

