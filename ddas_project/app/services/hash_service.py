import hashlib
import os
from fastapi import UploadFile
from typing import Dict, List, Union
from app.db.supabase_service import upload_hash_to_supabase, check_hash_exists

# In-memory storage for file hashes
hashes_db: Dict[str, Dict[str, Union[str, List[str], int]]] = {}
duplicates_db: Dict[str, Dict[str, Union[str, List[str], int]]] = {}

async def hash_and_store_file(file: UploadFile, file_location: str):
    sha256_hash = hashlib.sha256()
    file_size = 0
    
    # Handle file reading in chunks
    while chunk := await file.read(1024):  # Read the file in chunks of 1024 bytes
        sha256_hash.update(chunk)
        file_size += len(chunk)
    
    hash_hex = sha256_hash.hexdigest()
    file_extension = os.path.splitext(file.filename)[1][1:].lower()  # Get file extension without the dot
    
    # Check if the hash exists in the database
    if check_hash_exists(hash_hex, file_extension):
        if hash_hex not in duplicates_db:
            duplicates_db[hash_hex] = {
                'filenames': [file.filename],
                'extension': file_extension,
                'size': file_size,
                'location': [file_location]  # Save file location in list
            }
        else:
            duplicates_db[hash_hex]['filenames'].append(file.filename)
            duplicates_db[hash_hex]['location'].append(file_location)  # Append location

        result = {
            "sha256_hash": hash_hex,
            "filenames": duplicates_db[hash_hex]['filenames'],
            "extension": file_extension,
            "size": file_size,
            "location": duplicates_db[hash_hex]['location'],  # Include file location
            "message": "Duplicate detected",
            "duplicates": get_duplicate_files()
        }
    else:
        # Upload the hash to Supabase
        upload_success = upload_hash_to_supabase(hash_hex, file.filename, file_size, file_extension, file_location)
        if upload_success:
            result = {
                "sha256_hash": hash_hex,
                "filenames": [file.filename],
                "extension": file_extension,
                "size": file_size,
                "location": [file_location],  # Include file location in response
                "message": "Hash stored in database"
            }
        else:
            # If upload fails, store in memory
            hashes_db[hash_hex] = {
                'filenames': [file.filename],
                'extension': file_extension,
                'size': file_size,
                'location': [file_location]  # Save file location in list
            }
            result = {
                "sha256_hash": hash_hex,
                "filenames": [file.filename],
                "extension": file_extension,
                "size": file_size,
                "location": [file_location],  # Include file location in response
                "message": "Hash stored in memory"
            }

    return result

def get_all_files() -> Union[Dict[str, str], List[Dict[str, Union[str, List[str], int]]]]:
    if not hashes_db:
        return {"message": "No hashes found in memory"}
    return [{"sha256_hash": hash_hex, "filenames": info['filenames'], "extension": info['extension'], "size": info['size'], "location": info['location']} 
            for hash_hex, info in hashes_db.items()]

def get_duplicate_files() -> Union[Dict[str, str], List[Dict[str, Union[str, List[str], int, List[str]]]]]:
    if not duplicates_db:
        return {"message": "No duplicates found"}
    
    # Prepare the results with file locations included
    result = []
    for hash_hex, info in duplicates_db.items():
        file_locations = info.get('location', [])
        result.append({
            "sha256_hash": hash_hex,
            "filenames": info['filenames'],
            "extension": info['extension'],
            "size": info['size'],
            "locations": file_locations  # Include file locations in the response
        })
    
    return result
