from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.utils.transcribe import transcribe_video
import os
import uuid

app = FastAPI()

# Mount static frontend
app.mount("/ui", StaticFiles(directory="assets/ui", html=True), name="ui")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    temp_input = f"temp/{uuid.uuid4()}_{file.filename}"
    with open(temp_input, "wb") as f:
        f.write(await file.read())

    output_path = transcribe_video(temp_input)
    return FileResponse(output_path, filename=os.path.basename(output_path))
