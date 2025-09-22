import os
from dotenv import load_dotenv
import requests
import threading
import sys
import math 
import re
import uuid
import json
from pathlib import Path 
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGraphicsView, QGraphicsScene, QDockWidget,
    QListWidget, QTextEdit, QLineEdit, QComboBox, QColorDialog,
    QInputDialog, QMessageBox, QMenu, QStatusBar, QApplication,
    QFileSystemModel, QTreeView, QSplitter, QToolBar, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsItem, QSlider,
    QFileDialog, QScrollArea, QGroupBox, QRadioButton, QCheckBox,
    QSizePolicy, QTabWidget, QTextEdit, QDialog,
    QPlainTextEdit, QListWidgetItem 
)

from PySide6.QtGui import (
    QIcon, QAction, QCursor, QColor, QBrush, QTextCursor, QFont,
    QPen, QPainter, QTextFormat, QSyntaxHighlighter, QTextCharFormat, QPalette
)
from PySide6.QtCore import (
    Qt, QSize, QPoint, Signal, QDir, QRectF, QSettings, QThread, 
    Signal as pyqtSignal, QEvent, QTimer, QRect, QRegularExpression 
)


project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

class AIProvider:
    """Clase base para proveedores de IA"""
    DEEPSEEK = "deepseek"
    STARCODER = "starcoder"
    
    @staticmethod
    def get_available_providers():
        """Retorna los proveedores disponibles basados en las API keys configuradas"""
        providers = []
        
 
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key and deepseek_key.startswith("sk-"):
            providers.append(AIProvider.DEEPSEEK)

        starcoder_key = os.getenv("HUGGINGFACE_API_KEY")
        if starcoder_key and starcoder_key.startswith("hf_"):
            providers.append(AIProvider.STARCODER)
        
        return providers
    
