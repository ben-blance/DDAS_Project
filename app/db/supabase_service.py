from supabase import create_client, Client
from typing import List, Dict, Union, Tuple

# Supabase credentials
SUPABASE_URL = "https://ynalolrcynccrixjequv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluYWxvbHJjeW5jY3JpeGplcXV2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzMDUyMzAsImV4cCI6MjA0MTg4MTIzMH0.xS19vemTs59MJTjVZVeVvHWU7PJ5H9FywHbBHh2vfpY"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_table_name(file_extension: str) -> str:
    if file_extension.lower() == 'csv':
        return 'csv'
    elif file_extension.lower() == 'json':
        return 'json'
    else:
        return 'other'

def check_hash_exists(hash_hex: str, file_extension: str) -> bool:
    table_name = get_table_name(file_extension)
    try:
        response = supabase.table(table_name).select('hash').eq('hash', hash_hex).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking hash existence: {e}")
        return False

def upload_hash_to_supabase(hash_hex: str, file_name: str, file_size: int, file_extension: str) -> bool:
    table_name = get_table_name(file_extension)
    try:
        print(f"Attempting to insert hash into {table_name} table: {hash_hex}")
        response = supabase.table(table_name).insert({
            "hash": hash_hex,
            "NAME": file_name,
            "SIZE": file_size
        }).execute()
        print("Insert Response:", response)
        
        if len(response.data) > 0:
            print(f"Hash inserted successfully into {table_name} table: {hash_hex}")
            return True
        else:
            print(f"Error inserting hash into {table_name} table: {response}")
            return False
    except Exception as e:
        print(f"An error occurred while inserting into Supabase table: {e}")
        return False