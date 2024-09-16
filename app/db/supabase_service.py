import json
import tempfile
import os
from datetime import datetime
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://icifjmntjnnbkolhuetc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImljaWZqbW50am5uYmtvbGh1ZXRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYzMzkzODEsImV4cCI6MjA0MTkxNTM4MX0._51rIr3lJnagXCrz_3HnvULFZi2MYycL3IF0uLQAnqo"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_duplicates_to_supabase(duplicates):
    try:
        # Log duplicates data for debugging
        print(f"Uploading duplicates to Supabase: {duplicates}")

        # Ensure duplicates is a list of dictionaries
        if not isinstance(duplicates, list):
            raise ValueError("Invalid duplicates data format: expected a list")

        # Create a temporary file
        json_data = json.dumps(duplicates)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(json_data.encode('utf-8'))
            temp_file_path = temp_file.name

        # Generate a unique file path in Supabase Storage
        unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = f"duplicates_{unique_suffix}.json"  # Append timestamp to ensure uniqueness

        try:
            # Upload the temporary file to Supabase Storage
            bucket_name = "FIRBuck"  # Replace with your bucket name
            
            with open(temp_file_path, "rb") as file:
                upload_response = supabase.storage.from_(bucket_name).upload(file_path, file)

            # Print the entire response for debugging
            print("Upload Response:", upload_response)

            # Check if response is successful
            if upload_response.status_code == 200:
                print(f"File uploaded successfully as {file_path}.")
            else:
                print(f"Error uploading file: {upload_response.text}")

        except Exception as e:
            print(f"An error occurred while uploading to Supabase: {e}")

        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)

    except Exception as e:
        print(f"An error occurred while processing duplicates: {str(e)}")