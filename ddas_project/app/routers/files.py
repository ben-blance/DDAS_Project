from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.services.hash_service import hash_and_store_file, get_all_files, get_duplicate_files

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), file_location: str = Form(...)):
    try:
        result = await hash_and_store_file(file, file_location)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/found")
def get_found_files():
    try:
        files = get_all_files()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {str(e)}")

@router.get("/duplicate")
def get_duplicates():
    try:
        duplicates = get_duplicate_files()
        return duplicates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving duplicates: {str(e)}")
