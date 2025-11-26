from .common_imports import *
import torch
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM

class DeepSeekWorker(QThread):
    """Worker para llamadas al modelo DeepSeek local en segundo plano"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, message, conversation_history=None, model_path=None):
        super().__init__()
        self.message = message
        self.conversation_history = conversation_history or []

        self.model_path = model_path or r"C:\HuggingFace\coder_experto"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def run(self):
        try:
            response = self.call_deepseek_local()
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))
    def call_deepseek_local(self):
        try:
            model_path = r"C:\HuggingFace\coder_experto"
            
            if not os.path.exists(model_path):
                return "❌ Primero descarga el modelo especializado en código"
            
            print(f"🔧 Cargando genio de programación desde: {model_path}")
            
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            
            # PROMPT LIMPIO - solo la instrucción esencial
            prompt = f"Pregunta: {self.message}\n\nRespuesta:"
            
            inputs = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_new_tokens=800,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=3
                )  
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # EXTRAER SOLO LA RESPUESTA (lo que viene después de "Respuesta:")
            if "Respuesta:" in response:
                response = response.split("Respuesta:")[1].strip()
            
            return response  # Sin prefijos ni emojis
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def build_prompt(self):
        """Construye el prompt con el historial de conversación"""
        prompt = "Eres un asistente útil para gestión de archivos y desarrollo. Responde de forma clara y concisa.\n\n"
        

        for msg in self.conversation_history[-4:]: 
            if msg["role"] == "user":
                prompt += f"Usuario: {msg['content']}\n"
            else:
                prompt += f"Asistente: {msg['content']}\n"
        
        
        prompt += f"Usuario: {self.message}\nAsistente: "
        
        return prompt
class EnhancedAIChatPanel(QWidget):
    """Panel de IA con control TOTAL del sistema de archivos"""
    
    def __init__(self, code_generator, parent=None):
        super().__init__(parent)
        self.code_generator = code_generator
        self.parent_window = parent
        self.conversation_history = []
        self.current_provider = "deepseek"
        self.current_directory = Path.home()  
        self.setup_ui()
        self.load_api_keys()
    
        self.add_system_message("🚀 **SISTEMA DE CONTROL TOTAL INICIADO**")
        self.add_system_message(f"📂 **Directorio actual:** {self.current_directory}")
        self.add_system_message("**💡 Puedo realizar estas acciones:**")
        self.add_system_message("• 📁 Navegar por TODO el sistema de archivos")
        self.add_system_message("• 📄 Crear/editar/eliminar cualquier archivo")
        self.add_system_message("• 🗂️ Gestionar carpetas y directorios")
        self.add_system_message("• 🔍 Buscar y reemplazar en archivos")
        self.add_system_message("• ⚡ Ejecutar comandos del sistema")
        self.add_system_message("• 📊 Analizar espacio y estadísticas")
        self.add_system_message("• 🔄 Operaciones por lotes/múltiples archivos")

    def setup_ui(self):
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # NAVEGACIÓN
        nav_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("◀")
        self.back_btn.setToolTip("Directorio anterior")
        self.back_btn.clicked.connect(self.navigate_back)
        self.back_btn.setFixedSize(30, 25)
        
        self.forward_btn = QPushButton("▶")
        self.forward_btn.setToolTip("Directorio siguiente")
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.forward_btn.setFixedSize(30, 25)
        
        self.home_btn = QPushButton("Home")
        self.home_btn.setToolTip("Directorio home")
        self.home_btn.clicked.connect(self.go_home)
        self.home_btn.setFixedSize(40, 25)
        
        self.up_btn = QPushButton("Up")
        self.up_btn.setToolTip("Directorio padre")
        self.up_btn.clicked.connect(self.go_up)
        self.up_btn.setFixedSize(35, 25)
        
        self.path_label = QLabel(str(self.current_directory))
        self.path_label.setStyleSheet("""
            background-color: #2d2d30; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 11px;
            border: 1px solid #3e3e42;
        """)
        self.path_label.setWordWrap(True)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.up_btn)
        nav_layout.addWidget(self.path_label)
        nav_layout.addStretch()
        
        layout.addLayout(nav_layout)

        # HISTORIAL DE CHAT
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Escribe comandos como: 'crea un archivo.txt', 'lista los archivos', 'cambia a /ruta'...")
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 8px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
                padding: 8px;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #424245;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4f;
            }
        """)
        layout.addWidget(self.chat_history)
        
        # ENTRADA DE USUARIO
        input_container = QWidget()
        input_container.setStyleSheet("background-color: #252526; border-radius: 8px; padding: 4px;")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 4, 8, 4)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Escribe tu comando o pregunta...")
        self.user_input.returnPressed.connect(self.send_message)
        self.user_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d30;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: #264F78;
            }
            QLineEdit:focus {
                border: 1px solid #007ACC;
            }
        """)
        input_layout.addWidget(self.user_input)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedSize(80, 35)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(input_container)

        # ACCIONES RÁPIDAS
        quick_actions_container = QWidget()
        quick_actions_container.setStyleSheet("background-color: #252526; border-radius: 8px; padding: 4px;")
        quick_actions_layout = QHBoxLayout(quick_actions_container)
        quick_actions_layout.setContentsMargins(8, 4, 8, 4)

        actions = [
            ("Estadisticas", self.show_system_stats),
            ("Buscar", self.quick_search),
            ("Listar", self.list_current_directory),
            ("Terminal", self.open_terminal),
            ("Herramientas", self.show_tools_menu)
        ]
        
        for text, action in actions:
            btn = QPushButton(text)
            btn.setFixedHeight(30)
            btn.clicked.connect(action)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d30;
                    color: #d4d4d4;
                    border: 1px solid #3e3e42;
                    border-radius: 6px;
                    font-size: 11px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #3c3c3c;
                    border: 1px solid #007ACC;
                }
            """)
            quick_actions_layout.addWidget(btn)
        
        layout.addWidget(quick_actions_container)
        
        chat_widget.setLayout(layout)
        
        # ✅ CORRECCIÓN: Configurar el layout principal del widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(chat_widget)
      

  
    
    def _add_formatted_message(self, sender, message, color, is_user=False):
        """Añade mensaje formateado al chat - VERSIÓN LIMPIA CON BURBUJAS"""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        timestamp = QDateTime.currentDateTime().toString("HH:mm")
        
        # Solo el usuario tiene burbuja de chat
        if is_user:
            # BURBUJA para el usuario (derecha)
            formatted_message = f"""
            <div style="margin: 10px 5px; font-family: 'Segoe UI', Arial, sans-serif;">
                <div style="display: flex; justify-content: flex-end;">
                    <div style="background-color: #007ACC; color: white; padding: 10px 14px; 
                            border-radius: 18px 18px 4px 18px; max-width: 85%; 
                            line-height: 1.4; font-size: 13px; word-wrap: break-word;">
                        {message.replace(chr(10), '<br>')}
                    </div>
                </div>
                <div style="display: flex; justify-content: flex-end; margin-top: 2px;">
                    <span style="color: #858585; font-size: 10px; margin-right: 5px;">
                        {timestamp}
                    </span>
                    <span style="font-weight: bold; color: #1976D2; font-size: 11px;">
                        {sender}
                    </span>
                </div>
            </div>
            """
        else:
            # Texto normal para IA/Sistema (izquierda, sin burbuja)
            formatted_message = f"""
            <div style="margin: 5px 5px; font-family: 'Segoe UI', Arial, sans-serif;">
                <div style="display: flex; align-items: center; margin-bottom: 3px;">
                    <span style="font-weight: bold; color: {self._get_sender_color(sender)}; font-size: 12px;">
                        {sender}
                    </span>
                    <span style="color: #858585; font-size: 10px; margin-left: 8px;">
                        {timestamp}
                    </span>
                </div>
                <div style="color: #d4d4d4; font-size: 13px; line-height: 1.4; 
                        word-wrap: break-word; margin-left: 5px;">
                    {message.replace(chr(10), '<br>')}
                </div>
            </div>
            """
        
        cursor.insertHtml(formatted_message)
        self.chat_history.ensureCursorVisible()
        
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    def _get_sender_color(self, sender):
        """Retorna color específico para cada tipo de sender - SIN EMOJIS"""
        colors = {
            "Sistema": "#569CD6",
            "Exito": "#4CAF50", 
            "Advertencia": "#FF9800",
            "Error": "#F44336",
            "IA": "#388E3C",
            "Tu": "#1976D2"
        }
        return colors.get(sender, "#569CD6")

    def add_user_message(self, message):
        self._add_formatted_message("Tu", message, "#1a1a33", is_user=True)

    def add_ai_response(self, message):
        # Limpiar el texto de la IA antes de mostrar
        clean_message = self.clean_ai_response(message)
        self._add_formatted_message("IA", clean_message, "#1a331a", is_user=False)

    def add_system_message(self, message):
        self._add_formatted_message("Sistema", message, "#2d2d30", is_user=False)

    def add_success_message(self, message):
        self._add_formatted_message("Exito", message, "#1e3a1e", is_user=False)

    def add_warning_message(self, message):
        self._add_formatted_message("Advertencia", message, "#332300", is_user=False)

    def add_error_message(self, message):
        self._add_formatted_message("Error", message, "#330000", is_user=False)

    def clean_ai_response(self, message):
        """Método mínimo por si acaso, pero ya no debería ser necesario"""
        return message.strip()
    def navigate_back(self):
        """Navega al directorio anterior"""
        if hasattr(self, 'navigation_history') and self.navigation_history:
            prev_dir = self.navigation_history.pop()
            self.current_directory = prev_dir
            self.update_path_display()
            self.list_current_directory()

    def navigate_forward(self):
        """Navega al directorio siguiente"""

        pass

    def go_home(self):
        """Va al directorio home"""
        self.current_directory = Path.home()
        self.update_path_display()
        self.list_current_directory()

    def go_up(self):
        """Sube al directorio padre"""
        if self.current_directory.parent != self.current_directory:
            self.current_directory = self.current_directory.parent
            self.update_path_display()
            self.list_current_directory()

    def update_path_display(self):
        """Actualiza la visualización de la ruta"""
        self.path_label.setText(str(self.current_directory))


    def process_ai_commands(self, response):
        """Procesa comandos especiales que puedan venir en la respuesta de IA"""

        commands = {
            'navegar': self.handle_navigation_from_ai,
            'crear': self.handle_creation_from_ai,
            'listar': self.list_current_directory,
            'eliminar': self.handle_deletion_from_ai,
            'editar': self.handle_edit_from_ai
        }
        
        lower_response = response.lower()
        for cmd_key, cmd_handler in commands.items():
            if cmd_key in lower_response:
                cmd_handler(response)
                break
    def send_message(self):
        """Envía mensaje con formato mejorado - ÚNICA VERSIÓN"""
        user_text = self.user_input.text().strip()
        if not user_text:
            return
            
        # LIMPIAR mensajes de sistema automáticos
        self.clear_system_message()
        
        # Añadir TU mensaje como burbuja de chat
        self.add_user_message(user_text)
        self.user_input.clear()
        
        self.last_command = user_text
        
        # Procesar con IA
        self.process_with_ai(user_text)

    def clear_system_message(self):
        """Limpia mensajes de sistema automáticos"""
        current_text = self.chat_history.toPlainText()
        if any(msg in current_text for msg in ["Modo Java activado", "Modo Kotlin activado", "Modo Flutter activado"]):
            self.chat_history.clear()
            self.add_welcome_message()
    def test_deepseek_model(self):
        """Método para probar si el modelo carga correctamente"""
        try:
            model_path = "C:\\HuggingFace\\deepseek_model"
            
            if not os.path.exists(model_path):
                return "❌ La ruta del modelo no existe"
            

            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            

            test_prompt = "Hola, ¿puedes oírme?"
            inputs = tokenizer.encode(test_prompt, return_tensors="pt")
            
            return f"✅ Modelo cargado correctamente. Tokenizer funciona. Tokens: {len(inputs[0])}"
            
        except Exception as e:
            return f"❌ Error cargando el modelo: {str(e)}"
    def process_command(self, command):
        """Procesa comandos naturales del usuario"""
        lower_cmd = command.lower()
        
        try:  
            if any(word in lower_cmd for word in ['ve a', 'cambia a', 'entra a', 'cd ']):
                self.handle_navigation(command)
            
            elif any(word in lower_cmd for word in ['crea', 'nuevo', 'make', 'create']):
                self.handle_file_creation(command)
            
            elif any(word in lower_cmd for word in ['lista', 'muestra', 'ls', 'dir', 'contenido']):
                self.list_current_directory()
            
            elif any(word in lower_cmd for word in ['edita', 'modifica', 'edit', 'change']):
                self.handle_file_edit(command)
            
            elif any(word in lower_cmd for word in ['elimina', 'borra', 'delete', 'remove']):
                self.handle_deletion(command)
            
            elif any(word in lower_cmd for word in ['busca', 'find', 'search']):
                self.handle_search(command)
            
            elif any(word in lower_cmd for word in ['copia', 'mueve', 'copy', 'move']):
                self.handle_copy_move(command)
            
            elif any(word in lower_cmd for word in ['estadísticas', 'espacio', 'info', 'stats']):
                self.show_system_stats()
            
            elif lower_cmd.startswith('ejecuta ') or lower_cmd.startswith('run '):
                self.execute_system_command(command)
            
            else:
                self.process_with_ai(command)
                
        except Exception as e:  
            self.add_error_message(f"❌ Error procesando comando: {str(e)}")

    def handle_navigation_from_ai(self, response):
        """Maneja comandos de navegación desde IA"""
        try:
            import re
            paths = re.findall(r'/[^\s]+|\w:[\\/][^\s]+|~\S*', response)
            if paths:
                target_path = paths[0]
                self.handle_navigation(f"ir a {target_path}")
        except Exception as e:
            self.add_error_message(f"❌ Error en navegación por IA: {str(e)}")
    
    def handle_creation_from_ai(self, response):
        """Maneja comandos de creación desde IA"""
        try:
            import re
            files = re.findall(r'\b\w+\.\w{1,5}\b', response)
            if files:
                filename = files[0]
                content_match = re.search(r'contenido[:\s]*(.+)', response, re.IGNORECASE | re.DOTALL)
                content = content_match.group(1).strip() if content_match else ""
                self.create_file(filename, content)
        except Exception as e:
            self.add_error_message(f"❌ Error en creación por IA: {str(e)}")

    def handle_deletion_from_ai(self, response):
        """Maneja comandos de eliminación desde IA"""
        try:

            import re
            targets = re.findall(r'\b\w+\.\w{1,5}\b|\b\w+\b', response)
            if targets and len(targets) > 1: 
                target = targets[1]
                self.handle_deletion(f"eliminar {target}")
        except Exception as e:
            self.add_error_message(f"❌ Error en eliminación por IA: {str(e)}")

    def handle_edit_from_ai(self, response):
        """Maneja comandos de edición desde IA"""
        try:
            import re
            files = re.findall(r'\b\w+\.\w{1,5}\b', response)
            if files:
                filename = files[0]
                self.handle_file_edit(f"editar {filename}")
        except Exception as e:
            self.add_error_message(f"❌ Error en edición por IA: {str(e)}")
    def handle_navigation(self, command):
        """Maneja comandos de navegación"""
        parts = command.split()
        path_str = None

        for i, part in enumerate(parts):
            if part in ['a', 'to', 'en'] and i + 1 < len(parts):
                path_str = ' '.join(parts[i+1:])
                break
        
        if not path_str:
            path_str = parts[-1] 

        if path_str == "~" or path_str == "home":
            path_str = str(Path.home())
        elif path_str == "..":
            path_str = str(self.current_directory.parent)
        
        target_path = Path(path_str)

        if not target_path.is_absolute():
            target_path = self.current_directory / target_path
        
        if target_path.exists() and target_path.is_dir():
            self.current_directory = target_path
            self.update_path_display()
            self.list_current_directory()
            self.add_success_message(f"📂 Directorio cambiado a: {target_path}")
        else:
            self.add_error_message(f"❌ La ruta no existe o no es un directorio: {target_path}")

    def handle_file_creation(self, command):
        """Maneja creación de archivos y carpetas"""
        lower_cmd = command.lower()

        if any(word in lower_cmd for word in ['carpeta', 'folder', 'directorio']):
            folder_name = self.extract_filename(command, ['carpeta', 'folder'])
            if folder_name:
                self.create_folder(folder_name)
        
        elif any(word in lower_cmd for word in ['archivo', 'file']):
            file_name = self.extract_filename(command, ['archivo', 'file'])
            content = self.extract_content(command)
            if file_name:
                self.create_file(file_name, content)

    def extract_filename(self, command, keywords):
        """Extrae el nombre de archivo/carpeta del comando"""
        for keyword in keywords:
            if keyword in command.lower():
                start_idx = command.lower().index(keyword) + len(keyword)
                remaining = command[start_idx:].strip()
   
                filename = remaining.split()[0] if remaining.split() else None
                return filename
        return None

    def extract_content(self, command):
        """Extrae contenido para archivos del comando"""
        if 'contenido' in command.lower() or 'con' in command.lower():

            for separator in ['contenido', 'con', 'that says']:
                if separator in command.lower():
                    start_idx = command.lower().index(separator) + len(separator)
                    return command[start_idx:].strip()
        return ""

    def create_folder(self, folder_name):
        """Crea una nueva carpeta"""
        try:
            folder_path = self.current_directory / folder_name
            folder_path.mkdir(exist_ok=True)
            self.add_success_message(f"✅ Carpeta creada: {folder_path}")
            self.list_current_directory()
        except Exception as e:
            self.add_error_message(f"❌ Error creando carpeta: {str(e)}")

    def create_file(self, file_name, content=""):
        """Crea un nuevo archivo"""
        try:
            file_path = self.current_directory / file_name

            if '.' not in file_name:
                file_path = file_path.with_suffix('.txt')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.add_success_message(f"✅ Archivo creado: {file_path}")
            if content:
                self.add_system_message(f"📝 Contenido: {content}")
            self.list_current_directory()
        except Exception as e:
            self.add_error_message(f"❌ Error creando archivo: {str(e)}")

    def list_current_directory(self):
        """Lista el contenido del directorio actual"""
        try:
            items = list(self.current_directory.iterdir())
            
            if not items:
                self.add_system_message("📂 El directorio está vacío")
                return

            folders = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            message = f"📂 **Contenido de {self.current_directory}:**\n\n"
            
            if folders:
                message += "**📁 Carpetas:**\n"
                for folder in sorted(folders):
                    message += f"• {folder.name}/\n"
                message += "\n"
            
            if files:
                message += "**📄 Archivos:**\n"
                for file in sorted(files):
                    size = file.stat().st_size
                    message += f"• {file.name} ({size} bytes)\n"
            
            self.add_system_message(message)
            
        except Exception as e:
            self.add_error_message(f"❌ Error listando directorio: {str(e)}")

    def handle_file_edit(self, command):
        """Maneja edición de archivos"""
        try:
   
            filename = None
            for word in command.split():
                if '.' in word:
                    filename = word
                    break
            
            if filename:
                file_path = self.current_directory / filename
                if file_path.exists():
                    self.edit_file_interactive(file_path)
                else:
                    self.add_error_message(f"❌ Archivo no encontrado: {filename}")
            else:
                self.add_warning_message("⚠️ Especifica el nombre del archivo a editar")
                
        except Exception as e:
            self.add_error_message(f"❌ Error editando archivo: {str(e)}")

    def edit_file_interactive(self, file_path):
        """Abre editor interactivo para archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
        
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Editando: {file_path.name}")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            
            editor = QPlainTextEdit()
            editor.setPlainText(content)
            layout.addWidget(editor)
            
           
            btn_layout = QHBoxLayout()
            save_btn = QPushButton("💾 Guardar")
            save_btn.clicked.connect(lambda: self.save_edited_file(file_path, editor.toPlainText(), dialog))
            cancel_btn = QPushButton("❌ Cancelar")
            cancel_btn.clicked.connect(dialog.reject)
            
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)
            
            dialog.exec_()
            
        except Exception as e:
            self.add_error_message(f"❌ Error leyendo archivo: {str(e)}")

    def save_edited_file(self, file_path, content, dialog):
        """Guarda el archivo editado"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.add_success_message(f"✅ Archivo guardado: {file_path.name}")
            dialog.accept()
        except Exception as e:
            self.add_error_message(f"❌ Error guardando archivo: {str(e)}")

    def handle_deletion(self, command):
        """Maneja eliminación de archivos/carpetas"""
        try:
            target_name = None
            words = command.split()
            
            delete_keywords = ['elimina', 'borra', 'delete', 'remove']
            for i, word in enumerate(words):
                if word.lower() in delete_keywords and i + 1 < len(words):
                    target_name = words[i + 1]
                    break
            
            if target_name:
                target_path = self.current_directory / target_name
                
                if target_path.exists():
 
                    reply = QMessageBox.question(
                        self, "Confirmar eliminación",
                        f"¿Estás seguro de eliminar: {target_name}?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        if target_path.is_dir():
                            shutil.rmtree(target_path)
                            self.add_success_message(f"✅ Carpeta eliminada: {target_name}")
                        else:
                            target_path.unlink()
                            self.add_success_message(f"✅ Archivo eliminado: {target_name}")
                        
                        self.list_current_directory()
                else:
                    self.add_error_message(f"❌ No encontrado: {target_name}")
            else:
                self.add_warning_message("⚠️ Especifica qué quieres eliminar")
                
        except Exception as e:
            self.add_error_message(f"❌ Error eliminando: {str(e)}")

    def show_system_stats(self):
        """Muestra estadísticas del sistema"""
        try:

            disk_usage = psutil.disk_usage(str(self.current_directory))
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_used_gb = memory.used / (1024**3)
            
            stats_message = f"""
💻 **ESTADÍSTICAS DEL SISTEMA**

📊 **Espacio en disco:**
• Total: {total_gb:.2f} GB
• Usado: {used_gb:.2f} GB ({disk_usage.percent}%)
• Libre: {free_gb:.2f} GB

⚡ **Rendimiento:**
• CPU: {cpu_percent}% utilizado
• Memoria: {memory_used_gb:.2f} GB / {memory_gb:.2f} GB ({memory.percent}%)

📂 **Directorio actual:**
• Ruta: {self.current_directory}
• Archivos: {len(list(self.current_directory.glob('*')))} elementos
"""
            self.add_system_message(stats_message)
            
        except Exception as e:
            self.add_error_message(f"❌ Error obteniendo estadísticas: {str(e)}")

    def execute_system_command(self, command):
        """Ejecuta comandos del sistema"""
        try:

            cmd_text = command.split(' ', 1)[1] if ' ' in command else ""
            
            if cmd_text:
                result = subprocess.run(cmd_text, shell=True, capture_output=True, text=True, cwd=self.current_directory)
                
                output = f"**💻 Ejecutando: `{cmd_text}`**\n\n"
                if result.stdout:
                    output += f"**✅ Salida:**\n```\n{result.stdout}\n```\n"
                if result.stderr:
                    output += f"**❌ Errores:**\n```\n{result.stderr}\n```"
                if not result.stdout and not result.stderr:
                    output += "✅ Comando ejecutado (sin salida)"
                
                self.add_system_message(output)
            else:
                self.add_warning_message("⚠️ Especifica el comando a ejecutar")
                
        except Exception as e:
            self.add_error_message(f"❌ Error ejecutando comando: {str(e)}")


    
    def process_with_ai(self, command):
        """Procesa comandos con el modelo local de DeepSeek"""
        try:
            model_check = self.check_model_structure()
            self.add_system_message(model_check)
            
            self.add_system_message("Procesando con DeepSeek local...")
            
            self.ai_worker = DeepSeekWorker(
                command, 
                self.conversation_history
            )
            self.ai_worker.response_received.connect(self.handle_ai_response)
            self.ai_worker.error_occurred.connect(self.handle_ai_error)
            self.ai_worker.start()
            
        except Exception as e:
            self.add_error_message(f"Error iniciando DeepSeek local: {str(e)}")
    def check_model_structure(self):
        """Verifica la estructura del modelo DeepSeek local"""
        model_path = r"C:\HuggingFace\coder_experto"
        if os.path.exists(model_path):
            try:
                files = os.listdir(model_path)
                return f"✅ Modelo encontrado en: {model_path}\n📁 Archivos: {len(files)} archivos detectados"
            except Exception as e:
                return f"❌ Error accediendo al modelo: {str(e)}"
        else:
            return f"❌ No se encuentra el modelo en: {model_path}\n💡 Descarga el modelo DeepSeek y colócalo en esa ruta"

    def handle_ai_response(self, response):
        """Maneja la respuesta del modelo local - VERSIÓN LIMPIA"""
        self.conversation_history.append({"role": "user", "content": self.last_command})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Mostrar respuesta directamente (ya viene limpia del worker)
        self.add_ai_response(response)
        
        # Procesar comandos especiales
        self.process_ai_commands(response)

    def handle_ai_error(self, error_message):
        """Maneja errores del modelo local"""
        self.add_error_message(f"❌ Error en DeepSeek local: {error_message}")

        self.add_system_message("💡 Alternativas disponibles:")
        self.add_system_message("• Usa comandos directos del sistema")
        self.add_system_message("• Navegación manual de archivos")
        self.add_system_message("• Gestión básica de archivos y carpetas")
    def generate_smart_response(self, command):
        """Genera respuestas inteligentes para comandos no reconocidos"""
        lower_cmd = command.lower()
        
        if '?' in command or 'qué' in lower_cmd or 'cómo' in lower_cmd:
            return f"🤖 Para esa consulta necesitaría conectarme a DeepSeek. Por ahora puedo ayudarte con:\n• Gestión de archivos\n• Comandos del sistema\n• Navegación de directorios"
        
        return f"🔧 **Comando reconocido:** '{command}'\n\n💡 **Sugerencias:**\n• Usa 'lista' para ver archivos\n• 'crea archivo.txt' para crear archivos\n• 'edita nombre.txt' para modificar\n• 'estadísticas' para info del sistema"
    def _add_formatted_message(self, sender, message, color, is_user=False):
        """Añade mensaje formateado al chat - VERSIÓN CORREGIDA"""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        
        # Diseño diferente para usuario vs IA
        if is_user:
            # BURBUJA DE CHAT para el usuario (a la derecha)
            formatted_message = f"""
            <div style="margin: 12px 8px; font-family: 'Segoe UI', Arial, sans-serif;">
                <div style="display: flex; justify-content: flex-end; margin-bottom: 4px;">
                    <div style="text-align: right;">
                        <span style="color: #858585; font-size: 11px; margin-right: 8px;">
                            {timestamp}
                        </span>
                        <span style="font-weight: bold; color: #1976D2; font-size: 13px;">
                            {sender}
                        </span>
                    </div>
                </div>
                <div style="display: flex; justify-content: flex-end;">
                    <div style="background-color: #0084FF; color: white; padding: 12px 16px; 
                            border-radius: 18px 18px 5px 18px; max-width: 70%; 
                            line-height: 1.5; font-size: 13px; white-space: pre-wrap;">
                        {message.replace(chr(10), '<br>')}
                    </div>
                </div>
            </div>
            """
        else:
            # TEXTO NORMAL para la IA (sin burbuja)
            formatted_message = f"""
            <div style="margin: 12px 8px; font-family: 'Segoe UI', Arial, sans-serif;">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span style="font-weight: bold; color: {self._get_sender_color(sender)}; font-size: 13px;">
                        {sender}
                    </span>
                    <span style="color: #858585; font-size: 11px; margin-left: 8px;">
                        {timestamp}
                    </span>
                </div>
                <div style="line-height: 1.5; font-size: 13px; color: #d4d4d4; 
                        white-space: pre-wrap; margin-left: 8px;">
                    {message.replace(chr(10), '<br>')}
                </div>
            </div>
            """
        
        cursor.insertHtml(formatted_message)
        self.chat_history.ensureCursorVisible()
        
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    def add_system_message(self, message):
        self._add_formatted_message("🤖 **Sistema**", message, "#2d2d30")

    def add_success_message(self, message):
        self._add_formatted_message("✅ **Éxito**", message, "#4CAF50")

    def add_warning_message(self, message):
        self._add_formatted_message("⚠️ **Advertencia**", message, "#FF9800")

    def add_error_message(self, message):
        self._add_formatted_message("❌ **Error**", message, "#F44336")

    def add_ai_response(self, message):
        self._add_formatted_message("🤖 **IA**", message, "#388E3C")

    def quick_search(self):
        """Búsqueda rápida de archivos"""
        search_text, ok = QInputDialog.getText(self, "Buscar archivos", "Texto a buscar:")
        if ok and search_text:
            self.handle_search(f"busca {search_text}")

    def handle_search(self, command):
        """Maneja búsqueda de archivos"""
        try:
            search_term = command.split(' ', 1)[1] if ' ' in command else ""
            
            if search_term:
                results = []
                for root, dirs, files in os.walk(self.current_directory):
                    for file in files:
                        if search_term.lower() in file.lower():
                            results.append(Path(root) / file)
                
                if results:
                    message = f"🔍 **Resultados para '{search_term}':**\n\n"
                    for result in results[:10]:  
                        message += f"• {result.relative_to(self.current_directory)}\n"
                    
                    if len(results) > 10:
                        message += f"\n... y {len(results) - 10} más"
                    
                    self.add_system_message(message)
                else:
                    self.add_warning_message(f"❌ No se encontraron archivos con '{search_term}'")
            else:
                self.add_warning_message("⚠️ Especifica qué quieres buscar")
                
        except Exception as e:
            self.add_error_message(f"❌ Error en búsqueda: {str(e)}")

    def open_terminal(self):
        """Abre terminal en el directorio actual"""
        try:
            if os.name == 'nt':  
                subprocess.Popen(f'start cmd /K "cd /d {self.current_directory}"', shell=True)
            else: 
                subprocess.Popen(f'gnome-terminal --working-directory={self.current_directory}', shell=True)
            
            self.add_success_message("✅ Terminal abierto en el directorio actual")
        except Exception as e:
            self.add_error_message(f"❌ Error abriendo terminal: {str(e)}")

    def show_tools_menu(self):
        """Muestra menú de herramientas avanzadas"""
        menu = QMenu(self)
        
        tools = [
            ("📷 Capturar pantalla", self.take_screenshot),
            ("📁 Comprimir archivos", self.compress_files),
            ("🔒 Cambiar permisos", self.change_permissions),
            ("📈 Análisis detallado", self.detailed_analysis)
        ]
        
        for text, action in tools:
            act = QAction(text, self)
            act.triggered.connect(action)
            menu.addAction(act)
        
        menu.exec_(QCursor.pos())

    def take_screenshot(self):
        """Toma captura de pantalla (placeholder)"""
        self.add_system_message("📷 Función de captura de pantalla en desarrollo")

    def compress_files(self):
        """Comprime archivos (placeholder)"""
        self.add_system_message("📁 Función de compresión en desarrollo")

    def change_permissions(self):
        """Cambia permisos (placeholder)"""
        self.add_system_message("🔒 Función de permisos en desarrollo")

    def detailed_analysis(self):
        """Análisis detallado (placeholder)"""
        self.add_system_message("📈 Análisis detallado en desarrollo")

    def load_api_keys(self):
        """Carga las API keys (para futura integración con DeepSeek)"""
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")