class DeepSeekWorker(QThread):
    """Worker para llamadas a la API de DeepSeek en segundo plano"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key, message, conversation_history=None):
        super().__init__()
        self.api_key = api_key
        self.message = message
        self.conversation_history = conversation_history or []
    
    def run(self):
        try:
            response = self.call_deepseek_api()
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def call_deepseek_api(self):
        """Llama a la API de DeepSeek"""
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        

        messages = self.conversation_history.copy()
        messages.append({"role": "user", "content": self.message})
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]

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

class WorkspacePreset:
    def __init__(self, name, tool_panel_pos, panels):
        self.name = name
        self.tool_panel_pos = tool_panel_pos  
        self.panels = panels

class UIElement:
    """Clase que representa un elemento de UI con todas sus propiedades"""
    def __init__(self, element_type, x, y, width, height):
        self.id = str(uuid.uuid4())[:8] 
        self.type = element_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.properties = {
            "backgroundColor": "#FFFFFF",
            "textColor": "#000000",
            "textSize": "14sp",
            "text": "",
            "cornerRadius": "0dp",
            "hint": "",
            "inputType": "text",
            "orientation": "horizontal"
        }
        self.androidWidgetType = self.determineAndroidWidgetType()
        self.graphicsItem = None
        
    def determineAndroidWidgetType(self):
        """Determina el tipo de widget Android basado en el tipo de elemento"""
        mapping = {
            "rectangle": "View",
            "text": "TextView",
            "button": "Button",
            "circle": "ImageView",
            "input": "EditText",
            "switch": "Switch",
            "checkbox": "CheckBox",
            "radio": "RadioButton",
            "slider": "SeekBar",
            "image": "ImageView",
            "list": "ListView",
            "card": "CardView"
        }
        return mapping.get(self.type, "View")
    
    def setProperty(self, key, value):
        self.properties[key] = value
        
    def getProperty(self, key):
        return self.properties.get(key, "")
        
    def toXML(self):
        """Convierte el elemento a código XML Android"""
        if self.androidWidgetType == "TextView":
            return self.generateTextViewXML()
        elif self.androidWidgetType == "Button":
            return self.generateButtonXML()
        elif self.androidWidgetType == "EditText":
            return self.generateEditTextXML()
        elif self.androidWidgetType == "View":
            return self.generateViewXML()
        else:
            return self.generateGenericXML()
    
    def generateGenericXML(self):
        """Genera XML genérico para cualquier View"""
        bg_color = self.properties.get("backgroundColor", "#FFFFFF")
        corner_radius = self.properties.get("cornerRadius", "0dp")
        
        if corner_radius != "0dp":
           
            drawable_name = f"bg_{self.id}"
            self.generateShapeDrawable(drawable_name, bg_color, corner_radius)
            bg_reference = f"@drawable/{drawable_name}"
        else:
            bg_reference = f"\"{bg_color}\""
            
        return f'''<{self.androidWidgetType}
    android:id="@+id/{self.id}"
    android:layout_width="{self.width}px"
    android:layout_height="{self.height}px"
    android:layout_marginLeft="{self.x}px"
    android:layout_marginTop="{self.y}px"
    android:background={bg_reference} />\n'''
    
    def generateTextViewXML(self):
        """Genera XML para TextView"""
        text = self.properties.get("text", "")
        text_color = self.properties.get("textColor", "#000000")
        text_size = self.properties.get("textSize", "14sp")
        
        return f'''<TextView
    android:id="@+id/{self.id}"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:layout_marginLeft="{self.x}px"
    android:layout_marginTop="{self.y}px"
    android:text="{text}"
    android:textColor="{text_color}"
    android:textSize="{text_size}" />\n'''
    
    def generateButtonXML(self):
        """Genera XML para Button"""
        text = self.properties.get("text", "Button")
        bg_color = self.properties.get("backgroundColor", "#6200EE")
        text_color = self.properties.get("textColor", "#FFFFFF")
        
        return f'''<Button
    android:id="@+id/{self.id}"
    android:layout_width="{self.width}px"
    android:layout_height="{self.height}px"
    android:layout_marginLeft="{self.x}px"
    android:layout_marginTop="{self.y}px"
    android:text="{text}"
    android:backgroundTint="{bg_color}"
    android:textColor="{text_color}" />\n'''
    
    def generateEditTextXML(self):
        """Genera XML para EditText"""
        hint = self.properties.get("hint", "")
        input_type = self.properties.get("inputType", "text")
        
        return f'''<EditText
    android:id="@+id/{self.id}"
    android:layout_width="{self.width}px"
    android:layout_height="{self.height}px"
    android:layout_marginLeft="{self.x}px"
    android:layout_marginTop="{self.y}px"
    android:hint="{hint}"
    android:inputType="{input_type}" />\n'''
    
    def generateShapeDrawable(self, drawable_name, color, corner_radius):
        """Genera un archivo XML de shape drawable"""
        corner_radius_value = corner_radius.replace("dp", "")
        
        shape_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="{color}" />
    <corners android:radius="{corner_radius_value}dp" />
</shape>'''
        
        return shape_xml, drawable_name
    
    def toJavaCode(self):
        """Genera código Java para inicialización y event handlers"""
        if self.androidWidgetType == "Button":
            return self.generateButtonJava()
        elif self.androidWidgetType == "EditText":
            return self.generateEditTextJava()
        return ""
    
    def generateButtonJava(self):
        """Genera código Java para Button"""
        return f'''Button {self.id} = findViewById(R.id.{self.id});
{self.id}.setOnClickListener(v -> {{
    // TODO: Implement {self.id} click logic
}});\n'''
    
    def generateEditTextJava(self):
        """Genera código Java para EditText"""
        return f'''EditText {self.id} = findViewById(R.id.{self.id});
// Add text change listeners or validation as needed\n'''

class CodeGenerator:
    """Clase para generar código completo de Android"""
    
    def __init__(self, project_name, package_name="com.example.app"):
        self.project_name = project_name
        self.package_name = package_name
        self.elements = []
        self.layouts = {}
        self.drawables = {}
        
    def addElement(self, element):
        self.elements.append(element)
        
    def generateLayoutXML(self, layout_name="activity_main"):
        """Genera el XML completo del layout"""
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">\n'''
        
        for element in self.elements:
            xml_content += "    " + element.toXML().replace("\n", "\n    ") + "\n"
            

            if element.properties.get("cornerRadius", "0dp") != "0dp":
                drawable_name = f"bg_{element.id}"
                drawable_xml, _ = element.generateShapeDrawable(
                    drawable_name, 
                    element.properties.get("backgroundColor", "#FFFFFF"),
                    element.properties.get("cornerRadius", "0dp")
                )
                self.drawables[drawable_name] = drawable_xml
        
        xml_content += '</LinearLayout>'
        self.layouts[layout_name] = xml_content
        return xml_content
    
    def generateActivityJava(self, activity_name="MainActivity"):
        """Genera el código Java de la Activity"""
        java_code = f'''package {self.package_name};

import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class {activity_name} extends AppCompatActivity {{

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.{activity_name.replace("Activity", "").lower()});
        
        // Initialize UI elements
        initializeViews();
    }}
    
    private void initializeViews() {{
'''
        

        for element in self.elements:
            if element.androidWidgetType in ["Button", "EditText", "TextView"]:
                java_code += f"        {element.toJavaCode()}"
        
        java_code += '''    }
    
    // TODO: Add your activity logic here
    
}'''
        return java_code
    
    def generateStringsXML(self):
        """Genera strings.xml con todos los textos"""
        strings = set()
        for element in self.elements:
            if element.properties.get("text"):
                strings.add(f'    <string name="{element.id}_text">{element.properties["text"]}</string>')
            if element.properties.get("hint"):
                strings.add(f'    <string name="{element.id}_hint">{element.properties["hint"]}</string>')
        
        strings_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>\n'''
        strings_xml += "\n".join(strings)
        strings_xml += "\n</resources>"
        return strings_xml
    
    def generateColorsXML(self):
        """Genera colors.xml con todos los colores utilizados"""
        colors = set()
        for element in self.elements:
            bg_color = element.properties.get("backgroundColor")
            text_color = element.properties.get("textColor")
            
            if bg_color and bg_color.startswith("#"):
                colors.add(f'    <color name="{element.id}_bg">{bg_color}</color>')
            if text_color and text_color.startswith("#"):
                colors.add(f'    <color name="{element.id}_text">{text_color}</color>')
        
        colors_xml = '''<?xml version="1.0" encoding="utf-8"?>
<resources>\n'''
        colors_xml += "\n".join(colors)
        colors_xml += "\n</resources>"
        return colors_xml
    
    def exportProject(self, directory):
        """Exporta el proyecto completo a la estructura de Android"""

        os.makedirs(os.path.join(directory, "app", "src", "main", "java", *self.package_name.split(".")), exist_ok=True)
        os.makedirs(os.path.join(directory, "app", "src", "main", "res", "layout"), exist_ok=True)
        os.makedirs(os.path.join(directory, "app", "src", "main", "res", "values"), exist_ok=True)
        os.makedirs(os.path.join(directory, "app", "src", "main", "res", "drawable"), exist_ok=True)
        

        with open(os.path.join(directory, "app", "src", "main", "res", "layout", "activity_main.xml"), "w") as f:
            f.write(self.generateLayoutXML())
        
        with open(os.path.join(directory, "app", "src", "main", "java", *self.package_name.split("."), "MainActivity.java"), "w") as f:
            f.write(self.generateActivityJava())
        
        with open(os.path.join(directory, "app", "src", "main", "res", "values", "strings.xml"), "w") as f:
            f.write(self.generateStringsXML())
        
        with open(os.path.join(directory, "app", "src", "main", "res", "values", "colors.xml"), "w") as f:
            f.write(self.generateColorsXML())
        

        for drawable_name, drawable_xml in self.drawables.items():
            with open(os.path.join(directory, "app", "src", "main", "res", "drawable", f"{drawable_name}.xml"), "w") as f:
                f.write(drawable_xml)
        
    
        self.generateManifest(directory)
        self.generateBuildGradle(directory)
        
        return True
    
    def generateManifest(self, directory):
        """Genera AndroidManifest.xml"""
        manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{self.package_name}">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        <activity
            android:name=".MainActivity"
            android:label="@string/app_name">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>'''
        
        with open(os.path.join(directory, "app", "src", "main", "AndroidManifest.xml"), "w") as f:
            f.write(manifest)
    
    def generateBuildGradle(self, directory):
        """Genera build.gradle básico"""
        gradle = '''plugins {
    id 'com.android.application'
}

android {
    compileSdk 34

    defaultConfig {
        applicationId "com.example.app"
        minSdk 21
        targetSdk 34
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
    implementation 'com.google.android.material:material:1.10.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}'''
        
        with open(os.path.join(directory, "app", "build.gradle"), "w") as f:
            f.write(gradle)

class DesignCanvas(QGraphicsView):
    """Canvas personalizado para diseño de interfaces Android"""
    
    elementCreated = Signal(UIElement)
    elementSelected = Signal(UIElement)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        self.currentTool = "select"
        self.currentElement = None
        self.elements = []
        self.selectedElement = None
        

        self.setStyleSheet("background-color: #2C2C2C; border: none;")
        
    def setTool(self, tool):
        self.currentTool = tool
        if tool == "select":
            self.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.NoDrag)
    
    def mousePressEvent(self, event):
        if self.currentTool != "select":
         
            pos = self.mapToScene(event.pos())
            self.createElement(self.currentTool, pos.x(), pos.y())
        else:
            super().mousePressEvent(event)
    
    def createElement(self, element_type, x, y):
      
        if element_type == "rectangle":
            element = UIElement("rectangle", x, y, 100, 60)
            graphicsItem = QGraphicsRectItem(0, 0, 100, 60)
            graphicsItem.setBrush(QBrush(QColor(element.properties["backgroundColor"])))
            graphicsItem.setPen(QPen(Qt.black))
            
        elif element_type == "text":
            element = UIElement("text", x, y, 120, 40)
            element.setProperty("text", "Texto de ejemplo")
            graphicsItem = QGraphicsTextItem("Texto de ejemplo")
            graphicsItem.setDefaultTextColor(QColor(element.properties["textColor"]))
            
        elif element_type == "button":
            element = UIElement("button", x, y, 120, 50)
            element.setProperty("text", "Botón")
            element.setProperty("backgroundColor", "#6200EE")
            element.setProperty("textColor", "#FFFFFF")
            graphicsItem = QGraphicsRectItem(0, 0, 120, 50)
            graphicsItem.setBrush(QBrush(QColor(element.properties["backgroundColor"])))
            graphicsItem.setPen(QPen(Qt.black))
           
            textItem = QGraphicsTextItem("Botón")
            textItem.setDefaultTextColor(QColor(element.properties["textColor"]))
            textItem.setPos(30, 15)
            
        elif element_type == "input":
            element = UIElement("input", x, y, 200, 60)
            element.setProperty("hint", "Escribe aquí...")
            graphicsItem = QGraphicsRectItem(0, 0, 200, 60)
            graphicsItem.setBrush(QBrush(Qt.white))
            graphicsItem.setPen(QPen(Qt.gray))
        
            hintItem = QGraphicsTextItem("Escribe aquí...")
            hintItem.setDefaultTextColor(QColor("#80000000"))
            hintItem.setPos(10, 20)
            
        else:
            return
        
     
        graphicsItem.setPos(x, y)
        graphicsItem.setFlag(QGraphicsItem.ItemIsMovable)
        graphicsItem.setFlag(QGraphicsItem.ItemIsSelectable)
        graphicsItem.setData(0, element.id)  
  
        self.scene.addItem(graphicsItem)
        if element_type == "button":
            self.scene.addItem(textItem)
        elif element_type == "input":
            self.scene.addItem(hintItem)
        
 
        element.graphicsItem = graphicsItem
        self.elements.append(element)
        self.elementCreated.emit(element)
        
  
        self.selectElement(element)
        
    def selectElement(self, element):

        if self.selectedElement and self.selectedElement.graphicsItem:
            self.selectedElement.graphicsItem.setSelected(False)

        self.selectedElement = element
        if element and element.graphicsItem:
            element.graphicsItem.setSelected(True)
            self.elementSelected.emit(element)
  
            if self.parent() and hasattr(self.parent(), 'properties_panel'):
                self.parent().properties_panel.setVisible(True)
                self.update_properties_panel(element)

    def update_properties_panel(self, element):
        if not self.parent() or not hasattr(self.parent(), 'properties_panel'):
            return

        if hasattr(self.parent(), 'text_size_combo') and element.getProperty("textSize"):
            text_size = element.getProperty("textSize")
            self.parent().text_size_combo.setCurrentText(text_size)
        
        if hasattr(self.parent(), 'corner_radius_slider') and element.getProperty("cornerRadius"):
            radius_str = element.getProperty("cornerRadius")
            if radius_str.endswith("dp"):
                try:
                    radius = int(radius_str[:-2])
                    self.parent().corner_radius_slider.setValue(radius)
                except ValueError:
                    pass

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            CodeEditor {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                selection-background-color: #264F78;
            }
       
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #424242;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4f4f4f;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #1e1e1e;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #424242;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #4f4f4f;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        self.highlighter = None

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2d2d30"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingGeometry(block).height()
        
        font = painter.font()
        font.setFamily("Consolas")
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor("#858585"))
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, int(top), self.line_number_area.width() - 5, 
                                self.fontMetrics().height(), Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingGeometry(block).height()
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2f2f32")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)

    def set_highlighter(self, file_path):
        """Configura el resaltador de sintaxis según la extensión del archivo"""
        extension = os.path.splitext(file_path)[1].lower()
        

        if self.highlighter:
            self.highlighter.setDocument(None)
        

        if extension == '.java':
            self.highlighter = JavaHighlighter(self.document())
        elif extension == '.py':
            self.highlighter = PythonHighlighter(self.document())
        elif extension in ['.js', '.jsx']:
            self.highlighter = JavaScriptHighlighter(self.document())
        elif extension in ['.ts', '.tsx']:
            self.highlighter = TypeScriptHighlighter(self.document())
        elif extension == '.xml':
            self.highlighter = XmlHighlighter(self.document())
        elif extension == '.html':
            self.highlighter = HtmlHighlighter(self.document())
        elif extension == '.css':
            self.highlighter = CssHighlighter(self.document())
        elif extension == '.kt':
            self.highlighter = KotlinHighlighter(self.document())
        elif extension == '.dart':
            self.highlighter = DartHighlighter(self.document())
        else:
            self.highlighter = BaseHighlighter(self.document())

class BaseHighlighter(QSyntaxHighlighter):
    """Clase base para todos los highlighters"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        self.setup_highlight_rules()
    
    def setup_highlight_rules(self):
        """Método que deben implementar las clases hijas"""
        pass
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
        
        self.setCurrentBlockState(0)
        self.highlight_multiline_comments(text)

    def highlight_multiline_comments(self, text):
        """Maneja comentarios multilínea (debe ser implementado por subclases si es necesario)"""
        pass

