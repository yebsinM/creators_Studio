from .common_imports import *

class FileType:
    def __init__(self, name, extensions, icon, template):
        self.name = name
        self.extensions = extensions
        self.icon = icon
        self.template = template
class WorkspacePreset:
    def __init__(self, name, tool_panel_pos, panels):
        self.name = name
        self.tool_panel_pos = tool_panel_pos  
        self.panels = panels
class AIProvider:
    """Clase base para proveedores de IA"""
    DEEPSEEK_LOCAL = "deepseek_local"
    DEEPSEEK_API = "deepseek_api"
    STARCODER = "starcoder"
    
    @staticmethod
    def get_available_providers():
        """Retorna los proveedores disponibles"""
        providers = []
        

        local_model_path = r"C:\HuggingFace"
        if os.path.exists(local_model_path):
            providers.append(AIProvider.DEEPSEEK_LOCAL)
        

        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key and deepseek_key.startswith("sk-"):
            providers.append(AIProvider.DEEPSEEK_API)

        starcoder_key = os.getenv("HUGGINGFACE_API_KEY")
        if starcoder_key and starcoder_key.startswith("hf_"):
            providers.append(AIProvider.STARCODER)
        
        return providers