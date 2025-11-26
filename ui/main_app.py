import json
import sys 
import os
import datetime
from pathlib import Path
import subprocess

# ===== NUEVAS IMPORTACIONES CORREGIDAS =====
# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

def get_illustrator_window():
    """Función para importar IllustratorWindow"""
    try:
        # Intentar desde modules
        from modules.workspace import IllustratorWindow
        print("✅ IllustratorWindow cargado desde modules/workspace.py")
        return IllustratorWindow
    except ImportError as e:
        print(f"❌ Error desde modules: {e}")
    
    try:
        # Intentar desde archivo principal
        from entorno_java_main import IllustratorWindow
        print("✅ IllustratorWindow cargado desde entorno_java_main.py")
        return IllustratorWindow
    except ImportError as e:
        print(f"❌ Error desde entorno_java_main: {e}")
    
    try:
        # Intentar desde archivo legacy
        from entorno_java import IllustratorWindow
        print("✅ IllustratorWindow cargado desde entorno_java.py")
        return IllustratorWindow
    except ImportError as e:
        print(f"❌ Error desde entorno_java: {e}")
    
    # Si todo falla, crear clase dummy
    print("⚠️ Usando clase DummyIllustratorWindow")
    from PySide6.QtWidgets import QMainWindow
    
    class DummyIllustratorWindow(QMainWindow):
        def __init__(self, project_name="Dummy", project_path=None, project_language="Java"):
            super().__init__()
            self.setWindowTitle(f"Dummy: {project_name}")
            self.setMinimumSize(800, 600)
        
        def showMaximized(self):
            self.show()
            self.resize(1200, 800)
    
    return DummyIllustratorWindow

# Obtener IllustratorWindow dinámicamente
IllustratorWindow = get_illustrator_window()
# ===== FIN NUEVAS IMPORTACIONES =====

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QMenu, QMainWindow, QFileDialog, QComboBox,
    QApplication, QFrame, QSpacerItem, QSizePolicy, QStackedWidget,
    QGroupBox, QRadioButton, QCheckBox, QListWidget, QSplitter,
    QScrollArea, QMessageBox, QDialog, QListWidgetItem, QInputDialog  
)
from PySide6.QtGui import (
    QIcon, QCursor, QColor, QPainter, QBrush, 
    QRadialGradient, QPen, QMouseEvent, QFont
)
from PySide6.QtCore import (
    Qt, QPoint, QSize, Property, QPropertyAnimation, 
    QEvent, QEasingCurve, QRect, QTimer, QSettings, QThread, Signal
)

