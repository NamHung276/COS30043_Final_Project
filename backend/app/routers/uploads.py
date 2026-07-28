import os
import shutil
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/uploads", summary="Upload an image file")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    # Generate a unique filename using timestamp
    safe_filename = file.filename.replace(" ", "_")
    unique_filename = f"{int(time.time() * 1000)}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    # Construct the local URL to serve the static file
    file_url = f"http://localhost:8000/uploads/{unique_filename}"
    
    return {"url": file_url}
