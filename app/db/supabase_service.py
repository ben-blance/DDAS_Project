import hashlib
from fastapi import UploadFile
from typing import Dict, List, Union
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://ynalolrcynccrixjequv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluYWxvbHJjeW5jY3JpeGplcXV2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzMDUyMzAsImV4cCI6MjA0MTg4MTIzMH0.xS19vemTs59MJTjVZVeVvHWU7PJ5H9FywHbBHh2vfpY"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    if hash_hex in hashes_db:
        if hash_hex not in duplicates_db:
            duplicates_db[hash_hex] = list(hashes_db[hash_hex])
        if file.filename not in duplicates_db[hash_hex]:
            duplicates_db[hash_hex].append(file.filename)
        
        return {
            "filename": file.filename,
            "sha256_hash": hash_hex,
            "message": "Duplicate detected",
            "duplicates": get_duplicate_files()
        }
    else:
        # Store the hash in the Supabase 'other' table
        upload_duplicates_to_supabase(hash_hex)

        hashes_db[hash_hex] = [file.filename]
        return {
            "filename": file.filename,
            "sha256_hash": hash_hex,
            "message": "Hash stored"
        }

def upload_duplicates_to_supabase(hash_hex: str):
    try:
        print(f"Attempting to insert hash: {hash_hex}")
        insert_response = supabase.table('other').insert({"hash": hash_hex}).execute()
        print("Insert Response:", insert_response)
        print("Insert Response Data:", insert_response.data)

        if insert_response.status_code == 201:
            print(f"Hash inserted successfully: {hash_hex}")
        else:
            print(f"Error inserting hash: {insert_response.data}")

    except Exception as e:
        print(f"An error occurred while inserting into Supabase table: {e}")

def get_all_files() -> Union[Dict[str, str], List[Dict[str, Union[str, List[str]]]]]:
    if not hashes_db:
        return {"message": "No hashes found in memory"}
    unique_files = {hash_hex: list(set(filenames)) for hash_hex, filenames in hashes_db.items()}
    return [{"sha256_hash": hash_hex, "filenames": filenames} for hash_hex, filenames in unique_files.items()]

def get_duplicate_files() -> Union[Dict[str, str], List[Dict[str, Union[str, List[str]]]]]:
    if not duplicates_db:
        return {"message": "No duplicates found in memory"}
    return [{"sha256_hash": hash_hex, "filenames": filenames} for hash_hex, filenames in duplicates_db.items()]