import httpx
import os
from dotenv import load_dotenv

load_dotenv()

proxies = {
    "http://": os.getenv("HTTP_PROXY"),
    "https://": os.getenv("HTTPS_PROXY")
}

custom_client = httpx.Client(
    proxies=proxies,
    timeout=30.0
)

print("Cliente HTTPX creado correctamente con proxy")