class JavaHighlighter(BaseHighlighter):
    def setup_highlight_rules(self):
  
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "abstract", "assert", "boolean", "break", "byte", "case", "catch",
            "char", "class", "const", "continue", "default", "do", "double",
            "else", "enum", "extends", "final", "finally", "float", "for",
            "goto", "if", "implements", "import", "instanceof", "int", "interface",
            "long", "native", "new", "package", "private", "protected", "public",
            "return", "short", "static", "strictfp", "super", "switch",
            "synchronized", "this", "throw", "throws", "transient", "try",
            "void", "volatile", "while", "var", "record", "sealed", "non-sealed", "permits"
        ]
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))
        

        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        types = [
            "String", "Integer", "Double", "Float", "Boolean", "Object", 
            "List", "Map", "Set", "ArrayList", "HashMap", "HashSet",
            "Number", "Character", "Byte", "Short", "Long", "Void"
        ]
        for word in types:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, type_format))
        

        single_line_comment_format = QTextCharFormat()
        single_line_comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegularExpression("//[^\n]*"), single_line_comment_format))


        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression("\".*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("\'.*\'"), string_format))
        

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\.\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b0x[0-9A-Fa-f]+\b"), number_format))
        

        annotation_format = QTextCharFormat()
        annotation_format.setForeground(QColor("#C586C0"))
        self.highlighting_rules.append((QRegularExpression(r"@[^\s\(\)]+"), annotation_format))
        

        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#D4D4D4"))
        operators = [r"\=", r"\+", r"\-", r"\*", r"\/", r"\%", r"\=\=", r"\!=", 
                    r"\>", r"\<", r"\>\=", r"\<\=", r"\&", r"\|", r"\&", r"\|\|",
                    r"\+\+", r"\-\-", r"\+=", r"\-=", r"\*=", r"\/=", r"\%=",
                    r"\<\<", r"\>\>", r"\>\>\>", r"\<\<=", r"\>\>=", r"\>\>\>="]
        for op in operators:
            self.highlighting_rules.append((QRegularExpression(op), operator_format))
        

        method_format = QTextCharFormat()
        method_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+\([^\)]*\)\s*\{"), method_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+\s*\("), method_format))
        
   
        constant_format = QTextCharFormat()
        constant_format.setForeground(QColor("#4FC1FF"))
        self.highlighting_rules.append((QRegularExpression(r"\b[A-Z_][A-Z0-9_]+\b"), constant_format))

    def highlight_multiline_comments(self, text):
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = text.indexOf("/*")
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        
        while start_index >= 0:
            end_index = text.indexOf("*/", start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + 2
            
            self.setFormat(start_index, comment_length, comment_format)
            start_index = text.indexOf("/*", start_index + comment_length)

class PythonHighlighter(BaseHighlighter):
    def setup_highlight_rules(self):

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
            "while", "with", "yield"
        ]
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))
        

        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#C586C0"))
        self.highlighting_rules.append((QRegularExpression(r"@\w+"), decorator_format))
        
      
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))
        
   
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression("\"[^\"]*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("\'[^\']*\'"), string_format))
        self.highlighting_rules.append((QRegularExpression("\"\"\"[^\"]*\"\"\""), string_format))
        self.highlighting_rules.append((QRegularExpression("\'\'\'[^\']*\'\'\'"), string_format))
        
       
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\.\d+\b"), number_format))
        

        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+\([^\)]*\)\s*:"), function_format))
        self.highlighting_rules.append((QRegularExpression(r"\bdef\s+(\w+)"), function_format))
      
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((QRegularExpression(r"\bclass\s+(\w+)"), class_format))
        
        
        self_format = QTextCharFormat()
        self_format.setForeground(QColor("#4FC1FF"))
        self.highlighting_rules.append((QRegularExpression(r"\bself\b"), self_format))

class JavaScriptHighlighter(BaseHighlighter):
    def setup_highlight_rules(self):
     
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "export", "extends", "finally",
            "for", "function", "if", "import", "in", "instanceof", "new",
            "return", "super", "switch", "this", "throw", "try", "typeof",
            "var", "void", "while", "with", "yield", "let", "await", "async",
            "static", "get", "set", "from", "of", "finally"
        ]
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))
        
   
        constant_format = QTextCharFormat()
        constant_format.setForeground(QColor("#4FC1FF"))
        constants = ["true", "false", "null", "undefined", "NaN", "Infinity"]
        for word in constants:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, constant_format))
       
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegularExpression("//[^\n]*"), comment_format))
        
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression("\"[^\"]*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("\'[^\']*\'"), string_format))
        self.highlighting_rules.append((QRegularExpression("`[^`]*`"), string_format))
        
        
        template_format = QTextCharFormat()
        template_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((QRegularExpression(r"\$\{[^\}]*\}"), template_format))
        
       
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\.\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b0x[0-9A-Fa-f]+\b"), number_format))
        
       
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((QRegularExpression(r"\bfunction\s+(\w+)"), function_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+\s*\([^\)]*\)\s*\{"), function_format))
        self.highlighting_rules.append((QRegularExpression(r"\(\s*\)\s*=>"), function_format))
        
       
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((QRegularExpression(r"\bclass\s+(\w+)"), class_format))

    def highlight_multiline_comments(self, text):
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = text.indexOf("/*")
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        
        while start_index >= 0:
            end_index = text.indexOf("*/", start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + 2
            
            self.setFormat(start_index, comment_length, comment_format)
            start_index = text.indexOf("/*", start_index + comment_length)

class XmlHighlighter(BaseHighlighter):
    def setup_highlight_rules(self):
       
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#569CD6"))
        self.highlighting_rules.append((QRegularExpression(r"<\/?[\w:-]+"), tag_format))
        
        
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor("#9CDCFE"))
        self.highlighting_rules.append((QRegularExpression(r"[\w:-]+="), attribute_format))
        
       
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression(r"=\"[^\"]*\""), value_format))
        
     
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegularExpression(r"<!--[^>]*-->"), comment_format))
        
   
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(QColor("#569CD6"))
        self.highlighting_rules.append((QRegularExpression(r"<!DOCTYPE[^>]*>"), doctype_format))
        
      
        cdata_format = QTextCharFormat()
        cdata_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression(r"<!\[CDATA\[[^\]]*\]\]>"), cdata_format))

class CssHighlighter(BaseHighlighter):
    def setup_highlight_rules(self):
   
        property_format = QTextCharFormat()
        property_format.setForeground(QColor("#9CDCFE"))
        properties = [
            "color", "background", "font", "margin", "padding", "border", "width",
            "height", "display", "position", "top", "right", "bottom", "left",
            "flex", "grid", "animation", "transition", "transform", "opacity"
        ]
        for prop in properties:
            pattern = QRegularExpression(r"\b" + prop + r"\b\s*:")
            self.highlighting_rules.append((pattern, property_format))
        
     
        selector_format = QTextCharFormat()
        selector_format.setForeground(QColor("#569CD6"))
        self.highlighting_rules.append((QRegularExpression(r"[\.#]?[\w-]+\s*\{"), selector_format))
        
       
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression(r":\s*[^;]*"), value_format))
        
     
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegularExpression(r"\/\*[^\*]*\*\/"), comment_format))
        
       
        at_rule_format = QTextCharFormat()
        at_rule_format.setForeground(QColor("#C586C0"))
        at_rules = ["@import", "@media", "@keyframes", "@font-face", "@page"]
        for rule in at_rules:
            pattern = QRegularExpression(rule)
            self.highlighting_rules.append((pattern, at_rule_format))
        
       
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+[pxemsvh%]*\b"), number_format))
        
       
        color_format = QTextCharFormat()
        color_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((QRegularExpression(r"#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})\b"), color_format))

class TypeScriptHighlighter(JavaScriptHighlighter):
    """Resaltador para TypeScript (similar a JavaScript con añadidos)"""
    def setup_highlight_rules(self):
        super().setup_highlight_rules()
        
      
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        type_keywords = ["number", "string", "boolean", "any", "void", "null", "undefined",
                        "object", "never", "unknown", "symbol", "bigint", "readonly"]
        
        for word in type_keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, type_format))
        
        
        interface_format = QTextCharFormat()
        interface_format.setForeground(QColor("#569CD6"))
        self.highlighting_rules.append((QRegularExpression(r"\binterface\s+(\w+)"), interface_format))
        self.highlighting_rules.append((QRegularExpression(r"\btype\s+(\w+)"), interface_format))
        
     
        generic_format = QTextCharFormat()
        generic_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((QRegularExpression(r"<[^>]*>"), generic_format))

