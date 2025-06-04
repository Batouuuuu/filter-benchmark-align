from typing import Annotated

from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/files")
async def create_files(file_src: Annotated[UploadFile, File()], file_target: Annotated[UploadFile, File()] ):
    content_src = await file_src.read()
    content_target = await file_target.read()
    return {"file_tsrc" : content_src.decode("utf-8"),
            "file_target": content_target.decode("utf-8")}