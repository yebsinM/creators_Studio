import os
from dotenv import load_dotenv
import requests
from pathlib import Path

load_dotenv()

def test_models(model_name):
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(f"🔍 Probando inferencia con: {model_name}")
    
    try:
        url = f"https://api-inference.huggingface.co/models/{model_name}"
        payload = {
            "inputs": "def hello_world():",
            "parameters": {"max_new_tokens": 50, "do_sample": True}
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("   ✅ Inferencia funcionando")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


working_models = [
    "bigcode/starcoder",         
    "microsoft/DialoGPT-medium",  
    "gpt2",                      
    "bert-base-uncased"          
]

for model in working_models:
    success = test_models(model)
    if success:
        print(f"🎉 ¡Usa este modelo: {model}")
        break
    print()