class KotlinHighlighter(BaseHighlighter):
    """Resaltador para Kotlin"""
    def setup_highlight_rules(self):
       
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "as", "as?", "break", "class", "continue", "do", "else", "false", "for",
            "fun", "if", "in", "!in", "interface", "is", "!is", "null", "object",
            "package", "return", "super", "this", "throw", "true", "try", "typealias",
            "val", "var", "when", "while", "by", "catch", "constructor", "delegate",
            "dynamic", "field", "file", "finally", "get", "import", "init", "param",
            "property", "receiver", "set", "setparam", "where", "actual", "abstract",
            "annotation", "companion", "const", "crossinline", "data", "enum", "expect",
            "external", "final", "infix", "inline", "inner", "internal", "lateinit",
            "noinline", "open", "operator", "out", "override", "private", "protected",
            "public", "reified", "sealed", "suspend", "tailrec", "vararg", "it"
        ]
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))
        
      
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        types = ["Int", "Long", "Double", "Float", "String", "Boolean", "Char", "Byte",
                "Short", "Unit", "Any", "Nothing", "Array", "List", "Set", "Map", "MutableList",
                "MutableSet", "MutableMap", "Sequence", "Pair", "Triple"]
        for word in types:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, type_format))
        
       
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegularExpression("//[^\n]*"), comment_format))
        
       
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression("\"[^\"]*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("\'[^\']*\'"), string_format))
       
        self.highlighting_rules.append((QRegularExpression("\"\"\"[^\"]*\"\"\""), string_format))
        
      
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\.\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b0x[0-9A-Fa-f]+\b"), number_format))
        
       
        annotation_format = QTextCharFormat()
        annotation_format.setForeground(QColor("#C586C0"))
        self.highlighting_rules.append((QRegularExpression(r"@[^\s\(\)]+"), annotation_format))
        
     
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((QRegularExpression(r"\bfun\s+(\w+)"), function_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+\s*\([^\)]*\)\s*\{"), function_format))

class DartHighlighter(BaseHighlighter):
    """Resaltador para Dart"""
    def setup_highlight_rules(self):
     
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "abstract", "as", "assert", "async", "await", "break", "case", "catch",
            "class", "const", "continue", "covariant", "default", "deferred", "do",
            "dynamic", "else", "enum", "export", "extends", "extension", "external",
            "factory", "false", "final", "finally", "for", "Function", "get", "hide",
            "if", "implements", "import", "in", "interface", "is", "late", "library",
            "mixin", "new", "null", "on", "operator", "part", "rethrow", "return",
            "set", "show", "static", "super", "switch", "sync", "this", "throw",
            "true", "try", "typedef", "var", "void", "while", "with", "yield"
        ]
        for word in keywords:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, keyword_format))
        
      
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        types = ["int", "double", "num", "String", "bool", "List", "Set", "Map",
                "Runes", "Symbol", "Object", "Null", "Future", "Stream", "Iterable"]
        for word in types:
            pattern = QRegularExpression(r"\b" + word + r"\b")
            self.highlighting_rules.append((pattern, type_format))
        
      
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegularExpression("//[^\n]*"), comment_format))
        
    
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression("\"[^\"]*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("\'[^\']*\'"), string_format))
        self.highlighting_rules.append((QRegularExpression(r"\$\{[^\}]*\}"), string_format))
        
        
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b\d+\.\d+\b"), number_format))
        self.highlighting_rules.append((QRegularExpression(r"\b0x[0-9A-Fa-f]+\b"), number_format))
        
       
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        self.highlighting_rules.append((QRegularExpression(r"\b\w+\([^\)]*\)\s*\{"), function_format))
        
      
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((QRegularExpression(r"\bclass\s+(\w+)"), class_format))

class HtmlHighlighter(BaseHighlighter):
    def setup_highlight_rules(self):
       
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#569CD6"))
        html_tags = [
            "html", "head", "body", "div", "span", "p", "a", "img", "ul", "ol",
            "li", "table", "tr", "td", "th", "form", "input", "button", "select",
            "option", "textarea", "label", "h1", "h2", "h3", "h4", "h5", "h6",
            "style", "script", "meta", "link", "title", "header", "footer", "nav",
            "section", "article", "aside", "main", "figure", "figcaption"
        ]
        for tag in html_tags:
            pattern = QRegularExpression(r"<\/?" + tag + r"\b")
            self.highlighting_rules.append((pattern, tag_format))
        
       
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor("#9CDCFE"))
        html_attrs = [
            "class", "id", "href", "src", "alt", "title", "type", "value", "name",
            "placeholder", "required", "disabled", "checked", "selected", "style"
        ]
        for attr in html_attrs:
            pattern = QRegularExpression(attr + r"=")
            self.highlighting_rules.append((pattern, attribute_format))
        
       
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegularExpression(r"=\"[^\"]*\""), value_format))
        
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegularExpression(r"<!--[^>]*-->"), comment_format))
        
       
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(QColor("#569CD6"))
        self.highlighting_rules.append((QRegularExpression(r"<!DOCTYPE[^>]*>"), doctype_format))
        
     
        entity_format = QTextCharFormat()
        entity_format.setForeground(QColor("#4EC9B0"))
        self.highlighting_rules.append((QRegularExpression(r"&[a-z]+;"), entity_format))

class EnhancedAIChatPanel(QDockWidget):
    """Panel de IA mejorado para generación de código con múltiples proveedores"""
    def __init__(self, code_generator, parent=None):
        super().__init__("AI Assistant", parent)
        self.code_generator = code_generator
        self.conversation_history = []
        self.current_provider = None
        self.available_providers = []
        self.current_worker = None
        self.setupUI()
        self.load_api_keys()
        self.detect_available_providers()

    def setupUI(self):
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        
       
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Proveedor IA:"))
        
        self.provider_combo = QComboBox()
        self.provider_combo.currentTextChanged.connect(self.change_ai_provider)
        provider_layout.addWidget(self.provider_combo)
        
 
        self.config_btn = QPushButton("Configurar API")
        self.config_btn.clicked.connect(self.show_api_config_dialog)
        provider_layout.addWidget(self.config_btn)
        
        provider_layout.addStretch()
        layout.addLayout(provider_layout)
        
     
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Conversa con la IA sobre tu diseño...")
        layout.addWidget(self.chat_history)
        
     
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Escribe tu mensaje o pide generar código...")
        self.user_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.user_input)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        

        code_buttons_layout = QHBoxLayout()
        self.gen_xml_btn = QPushButton("Generar XML")
        self.gen_xml_btn.clicked.connect(self.generate_xml)
        self.gen_java_btn = QPushButton("Generar Java")
        self.gen_java_btn.clicked.connect(self.generate_java)
        self.export_btn = QPushButton("Exportar Proyecto")
        self.export_btn.clicked.connect(self.export_project)
        
        code_buttons_layout.addWidget(self.gen_xml_btn)
        code_buttons_layout.addWidget(self.gen_java_btn)
        code_buttons_layout.addWidget(self.export_btn)
        
        layout.addLayout(input_layout)
        layout.addLayout(code_buttons_layout)
        chat_widget.setLayout(layout)
        self.setWidget(chat_widget)
        
       
        self.add_message("Asistente IA", "¡Hola! Estoy listo para ayudarte a generar código Android. Puedes diseñar tu interfaz y yo me encargaré de crear el código XML y Java correspondiente.")

    def show_api_config_dialog(self):
        """Muestra diálogo para configurar API keys"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurar API Keys")
        dialog.setModal(True)
        dialog.setFixedSize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
       
        deepseek_layout = QHBoxLayout()
        deepseek_layout.addWidget(QLabel("DeepSeek API Key:"))
        deepseek_input = QLineEdit()
        deepseek_input.setPlaceholderText("sk-...")
        deepseek_input.setText(os.getenv("DEEPSEEK_API_KEY", ""))
        deepseek_input.setEchoMode(QLineEdit.Password)
        deepseek_layout.addWidget(deepseek_input)
        layout.addLayout(deepseek_layout)
        
       
        hf_layout = QHBoxLayout()
        hf_layout.addWidget(QLabel("Hugging Face API Key:"))
        hf_input = QLineEdit()
        hf_input.setPlaceholderText("hf_...")
        hf_input.setText(os.getenv("HUGGINGFACE_API_KEY", ""))
        hf_input.setEchoMode(QLineEdit.Password)
        hf_layout.addWidget(hf_input)
        layout.addLayout(hf_layout)
        
        
        info_label = QLabel(
            "Para obtener API keys:\n"
            "• DeepSeek: https://platform.deepseek.com/\n"
            "• Hugging Face: https://huggingface.co/settings/tokens"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(info_label)
        
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(lambda: self.save_api_keys(dialog, deepseek_input.text(), hf_input.text()))
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def save_api_keys(self, dialog, deepseek_key, hf_key):
        """Guarda las API keys en el archivo .env"""
        deepseek_key = deepseek_key.strip()
        hf_key = hf_key.strip()
        
        
        if deepseek_key and not deepseek_key.startswith("sk-"):
            QMessageBox.warning(self, "Error", "La API Key de DeepSeek debe comenzar con 'sk-'")
            return
        
        if hf_key and not hf_key.startswith("hf_"):
            QMessageBox.warning(self, "Error", "La API Key de Hugging Face debe comenzar con 'hf_'")
            return
        
        
        env_path = project_root / '.env'
        env_content = []
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_content = f.readlines()
        
       
        keys_to_update = {
            'DEEPSEEK_API_KEY': deepseek_key,
            'HUGGINGFACE_API_KEY': hf_key
        }
        
        new_env_content = []
        keys_updated = set()
        
        for line in env_content:
            line_stripped = line.strip()
            if '=' in line_stripped:
                key = line_stripped.split('=')[0].strip()
                if key in keys_to_update:
                    new_env_content.append(f"{key}={keys_to_update[key]}\n")
                    keys_updated.add(key)
                    continue
            new_env_content.append(line)
        
       
        for key, value in keys_to_update.items():
            if key not in keys_updated:
                new_env_content.append(f"{key}={value}\n")
        
        with open(env_path, 'w') as f:
            f.writelines(new_env_content)
        

        load_dotenv(env_path, override=True)
        
    
        self.load_api_keys()
        self.detect_available_providers()
        
        dialog.accept()
        QMessageBox.information(self, "Éxito", "API Keys guardadas correctamente. Reinicia la aplicación para que los cambios surtan efecto completo.")

    def load_api_keys(self):
        """Carga las API keys de los diferentes proveedores"""
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.huggingface_key = os.getenv("HUGGINGFACE_API_KEY")

    def detect_available_providers(self):
        """Detecta los proveedores de IA disponibles"""
        self.available_providers = []
        self.provider_combo.clear()
        
     
        if self.deepseek_key and self.deepseek_key.startswith("sk-"):
            self.available_providers.append(AIProvider.DEEPSEEK)
            self.provider_combo.addItem("DeepSeek", AIProvider.DEEPSEEK)
        
        
        if self.huggingface_key and self.huggingface_key.startswith("hf_"):
            self.available_providers.append(AIProvider.STARCODER)
            self.provider_combo.addItem("StarCoder (Hugging Face)", AIProvider.STARCODER)
        
        
        if self.available_providers:
            self.current_provider = self.available_providers[0]
            self.provider_combo.setCurrentIndex(0)
            self.add_message("Sistema", f"✅ Conectado a {self.provider_combo.currentText()}")
            
           
            self.set_ui_enabled(True)
        else:
            self.add_message("Sistema", "⚠️ No hay proveedores de IA configurados")
            self.add_message("Sistema", "Haz clic en 'Configurar API' para agregar tus API keys")
            
       
            self.set_ui_enabled(False)
            self.config_btn.setEnabled(True)

    def change_ai_provider(self, provider_text):
        """Cambia el proveedor de IA seleccionado"""
        provider_data = self.provider_combo.currentData()
        if provider_data:
            self.current_provider = provider_data
            self.add_message("Sistema", f"🔁 Cambiado a {provider_text}")

    def set_ui_enabled(self, enabled):
        """Habilita/deshabilita la UI durante las llamadas a API"""
        self.send_button.setEnabled(enabled)
        self.user_input.setEnabled(enabled)
        self.gen_xml_btn.setEnabled(enabled)
        self.gen_java_btn.setEnabled(enabled)
        self.export_btn.setEnabled(enabled)
        self.provider_combo.setEnabled(enabled and len(self.available_providers) > 1)
        self.config_btn.setEnabled(enabled)

    def send_message(self):
        user_text = self.user_input.text().strip()
        if not user_text:
            return
            
        self.add_message("Tú", user_text)
        self.user_input.clear()
        
      
        if not self.available_providers:
            self.add_message("Sistema", "❌ No hay proveedores de IA configurados")
            self.add_message("Sistema", "Por favor, configura tus API keys primero")
            self.use_local_response(user_text)
            return
        
      
        self.set_ui_enabled(False)
        self.add_message("Asistente IA", "Pensando...")
        
        try:
            if self.current_provider == AIProvider.DEEPSEEK:
                self.use_deepseek(user_text)
            elif self.current_provider == AIProvider.STARCODER:
                self.use_starcoder(user_text)
            else:
                self.use_local_response(user_text)
        except Exception as e:
            self.handle_ai_error(f"Error al iniciar la consulta: {str(e)}")

    def use_deepseek(self, user_message):
        """Usa DeepSeek para generar la respuesta"""
       
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.quit()
            self.current_worker.wait()
        
        self.current_worker = DeepSeekWorker(
            self.deepseek_key, 
            user_message, 
            self.conversation_history
        )
        self.current_worker.response_received.connect(self.handle_ai_response)
        self.current_worker.error_occurred.connect(self.handle_ai_error)
        self.current_worker.finished.connect(self.on_worker_finished)
        self.current_worker.start()

    def use_starcoder(self, user_message):
        """Usa StarCoder para generar la respuesta"""
        
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.quit()
            self.current_worker.wait()
        
        enhanced_prompt = self.enhance_prompt_for_starcoder(user_message)
        
        self.current_worker = StarCoderWorker(
            self.huggingface_key,
            enhanced_prompt,
            "bigcode/starcoder2-15b"
        )
        self.current_worker.response_received.connect(self.handle_ai_response)
        self.current_worker.error_occurred.connect(self.handle_ai_error)
        self.current_worker.finished.connect(self.on_worker_finished)
        self.current_worker.start()

    def on_worker_finished(self):
        """Se llama cuando el worker termina su ejecución"""
        self.current_worker = None

    def enhance_prompt_for_starcoder(self, user_message):
        """Mejora el prompt para StarCoder con contexto específico"""
        design_context = self.get_design_context()
        
        enhanced_prompt = f"""
