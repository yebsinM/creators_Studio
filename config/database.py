from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Missing Supabase credentials")

        self.client = create_client(url, key)
    
    def get_client(self):
        return self.client