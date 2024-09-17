import hashlib
import os
from fastapi import UploadFile
from typing import Dict, List, Union
from app.db.supabase_service import upload_hash_to_supabase, check_hash_exists

# In-memory storage for file hashes
hashes_db: Dict[str, Dict[str, Union[str, List[str]]]] = {}
duplicates_db: Dict[str, Dict[str, Union[str, List[str]]]] = {}

async def hash_and_store_file(file: UploadFile):
    sha256_hash = hashlib.sha256()
    
    # Handle file reading in chunks
    while chunk := await file.read(1024):  # Read the file in chunks of 1024 bytes
        sha256_hash.update(chunk)
    
    hash_hex = sha256_hash.hexdigest()
    file_extension = os.path.splitext(file.filename)[1][1:].lower()  # Get file extension without the dot
    
    # Check if the hash exists in the database
    if check_hash_exists(hash_hex, file_extension):
        if hash_hex not in duplicates_db:
            duplicates_db[hash_hex] = {'filenames': [file.filename], 'extension': file_extension}
        else:
            duplicates_db[hash_hex]['filenames'].append(file.filename)
        
        result = {
            "filename": file.filename,
            "sha256_hash": hash_hex,
            "extension": file_extension,
            "message": "Duplicate detected",
            "duplicates": get_duplicate_files()
        }
    else:
        # Upload the hash to Supabase
        upload_success = upload_hash_to_supabase(hash_hex, file_extension)
        if upload_success:
            result = {
                "filename": file.filename,
                "sha256_hash": hash_hex,
                "extension": file_extension,
                "message": "Hash stored in database"
            }
        else:
            # If upload fails, store in memory
            hashes_db[hash_hex] = {'filenames': [file.filename], 'extension': file_extension}
            result = {
                "filename": file.filename,
                "sha256_hash": hash_hex,
                "extension": file_extension,
                "message": "Hash stored in memory"
            }
    
    return result

def get_all_files() -> Union[Dict[str, str], List[Dict[str, Union[str, List[str]]]]]:
    if not hashes_db:
        return {"message": "No hashes found in memory"}
    return [{"sha256_hash": hash_hex, "filenames": info['filenames'], "extension": info['extension']} 
            for hash_hex, info in hashes_db.items()]

def get_duplicate_files() -> Union[Dict[str, str], List[Dict[str, Union[str, List[str]]]]]:
    if not duplicates_db:
        return {"message": "No duplicates found"}
    return [{"sha256_hash": hash_hex, "filenames": info['filenames'], "extension": info['extension']} 
            for hash_hex, info in duplicates_db.items()]