Eres un asistente especializado en desarrollo Android. Responde en español.

Contexto del diseño actual:
{design_context}

Pregunta del usuario: {user_message}

Por favor, proporciona una respuesta útil que incluya:
1. Explicación clara en español
2. Código relevante si es aplicable
3. Ejemplos prácticos

Respuesta:"""
        
        return enhanced_prompt

    def get_design_context(self):
        """Obtiene información sobre los elementos de diseño actuales"""
        if not hasattr(self, 'code_generator') or not self.code_generator.elements:
            return "No hay elementos de diseño actualmente."
        
        context = "Elementos actuales en el diseño:\n"
        for i, element in enumerate(self.code_generator.elements, 1):
            context += f"{i}. {element.androidWidgetType} "
            context += f"({element.x}px, {element.y}px) "
            context += f"{element.width}x{element.height}px\n"
            
            if element.properties.get("text"):
                context += f"   Texto: {element.properties['text']}\n"
            if element.properties.get("backgroundColor") != "#FFFFFF":
                context += f"   Color fondo: {element.properties['backgroundColor']}\n"
        
        return context

    def handle_ai_response(self, response):
        """Maneja la respuesta de la IA"""
        cleaned_response = self.clean_ai_response(response)
        self.add_message("Asistente IA", cleaned_response)
        
        self.conversation_history.append({"role": "assistant", "content": cleaned_response})
        self.set_ui_enabled(True)

    def clean_ai_response(self, response):
        """Limpia y formatea la respuesta de la IA"""
        if "```" in response:
            return response
        
        lines = response.split('\n')
        cleaned_lines = []
        skip = False
        
        for line in lines:
            if "Eres un asistente" in line or "Contexto del diseño" in line:
                skip = True
            elif "Pregunta del usuario:" in line:
                skip = False
            elif not skip:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

    def add_message(self, sender, message):
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        if sender == "Tú":
            cursor.insertHtml(f'<div style="background-color: #e3f2fd; padding: 8px; margin: 5px; border-radius: 8px; border: 1px solid #bbdefb;">'
                             f'<b>{sender}:</b> {message}</div>')
        else:
            if "```" in message:
                parts = message.split("```")
                formatted_message = ""
                for i, part in enumerate(parts):
                    if i % 2 == 1:
                        formatted_message += f'<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">{part}</pre>'
                    else:
                        formatted_message += part
                message = formatted_message
            
            cursor.insertHtml(f'<div style="background-color: #f5f5f5; padding: 8px; margin: 5px; border-radius: 8px; border: 1px solid #e0e0e0;">'
                             f'<b>{sender}:</b> {message}</div>')
        
        cursor.insertHtml("<br>")
        self.chat_history.ensureCursorVisible()

    def use_local_response(self, user_message):
        """Usar respuestas locales cuando no hay API key"""
        lower_msg = user_message.lower()
        
        if any(word in lower_msg for word in ["java", "android", "código"]):
            response = "Puedo ayudarte con código Java/Android. Para mejores resultados, configura tus API Keys."
        elif any(word in lower_msg for word in ["rectángulo", "cuadrado", "view"]):
            response = "Elemento rectangular detectado. Configura tus API Keys para generar código XML automático."
        elif any(word in lower_msg for word in ["texto", "textview"]):
            response = "Elemento de texto. Con las API Keys podré generar TextView personalizado."
        elif any(word in lower_msg for word in ["botón", "button"]):
            response = "Botón detectado. Las API Keys me permitirán generar onClick listeners."
        elif any(word in lower_msg for word in ["color", "colores"]):
            response = "Puedo ayudar con colores Android (#AARRGGBB). Ejemplo: #FF6200EE para púrpura."
        else:
            response = "Estoy aquí para ayudarte con desarrollo Android. Para respuestas más avanzadas, necesitas configurar API Keys."
        
        QTimer.singleShot(1000, lambda: self.add_message("Asistente IA", response))
        self.set_ui_enabled(True)

    def handle_ai_error(self, error_msg):
        """Maneja errores de la API"""
        error_text = f"Error al conectar con la IA: {error_msg}"
        self.add_message("Sistema", error_text)
        self.set_ui_enabled(True)

    def generate_xml(self):
        xml_code = self.code_generator.generateLayoutXML()
        self.add_message("Asistente IA", "He generado el código XML para tu layout:\n\n```xml\n" + xml_code + "\n```")
    
    def generate_java(self):
        java_code = self.code_generator.generateActivityJava()
        self.add_message("Asistente IA", "He generado el código Java para tu Activity:\n\n```java\n" + java_code + "\n```")
    
    def export_project(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar directorio para exportar")
        if directory:
            success = self.code_generator.exportProject(directory)
            if success:
                self.add_message("Asistente IA", f"¡Proyecto exportado exitosamente a {directory}! Ya puedes abrirlo en Android Studio.")
            else:
                self.add_message("Asistente IA", "Hubo un error al exportar el proyecto. Por favor, intenta nuevamente.")

    def closeEvent(self, event):
        """Maneja el cierre del panel para detener los workers"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.quit()
            self.current_worker.wait()
        super().closeEvent(event)

class AIResponseEvent(QEvent):
    """Evento personalizado para respuestas de IA"""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, response, is_error=False):
        super().__init__(self.EVENT_TYPE)
        self.response = response
        self.is_error = is_error

