from supabase import create_client
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Missing Supabase credentials")

        self.client = self._create_client(url, key)
    
    def _create_client(self, url, key):
        """Crea el cliente con soporte para proxy opcional"""
        proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        
        if proxy_url:
            proxies = {
                "http://": proxy_url,
                "https://": proxy_url
            }

            custom_client = httpx.Client(
                proxies=proxies,
                timeout=30.0
            )

            return create_client(
                supabase_url=url,
                supabase_key=key,
                http_client=custom_client
            )
        else:
            return create_client(
                supabase_url=url,
                supabase_key=key
            )

    def get_client(self):
        return self.client
