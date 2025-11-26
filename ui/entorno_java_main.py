from .common_imports import *
    
class StarCoderWorker(QThread):
    """Worker para llamadas a la API de StarCoder"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key, message, model_name):
        super().__init__()
        self.api_key = api_key
        self.message = message
        self.model_name = model_name
    
    def run(self):
        try:
            response = self.call_starcoder_api()
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def call_starcoder_api(self):
        """Llama a la API de Hugging Face para StarCoder"""
        url = "https://api-inference.huggingface.co/models/bigcode/starcoder"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": self.message,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        

        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "No se pudo generar respuesta")
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        else:
            return "Respuesta inesperada de la API"

class AIResponseEvent(QEvent):
    """Evento personalizado para respuestas de IA"""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, response, is_error=False):
        super().__init__(self.EVENT_TYPE)
        self.response = response
        self.is_error = is_error









