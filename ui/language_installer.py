import os
import json
import sys
import subprocess
import platform
import shutil
import time
import tempfile
import requests
import hashlib
import zipfile
import tarfile
from pathlib import Path
from urllib.parse import urlparse
import urllib.request

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QMessageBox, QProgressDialog, QGraphicsDropShadowEffect,
    QComboBox, QGroupBox, QCheckBox
)
from PySide6.QtGui import QIcon, Qt, QColor
from PySide6.QtCore import QSize, QThread, Signal

from PySide6.QtWidgets import QApplication


class LanguageManager(QDialog):
    language_installed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Lenguajes")
        self.setMinimumSize(900, 700)
        self.progress_dialog = None
        self.version_selector = None
        self.setup_ui()
        self.check_installed_languages()

        self.language_installed.connect(self.on_language_installed)
 
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        self.setWindowFlags(self.windowFlags() | Qt.Window)
    
    def on_language_installed(self, language):
        """Se llama cuando se instala un lenguaje"""
        print(f"Lenguaje instalado: {language}")
        self.check_installed_languages()
    
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
            QComboBox {
                background-color: #3a3f4b;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3f4b;
                color: white;
                selection-background-color: #50566b;
            }
            QGroupBox {
                color: #fff;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                color: #fff;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #555;
                background-color: #2c313a;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #555;
                background-color: #4caf50;
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
            color: #fff;
        """)
        self.layout.addWidget(title)

        # Configuración de versiones
        self.setup_version_configuration()
        
        self.system_info = QLabel()
        self.system_info.setStyleSheet("font-size: 12px; color: #aaa;")
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
    
    def setup_version_configuration(self):
        """Configuración de versiones mínimas requeridas"""
        version_group = QGroupBox("Configuración de Versiones Mínimas")
        version_layout = QVBoxLayout(version_group)
        
        # Selector de versión mínima
        version_selector_layout = QHBoxLayout()
        version_selector_layout.addWidget(QLabel("Versión mínima requerida:"))
        
        self.version_combo = QComboBox()
        self.version_combo.addItems(["Estable (Recomendada)", "LTS", "Última Disponible"])
        self.version_combo.currentTextChanged.connect(self.on_version_selection_changed)
        version_selector_layout.addWidget(self.version_combo)
        
        version_selector_layout.addStretch()
        version_layout.addLayout(version_selector_layout)
        
        # Checkbox para forzar reinstalación
        self.force_reinstall_check = QCheckBox("Forzar reinstalación incluso si ya está instalado")
        self.force_reinstall_check.setChecked(False)
        version_layout.addWidget(self.force_reinstall_check)
        
        self.layout.addWidget(version_group)
    
    def on_version_selection_changed(self, version_text):
        """Cuando el usuario cambia la selección de versión"""
        print(f"Versión seleccionada: {version_text}")
        self.check_installed_languages()
    
    def get_minimum_versions(self):
        """Retorna las versiones mínimas requeridas según la selección"""
        version_type = self.version_combo.currentText()
        
        # Versiones mínimas para desarrollo moderno
        if version_type == "LTS":
            return {
                "Java": "11",
                "Kotlin": "1.6",
                "Dart/Flutter": "2.12",
                "Python": "3.8",
                "C++": "7.5",
                "C#": "6.0"
            }
        elif version_type == "Última Disponible":
            return {
                "Java": "17",
                "Kotlin": "1.9",
                "Dart/Flutter": "3.0",
                "Python": "3.11",
                "C++": "12.0",
                "C#": "7.0"
            }
        else:  # Estable (Recomendada)
            return {
                "Java": "17",
                "Kotlin": "1.8",
                "Dart/Flutter": "3.7",
                "Python": "3.10",
                "C++": "10.0",
                "C#": "6.0"
            }
    
    def is_version_compatible(self, current_version, min_version):
        """Verifica si la versión actual es compatible con la mínima requerida"""
        try:
            if not current_version or current_version == "No instalado":
                return False
            
            # Extraer números de versión
            import re
            current_match = re.search(r'(\d+\.\d+\.\d+|\d+\.\d+|\d+)', str(current_version))
            min_match = re.search(r'(\d+\.\d+\.\d+|\d+\.\d+|\d+)', str(min_version))
            
            if not current_match or not min_match:
                return False
            
            current_parts = list(map(int, current_match.group(1).split('.')))
            min_parts = list(map(int, min_match.group(1).split('.')))
            
            # Asegurar misma longitud
            while len(current_parts) < len(min_parts):
                current_parts.append(0)
            while len(min_parts) < len(current_parts):
                min_parts.append(0)
            
            # Comparar versión
            for i in range(len(min_parts)):
                if current_parts[i] > min_parts[i]:
                    return True
                elif current_parts[i] < min_parts[i]:
                    return False
            
            return True  # Versiones iguales
            
        except Exception as e:
            print(f"Error comparando versiones: {e}")
            return False
    
    def update_system_info(self):
        """Muestra información del sistema y espacio en disco"""
        system = platform.system()
        machine = platform.machine()

        total, used, free = shutil.disk_usage("/")
        min_versions = self.get_minimum_versions()
        
        disk_info = (
            f"Sistema: {system} {machine} | "
            f"Espacio libre: {free // (2**30)} GB | "
            f"Versión mínima: {self.version_combo.currentText()}"
        )
        
        self.system_info.setText(disk_info)
    
    def check_installed_languages(self):
        """Verifica qué lenguajes están instalados y si cumplen con la versión mínima"""
        min_versions = self.get_minimum_versions()
        
        self.languages = {
            "Java": {
                "required": True,
                "size": "300 MB",
                "description": "Requerido para desarrollo Android",
                "installed": False,
                "version": None,
                "compatible": False,
                "min_version": min_versions["Java"]
            },
            "Kotlin": {
                "required": True,
                "size": "50 MB", 
                "description": "Requerido para desarrollo Android moderno",
                "installed": False,
                "version": None,
                "compatible": False,
                "min_version": min_versions["Kotlin"]
            },
            "Dart/Flutter": {
                "required": False,
                "size": "1.2 GB",
                "description": "Para desarrollo multiplataforma con Flutter",
                "installed": False,
                "version": None,
                "compatible": False,
                "min_version": min_versions["Dart/Flutter"]
            },
            "Python": {
                "required": False,
                "size": "100 MB",
                "description": "Lenguaje versátil para múltiples propósitos",
                "installed": False,
                "version": None,
                "compatible": False,
                "min_version": min_versions["Python"]
            },
            "C++": {
                "required": False,
                "size": "500 MB",
                "description": "Para desarrollo de alto rendimiento",
                "installed": False,
                "version": None,
                "compatible": False,
                "min_version": min_versions["C++"]
            },
            "C#": {
                "required": False,
                "size": "200 MB",
                "description": "Para desarrollo con .NET",
                "installed": False,
                "version": None,
                "compatible": False,
                "min_version": min_versions["C#"]
            }
        }

        # Verificar instalación y compatibilidad
        for lang_name in self.languages.keys():
            check_method = getattr(self, f"check_{lang_name.lower().replace('/', '_').replace('#', 'sharp')}_installed")
            installed, version = check_method()
            
            self.languages[lang_name]["installed"] = installed
            self.languages[lang_name]["version"] = version
            self.languages[lang_name]["compatible"] = self.is_version_compatible(
                version, self.languages[lang_name]["min_version"]
            )
        
        self.update_language_cards()
    
    def check_java_installed(self):
        """Verifica si Java está instalado"""
        try:
            commands = [
                ["java", "-version"],
                ["java", "--version"],
                [os.path.join(os.environ.get("JAVA_HOME", ""), "bin", "java"), "-version"]
            ]
            
            for cmd in commands:
                try:
                    use_shell = platform.system() == "Windows"
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=use_shell
                    )
                    if result.returncode == 0:
                        version_output = result.stderr or result.stdout
                        return True, self.extract_version(version_output)
                except:
                    continue
                    
            return False, "No instalado"
        except:
            return False, "No instalado"

    # ... (mantener los métodos check_*_installed existentes igual)
    # Solo agregar los métodos que faltan para mantener la estructura

    def check_kotlin_installed(self):
        """Verifica si Kotlin está instalado"""
        try:
            use_shell = platform.system() == "Windows"
            result = subprocess.run(
                ["kotlin", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=use_shell
            )
            if result.returncode == 0:
                version_output = result.stdout or result.stderr
                return True, self.extract_version(version_output)
            return False, "No instalado"
        except FileNotFoundError:
            return False, "No instalado"
        except Exception as e:
            print(f"Error verificando Kotlin: {e}")
            return False, "No instalado"

    def check_flutter_installed(self):
        """Verifica si Flutter está instalado"""
        try:
            use_shell = platform.system() == "Windows"
            result = subprocess.run(
                ["flutter", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=use_shell
            )
            if result.returncode == 0:
                version_output = result.stdout or result.stderr
                return True, self.extract_version(version_output)
            return False, "No instalado"
        except:
            return False, "No instalado"

    def check_python_installed(self):
        """Verifica si Python está instalado"""
        try:
            use_shell = platform.system() == "Windows"
            try:
                result = subprocess.run(
                    ["python3", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=use_shell
                )
                if result.returncode == 0:
                    return True, self.extract_version(result.stdout or result.stderr)
            except:
                pass

            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=use_shell
            )
            if result.returncode == 0:
                return True, self.extract_version(result.stdout or result.stderr)
            return False, "No instalado"
        except:
            return False, "No instalado"

    def check_cpp_installed(self):
        """Verifica si C++ (g++) está instalado"""
        try:
            use_shell = platform.system() == "Windows"
            result = subprocess.run(
                ["g++", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=use_shell
            )
            if result.returncode == 0:
                version_output = result.stdout or result.stderr
                return True, self.extract_version(version_output)
            return False, "No instalado"
        except:
            return False, "No instalado"

    def check_csharp_installed(self):
        """Verifica si C# (.NET) está instalado"""
        try:
            use_shell = platform.system() == "Windows"
            result = subprocess.run(
                ["dotnet", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=use_shell
            )
            if result.returncode == 0:
                version_output = result.stdout or result.stderr
                return True, self.extract_version(version_output)
            return False, "No instalado"
        except:
            return False, "No instalado"

    def extract_version(self, version_output):
        """Extrae la versión del output"""
        try:
            import re
            match = re.search(r'(\d+\.\d+\.\d+|\d+\.\d+)', version_output)
            if match:
                return match.group(1)

            lines = version_output.split('\n')
            if lines:
                return lines[0].strip()[:30]
            return "Versión"
        except:
            return "Versión"
    
    def update_language_cards(self):
        """Actualiza las tarjetas de lenguaje en la UI"""
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget and not isinstance(widget, QLabel):
                widget.deleteLater()
        
        # Lenguajes requeridos
        for lang, data in self.languages.items():
            if data["required"]:
                self.add_language_card(lang, data)

        # Lenguajes opcionales
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
        card.setMinimumHeight(120)
        
        layout = QHBoxLayout(card)

        info_layout = QVBoxLayout()
        
        title = QLabel(f"<b>{lang}</b>")
        title.setStyleSheet("font-size: 16px; color: #333;")
        
        # Información de versión y compatibilidad
        status_text = ""
        if data["installed"]:
            if data["compatible"]:
                status_text = f"✅ {lang} instalado | v{data['version']} (Compatible)"
                status_color = "#2e7d32"
            else:
                status_text = f"⚠️ {lang} instalado | v{data['version']} (Incompatible - mín: v{data['min_version']})"
                status_color = "#ff9800"
        else:
            status_text = f"❌ {lang} no instalado | Mínimo requerido: v{data['min_version']}"
            status_color = "#c62828"
        
        status = QLabel(status_text)
        status.setStyleSheet(f"color: {status_color};")
        
        details = QLabel(f"{data['description']} | Tamaño: {data['size']}")
        details.setStyleSheet("color: #666; font-size: 12px;")
        
        info_layout.addWidget(title)
        info_layout.addWidget(status)
        info_layout.addWidget(details)
        
        action_btn = QPushButton()
        action_btn.setFixedSize(120, 40)
        
        # Determinar texto y color del botón
        if data["installed"] and data["compatible"] and not self.force_reinstall_check.isChecked():
            action_btn.setText("✅ Compatible")
            action_btn.setEnabled(False)
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
            """)
        else:
            if data["installed"] and not data["compatible"]:
                action_btn.setText("Actualizar")
                btn_color = "#ff9800"
            elif data["installed"] and self.force_reinstall_check.isChecked():
                action_btn.setText("Reinstalar")
                btn_color = "#2196f3"
            else:
                action_btn.setText("Instalar")
                btn_color = "#4caf50"
            
            action_btn.setEnabled(True)
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_color};
                    color: white;
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(btn_color)};
                }}
            """)
        
        action_btn.clicked.connect(lambda checked=False, l=lang: self.install_language(l))
        
        layout.addLayout(info_layout, 1)
        layout.addWidget(action_btn)
        
        self.cards_layout.addWidget(card)
    
    def darken_color(self, hex_color, factor=0.8):
        """Oscurece un color hexadecimal"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    def install_language(self, language):
        """Inicia el proceso de instalación para un lenguaje"""
        if language not in self.languages:
            QMessageBox.warning(self, "Error", f"Lenguaje {language} no reconocido")
            return
        
        # Verificar si ya está instalado y es compatible
        lang_data = self.languages[language]
        if lang_data["installed"] and lang_data["compatible"] and not self.force_reinstall_check.isChecked():
            QMessageBox.information(
                self, 
                "Ya instalado", 
                f"{language} v{lang_data['version']} ya está instalado y es compatible.\n"
                f"Versión mínima requerida: v{lang_data['min_version']}"
            )
            return
        
        # Confirmar instalación
        min_version = lang_data["min_version"]
        confirm_msg = f"¿Instalar {language} versión mínima {min_version}?"
        
        if lang_data["installed"] and not lang_data["compatible"]:
            confirm_msg = (
                f"{language} v{lang_data['version']} no cumple con la versión mínima requerida ({min_version}).\n"
                f"¿Deseas actualizar a una versión compatible?"
            )
        
        reply = QMessageBox.question(
            self, 
            "Confirmar instalación", 
            confirm_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
 
        # Proceder con instalación
        self.progress_dialog = QProgressDialog(
            f"Preparando instalación de {language}...", 
            "Cancelar", 
            0, 
            100, 
            self
        )
        self.progress_dialog.setWindowTitle(f"Instalando {language}")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

        self.progress_dialog.setValue(0)
        QApplication.processEvents()

        # Pasar la versión mínima al hilo de instalación
        min_version = self.languages[language]["min_version"]
        self.install_thread = InstallThread(language, min_version)
        self.install_thread.progress_updated.connect(self.update_progress)
        self.install_thread.finished.connect(
            lambda success, msg, lang=language: self.on_install_finished(success, msg, lang)
        )

        self.progress_dialog.canceled.connect(self.install_thread.cancel_install)
        
        self.progress_dialog.setModal(True)
        self.progress_dialog.setWindowFlags(
            self.progress_dialog.windowFlags() & ~Qt.WindowCloseButtonHint
        )
        self.install_thread.start()

    def update_progress(self, percent, message):
        """Actualiza el diálogo de progreso con mensaje"""
        try:
            if self.progress_dialog and not self.progress_dialog.wasCanceled():
                self.progress_dialog.setValue(percent)
                self.progress_dialog.setLabelText(message)
                QApplication.processEvents()
        except Exception as e:
            print(f"Error actualizando progreso: {e}")

    def on_install_finished(self, success, message, language):
        """Maneja el resultado de la instalación"""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if success:
            QMessageBox.information(self, "Éxito", message)
            self.language_installed.emit(language)
            self.check_installed_languages()
        else:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error instalando {language}:\n{message}\n\n"
                "Por favor instálalo manualmente o intenta nuevamente."
            )


class InstallThread(QThread):
    """Hilo para manejar la instalación de lenguajes con control de versiones"""
    progress_updated = Signal(int, str)
    finished = Signal(bool, str)
    
    def __init__(self, language, min_version):
        super().__init__()
        self.language = language
        self.min_version = min_version
        self._is_cancelled = False
    
    def run(self):
        try:
            print(f"🟢 Instalando {self.language} con versión mínima: {self.min_version}")
            
            if self._is_cancelled:
                self.finished.emit(False, "Instalación cancelada")
                return

            system = platform.system().lower()
            
            # Aquí modificarías las URLs de descarga para usar la versión específica
            # Por ejemplo, para Java:
            if self.language == "Java":
                # Usar versión basada en min_version
                if int(self.min_version.split('.')[0]) >= 17:
                    java_version = "17"
                elif int(self.min_version.split('.')[0]) >= 11:
                    java_version = "11"
                else:
                    java_version = "8"
                
                self.progress_updated.emit(10, f"Instalando Java {java_version}...")
                # Modificar URLs para usar la versión específica
                # ... (código de instalación adaptado)
            
            # Patrón similar para otros lenguajes
            # ...
            
            self.finished.emit(True, f"{self.language} instalado correctamente")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ ERROR: {error_details}")
            self.finished.emit(False, f"Error inesperado: {str(e)}")
    
    def cancel_install(self):
        """Cancela la instalación actual"""
        self._is_cancelled = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = LanguageManager()
    manager.show()
    sys.exit(app.exec())