class IllustratorWindow(QMainWindow):
    closed = Signal()
    
    def __init__(self, project_name="Untitled", project_path=None, project_language="Java"):
        super().__init__()
        self.project_name = project_name
        self.project_language = project_language
        
        if project_path is None:
            default_dir = os.path.join(os.path.expanduser("~"), "CreatorsStudio", project_name)
            os.makedirs(default_dir, exist_ok=True)
            self.project_path = os.path.abspath(default_dir)
        else:
            self.project_path = os.path.abspath(project_path)
            if not os.path.exists(self.project_path):
                os.makedirs(self.project_path, exist_ok=True)
        
        print(f"DEBUG: Proyecto {project_name} - Lenguaje: {project_language}")
        print(f"DEBUG: Ruta del proyecto: {self.project_path}")
        
        self.setWindowTitle(f"Creators Studio - {project_name} [{project_language}]")
        self.setGeometry(100, 100, 1400, 800)
        
        
        self.code_generator = CodeGenerator(project_name)
        
       
        self.open_files = {}
        self.current_editor = None
        
      
        self.current_tool = "select"
        self.current_color = "#FFFFFF"
        self.tool_buttons = {}
        
        self.setup_workspace()
        self.create_workspace_presets()
        self.setup_ui()

        self.setup_enhanced_docks()

        self.create_menu_bar()
        self.setup_language_specific_features()

    def setup_enhanced_docks(self):
        """Configuración mejorada de docks inspirada en MainWindow"""
        
        # Lista de todos los docks posibles
        all_docks = [
            self.tool_panel, self.layers_panel, self.color_panel,
            self.ai_panel, self.file_explorer_panel
        ]
        
        # Añadir paragraph_panel solo si existe
        if hasattr(self, 'paragraph_panel') and self.paragraph_panel:
            all_docks.append(self.paragraph_panel)
        
        # Remover todos los docks existentes
        for dock in all_docks:
            if dock and dock in self.findChildren(QDockWidget):
                self.removeDockWidget(dock)
        
        # Añadir docks en posiciones específicas
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tool_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layers_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.color_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.ai_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_explorer_panel)
        
        # Agrupar docks relacionados
        self.tabifyDockWidget(self.tool_panel, self.layers_panel)
        self.tabifyDockWidget(self.tool_panel, self.file_explorer_panel)
        self.tabifyDockWidget(self.color_panel, self.ai_panel)
        
        # Traer al frente los docks principales
        self.tool_panel.raise_()
        self.color_panel.raise_()
    def open_android_designer(self):
        """Abre la ventana de diseñador Android"""
        if 'designer' not in self.open_windows:
            self.open_windows['designer'] = IllustratorWindow("Nuevo Diseño Android", project_language="Java")
            self.open_windows['designer'].closed.connect(lambda: self.on_window_closed('designer'))
        self.open_windows['designer'].show()
        self.open_windows['designer'].raise_()

    def open_java_editor(self):
        """Abre ventana de editor Java"""
        if 'java_editor' not in self.open_windows:
            self.open_windows['java_editor'] = self.create_code_editor_window("Editor Java", "java")
        self.open_windows['java_editor'].show()
        self.open_windows['java_editor'].raise_()

    def open_xml_editor(self):
        """Abre ventana de editor XML"""
        if 'xml_editor' not in self.open_windows:
            self.open_windows['xml_editor'] = self.create_code_editor_window("Editor XML", "xml")
        self.open_windows['xml_editor'].show()
        self.open_windows['xml_editor'].raise_()

    def open_ai_chat(self):
        """Abre ventana de chat IA independiente"""
        if 'ai_chat' not in self.open_windows:
            self.open_windows['ai_chat'] = self.create_ai_chat_window()
        self.open_windows['ai_chat'].show()
        self.open_windows['ai_chat'].raise_()

    def open_project_explorer(self):
        """Abre ventana de explorador de proyectos"""
        if 'project_explorer' not in self.open_windows:
            self.open_windows['project_explorer'] = self.create_project_explorer_window()
        self.open_windows['project_explorer'].show()
        self.open_windows['project_explorer'].raise_()

    def create_code_editor_window(self, title, language):
        """Crea ventana de editor de código"""
        window = QMainWindow(self)
        window.setWindowTitle(title)
        window.resize(800, 600)
        
        editor = CodeEditor()
        if language == "java":
            editor.setPlainText("// Editor Java\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hola Mundo\");\n    }\n}")
        elif language == "xml":
            editor.setPlainText("<!-- Editor XML -->\n<LinearLayout xmlns:android=\"http://schemas.android.com/apk/res/android\"\n    android:layout_width=\"match_parent\"\n    android:layout_height=\"match_parent\">\n</LinearLayout>")
        
        editor.set_highlighter(f"example.{language}")
        window.setCentralWidget(editor)
        
        return window

    def create_ai_chat_window(self):
        """Crea ventana de chat IA independiente"""
        window = QMainWindow(self)
        window.setWindowTitle("Chat IA - Asistente")
        window.resize(500, 600)
        
       
        ai_widget = QWidget()
        layout = QVBoxLayout(ai_widget)
        layout.addWidget(QLabel("Panel de Chat IA"))
        window.setCentralWidget(ai_widget)
        
        return window

    def create_project_explorer_window(self):
        """Crea ventana de explorador de proyectos"""
        window = QMainWindow(self)
        window.setWindowTitle("Explorador de Proyectos")
        window.resize(400, 600)
        
        fs_model = QFileSystemModel()
        fs_model.setRootPath("")
        tree = QTreeView()
        tree.setModel(fs_model)
        tree.setRootIndex(fs_model.index(""))
        
        window.setCentralWidget(tree)
        return window

    def cascade_windows(self):
        """Organiza ventanas en cascada"""
        if not self.open_windows:
            return
            
        x, y = 30, 30
        for i, (key, window) in enumerate(self.open_windows.items()):
            window.move(x * (i + 1), y * (i + 1))
            window.raise_()

    def tile_windows(self):
        """Organiza ventanas en mosaico"""
        if not self.open_windows:
            return
            
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        num_windows = len(self.open_windows)
        cols = int(math.sqrt(num_windows))
        rows = (num_windows + cols - 1) // cols
        
        width = screen_geometry.width() // cols
        height = screen_geometry.height() // rows
        
        for i, (key, window) in enumerate(self.open_windows.items()):
            row = i // cols
            col = i % cols
            x = col * width
            y = row * height
            window.setGeometry(x, y, width, height)
            window.raise_()

    def close_all_windows(self):
        """Cierra todas las ventanas abiertas"""
        for key, window in list(self.open_windows.items()):
            window.close()
        self.open_windows.clear()

    def on_window_closed(self, window_key):
        """Maneja el cierre de ventanas"""
        if window_key in self.open_windows:
            del self.open_windows[window_key]

    def setup_workspace(self):
        self.current_preset = "Default"
        self.tool_panel_position = "left"
        #self.visible_panels = ["Tools", "Layers", "Properties", "Color", "AI Assistant"]
        self.visible_panels = ["Tools", "Layers", "Color", "AI Assistant"]

    def create_workspace_presets(self):
        self.workspace_presets = {
            "Default": WorkspacePreset("Default", "left", ["Tools", "Layers", "AI Assistant"]),
            "Minimal": WorkspacePreset("Minimal", "left", ["Tools", "AI Assistant"]),
            "Painting": WorkspacePreset("Painting", "right", ["Tools", "Brushes", "Color", "AI Assistant"]),
            "Typography": WorkspacePreset("Typography", "left", ["Tools", "Character", "Paragraph", "AI Assistant"]),
            "Development": WorkspacePreset("Development", "right", ["Tools", "AI Assistant"])
        }

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
        self.emulator_container = QWidget()
        self.emulator_layout = QVBoxLayout(self.emulator_container)
        
        self.initial_message = QLabel("Haga doble clic en un archivo en el explorador para abrirlo")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet("font-size: 16px; color: #666; padding: 50px;")
        self.emulator_layout.addWidget(self.initial_message)
        
        self.design_canvas = None
        self.phone_frame = None
        
        self.tab_widget.addTab(self.emulator_container, "Emulador")
        self.tab_widget.setTabToolTip(0, "Vista de emulación móvil")
        
        self.main_layout.addWidget(self.tab_widget)
        
 
        self.create_tool_panel()
        self.create_layers_panel()
        #self.create_properties_panel()
        self.create_color_panel()
        self.create_brushes_panel()
        self.create_character_panel()
        self.create_paragraph_panel()
        self.create_ai_panel()
        self.create_file_explorer_panel()
        
        self.create_menu_bar()
        
        self.statusBar().showMessage("Ready | Zoom: 100%")
        self.apply_workspace_preset(self.current_preset)

    def setup_language_specific_features(self):
        if self.project_language == "Java":
            self.setup_java_features()
        elif self.project_language == "Kotlin":
            self.setup_kotlin_features()
        elif self.project_language == "Dart (Flutter)":
            self.setup_flutter_features()

    def setup_java_features(self):
        self.setWindowTitle(f"Creators Studio - {self.project_name} [Java]")
        if hasattr(self, 'ai_panel'):
            self.ai_panel.chat_history.setPlainText(
                "Modo Java activado. Puedo ayudarte con:\n"
                "- Código Java para Android\n- Layouts XML\n"
                "- Activities y Fragments\n- Intents y Services"
            )

    def setup_kotlin_features(self):
        self.setWindowTitle(f"Creators Studio - {self.project_name} [Kotlin]")
        if hasattr(self, 'ai_panel'):
            self.ai_panel.chat_history.setPlainText(
                "Modo Kotlin activado. Puedo ayudarte con:\n"
                "- Código Kotlin para Android\n- Extension functions\n"
                "- Coroutines\n- Null safety"
            )

    def setup_flutter_features(self):
        self.setWindowTitle(f"Creators Studio - {self.project_name} [Flutter]")
        if hasattr(self, 'ai_panel'):
            self.ai_panel.chat_history.setPlainText(
                "Modo Flutter activado. Puedo ayudarte con:\n"
                "- Widgets de Flutter\n- Estado con Provider/Bloc\n"
                "- Diseño responsive\n- Packages de pub.dev"
            )

    def create_tool_panel(self):
        self.tool_panel = QDockWidget("Herramientas", self)
        self.tool_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        tool_widget = QWidget()
        layout = QVBoxLayout(tool_widget)
        
        tools = [
            ("Seleccionar", "select"),
            ("Rectángulo", "rectangle"),
            ("Texto", "text"),
            ("Botón", "button"),
            ("Campo de texto", "input")
        ]
        
        self.tool_buttons = {}
        for tool_name, tool_id in tools:
            btn = QPushButton(tool_name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, tid=tool_id: self.set_tool(tid))
            layout.addWidget(btn)
            self.tool_buttons[tool_id] = btn
        
        self.tool_buttons["select"].setChecked(True)
        layout.addStretch()
        tool_widget.setLayout(layout)
        self.tool_panel.setWidget(tool_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tool_panel)

    def create_layers_panel(self):
        self.layers_panel = QDockWidget("Capas", self)
        self.layers_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        layers_widget = QWidget()
        layout = QVBoxLayout(layers_widget)
        
        self.layers_list = QListWidget()
        layout.addWidget(self.layers_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("+")
        remove_btn = QPushButton("-")
        up_btn = QPushButton("↑")
        down_btn = QPushButton("↓")
        
        add_btn.clicked.connect(self.add_layer)
        remove_btn.clicked.connect(self.remove_layer)
        up_btn.clicked.connect(self.move_layer_up)
        down_btn.clicked.connect(self.move_layer_down)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)
        
        layout.addLayout(btn_layout)
        layers_widget.setLayout(layout)
        self.layers_panel.setWidget(layers_widget)

   # def create_properties_panel(self):
   #     self.properties_panel = QDockWidget("Propiedades", self)
    #    self.properties_panel.setAllowedAreas(
    #        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea
   #     )

   #     self.properties_panel.setFeatures(
    #        QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable
     #   )
      #  properties_widget = QWidget()
     #   layout = QVBoxLayout(properties_widget)
    #    
   #     self.properties_label = QLabel("Seleccione un elemento para ver sus propiedades")
    #    layout.addWidget(self.properties_label)
        
        
     #   self.bg_color_btn = QPushButton("Color de fondo")
      #  self.bg_color_btn.clicked.connect(self.change_element_bg_color)
       # layout.addWidget(self.bg_color_btn)
        
      #  self.text_size_combo = QComboBox()
     #   self.text_size_combo.addItems(["12sp", "14sp", "16sp", "18sp", "20sp", "24sp"])
    #    self.text_size_combo.currentTextChanged.connect(self.change_text_size)
    #    layout.addWidget(QLabel("Tamaño de texto:"))
     #   layout.addWidget(self.text_size_combo)
        
    #    self.corner_radius_slider = QSlider(Qt.Horizontal)
    #    self.corner_radius_slider.setRange(0, 32)
    #    self.corner_radius_slider.valueChanged.connect(self.change_corner_radius)
    #    layout.addWidget(QLabel("Radio de esquinas:"))
    #    layout.addWidget(self.corner_radius_slider)
        
    #    layout.addStretch()
    #    properties_widget.setLayout(layout)
    #    self.properties_panel.setWidget(properties_widget)
        
        
    #    self.properties_panel.setVisible(False)
   
    def change_element_bg_color(self):
        if self.selected_element:
            color = QColorDialog.getColor()
            if color.isValid():
                self.selected_element.setProperty("backgroundColor", color.name())
                if self.selected_element.graphicsItem:
                    self.selected_element.graphicsItem.setBrush(QBrush(color))
               # self.properties_panel.update()

    def change_text_size(self, size):
        if self.selected_element:
            self.selected_element.setProperty("textSize", size)
           # self.properties_panel.update()

    def change_corner_radius(self, radius):
        if self.selected_element:
            self.selected_element.setProperty("cornerRadius", f"{radius}dp")
          #  self.properties_panel.update()
    def create_color_panel(self):
        self.color_panel = QDockWidget("Colores", self)
        self.color_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        color_widget = QWidget()
        layout = QVBoxLayout(color_widget)
        
        self.color_button = QPushButton("Seleccionar Color")
        self.color_button.clicked.connect(self.choose_color)
        layout.addWidget(self.color_button)
        
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(50, 50)
        self.color_preview.setStyleSheet("background-color: #FFFFFF; border: 1px solid black;")
        layout.addWidget(self.color_preview)
        
        color_widget.setLayout(layout)
        self.color_panel.setWidget(color_widget)

    def create_brushes_panel(self):
        self.brushes_panel = QDockWidget("Pinceles", self)
        brushes_widget = QWidget()
        brushes_widget.setLayout(QVBoxLayout())
        self.brushes_panel.setWidget(brushes_widget)

    def create_character_panel(self):
        self.character_panel = QDockWidget("Carácter", self)
        character_widget = QWidget()
        character_widget.setLayout(QVBoxLayout())
        self.character_panel.setWidget(character_widget)
    def create_paragraph_panel(self):
        self.paragraph_panel = QDockWidget("Párrafo", self)
        self.paragraph_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.paragraph_panel.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        
        paragraph_widget = QWidget()
        paragraph_widget.setLayout(QVBoxLayout())
        self.paragraph_panel.setWidget(paragraph_widget)
        
        # Añadir el panel al área de docks (pero mantenerlo oculto inicialmente)
        self.addDockWidget(Qt.RightDockWidgetArea, self.paragraph_panel)
        self.paragraph_panel.setVisible(False)  # Oculto por defecto
    def create_ai_panel(self):
        self.ai_panel = EnhancedAIChatPanel(self.code_generator, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.ai_panel)

    def create_file_explorer_panel(self):
        self.file_explorer_panel = QDockWidget("Explorador de Archivos", self)
        self.file_explorer_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        explorer_widget = QWidget()
        layout = QVBoxLayout(explorer_widget)
        
        # ===== CONFIGURACIÓN SIMPLIFICADA =====
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.project_path)
        
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(self.project_path))
        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
        
        # Ocultar columnas innecesarias (más simple)
        for i in range(1, 4):  # Columnas 1, 2 y 3
            self.file_tree.hideColumn(i)
        # ===== FIN CONFIGURACIÓN SIMPLIFICADA =====
        
        layout.addWidget(self.file_tree)
        explorer_widget.setLayout(layout)
        self.file_explorer_panel.setWidget(explorer_widget)

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Archivo")
        
        new_action = QAction("Nuevo", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Abrir", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Guardar", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_current_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menubar.addMenu("Editar")
        undo_action = QAction("Deshacer", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Rehacer", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # ===== MENÚ VER =====
        view_menu = menubar.addMenu("Ver")
        
        # Submenú para paneles
        panels_menu = view_menu.addMenu("Paneles")
        panels_menu.addAction(self.tool_panel.toggleViewAction())
        panels_menu.addAction(self.layers_panel.toggleViewAction())
        panels_menu.addAction(self.color_panel.toggleViewAction())
        panels_menu.addAction(self.ai_panel.toggleViewAction())
        panels_menu.addAction(self.file_explorer_panel.toggleViewAction())
        panels_menu.addAction(self.paragraph_panel.toggleViewAction())
        # Submenú para workspace presets
        workspace_menu = view_menu.addMenu("Espacio de Trabajo")
        for preset_name in self.workspace_presets.keys():
            action = QAction(preset_name, self)
            action.triggered.connect(lambda checked, name=preset_name: self.apply_workspace_preset(name))
            workspace_menu.addAction(action)
        # ===== FIN MENÚ VER =====
        
        windows_menu = menubar.addMenu("Ventanas")
        
        self.open_designer_action = QAction("Diseñador Android", self)
        windows_menu.addAction(self.open_designer_action)
        
        self.open_java_editor_action = QAction("Editor Java", self)
        windows_menu.addAction(self.open_java_editor_action)
        
        self.open_xml_editor_action = QAction("Editor XML", self)
        windows_menu.addAction(self.open_xml_editor_action)
        
        self.open_ai_chat_action = QAction("Chat IA", self)
        windows_menu.addAction(self.open_ai_chat_action)
        
        self.open_project_explorer_action = QAction("Explorador Proyectos", self)
        windows_menu.addAction(self.open_project_explorer_action)
        
        windows_menu.addSeparator()

        self.cascade_action = QAction("Cascada", self)
        self.cascade_action.triggered.connect(self.cascade_windows)
        windows_menu.addAction(self.cascade_action)

        self.tile_action = QAction("Mosaico", self)
        self.tile_action.triggered.connect(self.tile_windows)
        windows_menu.addAction(self.tile_action)

        self.close_all_action = QAction("Cerrar Todas", self)
        self.close_all_action.triggered.connect(self.close_all_windows)
        windows_menu.addAction(self.close_all_action)
    
        self.open_designer_action.triggered.connect(self.open_android_designer)
        self.open_java_editor_action.triggered.connect(self.open_java_editor)
        self.open_xml_editor_action.triggered.connect(self.open_xml_editor)
        self.open_ai_chat_action.triggered.connect(self.open_ai_chat)
        self.open_project_explorer_action.triggered.connect(self.open_project_explorer) 
        self.open_windows = {}
    def apply_workspace_preset(self, preset_name):
        if preset_name in self.workspace_presets:
            preset = self.workspace_presets[preset_name]
            self.current_preset = preset_name

            all_panels = {
                "Tools": self.tool_panel,
                "Layers": self.layers_panel,
                "Color": self.color_panel,
                "Brushes": self.brushes_panel,
                "Character": self.character_panel,
                "Paragraph": self.paragraph_panel,  # ← Asegúrate de que esté aquí
                "AI Assistant": self.ai_panel,
                "File Explorer": self.file_explorer_panel
            }
            
    #        for panel_name, panel in all_panels.items():
    #            if panel:
    #                panel.setVisible(False)
            
           
    #        for panel_name in preset.panels:
    #            if panel_name in all_panels and all_panels[panel_name]:
    #                all_panels[panel_name].setVisible(True)
    #                
    #                if panel_name == "Tools":
    #                    area = Qt.LeftDockWidgetArea if preset.tool_panel_pos == "left" else Qt.RightDockWidgetArea
    #                    self.addDockWidget(area, all_panels[panel_name])
  
    def set_tool(self, tool_id):
        self.current_tool = tool_id
        for tid, btn in self.tool_buttons.items():
            btn.setChecked(tid == tool_id)
        
        if self.design_canvas:
            self.design_canvas.setTool(tool_id)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self.current_color}; border: 1px solid black;")

    def on_file_double_clicked(self, index):
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            self.open_file_in_tab(file_path)

    def new_file(self):
        file_path, ok = QFileDialog.getSaveFileName(
            self, "Nuevo Archivo", self.project_path, "Todos los archivos (*)"
        )
        if ok and file_path:
            with open(file_path, 'w') as f:
                f.write("")
            self.open_file_in_tab(file_path)

    def open_file(self):
        file_path, ok = QFileDialog.getOpenFileName(
            self, "Abrir Archivo", self.project_path, "Todos los archivos (*)"
        )
        if ok and file_path:
            self.open_file_in_tab(file_path)

    def save_current_file(self):
        if self.current_editor:
            for path, tab_data in self.open_files.items():
                if tab_data['editor'] == self.current_editor:
                    content = self.current_editor.toPlainText()
                    self.save_file(path, content)
                    break

    def save_file(self, file_path=None, content=None):
        if file_path is None and self.current_editor:
            for path, tab_data in self.open_files.items():
                if tab_data['editor'] == self.current_editor:
                    file_path = path
                    break
            
            if file_path:
                content = self.current_editor.toPlainText()
        
        if file_path and content is not None:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                if self.current_editor:
                    self.current_editor.document().setModified(False)
                self.update_tab_title(file_path)
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{str(e)}")
                return False
        return False

    def update_tab_title(self, file_path):
        for path, tab_data in self.open_files.items():
            if path == file_path:
                index = self.tab_widget.indexOf(tab_data['widget'])
                file_name = os.path.basename(file_path)
                if tab_data['editor'].document().isModified():
                    self.tab_widget.setTabText(index, f"{file_name} *")
                else:
                    self.tab_widget.setTabText(index, file_name)
                break

    def add_layer(self):
        item = QListWidgetItem(f"Capa {self.layers_list.count() + 1}")
        self.layers_list.addItem(item)

    def remove_layer(self):
        current_row = self.layers_list.currentRow()
        if current_row >= 0:
            self.layers_list.takeItem(current_row)

    def move_layer_up(self):
        current_row = self.layers_list.currentRow()
        if current_row > 0:
            item = self.layers_list.takeItem(current_row)
            self.layers_list.insertItem(current_row - 1, item)
            self.layers_list.setCurrentRow(current_row - 1)

    def move_layer_down(self):
        current_row = self.layers_list.currentRow()
        if current_row < self.layers_list.count() - 1 and current_row >= 0:
            item = self.layers_list.takeItem(current_row)
            self.layers_list.insertItem(current_row + 1, item)
            self.layers_list.setCurrentRow(current_row + 1)

    def open_file_in_tab(self, file_path):
        if file_path in self.open_files:
            tab_data = self.open_files[file_path]
            index = self.tab_widget.indexOf(tab_data['widget'])
            self.tab_widget.setCurrentIndex(index)
            return
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
           
            tab_widget = QWidget()
            main_layout = QVBoxLayout(tab_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            
            
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            
        
            text_edit = CodeEditor()
            text_edit.setPlainText(content)
            text_edit.setFont(QFont("Consolas", 11))
            
           
            text_edit.set_highlighter(file_path)
            
            
            text_edit.document().modificationChanged.connect(
                lambda modified: self.update_tab_title(file_path)
            )
            
          
            scroll_area.setWidget(text_edit)
            main_layout.addWidget(scroll_area)
            
            tab_widget.text_edit = text_edit  
            tab_widget.scroll_area = scroll_area
           
            file_name = os.path.basename(file_path)
            tab_index = self.tab_widget.addTab(tab_widget, file_name)
            self.tab_widget.setCurrentIndex(tab_index)
            self.tab_widget.setTabToolTip(tab_index, file_path)
            

            self.open_files[file_path] = {
                'widget': tab_widget,
                'editor': text_edit,
                'original_content': content,
                'file_path': file_path
            }
            
       
            text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
            text_edit.customContextMenuRequested.connect(
                lambda pos: self.show_editor_context_menu(text_edit, pos)
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")

    def show_editor_context_menu(self, editor, pos):
        """Muestra el menú contextual para el editor"""
        menu = QMenu(self)
        
      
        undo_action = QAction("Deshacer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(editor.undo)
        menu.addAction(undo_action)
        
        redo_action = QAction("Rehacer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(editor.redo)
        menu.addAction(redo_action)
        
        menu.addSeparator()
        
        cut_action = QAction("Cortar", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(editor.cut)
        menu.addAction(cut_action)
        
        copy_action = QAction("Copiar", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(editor.copy)
        menu.addAction(copy_action)
        
        paste_action = QAction("Pegar", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(editor.paste)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        select_all_action = QAction("Seleccionar todo", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(editor.selectAll)
        menu.addAction(select_all_action)
        
      
        menu.exec_(editor.mapToGlobal(pos))

    def tab_changed(self, index):
        """Maneja el cambio de pestaña"""
        widget = self.tab_widget.widget(index)
        if hasattr(widget, 'text_edit'):
            self.current_editor = widget.text_edit
        else:
            self.current_editor = None

    def close_tab(self, index):
        """Cierra una pestaña"""
        if index == 0:
            return
            
        widget = self.tab_widget.widget(index)
        file_path = None
        
        for path, tab_data in self.open_files.items():
            if tab_data['widget'] == widget:
                file_path = path
                break
        
        if file_path:
            
            if widget.text_edit.document().isModified():
                reply = QMessageBox.question(
                    self, 
                    "Guardar cambios", 
                    f"¿Desea guardar los cambios en {os.path.basename(file_path)}?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Save:
                    self.save_file(file_path, widget.text_edit.toPlainText())
                elif reply == QMessageBox.Cancel:
                    return
            
            
            self.tab_widget.removeTab(index)
            if file_path in self.open_files:
                del self.open_files[file_path]

    def setup_phone_canvas(self):
        """Configura el canvas para que se vea como una pantalla de celular"""
        self.phone_width = 360
        self.phone_height = 640
        
        if self.design_canvas:
            self.design_canvas.setStyleSheet("""
                QGraphicsView {
                    background-color: #2C2C2C;
                    border: none;
                }
            """)

    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
       
        unsaved_files = []
        for file_path, tab_data in self.open_files.items():
            if tab_data['editor'].document().isModified():
                unsaved_files.append(os.path.basename(file_path))
        
        if unsaved_files:
            reply = QMessageBox.question(
                self,
                "Archivos sin guardar",
                f"Los siguientes archivos tienen cambios sin guardar:\n{', '.join(unsaved_files)}\n\n¿Estás seguro de que quieres salir?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                for file_path, tab_data in self.open_files.items():
                    if tab_data['editor'].document().isModified():
                        self.save_file(file_path, tab_data['editor'].toPlainText())
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        self.closed.emit()
        super().closeEvent(event)




#if __name__ == "__main__":
#    app = QApplication(sys.argv)

#    window = IllustratorWindow("Mi Proyecto Android", project_language="Java")
#    window.show()
  
#    rect_element = UIElement("rectangle", 50, 50, 200, 100)
#    rect_element.setProperty("backgroundColor", "#6200EE")
#    rect_element.setProperty("cornerRadius", "8dp")

#    text_element = UIElement("text", 70, 70, 160, 60)
#    text_element.setProperty("text", "Hola Mundo")
#    text_element.setProperty("textColor", "#FFFFFF")
#    text_element.setProperty("textSize", "18sp")

#    button_element = UIElement("button", 100, 200, 160, 60)
#    button_element.setProperty("text", "Presionar")
#    button_element.setProperty("backgroundColor", "#03DAC6")
#    button_element.setProperty("textColor", "#000000")

#    if hasattr(window, "code_generator") and window.code_generator:
#        window.code_generator.addElement(rect_element)
#        window.code_generator.addElement(text_element)
#        window.code_generator.addElement(button_element)

#    if hasattr(window, "layers_list"):
#        window.layers_list.addItem("Rectángulo (View)")
#        window.layers_list.addItem("Texto (TextView)")
#        window.layers_list.addItem("Botón (Button)")

 #   sys.exit(app.exec())