class PathManager:
    def __init__(self):
        self.rutas_file = Path("rutas.txt")
        self.ensure_rutas_file()
    
    def ensure_rutas_file(self):
        """Crea el archivo rutas.txt si no existe"""
        if not self.rutas_file.exists():
            with open(self.rutas_file, 'w', encoding='utf-8') as f:
                f.write("# Archivo de rutas de proyectos Creators Studio\n")
                f.write("# Formato: nombre_proyecto|ruta_completa\n")

    def add_project_path(self, project_name, project_path):
        absolute_path = os.path.abspath(project_path)
        
        with open(self.rutas_file, 'a', encoding='utf-8') as f:
            f.write(f"{project_name}|{absolute_path}\n")
    
    def get_all_projects(self):
        """Obtiene todos los proyectos del archivo de rutas"""
        projects = []
        if self.rutas_file.exists():
            with open(self.rutas_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('|', 1)
                        if len(parts) == 2:
                            name, path = parts
                            projects.append({"name": name, "path": path})
        return projects
    
    def get_project_path(self, project_name, exact_match=True):
        """Obtiene la ruta de un proyecto por nombre"""
        projects = self.get_all_projects()
        for project in projects:
            if exact_match:
                if project["name"] == project_name:
                    return project["path"]
            else:
                if project_name in project["name"]:
                    return project["path"]
        return None
    
    def get_projects_by_name(self, project_name):
        """Obtiene todos los proyectos que coinciden con el nombre"""
        projects = self.get_all_projects()
        return [p for p in projects if p["name"] == project_name]
    
    def remove_project(self, project_name, project_path):
        """Elimina un proyecto del archivo de rutas"""
        if not self.rutas_file.exists():
            return False

        lines = []
        with open(self.rutas_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
 
        new_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                parts = line.split('|', 1)
                if len(parts) == 2:
                    name, path = parts
                    if name.strip() == project_name and path.strip() == project_path:
                        continue 
            new_lines.append(line)
 
        with open(self.rutas_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return True

path_manager = PathManager()

class GradientWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            center = self.rect().center()
            radius = max(self.width(), self.height()) * 1.2
            gradient = QRadialGradient(center, radius)
            gradient.setColorAt(0, QColor(50, 50, 50))
            gradient.setColorAt(0.7, QColor(15, 15, 15))
            gradient.setColorAt(1, QColor(0, 0, 0))
            painter.setRenderHint(QPainter.Antialiasing)
            painter.fillRect(self.rect(), QBrush(gradient))
        finally:
            painter.end()

class BackButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #555555;
                border-radius: 15px;
                padding: 0px;
                background-color: #333333;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(os.path.join("assets", "back_arrow.png")))
        self.setIconSize(QSize(16, 16))

class UserProfileButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.setStyleSheet("""
            QPushButton {
                border: 2px solid white;
                border-radius: 20px;
                padding: 0px;
                background-color: transparent;
            }
            QPushButton:hover {
                border: 2px solid #BB86FC;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(os.path.join("assets", "default_user.png")))
        self.setIconSize(QSize(36, 36))
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #BB86FC;
                color: black;
            }
        """)
        self.logout_action = self.menu.addAction("Cerrar sesión")
        self.logout_action.setIcon(QIcon(os.path.join("assets", "logout.png")))
        self.clicked.connect(self.show_menu)
    
    def show_menu(self):
        self.menu.exec_(self.mapToGlobal(QPoint(0, self.height())))

class ProjectSetupWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 20, 40, 20)
        self.layout.setSpacing(20)
 
        self.name_label = QLabel("Nombre de tu Proyecto:")
        self.name_label.setStyleSheet("color: white; font-size: 14px;")
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.name_input.setFixedHeight(35)

        self.location_label = QLabel("Ubicación de tu Proyecto:")
        self.location_label.setStyleSheet("color: white; font-size: 14px;")
        self.location_layout = QHBoxLayout()
        self.location_input = QLineEdit()
        self.location_input.setStyleSheet(self.name_input.styleSheet())
        self.location_input.setFixedHeight(35)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px 12px;
                min-width: 80px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.browse_btn.setFixedHeight(35)
        self.browse_btn.clicked.connect(self.browse_location)
        self.location_layout.addWidget(self.location_input)
        self.location_layout.addWidget(self.browse_btn)
        
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.location_label)
        self.layout.addLayout(self.location_layout)
        
    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if folder:
            self.location_input.setText(folder)

class AndroidSetupWidget(ProjectSetupWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("MiEmpresa", "MiApp")
        self.projects_dir = Path.home() / ".myapp_projects"
        self.setup_android_specific_ui()
        self.load_last_location()
        self.progress_msg = None
    
    def setup_android_specific_ui(self):
        self.layout.setContentsMargins(40, 20, 40, 20)
        self.layout.setSpacing(20)

        self.language_label = QLabel("Lenguaje:")
        self.language_label.setStyleSheet("color: white; font-size: 14px;")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Java", "Kotlin", "Dart (Flutter)"])
        self.language_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.language_combo.setFixedHeight(35)

        self.device_group = QGroupBox("Target Device")
        self.device_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 14px;
            }
        """)
        self.device_layout = QVBoxLayout()
        self.device_layout.setContentsMargins(15, 15, 15, 15)
        self.device_layout.setSpacing(10)
        
        self.emulator_radio = QRadioButton("Use Emulator")
        self.emulator_radio.setChecked(True)
        self.emulator_radio.setStyleSheet("color: white; font-size: 14px;")
        
        self.physical_radio = QRadioButton("Use Physical Device")
        self.physical_radio.setStyleSheet("color: white; font-size: 14px;")
        
        self.emulator_combo = QComboBox()
        self.emulator_combo.addItems([
            "Pixel 6 - API 33",
            "Pixel 5 - API 31",
            "Pixel 4 - API 30",
            "Nexus 5 - API 28"
        ])
        self.emulator_combo.setStyleSheet(self.language_combo.styleSheet())
        self.emulator_combo.setFixedHeight(35)
        
        self.device_layout.addWidget(self.emulator_radio)
        self.device_layout.addWidget(self.emulator_combo)
        self.device_layout.addWidget(self.physical_radio)
        self.device_group.setLayout(self.device_layout)
        
        self.options_group = QGroupBox("Additional Options")
        self.options_group.setStyleSheet(self.device_group.styleSheet())
        self.options_layout = QVBoxLayout()
        self.options_layout.setContentsMargins(15, 15, 15, 15)
        self.options_layout.setSpacing(10)
        
        self.instant_run_check = QCheckBox("Enable Instant Run")
        self.instant_run_check.setChecked(True)
        self.instant_run_check.setStyleSheet("color: white; font-size: 14px;")
        
        self.vector_drawable_check = QCheckBox("Enable Vector Drawables")
        self.vector_drawable_check.setChecked(True)
        self.vector_drawable_check.setStyleSheet("color: white; font-size: 14px;")
        
        self.options_layout.addWidget(self.instant_run_check)
        self.options_layout.addWidget(self.vector_drawable_check)
        self.options_group.setLayout(self.options_layout)

        self.create_btn = QPushButton("Create Android Project")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #BB86FC;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-weight: bold;
                font-size: 16px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #A370D8;
            }
        """)
        self.create_btn.setFixedWidth(250)
        self.create_btn.clicked.connect(self.create_project)

        btn_container = QWidget()
        btn_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()
        btn_layout.addWidget(self.create_btn)
        btn_layout.addStretch()

        self.layout.addWidget(self.language_label)
        self.layout.addWidget(self.language_combo)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.device_group)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.options_group)
        self.layout.addStretch(1)
        self.layout.addWidget(btn_container)
        self.layout.addSpacing(20)
    
    def load_last_location(self):
        last_location = self.settings.value("last_project_location", "")
        if last_location and os.path.isdir(last_location):
            self.location_input.setText(last_location)
            
    def save_last_location(self):
        location = self.location_input.text()
        if location and os.path.isdir(location):
            self.settings.setValue("last_project_location", location)
    
    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Project Directory",
            self.settings.value("last_project_location", "")
        )
        if folder:
            self.location_input.setText(folder)
            self.save_last_location()

    def check_language_installed(self, language):
        """Verifica si el lenguaje seleccionado está instalado y en la versión correcta"""
        try:
            if language == "Java":
                result = subprocess.run(["java", "-version"], stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    version_output = result.stderr.lower()
                    if 'jdk' in version_output:  
                        version_line = version_output.split('\n')[0]
                        version = version_line.split(' ')[2].replace('"', '')
                        major_version = int(version.split('.')[0])
                        return major_version in [11, 17] 
                return False
                
            elif language == "Kotlin":
                result = subprocess.run(["kotlin", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    version_output = result.stderr or result.stdout
                    if 'version' in version_output.lower():
                        version = version_output.split()[2].split('-')[0]
                        major_version = int(version.split('.')[0])
                        return major_version >= 1 
                return False
                
            elif language == "Dart (Flutter)":
                try:
                    result = subprocess.run(["flutter", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.returncode == 0:
                        version_line = result.stdout.split('\n')[0]
                        if 'flutter' in version_line.lower():
                            return True
                except FileNotFoundError:
                    pass
                return False
                
        except Exception as e:
            print(f"Error verificando {language}: {e}")
            return False
        
    def create_project(self):
        if not self.name_input.text().strip():
            QMessageBox.critical(self, "Error", "El nombre del proyecto es requerido")
            return
            
        if not self.location_input.text().strip():
            QMessageBox.critical(self, "Error", "La ubicación del proyecto es requerida")
            return
            
        if not os.path.isdir(self.location_input.text()):
            QMessageBox.critical(self, "Error", "La ubicación especificada no existe")
            return
        
        project_name = self.name_input.text().strip()

        if self.check_project_name_exists(project_name):
            QMessageBox.warning(
                self, 
                "Nombre duplicado", 
                f"Ya existe un proyecto con el nombre '{project_name}'. "
                "Por favor elige un nombre diferente."
            )
            return

        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in project_name for char in invalid_chars):
            QMessageBox.warning(
                self,
                "Nombre inválido",
                "El nombre del proyecto contiene caracteres no permitidos: "
                "< > : \" / \\ | ? *"
            )
            return

        self.save_last_location()

        selected_language = self.language_combo.currentText()
        if not self.check_language_installed(selected_language):
            reply = QMessageBox.question(
                self,
                "Lenguaje no instalado",
                f"{selected_language} no está instalado en tu sistema. ¿Deseas abrir el gestor de lenguajes para instalarlo?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                from ui.language_manager import LanguageManager
                self.language_manager = LanguageManager(self)

                self.language_manager.language_installed.connect(
                    lambda lang: self.on_language_installed(lang, selected_language)
                )
                self.language_manager.show()
                return
            else:
                QMessageBox.information(
                    self,
                    "Instalación requerida",
                    f"Debes instalar {selected_language} antes de crear el proyecto."
                )
                return
        
        self.continue_project_creation(project_name, selected_language)

    def check_project_name_exists(self, project_name):
        """Verifica si ya existe un proyecto con el mismo nombre"""
        projects_dir = Path.home() / ".myapp_projects"
        projects_dir.mkdir(exist_ok=True, parents=True)
        
        for file in projects_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                    if project_data.get("name") == project_name:
                        return True
            except:
                continue
        
        project_path = Path(self.location_input.text()) / project_name
        return project_path.exists()

    def continue_project_creation(self, project_name, selected_language):
        """Continúa con la creación del proyecto después de verificar el lenguaje"""
        base_dir = self.location_input.text()
        project_dir = os.path.join(base_dir, project_name)
        project_dir = os.path.abspath(project_dir)

        os.makedirs(project_dir, exist_ok=True)

        project_data = {
            "name": project_name,
            "project_type": "Android",
            "language": selected_language, 
            "location_path": project_dir,
            "android_device_type": "Emulator" if self.emulator_radio.isChecked() else "Physical",
            "android_emulator_type": self.emulator_combo.currentText() if self.emulator_radio.isChecked() else None,
            "android_instant_run": self.instant_run_check.isChecked(),
            "android_vector_drawables": self.vector_drawable_check.isChecked(),
            "created_at": datetime.datetime.now().isoformat(),
            "last_modified": datetime.datetime.now().isoformat()
        }

        projects_dir = Path.home() / ".myapp_projects"
        projects_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in project_name if c.isalnum() or c in " _-").rstrip()
        filename = f"{safe_name}_{timestamp}.json"
        filepath = projects_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)

        self.create_project_structure(project_dir, selected_language)
        
        path_manager.add_project_path(project_name, project_dir)
        
        QMessageBox.information(
            self, 
            "Éxito", 
            f"Proyecto {project_name} creado exitosamente!\n\n"
            f"Lenguaje: {selected_language}\n"
            f"Ubicación: {project_dir}"
        )
        
        self.entorno_window = IllustratorWindow(
            project_name=project_name,
            project_path=project_dir,
            project_language=selected_language  
        )
        self.entorno_window.show()
        
        if hasattr(self, 'parent') and self.parent():
            main_window = self.parent()
            while main_window.parent() is not None:
                main_window = main_window.parent()
            main_window.close()
            
        if hasattr(self.parent(), 'update_project_list'):
            self.parent().update_project_list()

    def create_project_structure(self, project_dir, language):
        """Crea la estructura de archivos según el lenguaje seleccionado"""
        try:
            if language == "Java":
                self.create_java_structure(project_dir)
            elif language == "Kotlin":
                self.create_kotlin_structure(project_dir)
            elif language == "Dart (Flutter)":
                self.create_flutter_structure(project_dir)
                
        except Exception as e:
            print(f"Error creando estructura: {e}")

    def create_java_structure(self, project_dir):
        """Estructura para proyecto Android Java"""
        dirs = [
            "app/src/main/java/com/example/myapp",
            "app/src/main/res/layout",
            "app/src/main/res/drawable",
            "app/src/main/res/values",
            "app/src/main/res/mipmap",
            "gradle/wrapper"
        ]
        
        for dir_path in dirs:
            os.makedirs(os.path.join(project_dir, dir_path), exist_ok=True)
        
        self.create_java_main_activity(project_dir)
        self.create_android_manifest(project_dir)
        self.create_strings_xml(project_dir)
        self.create_build_gradle(project_dir, "java")
        self.create_gradle_wrapper(project_dir)

    def create_java_main_activity(self, project_dir):
        """Crea el archivo MainActivity.java"""
        content = '''package com.example.myapp;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }
}
'''
        with open(os.path.join(project_dir, "app/src/main/java/com/example/myapp/MainActivity.java"), "w", encoding='utf-8') as f:
            f.write(content)

    def create_android_manifest(self, project_dir):
        """Crea AndroidManifest.xml"""
        content = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
'''
        with open(os.path.join(project_dir, "app/src/main/AndroidManifest.xml"), "w", encoding='utf-8') as f:
            f.write(content)

    def create_strings_xml(self, project_dir):
        """Crea strings.xml"""
        content = '''<resources>
    <string name="app_name">My App</string>
</resources>
'''
        with open(os.path.join(project_dir, "app/src/main/res/values/strings.xml"), "w", encoding='utf-8') as f:
            f.write(content)

    def create_build_gradle(self, project_dir, language):
        """Crea build.gradle según el lenguaje"""
        if language == "java":
            content = '''plugins {
    id 'com.android.application'
}

android {
    compileSdk 33

    defaultConfig {
        applicationId "com.example.myapp"
        minSdk 21
        targetSdk 33
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.8.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}
'''
        with open(os.path.join(project_dir, "app/build.gradle"), "w", encoding='utf-8') as f:
            f.write(content)

    def create_gradle_wrapper(self, project_dir):
        """Crea archivos básicos de Gradle"""
        wrapper_content = '''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-7.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
'''
        with open(os.path.join(project_dir, "gradle/wrapper/gradle-wrapper.properties"), "w", encoding='utf-8') as f:
            f.write(wrapper_content)

    def on_language_installed(self, installed_language, required_language):
        """Se llama cuando se instala un lenguaje desde el gestor"""
        if installed_language == required_language:
            if self.check_language_installed(required_language):
                self.continue_project_creation(self.name_input.text().strip(), required_language)
            else:
                QMessageBox.warning(
                    self,
                    "Lenguaje no instalado",
                    f"El lenguaje {required_language} sigue sin estar instalado correctamente."
                )

class ProjectListWidget(QWidget):
    project_opened_signal = Signal(str, str, str) 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects_dir = Path.home() / ".myapp_projects"
        self.setup_ui()
    
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar proyectos...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_projects)
        
        self.title = QLabel("Tus proyectos locales")
        self.title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding-bottom: 10px;
            border-bottom: 1px solid #555555;
        """)
 
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
        """)
 
        self.project_list = QListWidget()
        self.project_list.setStyleSheet("""
            QListWidget {
                background-color: #252525;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:hover {
                background-color: #333333;
            }
            QListWidget::item:selected {
                background-color: #BB86FC;
                color: black;
            }
        """)
        self.project_list.itemDoubleClicked.connect(self.open_project)

        self.btn_refresh = QPushButton("Actualizar lista")
        self.btn_delete = QPushButton("Eliminar proyecto")
        self.btn_open_folder = QPushButton("Abrir ubicación")
        
        for btn in [self.btn_refresh, self.btn_delete, self.btn_open_folder]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #444444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
        
        self.btn_refresh.clicked.connect(self.load_projects)
        self.btn_delete.clicked.connect(self.delete_selected_project)
        self.btn_open_folder.clicked.connect(self.open_project_folder)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_open_folder)

        list_container = QWidget()
        list_container.setStyleSheet("background: transparent;")
        list_layout = QVBoxLayout(list_container)
        list_layout.addWidget(self.project_list)
        
        scroll_area.setWidget(list_container)
        
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(scroll_area, 1)
        self.layout.addLayout(btn_layout)
  
        self.load_projects()
    
    def load_projects(self):
        self.project_list.clear()
        try:
            projects = path_manager.get_all_projects()
            for project in projects:
                if not os.path.isabs(project["path"]):
                    project["path"] = os.path.abspath(project["path"])

            self.projects_dir.mkdir(exist_ok=True, parents=True)
            for file in self.projects_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)

                    json_path = project_data.get("location_path", "")
                    if json_path and not os.path.isabs(json_path):
                        json_path = os.path.abspath(json_path)

                    existing = any(
                        p["name"] == project_data["name"] and 
                        os.path.abspath(p["path"]) == os.path.abspath(json_path)
                        for p in projects
                    )
                    
                    if not existing and json_path:
                        path_manager.add_project_path(project_data["name"], json_path)
                        projects.append({"name": project_data["name"], "path": json_path})
                    
                except json.JSONDecodeError:
                    continue

            projects.sort(key=lambda x: x["name"].lower())
            
            for project in projects:
                path_exists = os.path.exists(project["path"])
                status = "✅" if path_exists else "❌"
                
                item_text = f"{status} {project['name']} - {project['path']}"
                item = QListWidgetItem(item_text)
                
                if not path_exists:
                    item.setForeground(QColor("red"))
                    item.setToolTip("La ruta del proyecto no existe")
                
                item.setData(Qt.UserRole, project)
                self.project_list.addItem(item)
                
            if not projects:
                self.project_list.addItem("No hay proyectos creados aún")
                
        except Exception as e:
            self.project_list.addItem(f"Error al cargar proyectos: {str(e)}")

    def filter_projects(self, text):
        for i in range(self.project_list.count()):
            item = self.project_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def open_project_folder(self):
        selected = self.project_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Selecciona un proyecto primero")
            return
            
        project_data = selected.data(Qt.UserRole)
        if isinstance(project_data, str):
            return
            
        try:
            path = Path(project_data["path"])
            if path.exists():
                if os.name == 'nt':
                    os.startfile(path)
                elif os.name == 'posix': 
                    if sys.platform == 'darwin': 
                        subprocess.run(['open', path])
                    else:
                        subprocess.run(['xdg-open', path])
            else:
                QMessageBox.warning(self, "Advertencia", "La ubicación del proyecto no existe")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ubicación:\n{str(e)}")

    def delete_selected_project(self):
        selected = self.project_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Selecciona un proyecto primero")
            return
            
        project_data = selected.data(Qt.UserRole)
        if isinstance(project_data, str): 
            return
            
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de querer eliminar el proyecto '{project_data['name']}'?\n\n"
            f"Ubicación: {project_data['path']}\n\n"
            "⚠️ Esta acción ELIMINARÁ TODOS LOS ARCHIVOS del proyecto y no puede deshacerse.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  
        )
        
        if reply == QMessageBox.Yes:
            try:
                project_path = Path(project_data["path"])
                
                if project_path.exists():
                    import shutil
                    try:
                        shutil.rmtree(project_path)
                        files_deleted = True
                    except Exception as e:
                        QMessageBox.warning(
                            self, 
                            "Advertencia", 
                            f"No se pudieron eliminar todos los archivos:\n{str(e)}\n\n"
                            "Pero se eliminará la referencia del proyecto."
                        )
                        files_deleted = False
                else:
                    files_deleted = False
                    QMessageBox.information(
                        self,
                        "Proyecto no encontrado",
                        "La carpeta del proyecto no existe en el sistema.\n"
                        "Solo se eliminará la referencia del proyecto."
                    )
                
                path_manager.remove_project(project_data["name"], project_data["path"])
                projects_dir = Path.home() / ".myapp_projects"
                json_deleted = False
                for file in projects_dir.glob("*.json"):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                            if (json_data.get("name") == project_data["name"] and 
                                json_data.get("location_path") == project_data["path"]):
                                os.remove(file)
                                json_deleted = True
                                break
                    except:
                        continue

                self.load_projects()
                if files_deleted:
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        "Proyecto eliminado completamente:\n"
                        "✓ Archivos físicos eliminados\n"
                        "✓ Referencias removidas"
                    )
                else:
                    QMessageBox.information(
                        self, 
                        "Éxito parcial", 
                        "Referencia del proyecto eliminada.\n"
                        "Los archivos físicos ya no existían o no se pudieron eliminar."
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"No se pudo eliminar el proyecto completamente:\n{str(e)}"
                )

    def open_project(self, item):
        project_data = item.data(Qt.UserRole)
        if not project_data or isinstance(project_data, str):
            return
            
        try:
            project_name = project_data["name"]
            project_path = project_data["path"]
            project_language = self.load_project_language(project_name, project_path)
            
            if not project_path or not os.path.exists(project_path):
                default_path = os.path.join(os.path.expanduser("~"), "CreatorsStudio", project_name)
                os.makedirs(default_path, exist_ok=True)
                project_path = os.path.abspath(default_path)

            self.project_opened_signal.emit(project_name, project_path, project_language)
                
        except Exception as e:
            print(f"Error al abrir proyecto: {e}")
            import traceback
            traceback.print_exc()

    def load_project_language(self, project_name, project_path):
        """Carga el lenguaje del proyecto desde los metadatos"""
        try:
            projects_dir = Path.home() / ".myapp_projects"
            for file in projects_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("name") == project_name and data.get("location_path") == project_path:
                            return data.get("language", "Java")
                except:
                    continue
        except:
            pass
        return "Java"  
    
class MainApp(QWidget):
    project_opened = Signal(str, str, str)  
    def __init__(self, on_logout, show_entorno_callback):
        super().__init__()
        self.on_logout = on_logout
        self.show_entorno = show_entorno_callback
        self.setup_ui()
        
        self.right_panel.project_opened_signal.connect(self.handle_project_opened)

    def handle_project_opened(self, project_name, project_path, project_language):
        """Maneja la señal de proyecto abierto"""
        print(f"Proyecto seleccionado: {project_name}, {project_path}, {project_language}")
        self.show_entorno(project_name, project_path, project_language)
              
    def setup_ui(self):
        self.setMinimumSize(1000, 650)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        background = GradientWidget()
        background_layout = QVBoxLayout(background)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)

        self.header = QWidget()
        self.header.setFixedHeight(50)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.back_btn = BackButton()
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.hide()
        
        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        
        self.user_btn = UserProfileButton()
        self.user_btn.logout_action.triggered.connect(self.on_logout)
        header_layout.addWidget(self.user_btn)
        
        background_layout.addWidget(self.header)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background: #555555;
            }
        """)

        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(40, 20, 40, 20)
        left_layout.setSpacing(20)
        
        button_style = """
            QPushButton {
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: black;
                color: white;
                border: 1px solid black;
            }
        """

        self.android_btn = QPushButton("ANDROID PROJECT")
        self.android_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.android_btn.setStyleSheet(button_style)
        self.android_btn.setFixedHeight(50)

        self.pc_btn = QPushButton("PC PROJECT (.exe)")
        self.pc_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.pc_btn.setStyleSheet(button_style)
        self.pc_btn.setFixedHeight(50)

        self.web_btn = QPushButton("WEB PROJECT")
        self.web_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.web_btn.setStyleSheet(button_style)
        self.web_btn.setFixedHeight(50)

        left_layout.addWidget(self.android_btn)
        left_layout.addWidget(self.pc_btn)
        left_layout.addWidget(self.web_btn)
        left_layout.addStretch()

        self.right_panel = ProjectListWidget()
 
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([300, 600])

        self.main_stack = QStackedWidget()
        self.main_stack.addWidget(self.splitter)

        self.android_setup = AndroidSetupWidget()
        self.android_setup.setMinimumWidth(500)
        self.android_setup.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.android_scroll_area = QScrollArea()
        self.android_scroll_area.setWidgetResizable(True)
        self.android_scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.android_scroll_area.setWidget(self.android_setup)
        self.main_stack.addWidget(self.android_scroll_area)
        
        background_layout.addWidget(self.main_stack)
        main_layout.addWidget(background)

        self.android_btn.clicked.connect(self.show_android_setup)

    def show_android_setup(self):
        self.main_stack.setCurrentIndex(1)
        self.back_btn.show()
        self.splitter.hide()
        self.android_scroll_area.ensureWidgetVisible(self.android_setup)

    def go_back(self):
        self.main_stack.setCurrentIndex(0)
        self.back_btn.hide()
        self.splitter.show()

    def show_install_progress(self, percent, message):
        if hasattr(self, 'progress_msg') and self.progress_msg:
            self.progress_msg.setText(f"{message}\n\nProgreso: {percent}%")
            QApplication.processEvents()

    def install_finished(self, success, message):
        if hasattr(self, 'progress_msg') and self.progress_msg:
            self.progress_msg.hide()
            self.progress_msg = None
        if success:
            QMessageBox.information(self, "Instalación completada", message)
        else:
            QMessageBox.critical(self, "Error de instalación", message)

    def start_install_thread(self, language):
        self.install_thread = InstallThread(language)
        self.install_thread.progress_updated.connect(self.show_install_progress)
        self.install_thread.finished.connect(self.install_finished)
        self.install_thread.start()