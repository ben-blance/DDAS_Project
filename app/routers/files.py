from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services import hash_service

router = APIRouter()

@router.post("/hash")
async def hash_file(file: UploadFile = File(...)):
    try:
        return await hash_service.hash_and_store_file(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/found")
def get_found_files():
    try:
        return hash_service.get_all_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {str(e)}")

@router.get("/duplicate")
def get_duplicates():
    try:
        return hash_service.get_duplicate_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving duplicates: {str(e)}")