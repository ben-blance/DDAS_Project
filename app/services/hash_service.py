import hashlib
from fastapi import UploadFile
from typing import Dict, List, Union, Set
from app.db.supabase_service import upload_hashes_to_supabase, check_hash_exists

# In-memory storage for file hashes
hashes_db: Dict[str, List[str]] = {}
duplicates_db: Dict[str, List[str]] = {}

async def hash_and_store_file(file: UploadFile):
    sha256_hash = hashlib.sha256()
    
    # Handle file reading in chunks
    while chunk := await file.read(1024):  # Read the file in chunks of 1024 bytes
        sha256_hash.update(chunk)
    
    hash_hex = sha256_hash.hexdigest()
    
    # Check for duplicates and update databases
    if hash_hex in hashes_db or check_hash_exists(hash_hex):
        if hash_hex not in duplicates_db:
            duplicates_db[hash_hex] = list(hashes_db.get(hash_hex, []))
        if file.filename not in duplicates_db[hash_hex]:
            duplicates_db[hash_hex].append(file.filename)
        
        result = {
            "filename": file.filename,
            "sha256_hash": hash_hex,
            "message": "Duplicate detected",
            "duplicates": get_duplicate_files()
        }
    else:
        hashes_db[hash_hex] = [file.filename]
        result = {
            "filename": file.filename,
            "sha256_hash": hash_hex,
            "message": "Hash stored"
        }
    
    # Automatically process and update data
    process_and_update_data()
    
    return result

def process_and_update_data():
    if not hashes_db:
        return {"message": "No hashes found in memory"}
    
    files = [{"sha256_hash": hash_hex, "filenames": filenames} for hash_hex, filenames in hashes_db.items()]
    
    # Upload hashes to Supabase and get the sets of existing and new hashes
    existing_hashes, new_hashes = upload_hashes_to_supabase(files)
    
    # Move existing hashes to duplicates_db
    for hash_hex in existing_hashes:
        if hash_hex in hashes_db:
            if hash_hex not in duplicates_db:
                duplicates_db[hash_hex] = hashes_db[hash_hex]
            else:
                duplicates_db[hash_hex].extend(hashes_db[hash_hex])
            duplicates_db[hash_hex] = list(set(duplicates_db[hash_hex]))  # Remove any duplicates
            hashes_db.pop(hash_hex)
    
    # Remove new hashes from memory
    remove_uploaded_hashes(new_hashes)

def get_all_files() -> Union[Dict[str, str], List[Dict[str, Union[str, List[str]]]]]:
    if not hashes_db:
        return {"message": "No hashes found in memory"}
    return [{"sha256_hash": hash_hex, "filenames": filenames} for hash_hex, filenames in hashes_db.items()]

def get_duplicate_files() -> Union[Dict[str, str], List[Dict[str, Union[str, List[str]]]]]:
    if not duplicates_db:
        return {"message": "No duplicates found in memory"}
    return [{"sha256_hash": hash_hex, "filenames": filenames} for hash_hex, filenames in duplicates_db.items()]

def remove_uploaded_hashes(uploaded_hashes: Set[str]):
    for hash_hex in uploaded_hashes:
        hashes_db.pop(hash_hex, None)
    print(f"Removed {len(uploaded_hashes)} hashes from memory storage.")