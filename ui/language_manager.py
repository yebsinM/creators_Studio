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
    QScrollArea, QFrame, QMessageBox, QProgressDialog, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon, Qt, QColor
from PySide6.QtCore import QSize, QThread, Signal

from PySide6.QtWidgets import QApplication



class LanguageManager(QDialog):

    language_installed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Lenguajes")
        self.setMinimumSize(800, 600)
        self.progress_dialog = None  
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
                "installed": False,
                "version": None
            },
            "Kotlin": {
                "required": True,
                "size": "50 MB", 
                "description": "Requerido para desarrollo Android moderno",
                "installed": False,
                "version": None
            },
            "Dart/Flutter": {
                "required": False,
                "size": "1.2 GB",
                "description": "Para desarrollo multiplataforma con Flutter",
                "installed": False,
                "version": None
            },
            "Python": {
                "required": False,
                "size": "100 MB",
                "description": "Lenguaje versátil para múltiples propósitos",
                "installed": False,
                "version": None
            },
            "C++": {
                "required": False,
                "size": "500 MB",
                "description": "Para desarrollo de alto rendimiento",
                "installed": False,
                "version": None
            },
            "C#": {
                "required": False,
                "size": "200 MB",
                "description": "Para desarrollo con .NET",
                "installed": False,
                "version": None
            }
        }

        self.languages["Java"]["installed"], self.languages["Java"]["version"] = self.check_java_installed()
        self.languages["Kotlin"]["installed"], self.languages["Kotlin"]["version"] = self.check_kotlin_installed()
        self.languages["Dart/Flutter"]["installed"], self.languages["Dart/Flutter"]["version"] = self.check_flutter_installed()
        self.languages["Python"]["installed"], self.languages["Python"]["version"] = self.check_python_installed()
        self.languages["C++"]["installed"], self.languages["C++"]["version"] = self.check_cpp_installed()
        self.languages["C#"]["installed"], self.languages["C#"]["version"] = self.check_csharp_installed()
        
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
        
   
        action_btn.clicked.connect(lambda checked=False, l=lang: self.install_language(l))
        
        layout.addLayout(info_layout, 1)
        layout.addWidget(action_btn)
        
        self.cards_layout.addWidget(card)
        
    def install_language(self, language):
        """Inicia el proceso de instalación para un lenguaje"""
        if language not in self.languages:
            QMessageBox.warning(self, "Error", f"Lenguaje {language} no reconocido")
            return
 
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

        self.install_thread = InstallThread(language)
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
    """Hilo para manejar la instalación de lenguajes"""
    progress_updated = Signal(int, str)
    finished = Signal(bool, str)
    
    def __init__(self, language):
        super().__init__()
        self.language = language
        self._is_cancelled = False
    
    def run(self):
        try:
            print(f"🟢 Hilo de instalación INICIADO para: {self.language}")
            
            if self._is_cancelled:
                print("🔴 Instalación cancelada por usuario")
                self.finished.emit(False, "Instalación cancelada")
                return

            system = platform.system().lower()
            print(f"🔍 Sistema detectado: {system}")

            if self.language == "Java":
                self.progress_updated.emit(10, "Iniciando instalación de Java...")
                
                if system == "windows":
                    self.progress_updated.emit(20, "Buscando última versión de Java...")

                    java_urls = [
                        "https://aka.ms/download-jdk/microsoft-jdk-17-windows-x64.msi",
                        "https://corretto.aws/downloads/latest/amazon-corretto-17-x64-windows-jdk.msi",
                        "https://github.com/adoptium/temurin17-binaries/releases/latest/download/OpenJDK17U-jdk_x64_windows_hotspot_17.0.8_7.msi"
                    ]
                    
                    download_path = os.path.join(os.environ["TEMP"], "jdk_installer.msi")
                    success = False
                    last_error = ""

                    for i, java_url in enumerate(java_urls):
                        if self._is_cancelled:
                            break
                            
                        try:
                            print(f"🔄 Intentando URL {i+1}/{len(java_urls)}: {java_url}")
                            self.progress_updated.emit(30, f"Descargando desde fuente {i+1}...")

                            opener = urllib.request.build_opener()
                            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
                            urllib.request.install_opener(opener)

                            urllib.request.urlretrieve(java_url, download_path)

                            if os.path.exists(download_path):
                                file_size = os.path.getsize(download_path)
                                print(f"📦 Tamaño del archivo: {file_size} bytes")
                                
                                if file_size > 5000000:  
                                    print(f"✅ Éxito con URL {i+1}")
                                    success = True
                                    break
                                else:
                                    os.remove(download_path)
                                    print("❌ Archivo demasiado pequeño, intentando siguiente...")
                                    last_error = "Archivo descargado inválido"
                            else:
                                print("❌ El archivo no se descargó")
                                last_error = "Error en la descarga"
                                
                        except urllib.error.HTTPError as http_err:
                            print(f"❌ Error HTTP {http_err.code} con URL {i+1}")
                            last_error = f"Error HTTP: {http_err.code}"
                            continue
                        except urllib.error.URLError as url_err:
                            print(f"❌ Error URL {url_err.reason} con URL {i+1}")
                            last_error = f"Error de conexión: {url_err.reason}"
                            continue
                        except Exception as e:
                            print(f"❌ Error general con URL {i+1}: {e}")
                            last_error = str(e)
                            continue
                    
                    if not success or self._is_cancelled:
                        error_message = (
                            "No se pudo descargar Java automáticamente.\n\n"
                            f"Último error: {last_error}\n\n"
                            "Por favor instálalo manualmente:\n"
                            "1. Ve a https://adoptium.net/\n"
                            "2. Descarga Java 17 para Windows\n"
                            "3. Ejecuta el instalador\n"
                            "4. Reinicia la aplicación"
                        )
                        self.finished.emit(False, error_message)
                        return

                    self.progress_updated.emit(60, "Instalando Java... (esto puede tomar unos minutos)")
                    try:
                        result = subprocess.run(
                            ["msiexec", "/i", download_path, "/quiet", "/norestart"],
                            capture_output=True,
                            text=True,
                            timeout=600,
                            shell=True
                        )
                        
                        print(f"📊 Código de salida: {result.returncode}")
                        if result.stdout:
                            print(f"📋 Salida: {result.stdout}")
                        if result.stderr:
                            print(f"❌ Error: {result.stderr}")

                        time.sleep(5)

                        java_installed, java_version = self.check_java_installed()
                        
                        if java_installed:
                            self.progress_updated.emit(100, "✅ Java instalado correctamente!")
                            self.finished.emit(True, f"Java {java_version} instalado correctamente")
                        elif result.returncode == 0:
                            self.progress_updated.emit(100, "✅ Java instalado!")
                            self.finished.emit(True, 
                                "Java se instaló pero necesita reiniciar la aplicación para ser detectado.\n"
                                "Por favor cierra y vuelve a abrir el programa."
                            )
                        elif result.returncode == 1603:

                            print("⚠️ Instalación silenciosa falló con error 1603. Ejecutando instalador manual...")
                            self.progress_updated.emit(80, "Error en instalación silenciosa. Abriendo instalador manual...")

                            try:
                                subprocess.Popen([download_path], shell=True)
                                self.finished.emit(False, 
                                    "La instalación silenciosa falló (código 1603).\n\n"
                                    "Se ha abierto el instalador manualmente. Por favor:\n"
                                    "1. Completa la instalación manual\n"
                                    "2. Reinicia la aplicación\n"
                                    "3. Verifica que Java esté instalado"
                                )
                            except Exception as e:
                                self.finished.emit(False, f"No se pudo abrir el instalador manual: {str(e)}")
                        else:
                            error_msg = result.stderr or result.stdout or "Error desconocido"
                            self.finished.emit(False, f"Error en instalación: {error_msg}")
                            
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Tiempo de espera agotado. La instalación tomó demasiado tiempo.")
                    except Exception as e:
                        self.finished.emit(False, f"Error ejecutando instalador: {str(e)}")
                    finally:
                        try:

                            if os.path.exists(download_path):
                                os.remove(download_path)
                                print("🧹 Archivo temporal eliminado")
                        except:
                            pass
                            
                elif system == "linux":
                    self.progress_updated.emit(30, "Instalando Java en Linux...")
                    try:
                        subprocess.run(["sudo", "apt-get", "update"], 
                                     capture_output=True, text=True, timeout=300)
                        
                        result = subprocess.run(
                            ["sudo", "apt-get", "install", "-y", "openjdk-17-jdk"],
                            capture_output=True,
                            text=True,
                            timeout=600
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100, "✅ Java instalado!")
                            self.finished.emit(True, "Java instalado correctamente en Linux")
                        else:
                            self.finished.emit(False, f"Error al instalar Java: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Timeout al instalar Java en Linux")
                    except Exception as e:
                        self.finished.emit(False, f"Error al instalar Java en Linux: {str(e)}")
                
                elif system == "darwin":
                    self.progress_updated.emit(30, "Instalando Java en macOS...")
                    try:
                        result = subprocess.run(
                            ["brew", "install", "--cask", "temurin"],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100, "✅ Java instalado!")
                            self.finished.emit(True, "Java instalado correctamente en macOS")
                        else:
                            self.finished.emit(False, f"Error al instalar Java: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Timeout al instalar Java en macOS")
                    except Exception as e:
                        self.finished.emit(False, f"Error al instalar Java en macOS: {str(e)}")
                
                else:
                    self.finished.emit(False, "Sistema operativo no soportado para Java.")
                    return


            elif self.language == "Kotlin":
                if self._is_cancelled:
                    return
                    
                self.progress_updated.emit(10, "Iniciando instalación de Kotlin...")
                
                if system == "windows":
                    self.progress_updated.emit(20, "Buscando última versión de Kotlin...")
                    

                    kotlin_urls = [
                        "https://github.com/JetBrains/kotlin/releases/latest/download/kotlin-compiler-1.9.0.zip",
                        "https://github.com/JetBrains/kotlin/releases/download/v1.9.0/kotlin-compiler-1.9.0.zip"
                    ]
                    
                    download_path = os.path.join(os.environ["TEMP"], "kotlin-compiler.zip")
                    install_path = os.path.join(os.environ["LOCALAPPDATA"], "Kotlin")
                    success = False
                    last_error = ""
                    
                    for i, kotlin_url in enumerate(kotlin_urls):
                        if self._is_cancelled:
                            break
                            
                        try:
                            print(f"🔄 Intentando URL {i+1}/{len(kotlin_urls)}: {kotlin_url}")
                            self.progress_updated.emit(30, f"Descargando Kotlin desde fuente {i+1}...")

                            opener = urllib.request.build_opener()
                            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
                            urllib.request.install_opener(opener)

                            urllib.request.urlretrieve(kotlin_url, download_path)

                            if os.path.exists(download_path):
                                file_size = os.path.getsize(download_path)
                                print(f"📦 Tamaño del archivo: {file_size} bytes")
                                
                                if file_size > 1000000:  
                                    print(f"✅ Éxito con URL {i+1}")
                                    success = True
                                    break
                                else:
                                    os.remove(download_path)
                                    print("❌ Archivo demasiado pequeño, intentando siguiente...")
                                    last_error = "Archivo descargado inválido"
                            else:
                                print("❌ El archivo no se descargó")
                                last_error = "Error en la descarga"
                                
                        except urllib.error.HTTPError as http_err:
                            print(f"❌ Error HTTP {http_err.code} con URL {i+1}")
                            last_error = f"Error HTTP: {http_err.code}"
                            continue
                        except urllib.error.URLError as url_err:
                            print(f"❌ Error URL {url_err.reason} con URL {i+1}")
                            last_error = f"Error de conexión: {url_err.reason}"
                            continue
                        except Exception as e:
                            print(f"❌ Error general con URL {i+1}: {e}")
                            last_error = str(e)
                            continue
                    
                    if not success or self._is_cancelled:
                        error_message = (
                            "No se pudo descargar Kotlin automáticamente.\n\n"
                            f"Último error: {last_error}\n\n"
                            "Por favor instálalo manualmente:\n"
                            "1. Ve a https://github.com/JetBrains/kotlin/releases/latest\n"
                            "2. Descarga kotlin-compiler-*.zip\n"
                            "3. Extrae y configura manualmente"
                        )
                        self.finished.emit(False, error_message)
                        return

                    self.progress_updated.emit(60, "Extrayendo Kotlin...")
                    try:

                        os.makedirs(install_path, exist_ok=True)

                        with zipfile.ZipFile(download_path, 'r') as zip_ref:
                            zip_ref.extractall(install_path)

                        kotlin_bin_path = None
                        for root, dirs, files in os.walk(install_path):
                            if "bin" in dirs and "kotlin" in files:
                                kotlin_bin_path = os.path.join(root, "bin")
                                break
                        
                        if kotlin_bin_path and os.path.exists(kotlin_bin_path):
                            try:
                                import winreg
                                
                                reg_path = r"Environment"
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as key:
                                    current_path, _ = winreg.QueryValueEx(key, "PATH")

                                if kotlin_bin_path not in current_path:
                                    new_path = f"{current_path};{kotlin_bin_path}" if current_path else kotlin_bin_path
                                    
                                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE) as key:
                                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                                    

                                    try:
                                        import ctypes
                                        from ctypes import wintypes
                                        HWND_BROADCAST = 0xFFFF
                                        WM_SETTINGCHANGE = 0x001A
                                        ctypes.windll.user32.SendMessageTimeoutW(
                                            HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 0, 5000, None
                                        )
                                    except:
                                        pass
                            
                            except Exception as reg_error:
                                print(f"⚠️ Error actualizando registro: {reg_error}")
                            
                            self.progress_updated.emit(100, "✅ Kotlin instalado!")
                            self.finished.emit(True, 
                                f"Kotlin instalado correctamente en: {install_path}\n\n"
                                f"Se agregó al PATH: {kotlin_bin_path}\n"
                                "Reinicia la aplicación para que los cambios surtan efecto."
                            )
                        else:
                            self.finished.emit(False, 
                                "Kotlin se descargó pero no se pudo encontrar el directorio bin.\n"
                                f"Revisa manualmente: {install_path}"
                            )
                            
                    except Exception as e:
                        self.finished.emit(False, f"Error extrayendo Kotlin: {str(e)}")
                    finally:
                        try:
                            if os.path.exists(download_path):
                                os.remove(download_path)
                                print("🧹 Archivo ZIP temporal eliminado")
                        except:
                            pass
                                
                elif system == "linux":
                    if self._is_cancelled:
                        return
                        
                    self.progress_updated.emit(30, "Instalando Kotlin en Linux...")
                    try:

                        result = subprocess.run(
                            ["sudo", "snap", "install", "--classic", "kotlin"],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100, "✅ Kotlin instalado!")
                            self.finished.emit(True, "Kotlin instalado correctamente via snap")
                        else:

                            self.progress_updated.emit(50, "Intentando método alternativo...")
                            install_script = (
                                "curl -s https://get.sdkman.io | bash && "
                                "source \"$HOME/.sdkman/bin/sdkman-init.sh\" && "
                                "sdk install kotlin"
                            )
                            
                            result2 = subprocess.run(
                                ["bash", "-c", install_script],
                                capture_output=True,
                                text=True,
                                timeout=300
                            )
                            
                            if result2.returncode == 0:
                                self.progress_updated.emit(100, "✅ Kotlin instalado!")
                                self.finished.emit(True, "Kotlin instalado correctamente via SDKMAN")
                            else:
                                self.finished.emit(False, f"Error al instalar Kotlin: {result.stderr}\n{result2.stderr}")
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Timeout al instalar Kotlin")
                    except Exception as e:
                        self.finished.emit(False, f"Error al instalar Kotlin: {str(e)}")
                    
                elif system == "darwin":
                    if self._is_cancelled:
                        return
                        
                    self.progress_updated.emit(30, "Instalando Kotlin en macOS...")
                    try:
                        result = subprocess.run(
                            ["brew", "install", "kotlin"],
                            capture_output=True,
                            text=True,
                            timeout=180
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100, "✅ Kotlin instalado!")
                            self.finished.emit(True, "Kotlin instalado correctamente")
                        else:
                            self.finished.emit(False, f"Error al instalar Kotlin: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Timeout al instalar Kotlin")
                    except Exception as e:
                        self.finished.emit(False, f"Error al instalar Kotlin: {str(e)}")
                    
                else:
                    self.finished.emit(False, "Sistema operativo no soportado para Kotlin.")

            elif self.language == "Dart/Flutter":
                self.progress_updated.emit(10, "Iniciando instalación de Flutter...")
                
                if system == "windows":
                    self.progress_updated.emit(30, "Descargando Flutter para Windows...")
                    try:
                        flutter_url = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.13.0-stable.zip"
                        download_path = os.path.join(os.environ["TEMP"], "flutter.zip")

                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(flutter_url, download_path)

                        self.progress_updated.emit(60, "Extrayendo Flutter...")
                        extract_path = os.path.join(os.environ["LOCALAPPDATA"], "flutter")
                        os.makedirs(extract_path, exist_ok=True)
                        
                        with zipfile.ZipFile(download_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_path)

                        self.progress_updated.emit(100, "✅ Flutter instalado!")
                        self.finished.emit(True, 
                            "Flutter instalado correctamente. Por favor reinicia tu aplicación "
                            "y agrega la siguiente ruta a tu variable de entorno PATH:\n"
                            f"{extract_path}\\bin"
                        )
                        
                    except Exception as e:
                        self.finished.emit(False, f"Error instalando Flutter: {str(e)}")
                
                elif system == "linux":
                    self.progress_updated.emit(30, "Instalando Flutter en Linux...")
                    try:

                        flutter_url = "https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.13.0-stable.tar.xz"
                        download_path = os.path.join(tempfile.gettempdir(), "flutter.tar.xz")
                        
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(flutter_url, download_path)

                        self.progress_updated.emit(60, "Extrayendo Flutter...")
                        extract_path = os.path.expanduser("~/flutter")
                        os.makedirs(extract_path, exist_ok=True)
                        
                        subprocess.run(["tar", "-xf", download_path, "-C", extract_path], check=True)
                        
                        self.progress_updated.emit(100, "✅ Flutter instalado!")
                        self.finished.emit(True, 
                            "Flutter instalado correctamente. Agrega la siguiente línea a tu ~/.bashrc:\n"
                            f"export PATH=\"$PATH:{extract_path}/bin\""
                        )
                        
                    except Exception as e:
                        self.finished.emit(False, f"Error instalando Flutter en Linux: {str(e)}")
                
                elif system == "darwin":
                    self.progress_updated.emit(30, "Instalando Flutter en macOS...")
                    try:
                        result = subprocess.run(
                            ["brew", "install", "--cask", "flutter"],
                            capture_output=True,
                            text=True,
                            timeout=600
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100, "✅ Flutter instalado!")
                            self.finished.emit(True, "Flutter instalado correctamente en macOS")
                        else:
                            self.finished.emit(False, f"Error al instalar Flutter: {result.stderr}")
                    except subprocess.TimeoutExpired:
                        self.finished.emit(False, "Timeout al instalar Flutter")
                    except Exception as e:
                        self.finished.emit(False, f"Error al instalar Flutter: {str(e)}")
                
                else:
                    self.finished.emit(False, "Sistema operativo no soportado para Flutter.")
                    return

            elif self.language == "Python":
                self.progress_updated.emit(10, "Verificando Python...")
                
                if system == "windows":
                    self.progress_updated.emit(30, "Instalando Python en Windows...")
                    try:
                        python_url = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
                        download_path = os.path.join(os.environ["TEMP"], "python_installer.exe")
                        
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(python_url, download_path)
                        

                        self.progress_updated.emit(60, "Instalando Python...")
                        result = subprocess.run(
                            [download_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"], 
                            capture_output=True, text=True, timeout=600, shell=True
                        )

                        if result.returncode == 0:
                            self.progress_updated.emit(100, "✅ Python instalado!")
                            self.finished.emit(True, "Python instalado correctamente")
                        else:
                            print(f"⚠️ Instalación silenciosa de Python falló (código {result.returncode})")
                            self.progress_updated.emit(80, "Error en instalación silenciosa. Abriendo instalador manual...")
                            subprocess.Popen([download_path], shell=True)
                            self.finished.emit(False, 
                                "La instalación silenciosa de Python falló.\n"
                                "Se ha abierto el instalador manualmente. Completa la instalación y reinicia la aplicación."
                            )
                    except Exception as e:
                        self.finished.emit(False, f"Error instalando Python: {str(e)}")
                else:
                    self.finished.emit(True, "Python generalmente viene preinstalado en este sistema. Verifica con 'python3 --version'")

            elif self.language == "C++":
                self.progress_updated.emit(10, "Instalando herramientas de compilación C++...")
                
                if system == "windows":
                    self.progress_updated.emit(30, "Instalando Visual Studio Build Tools...")
                    try:

                        try:
                            subprocess.run(["choco", "--version"], capture_output=True, timeout=30)
                        except:
                            self.progress_updated.emit(50, "Instalando Chocolatey...")
                            install_script = (
                                "Set-ExecutionPolicy Bypass -Scope Process -Force; "
                                "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
                                "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
                            )
                            subprocess.run(["powershell", "-Command", install_script], 
                                         timeout=300, shell=True)
                        

                        self.progress_updated.emit(70, "Instalando herramientas de compilación...")
                        subprocess.run(["choco", "install", "visualstudio2019buildtools", "-y"], 
                                     timeout=600, shell=True)
                        
                        self.progress_updated.emit(100, "✅ Herramientas C++ instaladas!")
                        self.finished.emit(True, "Herramientas de compilación C++ instaladas")
                        
                    except Exception as e:
                        self.finished.emit(False, f"Error instalando herramientas C++: {str(e)}")
                
                elif system == "linux":
                    self.progress_updated.emit(30, "Instalando g++ en Linux...")
                    try:
                        result = subprocess.run(
                            ["sudo", "apt-get", "install", "-y", "g++"],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        if result.returncode == 0:
                            self.progress_updated.emit(100, "✅ g++ instalado!")
                            self.finished.emit(True, "Compilador C++ instalado correctamente")
                        else:
                            self.finished.emit(False, f"Error al instalar g++: {result.stderr}")
                    except Exception as e:
                        self.finished.emit(False, f"Error al instalar g++: {str(e)}")
                
                elif system == "darwin":
                    self.progress_updated.emit(30, "Instalando Xcode Command Line Tools...")
                    try:
                        result = subprocess.run(
                            ["xcode-select", "--install"],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        self.progress_updated.emit(100, "✅ Herramientas instaladas!")
                        self.finished.emit(True, "Herramientas de desarrollo instaladas. Puede requerir reinicio.")
                    except Exception as e:
                        self.finished.emit(False, f"Error instalando herramientas: {str(e)}")
                
                else:
                    self.finished.emit(False, "Sistema operativo no soportado para C++.")
                    return

            elif self.language == "C#":
                self.progress_updated.emit(10, "Instalando .NET SDK...")
                
                if system == "windows":
                    self.progress_updated.emit(30, "Descargando .NET SDK...")
                    try:
                        dotnet_url = "https://dotnet.microsoft.com/download/dotnet/thank-you/sdk-7.0.400-windows-x64-installer"
                        download_path = os.path.join(os.environ["TEMP"], "dotnet-sdk.exe")
                        
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(dotnet_url, download_path)

                        self.progress_updated.emit(60, "Instalando .NET SDK...")
                        subprocess.run([download_path, "/install", "/quiet", "/norestart"], 
                                     timeout=600, shell=True)
                        
                        self.progress_updated.emit(100, "✅ .NET SDK instalado!")
                        self.finished.emit(True, ".NET SDK instalado correctamente")
                        
                    except Exception as e:
                        self.finished.emit(False, f"Error instalando .NET: {str(e)}")
                
                elif system in ["linux", "darwin"]:
                    self.progress_updated.emit(30, "Instalando .NET SDK...")
                    try:
               
                        script_url = "https://dot.net/v1/dotnet-install.sh"
                        script_path = os.path.join(tempfile.gettempdir(), "dotnet-install.sh")
                        
                        opener = urllib.request.build_opener()
                        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(script_url, script_path)

                        subprocess.run(["chmod", "+x", script_path])
                        subprocess.run([script_path, "--channel", "LTS"], timeout=300)
                        
                        self.progress_updated.emit(100, "✅ .NET SDK instalado!")
                        self.finished.emit(True, ".NET SDK instalado. Agrega ~/.dotnet a tu PATH")
                        
                    except Exception as e:
                        self.finished.emit(False, f"Error instalando .NET: {str(e)}")
                
                else:
                    self.finished.emit(False, "Sistema operativo no soportado para C#.")
                    return

            else:
                self.finished.emit(False, f"Instalación para {self.language} no implementada aún.")
                return

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ ERROR CRÍTICO: {error_details}")
            self.finished.emit(False, f"Error inesperado: {str(e)}")
    
    def cancel_install(self):
        """Cancela la instalación actual"""
        print("🟡 Cancelando instalación...")
        self._is_cancelled = True
        self.finished.emit(False, "Instalación cancelada por el usuario")
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    manager = LanguageManager()
    manager.show()
    sys.exit(app.exec())
