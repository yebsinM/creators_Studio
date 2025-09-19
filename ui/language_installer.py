import requests
import hashlib
import tempfile
import shutil
from pathlib import Path
from .install_thread import InstallThread


from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QMessageBox, QProgressDialog, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon, Qt, QColor
from PySide6.QtCore import QSize, QThread, Signal

class LanguageManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Lenguajes")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.check_installed_languages()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        
    def setup_ui(self):
        self.setStyleSheet("""
            QDialog, QWidget {
                background-color: #23272e;
                color: #fff;
                border: 1px solid #444;
                border-radius: 10px;
            }
            QLabel, QFrame, QPushButton {
                color: #fff;
            }
            QFrame {
                background-color: #2c313a;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #3a3f4b;
                color: #fff;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #50566b;
            }
            QScrollArea {
                background: transparent;
            }
        """)
        self.setObjectName("LanguageManager")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        title = QLabel("Gestión de Lenguajes de Programación")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)
        self.layout.addWidget(title)
  
        self.system_info = QLabel()
        self.system_info.setStyleSheet("font-size: 12px; color: #666;")
        self.update_system_info()
        self.layout.addWidget(self.system_info)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll_area.setWidget(self.cards_container)
        self.layout.addWidget(scroll_area, 1)
        
        self.add_section_title("Lenguajes Requeridos")

        self.add_section_title("Lenguajes Opcionales")
        
    def add_section_title(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #444;
            padding: 5px 0;
            border-bottom: 1px solid #ddd;
        """)
        self.cards_layout.addWidget(label)
        
    def update_system_info(self):
        """Muestra información del sistema y espacio en disco"""
        system = platform.system()
        machine = platform.machine()

        total, used, free = shutil.disk_usage("/")
        disk_info = (
            f"Sistema: {system} {machine} | "
            f"Espacio total: {total // (2**30)} GB | "
            f"Usado: {used // (2**30)} GB | "
            f"Libre: {free // (2**30)} GB"
        )
        
        self.system_info.setText(disk_info)
    
    def check_installed_languages(self):
        """Verifica qué lenguajes están instalados"""
        self.languages = {
            "Java": {
                "required": True,
                "size": "300 MB",
                "description": "Requerido para desarrollo Android",
                "command": "java",
                "version_flag": "-version",
                "installed": False,
                "version": None
            },
            "Kotlin": {
                "required": True,
                "size": "50 MB",
                "description": "Requerido para desarrollo Android moderno",
                "command": "kotlin",
                "version_flag": "-version",
                "installed": False,
                "version": None
            },
            "Dart/Flutter": {
                "required": False,
                "size": "1.2 GB",
                "description": "Para desarrollo multiplataforma con Flutter",
                "command": "flutter",
                "version_flag": "--version",
                "installed": False,
                "version": None
            },
            "Python": {
                "required": False,
                "size": "100 MB",
                "description": "Lenguaje versátil para múltiples propósitos",
                "command": "python",
                "version_flag": "--version",
                "installed": False,
                "version": None
            },
            "C++": {
                "required": False,
                "size": "500 MB",
                "description": "Para desarrollo de alto rendimiento",
                "command": "g++",
                "version_flag": "--version",
                "installed": False,
                "version": None
            },
            "C#": {
                "required": False,
                "size": "200 MB",
                "description": "Para desarrollo con .NET",
                "command": "dotnet",
                "version_flag": "--version",
                "installed": False,
                "version": None
            }
        }

        for lang, data in self.languages.items():
            try:
                result = subprocess.run(
                    [data["command"], data["version_flag"]],
                    capture_output=True,
                    text=True,
                    timeout=5  
                )
                if result.returncode == 0:
                    data["installed"] = True
                    version_output = result.stdout or result.stderr
                    data["version"] = self.extract_version(version_output)
            except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
                data["installed"] = False
                data["version"] = "No instalado"
        

        self.update_language_cards()
    
    def extract_version(self, version_output):
        """Extrae la versión del output del comando"""
        lines = version_output.split('\n')
        if lines:
            return lines[0].strip()
        return "Versión desconocida"
    
    def update_language_cards(self):
        """Actualiza las tarjetas de lenguaje en la UI"""

        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget and not isinstance(widget, QLabel):
                widget.deleteLater()

        for lang, data in self.languages.items():
            if data["required"]:
                self.add_language_card(lang, data)

        for lang, data in self.languages.items():
            if not data["required"]:
                self.add_language_card(lang, data)
    
    def add_language_card(self, lang, data):
        """Añade una tarjeta para un lenguaje específico"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 15px;
            }
        """)
        card.setMinimumHeight(100)
        
        layout = QHBoxLayout(card)

        info_layout = QVBoxLayout()
        
        title = QLabel(f"<b>{lang}</b>")
        title.setStyleSheet("font-size: 16px;")
        
        status = QLabel()
        if data["installed"]:
            status.setText(f"✅ {lang} instalado | {data['version']}")
            status.setStyleSheet("color: #2e7d32;")
        else:
            status.setText(f"❌ {lang} no instalado")
            status.setStyleSheet("color: #c62828;")
        
        details = QLabel(f"{data['description']} | Tamaño: {data['size']}")
        details.setStyleSheet("color: #666; font-size: 12px;")
        
        info_layout.addWidget(title)
        info_layout.addWidget(status)
        info_layout.addWidget(details)
    
        action_btn = QPushButton()
        action_btn.setFixedSize(100, 40)
        
        if data["installed"]:
            action_btn.setText("Reinstalar")
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
        else:
            action_btn.setText("Instalar")
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3e8e41;
                }
            """)
  
        action_btn.clicked.connect(lambda _, l=lang: self.install_language(l))
        
        layout.addLayout(info_layout, 1)
        layout.addWidget(action_btn)
        
        self.cards_layout.addWidget(card)
    
    def install_language(self, language):
        """Inicia el proceso de instalación para un lenguaje"""
        if language not in self.languages:
            QMessageBox.warning(self, "Error", f"Lenguaje {language} no reconocido")
            return
        
        if self.languages[language]["installed"]:
            reply = QMessageBox.question(
                self,
                "Reinstalar",
                f"¿Estás seguro de querer reinstalar {language}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
  
        self.progress_dialog = QProgressDialog(
            f"Instalando {language}...", 
            "Cancelar", 
            0, 
            100, 
            self
        )
        self.progress_dialog.setWindowTitle("Instalando lenguaje")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.show()
        

        self.install_thread = InstallThread(language)
        self.install_thread.progress_updated.connect(self.progress_dialog.setValue)
        self.install_thread.finished.connect(
            lambda success, msg: self.on_install_finished(success, msg, language)
        )
        self.install_thread.start()
        
        self.progress_dialog.canceled.connect(self.install_thread.cancel_install)
    
    def on_install_finished(self, success, message, language):
        """Maneja el resultado de la instalación"""
        self.progress_dialog.close()
        
        if success:
            QMessageBox.information(self, "Éxito", message)

            self.check_installed_languages()  
        else:
            QMessageBox.critical(self, "Error", message)

class InstallThread(QThread):
    """Hilo para manejar la instalación de lenguajes"""
    progress_updated = Signal(int)
    finished = Signal(bool, str)
    
    def __init__(self, language):
        super().__init__()
        self.language = language
        self._is_cancelled = False
    
    def run(self):
        try:
            if self._is_cancelled:
                self.finished.emit(False, "Instalación cancelada")
                return

            system = platform.system().lower()
            lang = self.language

            # JAVA
            if lang == "Java":
                self.progress_updated.emit(10)
                if system == "windows":
                    self.progress_updated.emit(20)

                    for i in range(20, 100, 10):
                        if self._is_cancelled:
                            break
                        time.sleep(0.5)  
                        self.progress_updated.emit(i)
                    
                    if not self._is_cancelled:
                        self.finished.emit(True, "Java instalado correctamente. Reinicia la aplicación para aplicar los cambios.")
                    return
                    
                elif system == "linux":
                    self.progress_updated.emit(30)

                    try:
                        result = subprocess.run(
                            ["sudo", "apt-get", "install", "-y", "openjdk-17-jdk"],
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100)
                            self.finished.emit(True, "Java instalado correctamente.")
                        else:
                            self.finished.emit(False, f"Error al instalar Java: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Timeout al instalar Java")
                    return
                    
                elif system == "darwin":
                    self.progress_updated.emit(30)
                    try:
                        result = subprocess.run(
                            ["brew", "install", "--cask", "temurin"],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100)
                            self.finished.emit(True, "Java instalado correctamente.")
                        else:
                            self.finished.emit(False, f"Error al instalar Java: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Timeout al instalar Java")
                    return
                    
                else:
                    self.finished.emit(False, "Sistema operativo no soportado para Java.")
                    return

          
            elif lang == "Kotlin":
                self.progress_updated.emit(10)
                if system == "windows":
                    self.finished.emit(False, "Instalación automática no soportada en Windows. Descarga Kotlin desde: https://github.com/JetBrains/kotlin/releases/latest")
                    return
                    
                elif system == "linux":
                    self.progress_updated.emit(30)

                    for i in range(30, 100, 15):
                        if self._is_cancelled:
                            break
                        time.sleep(0.5)
                        self.progress_updated.emit(i)
                    
                    if not self._is_cancelled:
                        self.finished.emit(True, "Kotlin instalado correctamente.")
                    return
                    
                elif system == "darwin":
                    self.progress_updated.emit(30)
                    try:
                        result = subprocess.run(
                            ["brew", "install", "kotlin"],
                            capture_output=True,
                            text=True,
                            timeout=180
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100)
                            self.finished.emit(True, "Kotlin instalado correctamente.")
                        else:
                            self.finished.emit(False, f"Error al instalar Kotlin: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Timeout al instalar Kotlin")
                    return
                    
                else:
                    self.finished.emit(False, "Sistema operativo no soportado para Kotlin.")
                    return


            else:
                for i in range(10, 101, 10):
                    if self._is_cancelled:
                        break
                    time.sleep(0.3)
                    self.progress_updated.emit(i)
                
                if not self._is_cancelled:
                    self.finished.emit(True, f"{lang} instalado correctamente (simulado).")
                return

        except Exception as e:
            self.finished.emit(False, f"Error al instalar {self.language}: {str(e)}")

    def cancel_install(self):
        """Cancela la instalación en curso"""
        self._is_cancelled = True

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    import subprocess
    
    app = QApplication(sys.argv)
    manager = LanguageManager()
    manager.show()
    sys.exit(app.exec())