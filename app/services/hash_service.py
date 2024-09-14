import hashlib
from fastapi import UploadFile
from typing import Dict, List

# In-memory storage for file hashes
hashes_db: Dict[str, List[str]] = {}  # Maps hash to a list of filenames
duplicates_db: Dict[str, List[str]] = {}  # Maps hash to a list of filenames with duplicate entries

async def hash_and_store_file(file: UploadFile):
    sha256_hash = hashlib.sha256()
    while chunk := await file.read(1024):  # Read the file in chunks of 1024 bytes
        sha256_hash.update(chunk)
    
    hash_hex = sha256_hash.hexdigest()
    
    # Check if the hash already exists
    if hash_hex in hashes_db:
        # If it's already in the hash list, check for duplicates
        if hash_hex not in duplicates_db:
            duplicates_db[hash_hex] = list(hashes_db[hash_hex])  # Store previous filenames
        if file.filename not in duplicates_db[hash_hex]:
            duplicates_db[hash_hex].append(file.filename)
        return {"filename": file.filename, "sha256_hash": hash_hex, "message": "Duplicate detected"}
    else:
        # If the hash is not found, store it
        hashes_db[hash_hex] = [file.filename]
        return {"filename": file.filename, "sha256_hash": hash_hex, "message": "Hash stored"}

def get_all_files():
    if not hashes_db:
        return {"message": "No hashes found in memory"}
    # Ensure unique filenames
    unique_files = {hash_hex: list(set(filenames)) for hash_hex, filenames in hashes_db.items()}
    return [{"sha256_hash": hash_hex, "filenames": filenames} for hash_hex, filenames in unique_files.items()]

def get_duplicate_files():
    if not duplicates_db:
        return {"message": "No duplicates found in memory"}
    return [{"sha256_hash": hash_hex, "filenames": filenames} for hash_hex, filenames in duplicates_db.items()]