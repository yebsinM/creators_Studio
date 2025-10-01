import os
import subprocess
import platform
from dotenv import load_dotenv
import requests
import shutil
import threading
import sys
import math 
import re
import psutil
from datetime import datetime
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
    QPlainTextEdit, QListWidgetItem, QStyledItemDelegate, QToolBox, 
    QScrollArea, QButtonGroup, QGridLayout, QToolBar, QStatusBar,  
    QGraphicsPathItem, QGraphicsLineItem, QGraphicsItemGroup
)

from PySide6.QtSvg import QSvgGenerator

from PySide6.QtGui import (
    QIcon, QAction, QCursor, QColor, QBrush, QTextCursor, QFont,
    QPen, QPainter, QTextFormat, QSyntaxHighlighter, QTextCharFormat, 
    QPalette, QShortcut, QKeySequence, QPixmap, QPainter, 
    QLinearGradient, QRadialGradient, QMouseEvent
)
from PySide6.QtCore import (
    Qt, QSize, QPoint, Signal, QDir, QRectF, QSettings, QThread, 
    Signal as pyqtSignal, QEvent, QTimer, QRect, QRegularExpression, QDateTime, QPointF
)


class VSCodeHighlighter(QSyntaxHighlighter):
    """Sistema de resaltado similar a Visual Studio Code para TODOS los lenguajes"""
    
    def __init__(self, document, theme="dark", language="auto"):
        super().__init__(document)
        self.theme = theme
        self.language = language
        self.highlighting_rules = []
        self.setup_theme()
        self.setup_highlight_rules()
    
    def setup_theme(self):
        """Configura los temas de colores como VS Code"""
        if self.theme == "dark":
            self.colors = {
                "background": "#1e1e1e",
                "foreground": "#d4d4d4",
                "keywords": "#569CD6",       
                "types": "#4EC9B0",         
                "strings": "#CE9178",       
                "comments": "#6A9955",     
                "numbers": "#B5CEA8",       
                "functions": "#DCDCAA",     
                "variables": "#9CDCFE",      
                "constants": "#4FC1FF",      
                "operators": "#d4d4d4",      
                "preprocessor": "#C586C0",   
                "error": "#f44747",         
                "regex": "#D16969",          
                "tags": "#569CD6",         
                "attributes": "#9CDCFE",     
                "values": "#CE9178",        
                "classes": "#4EC9B0",        
                "imports": "#C586C0",        
            }
        else: 
            self.colors = {
                "background": "#ffffff",
                "foreground": "#000000",
                "keywords": "#0000ff",       
                "types": "#267f99",         
                "strings": "#a31515",        
                "comments": "#008000",       
                "numbers": "#098658",        
                "functions": "#795e26",    
                "variables": "#001080",     
                "constants": "#0070c1",     
                "operators": "#000000",     
                "preprocessor": "#af00db",   
                "error": "#e51400",         
                "regex": "#811f3f",        
                "tags": "#800000",        
                "attributes": "#ff0000",     
                "values": "#0451a5",         
                "classes": "#267f99",      
                "imports": "#af00db",    
            }
    
    def create_format(self, color_name, bold=False, italic=False, underline=False):
        """Crea un formato de texto consistente"""
        format = QTextCharFormat()
        format.setForeground(QColor(self.colors[color_name]))
        if bold:
            format.setFontWeight(QFont.Bold)
        if italic:
            format.setFontItalic(True)
        if underline:
            format.setFontUnderline(True)
        return format
    
    def setup_highlight_rules(self):
        """Configura reglas básicas de resaltado"""
        
        comment_format = self.create_format("comments", italic=True)
        self.highlighting_rules.append((r"//[^\n]*", comment_format))
        self.highlighting_rules.append((r"#[^\n]*", comment_format))
        
        
        string_format = self.create_format("strings")
        self.highlighting_rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', string_format))
        self.highlighting_rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", string_format))
        
      
        number_format = self.create_format("numbers")
        self.highlighting_rules.append((r"\b\d+\b", number_format))
        self.highlighting_rules.append((r"\b\d+\.\d+\b", number_format))
        
        
        if self.language == "java":
            self.setup_java_rules()
        elif self.language == "xml":
            self.setup_xml_rules()
        
    
    def setup_common_rules(self):
        """Reglas comunes a todos los lenguajes de programación"""

        comment_format = self.create_format("comments", italic=True)
        self.highlighting_rules.append((r"//[^\n]*", comment_format))
        self.highlighting_rules.append((r"#[^\n]*", comment_format)) 

        number_format = self.create_format("numbers")
        self.highlighting_rules.append((r"\b\d+\b", number_format)) 
        self.highlighting_rules.append((r"\b\d+\.\d+\b", number_format)) 
        self.highlighting_rules.append((r"\b0x[0-9A-Fa-f]+\b", number_format)) 
        self.highlighting_rules.append((r"\b0b[01]+\b", number_format))  
        self.highlighting_rules.append((r"\b\d+[lLfFdD]?\b", number_format))  

        operator_format = self.create_format("operators")
        operators = [
            r"\=", r"\+", r"\-", r"\*", r"\/", r"\%", r"\=\=", r"\!=", r"\>", r"\<",
            r"\>\=", r"\<\=", r"\&\&", r"\|\|", r"\!", r"\+\+", r"\-\-", r"\+=",
            r"\-=", r"\*=", r"\/=", r"\%=", r"\<\<", r"\>\>", r"\&", r"\|", r"\^",
            r"\~", r"\&=", r"\|=", r"\^=", r"\?", r"\:", r"\.", r"\,", r"\;"
        ]
        for op in operators:
            self.highlighting_rules.append((op, operator_format))
    
    def setup_language_specific_rules(self):
        """Configura reglas específicas para cada lenguaje"""
        if self.language == "java":
            self.setup_java_rules()
        elif self.language == "kt":
            self.setup_kotlin_rules()
        elif self.language == "dart":
            self.setup_dart_rules()
        elif self.language == "py":
            self.setup_python_rules()
        elif self.language in ["js", "ts"]:
            self.setup_javascript_rules()
        elif self.language in ["xml", "html"]:
            self.setup_xml_rules()
        elif self.language == "css":
            self.setup_css_rules()
        elif self.language in ["cpp", "c"]:
            self.setup_cpp_rules()
        elif self.language == "cs":
            self.setup_csharp_rules()
        elif self.language == "php":
            self.setup_php_rules()
        elif self.language == "rb":
            self.setup_ruby_rules()
        elif self.language == "go":
            self.setup_go_rules()
        elif self.language == "rs":
            self.setup_rust_rules()
        elif self.language == "swift":
            self.setup_swift_rules()
 
    
    def setup_java_rules(self):
        """Reglas específicas para Java"""
        keywords = [
            "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class",
            "const", "continue", "default", "do", "double", "else", "enum", "extends", "final",
            "finally", "float", "for", "goto", "if", "implements", "import", "instanceof", "int",
            "interface", "long", "native", "new", "package", "private", "protected", "public",
            "return", "short", "static", "strictfp", "super", "switch", "synchronized", "this",
            "throw", "throws", "transient", "try", "void", "volatile", "while", "var", "record",
            "sealed", "non-sealed", "permits", "yield"
        ]
        
        keyword_format = self.create_format("keywords", bold=True)
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((pattern, keyword_format))
        
       
        type_format = self.create_format("types")
        types = ["String", "Integer", "Double", "Float", "Boolean", "Object", "List", "Map", "Set",
                "ArrayList", "HashMap", "HashSet", "Number", "Character", "Byte", "Short", "Long", "Void"]
        for word in types:
            self.highlighting_rules.append((r"\b" + word + r"\b", type_format))
        
      
        annotation_format = self.create_format("preprocessor")
        self.highlighting_rules.append((r"@\w+", annotation_format))
      
        string_format = self.create_format("strings")
        self.highlighting_rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', string_format))
        self.highlighting_rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", string_format))
        
     
        import_format = self.create_format("imports")
        self.highlighting_rules.append((r"import\s+[\w\.]+;", import_format))
    
    def setup_kotlin_rules(self):
        """Reglas específicas para Kotlin"""
        keywords = [
            "as", "as?", "break", "class", "continue", "do", "else", "false", "for", "fun", "if",
            "in", "!in", "interface", "is", "!is", "null", "object", "package", "return", "super",
            "this", "throw", "true", "try", "typealias", "val", "var", "when", "while", "by",
            "catch", "constructor", "delegate", "dynamic", "field", "file", "finally", "get",
            "import", "init", "param", "property", "receiver", "set", "setparam", "where",
            "actual", "abstract", "annotation", "companion", "const", "crossinline", "data",
            "enum", "expect", "external", "final", "infix", "inline", "inner", "internal",
            "lateinit", "noinline", "open", "operator", "out", "override", "private", "protected",
            "public", "reified", "sealed", "suspend", "tailrec", "vararg", "it"
        ]
        
        keyword_format = self.create_format("keywords", bold=True)
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((pattern, keyword_format))
        
    
        template_format = self.create_format("variables")
        self.highlighting_rules.append((r"\$\{.*?\}", template_format))
        self.highlighting_rules.append((r"\$\w+", template_format))
    
    def setup_dart_rules(self):
        """Reglas específicas para Dart"""
        keywords = [
            "abstract", "as", "assert", "async", "await", "break", "case", "catch", "class",
            "const", "continue", "covariant", "default", "deferred", "do", "dynamic", "else",
            "enum", "export", "extends", "extension", "external", "factory", "false", "final",
            "finally", "for", "Function", "get", "hide", "if", "implements", "import", "in",
            "interface", "is", "late", "library", "mixin", "new", "null", "on", "operator",
            "part", "rethrow", "return", "set", "show", "static", "super", "switch", "sync",
            "this", "throw", "true", "try", "typedef", "var", "void", "while", "with", "yield"
        ]
        
        keyword_format = self.create_format("keywords", bold=True)
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((pattern, keyword_format))
    
        interpolation_format = self.create_format("variables")
        self.highlighting_rules.append((r"\$\{.*?\}", interpolation_format))
        self.highlighting_rules.append((r"\$\w+", interpolation_format))
    
    def setup_python_rules(self):
        """Reglas específicas para Python"""
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del",
            "elif", "else", "except", "False", "finally", "for", "from", "global", "if", "import",
            "in", "is", "lambda", "None", "nonlocal", "not", "or", "pass", "raise", "return",
            "True", "try", "while", "with", "yield"
        ]
        
        keyword_format = self.create_format("keywords", bold=True)
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((pattern, keyword_format))
        
      
        decorator_format = self.create_format("preprocessor")
        self.highlighting_rules.append((r"@\w+", decorator_format))
        
       
        docstring_format = self.create_format("strings")
        self.highlighting_rules.append((r'"""[^"]*"""', docstring_format))
        self.highlighting_rules.append((r"'''[^']*'''", docstring_format))
    
    def setup_javascript_rules(self):
        """Reglas específicas para JavaScript/TypeScript"""
        keywords = [
            "break", "case", "catch", "class", "const", "continue", "debugger", "default",
            "delete", "do", "else", "export", "extends", "finally", "for", "function", "if",
            "import", "in", "instanceof", "new", "return", "super", "switch", "this", "throw",
            "try", "typeof", "var", "void", "while", "with", "yield", "let", "await", "async",
            "static", "get", "set", "from", "of", "finally"
        ]
        
        keyword_format = self.create_format("keywords", bold=True)
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((pattern, keyword_format))
        
      
        template_format = self.create_format("variables")
        self.highlighting_rules.append((r"\$\{.*?\}", template_format))
    
    def setup_xml_rules(self):
        """Reglas específicas para XML/HTML"""
        
        tag_format = self.create_format("tags")
        self.highlighting_rules.append((r"</?\w+", tag_format))
        
        attribute_format = self.create_format("attributes")
        self.highlighting_rules.append((r'\b\w+(?=\=)', attribute_format))
        
        value_format = self.create_format("values")
        self.highlighting_rules.append((r'="[^"]*"', value_format))
    
    def setup_css_rules(self):
        """Reglas específicas para CSS"""
        property_format = self.create_format("attributes")
        self.highlighting_rules.append((r"\b[\w-]+\s*:", property_format))
        
        selector_format = self.create_format("tags")
        self.highlighting_rules.append((r"[\.#]?[\w-]+\s*\{", selector_format))
    
    def setup_cpp_rules(self):
        """Reglas específicas para C/C++"""
        keywords = [
            "auto", "break", "case", "char", "const", "continue", "default", "do", "double",
            "else", "enum", "extern", "float", "for", "goto", "if", "int", "long", "register",
            "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef",
            "union", "unsigned", "void", "volatile", "while", "class", "namespace", "template",
            "typename", "virtual", "public", "private", "protected", "new", "delete", "using"
        ]
        
        keyword_format = self.create_format("keywords", bold=True)
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((pattern, keyword_format))

    
    def highlightBlock(self, text):
        """Aplica el resaltado de sintaxis al bloque de texto"""

        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            matches = expression.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        self.highlight_multiline_comments(text)
    
    def highlight_multiline_comments(self, text):
        """Maneja comentarios multilínea (/* */, <!-- -->, etc.)"""
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = text.find("/*")
        
        comment_format = self.create_format("comments", italic=True)
        
        while start_index >= 0:
            end_index = text.find("*/", start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
                self.setFormat(start_index, comment_length, comment_format)
                break
            else:
                comment_length = end_index - start_index + 2
                self.setFormat(start_index, comment_length, comment_format)
                start_index = text.find("/*", start_index + comment_length)

        start_index = text.find("<!--")
        while start_index >= 0:
            end_index = text.find("-->", start_index)
            if end_index == -1:
                comment_length = len(text) - start_index
                self.setFormat(start_index, comment_length, comment_format)
                break
            else:
                comment_length = end_index - start_index + 3
                self.setFormat(start_index, comment_length, comment_format)
                start_index = text.find("<!--", start_index + comment_length)


class HighlighterFactory:
    """Factory para crear resaltadores específicos basados en la extensión del archivo"""
    
    LANGUAGE_MAP = {
        '.java': 'java',
        '.jav': 'java',

        '.kt': 'kt',
        '.kts': 'kt',

        '.dart': 'dart',

        '.py': 'py',
        '.pyw': 'py',

        '.js': 'js',
        '.jsx': 'js',
        '.ts': 'ts',
        '.tsx': 'ts',

        '.xml': 'xml',
        '.html': 'xml',
        '.htm': 'xml',
        '.xhtml': 'xml',

        '.css': 'css',
        '.scss': 'css',
        '.sass': 'css',
        '.less': 'css',

        '.c': 'cpp',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.h': 'cpp',
        '.hpp': 'cpp',

        '.cs': 'cs',

        '.php': 'php',
        '.phtml': 'php',

        '.rb': 'rb',
        '.ruby': 'rb',
 
        '.go': 'go',
 
        '.rs': 'rs',
        '.rust': 'rs',

        '.swift': 'swift',

        '.json': 'js',
        '.md': 'xml',  
        '.sql': 'sql',
        '.sh': 'py',   
        '.bat': 'py',  
        '.ps1': 'py',  
    }
    
    @staticmethod
    def create_highlighter(file_path, document, theme="dark"):
        """Crea el resaltador apropiado basado en la extensión del archivo"""
        extension = os.path.splitext(file_path)[1].lower()
        language = HighlighterFactory.LANGUAGE_MAP.get(extension, 'auto')
        
        return VSCodeHighlighter(document, theme, language)

project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

class FileType:
    def __init__(self, name, extensions, icon, template):
        self.name = name
        self.extensions = extensions
        self.icon = icon
        self.template = template

class NewFileDialog(QDialog):
    def __init__(self, project_language, parent=None, current_path=None):
        super().__init__(parent)
        self.project_language = project_language
        self.current_path = current_path 
        self.selected_type = None
        self.setup_ui()
        
    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        

        self.initial_container = QWidget()
        self.initial_layout = QVBoxLayout(self.initial_container)
        
        self.initial_message = QLabel("Bienvenido a Creators Studio\n\nHaga doble clic en un archivo .xml en el explorador para comenzar a diseñar")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet("font-size: 16px; color: #666; padding: 100px; background-color: #f5f5f5; border-radius: 10px;")
        self.initial_message.setWordWrap(True)
        self.initial_layout.addWidget(self.initial_message)
        
        self.tab_widget.addTab(self.initial_container, "Inicio")
        
        self.main_layout.addWidget(self.tab_widget)

        self.create_tool_panel()
        self.create_layers_panel()
        self.create_color_panel()
        self.create_brushes_panel()
        self.create_character_panel()
        self.create_paragraph_panel()
        self.create_ai_panel()
        self.create_file_explorer_panel()
        
        self.create_menu_bar()

        self.setup_enhanced_docks()

        self.ai_panel.setVisible(True)
        self.file_explorer_panel.setVisible(True)

        self.ai_panel_action.setChecked(True)
        self.explorer_panel_action.setChecked(True)
        
        self.statusBar().showMessage("Listo | Centro vacío - Abra un archivo .xml para comenzar")
        
    def load_file_types(self):
        """Carga los tipos de archivo disponibles según el lenguaje del proyecto"""
        file_types = []

        if self.project_language.lower() == "java":
            file_types.extend([
                FileType("Clase Java", [".java"], "⚙️", 
                        "public class {class_name} {\n    public static void main(String[] args) {\n        // TODO: Agregar código aquí\n    }\n}"),
                FileType("Interface Java", [".java"], "🔌", 
                        "public interface {interface_name} {\n    // TODO: Definir métodos\n}"),
                FileType("Activity Android", [".java"], "📱", 
                        "public class {class_name} extends AppCompatActivity {\n    @Override\n    protected void onCreate(Bundle savedInstanceState) {\n        super.onCreate(savedInstanceState);\n        setContentView(R.layout.activity_main);\n    }\n}"),
                FileType("Fragment Android", [".java"], "🧩", 
                        "public class {class_name} extends Fragment {\n    @Override\n    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {\n        return inflater.inflate(R.layout.fragment_layout, container, false);\n    }\n}")
            ])
        elif self.project_language.lower() == "kotlin":
            file_types.extend([
                FileType("Clase Kotlin", [".kt"], "⚙️", 
                        "class {class_name} {\n    // TODO: Agregar código aquí\n}"),
                FileType("Activity Kotlin", [".kt"], "📱", 
                        "class {class_name} : AppCompatActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        setContentView(R.layout.activity_main)\n    }\n}"),
                FileType("Fragment Kotlin", [".kt"], "🧩", 
                        "class {class_name} : Fragment() {\n    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {\n        return inflater.inflate(R.layout.fragment_layout, container, false)\n    }\n}")
            ])
        elif self.project_language.lower() == "flutter":
            file_types.extend([
                FileType("Widget Flutter", [".dart"], "🎯", 
                        "class {class_name} extends StatelessWidget {\n  @override\n  Widget build(BuildContext context) {\n    return Container();\n  }\n}"),
                FileType("Stateful Widget", [".dart"], "🔄", 
                        "class {class_name} extends StatefulWidget {\n  @override\n  _${class_name}State createState() => _${class_name}State();\n}\n\nclass _${class_name}State extends State<{class_name}> {\n  @override\n  Widget build(BuildContext context) {\n    return Container();\n  }\n}"),
                FileType("Dart Class", [".dart"], "📦", 
                        "class {class_name} {\n  // TODO: Agregar código aquí\n}")
            ])

        common_types = [
            FileType("Layout XML", [".xml"], "📐", 
                    '<?xml version="1.0" encoding="utf-8"?>\n<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"\n    android:layout_width="match_parent"\n    android:layout_height="match_parent"\n    android:orientation="vertical">\n    \n</LinearLayout>'),
            FileType("Recursos XML", [".xml"], "🎨", 
                    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="app_name">Mi Aplicación</string>\n</resources>'),
            FileType("Archivo de Texto", [".txt"], "📄", ""),
            FileType("Archivo JSON", [".json"], "🔷", 
                    "{\n    \"name\": \"example\",\n    \"version\": \"1.0.0\"\n}"),
            FileType("Archivo Markdown", [".md"], "📝", 
                    "# Título\n\nDescripción del archivo."),
            FileType("Archivo HTML", [".html"], "🌐", 
                    "<!DOCTYPE html>\n<html>\n<head>\n    <title>Document</title>\n</head>\n<body>\n    \n</body>\n</html>"),
            FileType("Hoja de Estilos CSS", [".css"], "🎨", 
                    "/* Estilos CSS */\nbody {\n    margin: 0;\n    padding: 0;\n}"),
            FileType("Script JavaScript", [".js"], "📜", 
                    "// Código JavaScript\nconsole.log('Hola Mundo');"),
            FileType("Archivo Python", [".py"], "🐍", 
                    "# Código Python\nprint('Hola Mundo')"),
            FileType("Archivo SQL", [".sql"], "🗃️", 
                    "-- Consultas SQL\nSELECT * FROM tabla;")
        ]
        
        file_types.extend(common_types)

        for file_type in file_types:
            item = QListWidgetItem(f"{file_type.icon} {file_type.name} ({', '.join(file_type.extensions)})")
            item.setData(Qt.UserRole, file_type)
            self.file_types_list.addItem(item)
        
        self.file_types_list.setCurrentRow(0)
        
    def accept_selection(self):
        """Valida y acepta la selección"""
        current_item = self.file_types_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Seleccione un tipo de archivo")
            return
            
        filename = self.filename_input.text().strip()
        if not filename:
            QMessageBox.warning(self, "Error", "Ingrese un nombre para el archivo")
            return
        
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in filename for char in invalid_chars):
            QMessageBox.warning(self, "Error", f"El nombre contiene caracteres no permitidos: {''.join(invalid_chars)}")
            return
            
        self.selected_type = current_item.data(Qt.UserRole)
        self.selected_filename = filename
        self.accept()
        
    def update_preview(self):
        """Actualiza la vista previa cuando cambia la selección o el nombre"""
        current_item = self.file_types_list.currentItem()
        if not current_item:
            return
            
        file_type = current_item.data(Qt.UserRole)
        filename = self.filename_input.text().strip()
        
        if not filename:
            self.preview_editor.setPlainText("")
            return

        preview = file_type.template

        class_name = filename.replace(" ", "_").replace(".java", "").replace(".kt", "").replace(".dart", "")
        preview = preview.replace("{class_name}", class_name)
        preview = preview.replace("{interface_name}", class_name)
        preview = preview.replace("{layout_name}", class_name.lower())
        
        self.preview_editor.setPlainText(preview)
class FileExplorerContextMenu(QMenu):
    """Menú contextual personalizado para el explorador de archivos"""
    
    def __init__(self, parent=None):
        super().__init__("Explorador", parent)
        self.parent = parent
        self.setup_menu()
    
    def setup_menu(self):
        """Configura las opciones del menú contextual"""
        new_file_action = QAction("📄 Nuevo Archivo", self)
        new_file_action.setShortcut("Ctrl+N")
        new_file_action.triggered.connect(self.create_new_file)
        self.addAction(new_file_action)

        new_folder_action = QAction("📁 Nueva Carpeta", self)
        new_folder_action.setShortcut("Ctrl+Shift+N")
        new_folder_action.triggered.connect(self.create_new_folder)
        self.addAction(new_folder_action)
        
        self.addSeparator()

        rename_action = QAction("✏️ Renombrar", self)
        rename_action.setShortcut("F2")
        rename_action.triggered.connect(self.rename_item)
        self.addAction(rename_action)

        delete_action = QAction("🗑️ Eliminar", self)
        delete_action.setShortcut("Del")
        delete_action.triggered.connect(self.delete_item)
        self.addAction(delete_action)
        
        self.addSeparator()

        copy_path_action = QAction("📋 Copiar Ruta", self)
        copy_path_action.triggered.connect(self.copy_path)
        self.addAction(copy_path_action)

        open_explorer_action = QAction("📂 Abrir en Explorador", self)
        open_explorer_action.triggered.connect(self.open_in_system_explorer)
        self.addAction(open_explorer_action)
    
    def create_new_file(self):
        """Crea un nuevo archivo en la ubicación actual"""
        if hasattr(self.parent, 'file_tree'):
            index = self.parent.file_tree.currentIndex()
            if index.isValid():
                current_path = self.parent.file_model.filePath(index)
                
                if os.path.isfile(current_path):
                    current_path = os.path.dirname(current_path)
                
                dialog = NewFileDialog(
                    self.parent.project_language, 
                    self.parent, 
                    current_path
                )
                
                if dialog.exec_() == QDialog.Accepted:
                    self.parent.create_file_from_dialog(dialog, current_path)
    
    def create_new_folder(self):
        """Crea una nueva carpeta en la ubicación actual"""
        if hasattr(self.parent, 'file_tree'):
            index = self.parent.file_tree.currentIndex()
            if index.isValid():
                current_path = self.parent.file_model.filePath(index)

                if os.path.isfile(current_path):
                    current_path = os.path.dirname(current_path)
                
                folder_name, ok = QInputDialog.getText(
                    self.parent, 
                    "Nueva Carpeta", 
                    "Nombre de la carpeta:",
                    text="NuevaCarpeta"
                )
                
                if ok and folder_name:
                    new_folder_path = os.path.join(current_path, folder_name)
                    try:
                        os.makedirs(new_folder_path, exist_ok=False)
                        self.parent.file_model.setRootPath(self.parent.project_path)
                        QMessageBox.information(self.parent, "Éxito", f"Carpeta '{folder_name}' creada correctamente")
                    except FileExistsError:
                        QMessageBox.warning(self.parent, "Error", f"La carpeta '{folder_name}' ya existe")
                    except Exception as e:
                        QMessageBox.critical(self.parent, "Error", f"No se pudo crear la carpeta: {str(e)}")
    
    def rename_item(self):
        """Renombra el archivo o carpeta seleccionado"""
        if hasattr(self.parent, 'file_tree'):
            index = self.parent.file_tree.currentIndex()
            if index.isValid():
                current_path = self.parent.file_model.filePath(index)
                current_name = os.path.basename(current_path)
                
                new_name, ok = QInputDialog.getText(
                    self.parent, 
                    "Renombrar", 
                    "Nuevo nombre:",
                    text=current_name
                )
                
                if ok and new_name and new_name != current_name:
                    new_path = os.path.join(os.path.dirname(current_path), new_name)
                    try:
                        os.rename(current_path, new_path)
                        self.parent.file_model.setRootPath(self.parent.project_path)
                        QMessageBox.information(self.parent, "Éxito", "Elemento renombrado correctamente")
                    except Exception as e:
                        QMessageBox.critical(self.parent, "Error", f"No se pudo renombrar: {str(e)}")
    
    def delete_item(self):
        """Elimina el archivo o carpeta seleccionado"""
        if hasattr(self.parent, 'file_tree'):
            index = self.parent.file_tree.currentIndex()
            if index.isValid():
                current_path = self.parent.file_model.filePath(index)
                item_name = os.path.basename(current_path)
                item_type = "archivo" if os.path.isfile(current_path) else "carpeta"
                
                reply = QMessageBox.question(
                    self.parent,
                    "Confirmar Eliminación",
                    f"¿Está seguro de que desea eliminar el {item_type} '{item_name}'?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        if os.path.isfile(current_path):
                            os.remove(current_path)
                        else:
                            import shutil
                            shutil.rmtree(current_path)
                        
                        self.parent.file_model.setRootPath(self.parent.project_path)
                        QMessageBox.information(self.parent, "Éxito", f"{item_type.capitalize()} eliminado correctamente")
                    except Exception as e:
                        QMessageBox.critical(self.parent, "Error", f"No se pudo eliminar: {str(e)}")
    
    def copy_path(self):
        """Copia la ruta del archivo/carpeta al portapapeles"""
        if hasattr(self.parent, 'file_tree'):
            index = self.parent.file_tree.currentIndex()
            if index.isValid():
                current_path = self.parent.file_model.filePath(index)
                QApplication.clipboard().setText(current_path)
                QMessageBox.information(self.parent, "Portapapeles", "Ruta copiada al portapapeles")
    
    def open_in_system_explorer(self):
        """Abre la ubicación en el explorador del sistema"""
        if hasattr(self.parent, 'file_tree'):
            index = self.parent.file_tree.currentIndex()
            if index.isValid():
                current_path = self.parent.file_model.filePath(index)

                if os.path.isfile(current_path):
                    current_path = os.path.dirname(current_path)
                
                try:
                    if platform.system() == "Windows":
                        os.startfile(current_path)
                    elif platform.system() == "Darwin":
                        subprocess.run(["open", current_path])
                    else:  
                        subprocess.run(["xdg-open", current_path])
                except Exception as e:
                    QMessageBox.warning(self.parent, "Error", f"No se pudo abrir el explorador: {str(e)}")
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



class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class EnhancedCodeEditor(QPlainTextEdit):
    """Editor de código mejorado con resaltado estilo VS Code y números de línea CORREGIDO"""
    
    def __init__(self, parent=None, theme="dark"):
        super().__init__(parent)
        self.theme = theme
        self.highlighter = None
        self.setup_editor()
        self.setup_line_numbers()
    
    def setup_editor(self):
        """Configura el editor con tema VS Code"""
        if self.theme == "dark":
            self.setStyleSheet("""
                EnhancedCodeEditor {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #3e3e42;
                    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    selection-background-color: #264F78;
                    line-height: 1.5;
                }
            """)
        else:
            self.setStyleSheet("""
                EnhancedCodeEditor {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
                    font-size: 14px;
                    selection-background-color: #add6ff;
                    line-height: 1.5;
                }
            """)
        
        font = QFont("Consolas", 12) 
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        
        self.setTabStopDistance(40)
    
    def setup_line_numbers(self):
        """Configura el área de números de línea CORREGIDO"""
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()
    
    def line_number_area_width(self):
        """Calcula el ancho del área de números de línea"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, new_block_count):
        """Actualiza el margen para el área de números"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Actualiza el área de números de línea cuando se desplaza"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Maneja el redimensionamiento del editor"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
    
    def line_number_area_paint_event(self, event):
        """Pinta los números de línea - CORREGIDO"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#2d2d30"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingGeometry(block).height())
        
        font = painter.font()
        font.setFamily("Consolas")
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor("#858585"))
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, top, self.line_number_area.width() - 5, 
                               self.fontMetrics().height(), Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingGeometry(block).height())
            block_number += 1
    
    def highlight_current_line(self):
        """Resalta la línea actual"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#2f2f32") if self.theme == "dark" else QColor("#efefef")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def set_highlighter(self, file_path):
        """Configura el resaltador de sintaxis para el archivo"""
        if self.highlighter:
            self.highlighter.setDocument(None)
        
        self.highlighter = HighlighterFactory.create_highlighter(file_path, self.document(), self.theme)

class EnhancedAIChatPanel(QDockWidget):
    """Panel de IA con control TOTAL del sistema de archivos"""
    
    def __init__(self, code_generator, parent=None):
        super().__init__("AI Assistant - Control Total del Sistema", parent)
        self.code_generator = code_generator
        self.parent_window = parent
        self.conversation_history = []
        self.current_provider = "deepseek"
        self.current_directory = Path.home()  # Directorio actual
        self.setupUI()
        self.load_api_keys()
        
        # Mensaje de bienvenida con capacidades
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

    def setupUI(self):
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        
        # Barra de navegación
        nav_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("◀️")
        self.back_btn.setToolTip("Directorio anterior")
        self.back_btn.clicked.connect(self.navigate_back)
        self.back_btn.setFixedSize(30, 30)
        
        self.forward_btn = QPushButton("▶️")
        self.forward_btn.setToolTip("Directorio siguiente")
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.forward_btn.setFixedSize(30, 30)
        
        self.home_btn = QPushButton("🏠")
        self.home_btn.setToolTip("Directorio home")
        self.home_btn.clicked.connect(self.go_home)
        self.home_btn.setFixedSize(30, 30)
        
        self.up_btn = QPushButton("📁")
        self.up_btn.setToolTip("Directorio padre")
        self.up_btn.clicked.connect(self.go_up)
        self.up_btn.setFixedSize(30, 30)
        
        self.path_label = QLabel(str(self.current_directory))
        self.path_label.setStyleSheet("background-color: #2d2d30; padding: 5px; border-radius: 3px;")
        self.path_label.setWordWrap(True)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.up_btn)
        nav_layout.addWidget(self.path_label)
        nav_layout.addStretch()
        
        layout.addLayout(nav_layout)
        
        # Historial de chat
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Escribe comandos como: 'crea un archivo.txt', 'lista los archivos', 'cambia a /ruta'...")
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.chat_history)
        
        # Panel de entrada
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Escribe tu comando (ej: 'crea archivo.txt con contenido', 'muestra archivos', 'edita config.ini')...")
        self.user_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.user_input)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Botones de acción rápida
        quick_actions_layout = QHBoxLayout()
        
        actions = [
            ("📊", "Estadísticas", self.show_system_stats),
            ("🔍", "Buscar", self.quick_search),
            ("📋", "Listar", self.list_current_directory),
            ("⚡", "Terminal", self.open_terminal),
            ("🛠️", "Herramientas", self.show_tools_menu)
        ]
        
        for icon, text, action in actions:
            btn = QPushButton(f"{icon} {text}")
            btn.setFixedHeight(30)
            btn.clicked.connect(action)
            quick_actions_layout.addWidget(btn)
        
        layout.addLayout(quick_actions_layout)
        
        chat_widget.setLayout(layout)
        self.setWidget(chat_widget)

    # ===== NAVEGACIÓN DEL SISTEMA =====
    
    def navigate_back(self):
        """Navega al directorio anterior"""
        if hasattr(self, 'navigation_history') and self.navigation_history:
            prev_dir = self.navigation_history.pop()
            self.current_directory = prev_dir
            self.update_path_display()
            self.list_current_directory()

    def navigate_forward(self):
        """Navega al directorio siguiente"""
        # Implementar si es necesario
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

    # ===== COMANDOS PRINCIPALES =====
    
    def send_message(self):
        """Procesa los comandos del usuario"""
        user_text = self.user_input.text().strip()
        if not user_text:
            return
            
        self._add_formatted_message("👤 **Tú**", user_text, "#1976D2")
        self.user_input.clear()
        
        # Procesar el comando
        self.process_command(user_text)

    def process_command(self, command):
        """Procesa comandos naturales del usuario"""
        lower_cmd = command.lower()
        
        try:
            # NAVEGACIÓN
            if any(word in lower_cmd for word in ['ve a', 'cambia a', 'entra a', 'cd ']):
                self.handle_navigation(command)
            
            # CREACIÓN DE ARCHIVOS
            elif any(word in lower_cmd for word in ['crea', 'nuevo', 'make', 'create']):
                self.handle_file_creation(command)
            
            # LISTAR CONTENIDO
            elif any(word in lower_cmd for word in ['lista', 'muestra', 'ls', 'dir', 'contenido']):
                self.list_current_directory()
            
            # EDITAR ARCHIVOS
            elif any(word in lower_cmd for word in ['edita', 'modifica', 'edit', 'change']):
                self.handle_file_edit(command)
            
            # ELIMINAR
            elif any(word in lower_cmd for word in ['elimina', 'borra', 'delete', 'remove']):
                self.handle_deletion(command)
            
            # BUSCAR
            elif any(word in lower_cmd for word in ['busca', 'find', 'search']):
                self.handle_search(command)
            
            # COPIAR/MOVER
            elif any(word in lower_cmd for word in ['copia', 'mueve', 'copy', 'move']):
                self.handle_copy_move(command)
            
            # INFORMACIÓN DEL SISTEMA
            elif any(word in lower_cmd for word in ['estadísticas', 'espacio', 'info', 'stats']):
                self.show_system_stats()
            
            # EJECUTAR COMANDOS
            elif lower_cmd.startswith('ejecuta ') or lower_cmd.startswith('run '):
                self.execute_system_command(command)
            
            else:
                # Si no reconoce el comando, usar IA
                self.process_with_ai(command)
                
        except Exception as e:
            self.add_error_message(f"❌ Error procesando comando: {str(e)}")

    # ===== MANEJADORES DE COMANDOS =====
    
    def handle_navigation(self, command):
        """Maneja comandos de navegación"""
        parts = command.split()
        path_str = None
        
        # Extraer la ruta del comando
        for i, part in enumerate(parts):
            if part in ['a', 'to', 'en'] and i + 1 < len(parts):
                path_str = ' '.join(parts[i+1:])
                break
        
        if not path_str:
            path_str = parts[-1]  # Última palabra como ruta
        
        # Expandir rutas especiales
        if path_str == "~" or path_str == "home":
            path_str = str(Path.home())
        elif path_str == "..":
            path_str = str(self.current_directory.parent)
        
        target_path = Path(path_str)
        
        # Si es relativa, hacerla absoluta
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
        
        # CREAR CARPETA
        if any(word in lower_cmd for word in ['carpeta', 'folder', 'directorio']):
            folder_name = self.extract_filename(command, ['carpeta', 'folder'])
            if folder_name:
                self.create_folder(folder_name)
        
        # CREAR ARCHIVO
        elif any(word in lower_cmd for word in ['archivo', 'file']):
            file_name = self.extract_filename(command, ['archivo', 'file'])
            content = self.extract_content(command)
            if file_name:
                self.create_file(file_name, content)

    def extract_filename(self, command, keywords):
        """Extrae el nombre de archivo/carpeta del comando"""
        for keyword in keywords:
            if keyword in command.lower():
                # Buscar después de la palabra clave
                start_idx = command.lower().index(keyword) + len(keyword)
                remaining = command[start_idx:].strip()
                # Tomar la primera palabra como nombre
                filename = remaining.split()[0] if remaining.split() else None
                return filename
        return None

    def extract_content(self, command):
        """Extrae contenido para archivos del comando"""
        if 'contenido' in command.lower() or 'con' in command.lower():
            # Buscar después de "contenido" o "con"
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
            
            # Asegurar extensión si es necesario
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
            
            # Separar archivos y carpetas
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
            # Extraer nombre de archivo
            filename = None
            for word in command.split():
                if '.' in word:  # Buscar palabras con extensión
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
            
            # Diálogo de edición
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Editando: {file_path.name}")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Editor
            editor = QPlainTextEdit()
            editor.setPlainText(content)
            layout.addWidget(editor)
            
            # Botones
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
            
            # Buscar nombre después de palabras clave de eliminación
            delete_keywords = ['elimina', 'borra', 'delete', 'remove']
            for i, word in enumerate(words):
                if word.lower() in delete_keywords and i + 1 < len(words):
                    target_name = words[i + 1]
                    break
            
            if target_name:
                target_path = self.current_directory / target_name
                
                if target_path.exists():
                    # Confirmar eliminación
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
            # Espacio en disco
            disk_usage = psutil.disk_usage(str(self.current_directory))
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            
            # Información del sistema
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
            # Extraer el comando después de "ejecuta" o "run"
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

    # ===== MÉTODOS DE IA (MEJORADOS) =====
    
    def process_with_ai(self, command):
        """Procesa comandos complejos con IA"""
        # Por ahora, respuesta básica - luego integrar DeepSeek real
        response = self.generate_smart_response(command)
        self.add_ai_response(response)

    def generate_smart_response(self, command):
        """Genera respuestas inteligentes para comandos no reconocidos"""
        lower_cmd = command.lower()
        
        if '?' in command or 'qué' in lower_cmd or 'cómo' in lower_cmd:
            return f"🤖 Para esa consulta necesitaría conectarme a DeepSeek. Por ahora puedo ayudarte con:\n• Gestión de archivos\n• Comandos del sistema\n• Navegación de directorios"
        
        return f"🔧 **Comando reconocido:** '{command}'\n\n💡 **Sugerencias:**\n• Usa 'lista' para ver archivos\n• 'crea archivo.txt' para crear archivos\n• 'edita nombre.txt' para modificar\n• 'estadísticas' para info del sistema"

    # ===== MÉTODOS AUXILIARES =====
    
    def _add_formatted_message(self, sender, message, color):
        """Añade mensaje formateado al chat"""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        
        formatted_message = f"""
        <div style="background-color: {color}; padding: 10px; margin: 5px; border-radius: 8px;">
            <div style="color: white; font-weight: bold;">{sender} <span style="color: #ccc; font-size: 0.8em;">[{timestamp}]</span></div>
            <div style="color: white; margin-top: 5px;">{message.replace(chr(10), '<br>')}</div>
        </div>
        <br>
        """
        
        cursor.insertHtml(formatted_message)
        self.chat_history.ensureCursorVisible()

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
                    for result in results[:10]:  # Limitar a 10 resultados
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
            if os.name == 'nt':  # Windows
                subprocess.Popen(f'start cmd /K "cd /d {self.current_directory}"', shell=True)
            else:  # Linux/Mac
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
class AIResponseEvent(QEvent):
    """Evento personalizado para respuestas de IA"""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, response, is_error=False):
        super().__init__(self.EVENT_TYPE)
        self.response = response
        self.is_error = is_error

class FileIconDelegate(QStyledItemDelegate):
    """Delegate personalizado para mostrar íconos en el explorador"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon_map = {

            '.java': '⚙️', '.kt': '⚙️', '.dart': '🎯', '.py': '🐍',
            '.js': '📜', '.ts': '📜', '.jsx': '⚛️', '.tsx': '⚛️',
            '.cpp': '🔧', '.c': '🔧', '.h': '🔧', '.cs': '🔷',
            '.php': '🐘', '.rb': '💎', '.go': '🐹', '.rs': '🦀',
            '.swift': '🐦', '.m': '🍎', '.mm': '🍎',
            
   
            '.html': '🌐', '.htm': '🌐', '.xml': '📐', '.css': '🎨',
            '.scss': '🎨', '.sass': '🎨', '.less': '🎨',
            

            '.json': '🔷', '.yaml': '🔷', '.yml': '🔷', '.csv': '📊',
            '.sql': '🗃️', '.db': '🗃️', '.sqlite': '🗃️',
  
            '.md': '📝', '.txt': '📄', '.pdf': '📕', '.doc': '📘',
            '.docx': '📘', '.xls': '📗', '.xlsx': '📗', '.ppt': '📙',
            
            '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️',
            '.svg': '🖼️', '.ico': '🖼️', '.bmp': '🖼️',

            '.gradle': '📦', '.kts': '📦', '.pro': '📦', '.cmake': '📦',
            '.gitignore': '🔒', '.gitattributes': '🔒',

            '.exe': '⚡', '.dll': '📚', '.so': '📚', '.a': '📚',
            '.jar': '☕', '.war': '☕', '.apk': '📱',
        }
    
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        
        if index.column() == 0:
            file_path = index.model().filePath(index)
            file_name = index.model().fileName(index)
            _, ext = os.path.splitext(file_path)
            

            if os.path.isdir(file_path):
                icon_text = '📁' 
            else:
                icon_text = self.icon_map.get(ext.lower(), '📄')  

            option.text = f"{icon_text} {file_name}"


class IllustratorToolsPanel(QDockWidget):
    """Panel de herramientas de Illustrator para diseño Android"""
    
    def __init__(self, parent=None):
        super().__init__("Herramientas Illustrator", parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        tool_widget = QWidget()
        layout = QVBoxLayout(tool_widget)
        
        # ToolBox para organizar las herramientas por categorías
        self.tool_box = QToolBox()
        
        # Grupo de botones para herramientas de selección
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        
        # Herramientas básicas
        self.setup_basic_tools()
        
        # Herramientas de forma
        self.setup_shape_tools()
        
        # Herramientas de texto
        self.setup_text_tools()
        
        # Herramientas de transformación
        self.setup_transform_tools()
        
        layout.addWidget(self.tool_box)
        layout.addStretch()
        
        tool_widget.setLayout(layout)
        self.setWidget(tool_widget)
    
    def setup_basic_tools(self):
        """Configura herramientas básicas de selección y navegación"""
        basic_widget = QWidget()
        layout = QGridLayout(basic_widget)
        
        tools = [
            ("🔍", "Selección", "select", "Seleccionar y mover elementos"),
            ("✋", "Mano", "hand", "Navegar por el canvas"),
            ("🔎", "Zoom", "zoom", "Acercar/alejar la vista"),
            ("📏", "Regla", "ruler", "Medir distancias y alinear")
        ]
        
        row, col = 0, 0
        for icon, name, tool_id, tooltip in tools:
            btn = self.create_tool_button(icon, name, tool_id, tooltip)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        basic_widget.setLayout(layout)
        self.tool_box.addItem(basic_widget, "Básicas")
    
    def setup_shape_tools(self):
        """Configura herramientas de forma"""
        shape_widget = QWidget()
        layout = QGridLayout(shape_widget)
        
        tools = [
            ("⬜", "Rectángulo", "rectangle", "Crear rectángulos y cuadrados"),
            ("⭕", "Elipse", "ellipse", "Crear círculos y elipses"),
            ("🔺", "Polígono", "polygon", "Crear polígonos regulares"),
            ("⭐", "Estrella", "star", "Crear estrellas"),
            ("🔄", "Espiral", "spiral", "Crear espirales"),
            ("✏️", "Lápiz", "pencil", "Dibujar formas libres"),
            ("🖌️", "Pincel", "brush", "Pinceles artísticos")
        ]
        
        row, col = 0, 0
        for icon, name, tool_id, tooltip in tools:
            btn = self.create_tool_button(icon, name, tool_id, tooltip)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        shape_widget.setLayout(layout)
        self.tool_box.addItem(shape_widget, "Formas")
    
    def setup_text_tools(self):
        """Configura herramientas de texto"""
        text_widget = QWidget()
        layout = QGridLayout(text_widget)
        
        tools = [
            ("🔤", "Texto Horizontal", "text_h", "Texto horizontal"),
            ("🔠", "Texto Vertical", "text_v", "Texto vertical"),
            ("📝", "Texto en área", "text_area", "Texto en área delimitada"),
            ("🎨", "Texto en trayecto", "text_path", "Texto siguiendo un trayecto")
        ]
        
        row, col = 0, 0
        for icon, name, tool_id, tooltip in tools:
            btn = self.create_tool_button(icon, name, tool_id, tooltip)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        text_widget.setLayout(layout)
        self.tool_box.addItem(text_widget, "Texto")
    
    def setup_transform_tools(self):
        """Configura herramientas de transformación"""
        transform_widget = QWidget()
        layout = QGridLayout(transform_widget)
        
        tools = [
            ("↔️", "Escala", "scale", "Escalar elementos"),
            ("↩️", "Rotar", "rotate", "Rotar elementos"),
            ("✂️", "Tijeras", "scissors", "Dividir trayectos"),
            ("🔧", "Deformar", "warp", "Deformar elementos"),
            ("🔄", "Reflejar", "reflect", "Reflejar elementos")
        ]
        
        row, col = 0, 0
        for icon, name, tool_id, tooltip in tools:
            btn = self.create_tool_button(icon, name, tool_id, tooltip)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        transform_widget.setLayout(layout)
        self.tool_box.addItem(transform_widget, "Transformación")
    
    def create_tool_button(self, icon, name, tool_id, tooltip):
        """Crea un botón de herramienta personalizado"""
        btn = QPushButton(f"{icon} {name}")
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QPushButton:checked {
                background-color: #007acc;
                color: white;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        btn.clicked.connect(lambda: self.tool_selected(tool_id))
        self.tool_group.addButton(btn)
        
        return btn
    
    def tool_selected(self, tool_id):
        """Maneja la selección de una herramienta"""
        if self.parent and hasattr(self.parent, 'design_canvas'):
            self.parent.design_canvas.setTool(tool_id)
        
        # Actualizar estado de la herramienta seleccionada
        print(f"Herramienta seleccionada: {tool_id}")

class EffectsPanel(QDockWidget):
    """Panel de efectos para aplicaciones Android (XML/Java)"""
    
    def __init__(self, parent=None):
        super().__init__("Efectos Android", parent)
        self.parent = parent
        self.current_element = None  
        self.setup_ui()
    
    def setup_ui(self):
        effect_widget = QWidget()
        layout = QVBoxLayout(effect_widget)
        
        # Scroll area para efectos
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Efectos de animación
        self.setup_animation_effects(scroll_layout)
        
        # Efectos de vista
        self.setup_view_effects(scroll_layout)
        
        # Efectos de transición
        self.setup_transition_effects(scroll_layout)
        
        # Efectos de material design
        self.setup_material_effects(scroll_layout)
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        layout.addWidget(scroll_area)
        effect_widget.setLayout(layout)
        self.setWidget(effect_widget)
    
    def setup_animation_effects(self, layout):
        """Configura efectos de animación"""
        group = QGroupBox("🎭 Animaciones")
        group_layout = QGridLayout(group)
        
        animations = [
            ("Fade In", "fade_in", "android:alpha de 0 a 1"),
            ("Fade Out", "fade_out", "android:alpha de 1 a 0"),
            ("Slide In", "slide_in", "Deslizar desde los bordes"),
            ("Slide Out", "slide_out", "Deslizar hacia los bordes"),
            ("Zoom In", "zoom_in", "Escalar de pequeño a grande"),
            ("Zoom Out", "zoom_out", "Escalar de grande a pequeño"),
            ("Rotate", "rotate", "Rotación continua"),
            ("Bounce", "bounce", "Efecto rebote")
        ]
        
        row, col = 0, 0
        for name, effect_id, description in animations:
            btn = QPushButton(name)
            btn.setToolTip(description)
            btn.clicked.connect(lambda checked, eid=effect_id: self.apply_animation_effect(eid))
            group_layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        layout.addWidget(group)
    
    def setup_view_effects(self, layout):
        """Configura efectos de vista"""
        group = QGroupBox("👁️ Efectos de Vista")
        group_layout = QGridLayout(group)
        
        effects = [
            ("Elevación", "elevation", "Sombras y profundidad"),
            ("Corner Radius", "corner_radius", "Esquinas redondeadas"),
            ("Border", "border", "Bordes personalizados"),
            ("Gradient", "gradient", "Fondos degradados"),
            ("Blur", "blur", "Desenfoque"),
            ("Shadow", "shadow", "Sombras avanzadas")
        ]
        
        row, col = 0, 0
        for name, effect_id, description in effects:
            btn = QPushButton(name)
            btn.setToolTip(description)
            btn.clicked.connect(lambda checked, eid=effect_id: self.apply_view_effect(eid))
            group_layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        layout.addWidget(group)
    
    def setup_transition_effects(self, layout):
        """Configura efectos de transición"""
        group = QGroupBox("🔄 Transiciones")
        group_layout = QGridLayout(group)
        
        transitions = [
            ("Crossfade", "crossfade", "Transición suave entre vistas"),
            ("Explode", "explode", "Efecto explosión"),
            ("Fade Through", "fade_through", "Fundido a través"),
            ("Slide", "slide", "Deslizamiento"),
            ("Shared Element", "shared_element", "Elementos compartidos")
        ]
        
        row, col = 0, 0
        for name, effect_id, description in transitions:
            btn = QPushButton(name)
            btn.setToolTip(description)
            btn.clicked.connect(lambda checked, eid=effect_id: self.apply_transition_effect(eid))
            group_layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        layout.addWidget(group)
    
    def setup_material_effects(self, layout):
        """Configura efectos de Material Design"""
        group = QGroupBox("🎨 Material Design")
        group_layout = QGridLayout(group)
        
        material_effects = [
            ("Ripple", "ripple", "Efecto de onda al tocar"),
            ("State List", "state_list", "Estados diferentes"),
            ("Reveal", "reveal", "Animación de revelado"),
            ("Morph", "morph", "Transformación de formas"),
            ("FAB", "fab", "Floating Action Button")
        ]
        
        row, col = 0, 0
        for name, effect_id, description in material_effects:
            btn = QPushButton(name)
            btn.setToolTip(description)
            btn.clicked.connect(lambda checked, eid=effect_id: self.apply_material_effect(eid))
            group_layout.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        layout.addWidget(group)
    
    def apply_animation_effect(self, effect_id):
        """Aplica efecto de animación al elemento seleccionado"""
        if self.parent and hasattr(self.parent, 'selected_element'):
            element = self.parent.selected_element
            if element:
                animation_xml = self.generate_animation_xml(effect_id, element)
                self.parent.apply_effect_to_element(element, animation_xml)
    
    def apply_view_effect(self, effect_id):
        """Aplica efecto de vista al elemento seleccionado"""
        if self.parent and hasattr(self.parent, 'selected_element'):
            element = self.parent.selected_element
            if element:
                view_effect = self.generate_view_effect(effect_id, element)
                self.parent.apply_effect_to_element(element, view_effect)
    
    def apply_transition_effect(self, effect_id):
        """Aplica efecto de transición"""
        if self.parent:
            transition_xml = self.generate_transition_xml(effect_id)
            self.parent.apply_transition_effect(transition_xml)
    
    def apply_material_effect(self, effect_id):
        """Aplica efecto de Material Design"""
        if self.parent and hasattr(self.parent, 'selected_element'):
            element = self.parent.selected_element
            if element:
                material_effect = self.generate_material_effect(effect_id, element)
                self.parent.apply_effect_to_element(element, material_effect)
    
    def generate_animation_xml(self, effect_id, element):
        """Genera código XML para animaciones"""
        animations = {
            'fade_in': f'''
                <alpha xmlns:android="http://schemas.android.com/apk/res/android"
                    android:fromAlpha="0.0"
                    android:toAlpha="1.0"
                    android:duration="300"/>
            ''',
            'fade_out': f'''
                <alpha xmlns:android="http://schemas.android.com/apk/res/android"
                    android:fromAlpha="1.0"
                    android:toAlpha="0.0"
                    android:duration="300"/>
            ''',
            'slide_in': f'''
                <translate xmlns:android="http://schemas.android.com/apk/res/android"
                    android:fromXDelta="-100%"
                    android:toXDelta="0%"
                    android:duration="400"/>
            ''',
            'bounce': f'''
                <set xmlns:android="http://schemas.android.com/apk/res/android"
                    android:interpolator="@android:anim/bounce_interpolator">
                    <scale
                        android:fromXScale="0.5"
                        android:toXScale="1.0"
                        android:fromYScale="0.5"
                        android:toYScale="1.0"
                        android:duration="600"/>
                </set>
            '''
        }
        return animations.get(effect_id, '')
    
    def generate_view_effect(self, effect_id, element):
        """Genera efectos de vista"""
        effects = {
            'elevation': f'android:elevation="8dp"',
            'corner_radius': f'android:background="@drawable/rounded_corner"',
            'gradient': f'android:background="@drawable/gradient_background"'
        }
        return effects.get(effect_id, '')
    
    def generate_material_effect(self, effect_id, element):
        """Genera efectos de Material Design"""
        effects = {
            'ripple': f'android:background="?attr/selectableItemBackground"',
            'fab': f'style="@style/Widget.MaterialComponents.FloatingActionButton"'
        }
        return effects.get(effect_id, '')

class AdvancedIllustratorCanvas(QGraphicsView):
    """Lienzo avanzado tipo Illustrator para diseño vectorial"""
    
    elementCreated = Signal(UIElement)
    elementSelected = Signal(UIElement)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        # Configuración profesional
        self.setStyleSheet("""
            QGraphicsView {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2C2C2C, stop:0.5 #3C3C3C, stop:1 #2C2C2C);
                border: 1px solid #555;
            }
        """)
        
        # Herramientas y estado
        self.current_tool = "select"
        self.current_element = None
        self.elements = []
        self.selected_elements = []
        self.temp_element = None
        
        # Propiedades de dibujo
        self.current_color = QColor("#569CD6")
        self.stroke_color = QColor("#000000")
        self.stroke_width = 2
        self.fill_enabled = True
        self.stroke_enabled = True
        
        # Modo de dibujo
        self.drawing = False
        self.start_point = QPointF()
            # AGREGAR ESTA INICIALIZACIÓN:
        self.current_path = None
        self.drawing = False
        self.current_path = None
        
        # Configuración de vista
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Cuadrícula y guías
        self.grid_visible = True
        self.grid_size = 20
        self.guides = []
        
        # Zoom
        self.zoom_level = 1.0
        self.setup_grid()
        
    def setup_grid(self):
        """Configura la cuadrícula de diseño"""
        if self.grid_visible:
            pen = QPen(QColor(60, 60, 60, 100))
            pen.setWidth(1)
            
            # Líneas principales cada 100px
            for x in range(-1000, 1000, 100):
                line = QGraphicsLineItem(x, -1000, x, 1000)
                line.setPen(pen)
                line.setZValue(-100)
                self.scene.addItem(line)
                
            for y in range(-1000, 1000, 100):
                line = QGraphicsLineItem(-1000, y, 1000, y)
                line.setPen(pen)
                line.setZValue(-100)
                self.scene.addItem(line)
    
    def set_tool(self, tool_id):
        """Establece la herramienta actual"""
        self.current_tool = tool_id
        self.setCursor(self.get_tool_cursor(tool_id))
        
        if tool_id == "select":
            self.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.NoDrag)
    
    def get_tool_cursor(self, tool_id):
        """Retorna el cursor apropiado para cada herramienta"""
        cursors = {
            "select": Qt.ArrowCursor,
            "rectangle": Qt.CrossCursor,
            "ellipse": Qt.CrossCursor,
            "pen": Qt.CrossCursor,
            "text": Qt.IBeamCursor,
            "line": Qt.CrossCursor,
            "hand": Qt.OpenHandCursor,
            "zoom": QPixmap(":/cursors/zoom.png")  # Puedes agregar iconos personalizados
        }
        return cursors.get(tool_id, Qt.ArrowCursor)
    
    def mousePressEvent(self, event):
        """Maneja el evento de presión del mouse"""
        scene_pos = self.mapToScene(event.pos())
        
        if event.button() == Qt.LeftButton:
            if self.current_tool == "select":
                # Selección normal
                super().mousePressEvent(event)
            else:
                # Iniciar creación de elemento
                self.start_drawing(scene_pos)
        
        elif event.button() == Qt.RightButton:
            # Herramienta de mano para navegar
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake_event = QMouseEvent(
                event.type(), event.localPos(), event.screenPos(),
                Qt.LeftButton, Qt.LeftButton, event.modifiers()
            )
            super().mousePressEvent(fake_event)
        
        elif event.button() == Qt.MiddleButton:
            # Zoom rápido
            self.zoom_to_point(scene_pos, 1.2)
    
    def mouseMoveEvent(self, event):
        """Maneja el movimiento del mouse"""
        scene_pos = self.mapToScene(event.pos())
        
        if self.drawing and self.current_tool != "select":
            self.update_drawing(scene_pos)
        
        # Actualizar coordenadas en la barra de estado
        if hasattr(self.parent(), 'statusBar'):
            self.parent().statusBar().showMessage(f"X: {scene_pos.x():.1f}, Y: {scene_pos.y():.1f} | Zoom: {self.zoom_level*100:.0f}%")
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Maneja la liberación del mouse"""
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        
        if self.drawing:
            self.finish_drawing()
        
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """Maneja el zoom con la rueda del mouse"""
        factor = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.zoom_to_point(self.mapToScene(event.pos()), factor)
    
    def zoom_to_point(self, point, factor):
        """Zoom centrado en un punto específico"""
        self.scale(factor, factor)
        self.zoom_level *= factor
        
        # Ajustar la vista para mantener el punto centrado
        old_pos = self.mapFromScene(point)
        center = self.mapToScene(self.viewport().rect().center())
        delta = point - center
        self.translate(delta.x(), delta.y())
    
    def start_drawing(self, pos):
        """Inicia el proceso de dibujo"""
        self.drawing = True
        self.start_point = pos
        
        if self.current_tool == "rectangle":
            self.create_rectangle(pos)
        elif self.current_tool == "ellipse":
            self.create_ellipse(pos)
        elif self.current_tool == "pen":
            self.start_path(pos)
        elif self.current_tool == "text":
            self.create_text(pos)
        elif self.current_tool == "line":
            self.create_line(pos)
    
    def update_drawing(self, pos):
        """Actualiza el elemento durante el dibujo"""
        if not self.temp_element:
            return
            
        if self.current_tool in ["rectangle", "ellipse"]:
            self.update_shape_dimensions(pos)
        elif self.current_tool == "line":
            self.update_line_endpoint(pos)
        elif self.current_tool == "pen":
            self.add_path_point(pos)
    
    def finish_drawing(self):
        """Finaliza el proceso de dibujo"""
        self.drawing = False
        
        if self.temp_element and self.temp_element.graphicsItem:
            # Hacer el elemento seleccionable y movable
            self.temp_element.graphicsItem.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.temp_element.graphicsItem.setFlag(QGraphicsItem.ItemIsMovable, True)
            
            self.elements.append(self.temp_element)
            self.elementCreated.emit(self.temp_element)
            
            # Seleccionar el nuevo elemento
            self.select_element(self.temp_element)
        
        self.temp_element = None
    
    def create_rectangle(self, pos):
        """Crea un rectángulo temporal"""
        element = UIElement("rectangle", pos.x(), pos.y(), 1, 1)
        rect_item = QGraphicsRectItem(0, 0, 1, 1)
        rect_item.setPos(pos)
        
        # Aplicar estilo
        brush = QBrush(self.current_color) if self.fill_enabled else QBrush(Qt.NoBrush)
        pen = QPen(self.stroke_color, self.stroke_width) if self.stroke_enabled else QPen(Qt.NoPen)
        
        rect_item.setBrush(brush)
        rect_item.setPen(pen)
        
        self.scene.addItem(rect_item)
        element.graphicsItem = rect_item
        self.temp_element = element
    
    def create_ellipse(self, pos):
        """Crea una elipse temporal"""
        element = UIElement("ellipse", pos.x(), pos.y(), 1, 1)
        ellipse_item = QGraphicsEllipseItem(0, 0, 1, 1)
        ellipse_item.setPos(pos)
        
        brush = QBrush(self.current_color) if self.fill_enabled else QBrush(Qt.NoBrush)
        pen = QPen(self.stroke_color, self.stroke_width) if self.stroke_enabled else QPen(Qt.NoPen)
        
        ellipse_item.setBrush(brush)
        ellipse_item.setPen(pen)
        
        self.scene.addItem(ellipse_item)
        element.graphicsItem = ellipse_item
        self.temp_element = element
    
    def create_text(self, pos):
        """Crea un elemento de texto"""
        element = UIElement("text", pos.x(), pos.y(), 200, 50)
        text_item = QGraphicsTextItem("Texto editable")
        text_item.setPos(pos)
        text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        text_item.setDefaultTextColor(self.current_color)
        
        # Fuente profesional
        font = QFont("Segoe UI", 12)
        text_item.setFont(font)
        
        self.scene.addItem(text_item)
        element.graphicsItem = text_item
        element.setProperty("text", "Texto editable")
        element.setProperty("textColor", self.current_color.name())
        element.setProperty("textSize", "12pt")
        
        self.temp_element = element
        self.finish_drawing()  # El texto se edita inmediatamente
    
    def create_line(self, pos):
        """Crea una línea temporal"""
        element = UIElement("line", pos.x(), pos.y(), 1, 1)
        line_item = QGraphicsLineItem(pos.x(), pos.y(), pos.x(), pos.y())
        
        pen = QPen(self.stroke_color, self.stroke_width)
        line_item.setPen(pen)
        
        self.scene.addItem(line_item)
        element.graphicsItem = line_item
        self.temp_element = element
    
    def start_path(self, pos):
        """Inicia un trazo de pluma"""
        element = UIElement("path", pos.x(), pos.y(), 0, 0)
        path_item = QGraphicsPathItem()
        
        pen = QPen(self.stroke_color, self.stroke_width)
        path_item.setPen(pen)
        if self.fill_enabled:
            path_item.setBrush(QBrush(self.current_color))
        
        self.path = QPainterPath()
        self.path.moveTo(pos)
        
        path_item.setPath(self.path)
        self.scene.addItem(path_item)
        
        element.graphicsItem = path_item
        self.temp_element = element
    
    def add_path_point(self, pos):
        """Añade un punto al trazo de pluma"""
        if hasattr(self, 'path') and self.temp_element:
            self.path.lineTo(pos)
            self.temp_element.graphicsItem.setPath(self.path)
    
    def update_shape_dimensions(self, pos):
        """Actualiza dimensiones de formas durante el dibujo"""
        if not self.temp_element:
            return
            
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = pos.x(), pos.y()
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # Actualizar elemento
        self.temp_element.x = x
        self.temp_element.y = y
        self.temp_element.width = width
        self.temp_element.height = height
        
        # Actualizar gráficos
        if isinstance(self.temp_element.graphicsItem, (QGraphicsRectItem, QGraphicsEllipseItem)):
            self.temp_element.graphicsItem.setRect(0, 0, width, height)
            self.temp_element.graphicsItem.setPos(x, y)
    
    def update_line_endpoint(self, pos):
        """Actualiza el punto final de la línea"""
        if self.temp_element and isinstance(self.temp_element.graphicsItem, QGraphicsLineItem):
            line = self.temp_element.graphicsItem.line()
            self.temp_element.graphicsItem.setLine(
                line.x1(), line.y1(), pos.x(), pos.y()
            )
    
    def select_element(self, element):
        """Selecciona un elemento y actualiza los paneles"""
        # Deseleccionar todos
        for elem in self.elements:
            if elem.graphicsItem:
                elem.graphicsItem.setSelected(False)
        
        # Seleccionar nuevo elemento
        if element and element.graphicsItem:
            element.graphicsItem.setSelected(True)
            self.selected_elements = [element]
            self.elementSelected.emit(element)
            
            # Actualizar panel de propiedades
            if hasattr(self.parent(), 'update_properties_panel'):
                self.parent().update_properties_panel(element)
    
    def delete_selected(self):
        """Elimina los elementos seleccionados"""
        for element in self.selected_elements[:]:
            if element.graphicsItem:
                self.scene.removeItem(element.graphicsItem)
                self.elements.remove(element)
        self.selected_elements.clear()
    
    def bring_to_front(self):
        """Trae al frente los elementos seleccionados"""
        for element in self.selected_elements:
            if element.graphicsItem:
                element.graphicsItem.setZValue(max([item.zValue() for item in self.scene.items()] or [0]) + 1)
    
    def send_to_back(self):
        """Envía al fondo los elementos seleccionados"""
        for element in self.selected_elements:
            if element.graphicsItem:
                element.graphicsItem.setZValue(min([item.zValue() for item in self.scene.items()] or [0]) - 1)
    
    def group_selected(self):
        """Agrupa elementos seleccionados"""
        if len(self.selected_elements) > 1:
            group = QGraphicsItemGroup()
            for element in self.selected_elements:
                if element.graphicsItem:
                    group.addToGroup(element.graphicsItem)
            self.scene.addItem(group)
    
    def export_to_svg(self, filename):
        """Exporta el diseño a SVG"""
        svg = QSvgGenerator()
        svg.setFileName(filename)
        svg.setSize(QSize(int(self.scene.width()), int(self.scene.height())))
        svg.setViewBox(QRectF(0, 0, self.scene.width(), self.scene.height()))
        
        painter = QPainter(svg)
        self.scene.render(painter)
        painter.end()

class HojaAIPanel(QDockWidget):
    """Panel Hoja_AI - Lienzo profesional tipo Illustrator con tamaño de celular"""
    
    def __init__(self, parent=None):
        super().__init__("Hoja_AI - Lienzo Profesional (Vista Celular)", parent)
        self.parent = parent
        self.phone_width = 360  # Ancho estándar para móviles (360dp en Android)
        self.phone_height = 640  # Alto estándar para móviles
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes
        layout.setSpacing(0)  # Sin espaciado
        
        # Lienzo principal con tamaño exacto de celular - SIMPLIFICADO
        self.canvas = AdvancedIllustratorCanvas(self)
        self.canvas.setFixedSize(self.phone_width, self.phone_height)
        self.canvas.elementSelected.connect(self.on_element_selected)
        
        # Configurar la escena con el tamaño del celular - FONDO BLANCO SIMPLE
        self.canvas.scene.setSceneRect(0, 0, self.phone_width, self.phone_height)
        self.canvas.scene.setBackgroundBrush(QBrush(QColor(255, 255, 255)))  # Fondo blanco
        
        # QUITAR el marco del teléfono y elementos decorativos
        # Solo el lienzo limpio
        
        layout.addWidget(self.canvas)
        main_widget.setLayout(layout)
        self.setWidget(main_widget)
        
        # Forzar el tamaño del dock
        self.setMinimumSize(self.phone_width, self.phone_height)
        self.setMaximumSize(self.phone_width + 50, self.phone_height + 50)  # Un poco de margen
    
    def setup_phone_frame(self):
        """Añade un marco que simula un teléfono celular"""
        # Marco exterior
        phone_frame = QGraphicsRectItem(0, 0, self.phone_width, self.phone_height)
        phone_frame.setPen(QPen(QColor(80, 80, 80), 2))
        phone_frame.setBrush(QBrush(QColor(240, 240, 240)))
        phone_frame.setZValue(-1000)  # Enviar al fondo
        self.canvas.scene.addItem(phone_frame)
        
        # Notch simulado (opcional)
        notch = QGraphicsRectItem(self.phone_width/2 - 30, 0, 60, 20)
        notch.setBrush(QBrush(QColor(20, 20, 20)))
        notch.setPen(QPen(Qt.NoPen))
        notch.setZValue(-900)
        self.canvas.scene.addItem(notch)
        
        # Botón home simulado
        home_button = QGraphicsEllipseItem(self.phone_width/2 - 15, self.phone_height - 10, 30, 30)
        home_button.setBrush(QBrush(QColor(60, 60, 60)))
        home_button.setPen(QPen(QColor(100, 100, 100)))
        home_button.setZValue(-900)
        self.canvas.scene.addItem(home_button)
    
    def create_toolbar(self):
        """Crea una barra de herramientas compacta"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        toolbar.setMaximumHeight(35)
        
        # Herramientas esenciales para móvil
        tools = [
            ("🔍", "select", "Selección (V)", True),
            ("⬜", "rectangle", "Rectángulo (R)", False),
            ("⭕", "ellipse", "Elipse (E)", False),
            ("🔤", "text", "Texto (T)", False),
            ("📏", "line", "Línea (L)", False),
        ]
        
        tool_group = QButtonGroup(self)
        
        for icon, tool_id, tooltip, checked in tools:
            btn = QPushButton(icon)
            btn.setCheckable(True)
            btn.setChecked(checked)
            btn.setToolTip(tooltip)
            btn.setFixedSize(30, 30)
            btn.clicked.connect(lambda checked, tid=tool_id: self.set_tool(tid))
            toolbar.addWidget(btn)
            tool_group.addButton(btn)
        
        toolbar.addSeparator()
        
        # Controles de zoom específicos para móvil
        zoom_out_btn = QPushButton("➖")
        zoom_out_btn.setToolTip("Alejar")
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_out_btn.setFixedSize(30, 30)
        toolbar.addWidget(zoom_out_btn)
        
        zoom_label = QLabel("100%")
        zoom_label.setAlignment(Qt.AlignCenter)
        zoom_label.setFixedWidth(40)
        toolbar.addWidget(zoom_label)
        
        zoom_in_btn = QPushButton("➕")
        zoom_in_btn.setToolTip("Acercar")
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_in_btn.setFixedSize(30, 30)
        toolbar.addWidget(zoom_in_btn)
        
        return toolbar
    
    def create_status_bar(self):
        """Crea una barra de estado compacta"""
        status_bar = QStatusBar()
        status_bar.setMaximumHeight(25)
        
        # Información de posición específica para móvil
        self.position_label = QLabel(f"X: 0, Y: 0 | {self.phone_width}x{self.phone_height}px")
        self.position_label.setStyleSheet("font-size: 10px;")
        status_bar.addWidget(self.position_label)
        
        # Indicador de densidad de píxeles (común en Android)
        density_label = QLabel("@3x")
        density_label.setStyleSheet("font-size: 10px; color: #666;")
        status_bar.addPermanentWidget(density_label)
        
        return status_bar
    
    def set_tool(self, tool_id):
        """Establece la herramienta actual"""
        self.canvas.set_tool(tool_id)
    
    def zoom_in(self):
        """Acercar zoom manteniendo proporciones de celular"""
        current_scale = self.canvas.transform().m11()
        if current_scale < 3.0:  # Límite máximo de zoom
            self.canvas.scale(1.2, 1.2)
            self.update_zoom_display()
    
    def zoom_out(self):
        """Alejar zoom manteniendo proporciones de celular"""
        current_scale = self.canvas.transform().m11()
        if current_scale > 0.3:  # Límite mínimo de zoom
            self.canvas.scale(0.8, 0.8)
            self.update_zoom_display()
    
    def update_zoom_display(self):
        """Actualiza la visualización del zoom"""
        zoom_level = int(self.canvas.transform().m11() * 100)
        # Buscar y actualizar la etiqueta de zoom en la toolbar
        for widget in self.findChildren(QLabel):
            if widget.text().endswith('%'):
                widget.setText(f"{zoom_level}%")
                break
    
    def on_element_selected(self, element):
        """Maneja la selección de elementos actualizando la posición"""
        if element:
            x, y = int(element.x), int(element.y)
            # Actualizar posición si es necesario
            pass



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
        self.open_windows = {} 
        self.current_editor = None
        

        self.create_illustrator_tools_panel()  
        self.create_effects_panel() 
        
        self.setup_workspace()
        self.create_workspace_presets()
        self.setup_ui()
        self.setup_shortcuts()

        self.setup_enhanced_docks()
        self.setup_hoja_ai()
        
        self.create_menu_bar()
        self.setup_language_specific_features()
        self.setup_context_menu()
    def setup_hoja_ai(self):
        """Configura el panel Hoja_AI como centro de la interfaz"""
        # Remover el widget inicial del emulador
        if hasattr(self, 'emulator_container'):
            self.tab_widget.removeTab(0)
        
        # Crear y configurar Hoja_AI
        self.hoja_ai_panel = HojaAIPanel(self)
        
        # Hacerlo el widget central principal
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.hoja_ai_panel)
        self.setCentralWidget(central_widget)
        
        # Conectar señales entre paneles
        self.connect_panels()

    def connect_panels(self):
        """Conecta Hoja_AI con los demás paneles"""
        try:
            if (hasattr(self, 'effects_panel') and 
                hasattr(self.hoja_ai_panel, 'canvas') and 
                hasattr(self.hoja_ai_panel.canvas, 'elementSelected') and
                hasattr(self.effects_panel, 'on_element_selected')):
                
                self.hoja_ai_panel.canvas.elementSelected.connect(self.effects_panel.on_element_selected)
                print("Conexión EffectsPanel establecida correctamente")
        except Exception as e:
            print(f"Error conectando EffectsPanel: {e}")
        
        try:
            if hasattr(self, 'illustrator_tools_panel'):
                # Conectar herramientas de Illustrator con Hoja_AI
                # Agrega aquí las conexiones necesarias
                pass
        except Exception as e:
            print(f"Error conectando IllustratorToolsPanel: {e}")
    
    def toggle_hoja_ai(self):
        """Alternar visibilidad de Hoja_AI"""
        if self.hoja_ai_panel.isVisible():
            self.hoja_ai_panel.hide()
        else:
            self.hoja_ai_panel.show()
            self.hoja_ai_panel.raise_()

    # Agregar estos métodos a la clase existente
    def setup_hoja_ai_in_current_class(self):
        """Integra Hoja_AI en la clase IllustratorWindow existente"""
        
        # Reemplazar el contenido del emulador por Hoja_AI
        if hasattr(self, 'emulator_layout'):
            # Limpiar el layout existente
            for i in reversed(range(self.emulator_layout.count())): 
                self.emulator_layout.itemAt(i).widget().setParent(None)
            
            # Agregar Hoja_AI
            self.hoja_ai = AdvancedIllustratorCanvas(self)
            self.emulator_layout.addWidget(self.hoja_ai)
            
            # Actualizar el título de la pestaña
            self.tab_widget.setTabText(0, "Hoja_AI")
            self.tab_widget.setTabToolTip(0, "Lienzo profesional de diseño vectorial")
            
            # Conectar con otros paneles
            self.hoja_ai.elementSelected.connect(self.on_canvas_element_selected)

    def on_canvas_element_selected(self, element):
        """Maneja la selección de elementos en el canvas"""
        # Actualizar panel de propiedades
        if hasattr(self, 'properties_panel'):
            self.update_properties_panel(element)
        
        # Actualizar panel de efectos
        if hasattr(self, 'effects_panel'):
            self.effects_panel.update_for_element(element)
        
        # Actualizar panel de capas
        if hasattr(self, 'layers_list'):
            self.update_layers_selection(element)
    def create_illustrator_tools_panel(self):
        """Crea el panel de herramientas de Illustrator CORREGIDO"""
        self.illustrator_tools_panel = IllustratorToolsPanel(self)
        
        # CONFIGURACIÓN CORREGIDA PARA QUE SEA VISIBLE Y MOVIBLE:
        self.illustrator_tools_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        
        # Hacerlo flotante por defecto
        self.illustrator_tools_panel.setFloating(True)
        
        # Configurar tamaño y posición inicial
        self.illustrator_tools_panel.setGeometry(100, 100, 300, 500)  # x, y, width, height
        
        # Permitir que sea movible y cerrable
        self.illustrator_tools_panel.setFeatures(
            QDockWidget.DockWidgetMovable | 
            QDockWidget.DockWidgetClosable | 
            QDockWidget.DockWidgetFloatable
        )
        
        # Añadirlo al área de docks
        self.addDockWidget(Qt.RightDockWidgetArea, self.illustrator_tools_panel)
        
        # Hacerlo visible inmediatamente
        self.illustrator_tools_panel.setVisible(True)
        
        # Traerlo al frente
        self.illustrator_tools_panel.raise_()
        self.illustrator_tools_panel.activateWindow()
    
    def create_effects_panel(self):
        """Crea el panel de efectos Android CORREGIDO"""
        self.effects_panel = EffectsPanel(self)
        
        # Misma configuración para el panel de efectos
        self.effects_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.effects_panel.setFloating(True)
        self.effects_panel.setGeometry(450, 100, 300, 500)  # Posición diferente para no solaparse
        
        self.effects_panel.setFeatures(
            QDockWidget.DockWidgetMovable | 
            QDockWidget.DockWidgetClosable | 
            QDockWidget.DockWidgetFloatable
        )
        
        self.addDockWidget(Qt.RightDockWidgetArea, self.effects_panel)
        self.effects_panel.setVisible(True)
        self.effects_panel.raise_()
        self.effects_panel.activateWindow()
        def apply_effect_to_element(self, element, effect_xml):
            """Aplica un efecto al elemento seleccionado"""
            if element and effect_xml:
                # Aquí implementarías la lógica para aplicar el efecto al elemento
                print(f"Aplicando efecto a {element.id}: {effect_xml}")
                
                # Actualizar las propiedades del elemento
                element.properties['effect'] = effect_xml
                
                # Regenerar el XML del elemento
                new_xml = element.toXML()
                
                # Actualizar la vista previa
                self.update_design_preview()
    
    def apply_transition_effect(self, transition_xml):
        """Aplica efecto de transición a la actividad"""
        if transition_xml:
            # Guardar el efecto de transición para la actividad
            self.transition_effect = transition_xml
            print(f"Transición aplicada: {transition_xml}")
    
    def update_design_preview(self):
        """Actualiza la vista previa del diseño"""
        if hasattr(self, 'design_canvas'):
            self.hoja_ai_canvas.update()
    def setup_context_menu(self):
        """Configura el menú contextual para el explorador de archivos"""
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_file_explorer_context_menu)

        self.file_tree.setDragEnabled(True)
        self.file_tree.setAcceptDrops(True)
        self.file_tree.setDragDropMode(QTreeView.InternalMove)
    
    def show_file_explorer_context_menu(self, position):
        """Muestra el menú contextual en el explorador de archivos"""
        index = self.file_tree.indexAt(position)
        if not index.isValid():
            current_path = self.project_path
        else:
            current_path = self.file_model.filePath(index)

            if os.path.isfile(current_path):
                current_path = os.path.dirname(current_path)

        context_menu = FileExplorerContextMenu(self)
        context_menu.exec_(self.file_tree.viewport().mapToGlobal(position))
    
    def create_file_from_dialog(self, dialog, base_path):
        """Crea un archivo basado en la selección del diálogo"""
        file_type = dialog.selected_type
        filename = dialog.selected_filename

        if not any(filename.endswith(ext) for ext in file_type.extensions):
            filename += file_type.extensions[0]
        
        file_path = os.path.join(base_path, filename)

        if os.path.exists(file_path):
            reply = QMessageBox.question(
                self,
                "Archivo Existente",
                f"El archivo '{filename}' ya existe. ¿Desea reemplazarlo?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                content = file_type.template

                class_name = filename.replace(" ", "_").replace(".java", "").replace(".kt", "").replace(".dart", "")
                content = content.replace("{class_name}", class_name)
                content = content.replace("{interface_name}", class_name)
                content = content.replace("{layout_name}", class_name.lower())
                
                f.write(content)
            
            self.file_model.setRootPath(self.project_path)
            
            self.open_file_in_tab(file_path)

            self.statusBar().showMessage(f"✅ Archivo '{filename}' creado exitosamente", 3000)

            new_index = self.file_model.index(file_path)
            self.file_tree.setCurrentIndex(new_index)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el archivo:\n{str(e)}")
    
    def update_file_explorer(self):
        """Actualiza la vista del explorador de archivos"""
        self.file_model.setRootPath(self.project_path)
        self.file_tree.setRootIndex(self.file_model.index(self.project_path))

    def dragEnterEvent(self, event):
        """Maneja el evento de arrastrar hacia la ventana"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Maneja el evento de soltar archivos"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    self.open_file_in_tab(file_path)
            event.acceptProposedAction()
    def setup_language_specific_features(self):
        """Configura las características específicas según el lenguaje del proyecto"""
        if self.project_language.lower() == "java":
            self.setup_java_features()
        elif self.project_language.lower() == "kotlin":
            self.setup_kotlin_features()
        elif self.project_language.lower() == "flutter":
            self.setup_flutter_features()
        else:
            self.setup_java_features()

    def setup_enhanced_docks(self):
        """Configuración mejorada de docks - respetar visibilidad existente"""

        existing_docks = self.findChildren(QDockWidget)
        for dock in existing_docks:
            self.removeDockWidget(dock)

        docks_to_add = [
            (Qt.LeftDockWidgetArea, self.tool_panel),
            (Qt.LeftDockWidgetArea, self.layers_panel),
            (Qt.LeftDockWidgetArea, self.file_explorer_panel),
            (Qt.RightDockWidgetArea, self.color_panel),
            (Qt.RightDockWidgetArea, self.ai_panel)
        ]

        if hasattr(self, 'character_panel') and self.character_panel:
            docks_to_add.append((Qt.BottomDockWidgetArea, self.character_panel))
        
        if hasattr(self, 'paragraph_panel') and self.paragraph_panel:
            docks_to_add.append((Qt.BottomDockWidgetArea, self.paragraph_panel))
        
        if hasattr(self, 'brushes_panel') and self.brushes_panel:
            docks_to_add.append((Qt.BottomDockWidgetArea, self.brushes_panel))
        
        for area, dock in docks_to_add:
            if dock:
                self.addDockWidget(area, dock)
                dock.setVisible(False)  

        self.tabifyDockWidget(self.tool_panel, self.layers_panel)
        self.tabifyDockWidget(self.tool_panel, self.file_explorer_panel)
        self.tabifyDockWidget(self.color_panel, self.ai_panel)

        if hasattr(self, 'character_panel') and hasattr(self, 'paragraph_panel'):
            if self.character_panel and self.paragraph_panel:
                self.tabifyDockWidget(self.character_panel, self.paragraph_panel)
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
    def show_xml_designer(self, parent_widget, xml_content, file_path):
        """NUEVA versión - Abre XML en Hoja_AI con editor dual"""
        layout = parent_widget.layout()
        
        splitter = QSplitter(Qt.Horizontal)
      
        xml_editor = EnhancedCodeEditor(theme="dark")
        xml_editor.setPlainText(xml_content)
        xml_editor.set_highlighter(file_path)
        
        design_view = AdvancedIllustratorCanvas(self)
        design_view.set_xml_content(xml_content) 
        
        splitter.addWidget(xml_editor)
        splitter.addWidget(design_view)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
    def setup_workspace(self):
        self.current_preset = "Minimal"  
        self.tool_panel_position = "left"
        self.visible_panels = []  
    def create_workspace_presets(self):
        self.workspace_presets = {
            "Default": WorkspacePreset("Default", "left", ["Tools", "Layers", "AI Assistant"]),
            "Minimal": WorkspacePreset("Minimal", "left", ["File Explorer", "AI Assistant"]),
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
        
        self.main_layout.addWidget(self.tab_widget)
        
        self.create_tool_panel()
        self.create_layers_panel()
        self.create_color_panel()
        self.create_brushes_panel()
        self.create_character_panel()
        self.create_paragraph_panel()
        self.create_ai_panel()
        self.create_file_explorer_panel()
        
        self.create_menu_bar()

        self.setup_enhanced_docks()

        self.ai_panel.setVisible(True)
        self.file_explorer_panel.setVisible(True)

        self.ai_panel_action.setChecked(True)
        self.explorer_panel_action.setChecked(True)

        self.statusBar().showMessage("Ready | Zoom: 100%")

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
        
        self.addDockWidget(Qt.RightDockWidgetArea, self.paragraph_panel)
        self.paragraph_panel.setVisible(False)  
    def create_ai_panel(self):
        self.ai_panel = EnhancedAIChatPanel(self.code_generator, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.ai_panel)

    def create_file_explorer_panel(self):
        """Crea el panel del explorador de archivos con mejoras"""
        self.file_explorer_panel = QDockWidget("Explorador de Archivos", self)
        self.file_explorer_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        explorer_widget = QWidget()
        layout = QVBoxLayout(explorer_widget)

        toolbar_layout = QHBoxLayout()

        new_file_btn = QPushButton("📄")
        new_file_btn.setToolTip("Nuevo Archivo (Ctrl+N)")
        new_file_btn.clicked.connect(self.show_new_file_dialog_at_root)
        new_file_btn.setFixedSize(30, 30)

        new_folder_btn = QPushButton("📁")
        new_folder_btn.setToolTip("Nueva Carpeta (Ctrl+Shift+N)")
        new_folder_btn.clicked.connect(self.create_new_folder_at_root)
        new_folder_btn.setFixedSize(30, 30)
  
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refrescar Explorador")
        refresh_btn.clicked.connect(self.update_file_explorer)
        refresh_btn.setFixedSize(30, 30)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar archivos...")
        self.search_input.textChanged.connect(self.filter_file_explorer)
        
        toolbar_layout.addWidget(new_file_btn)
        toolbar_layout.addWidget(new_folder_btn)
        toolbar_layout.addWidget(refresh_btn)
        toolbar_layout.addWidget(self.search_input)
        
        layout.addLayout(toolbar_layout)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.project_path)

        self.file_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(self.project_path))

        self.file_tree.setAnimated(True)
        self.file_tree.setIndentation(15)
        self.file_tree.setSortingEnabled(True)
        self.file_tree.sortByColumn(0, Qt.AscendingOrder)
        
        for i in range(1, 4): 
            self.file_tree.hideColumn(i)

        self.file_tree.setIconSize(QSize(16, 16))
        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
        
        layout.addWidget(self.file_tree)
        explorer_widget.setLayout(layout)
        self.file_explorer_panel.setWidget(explorer_widget)
        delegate = FileIconDelegate(self.file_tree)
        self.file_tree.setItemDelegateForColumn(0, delegate)

    def show_new_file_dialog_at_root(self):
        """Muestra el diálogo para crear archivo en la raíz del proyecto"""
        dialog = NewFileDialog(self.project_language, self, self.project_path)
        if dialog.exec_() == QDialog.Accepted:
            self.create_file_from_dialog(dialog, self.project_path)

    def create_new_folder_at_root(self):
        """Crea una nueva carpeta en la raíz del proyecto"""
        folder_name, ok = QInputDialog.getText(
            self, 
            "Nueva Carpeta", 
            "Nombre de la carpeta:",
            text="NuevaCarpeta"
        )
        
        if ok and folder_name:
            new_folder_path = os.path.join(self.project_path, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=False)
                self.update_file_explorer()
                QMessageBox.information(self, "Éxito", f"Carpeta '{folder_name}' creada correctamente")
            except FileExistsError:
                QMessageBox.warning(self, "Error", f"La carpeta '{folder_name}' ya existe")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear la carpeta: {str(e)}")

    def filter_file_explorer(self, text):
        """Filtra los archivos visibles en el explorador"""
        if not text.strip():
            self.file_model.setNameFilters(["*"])
        else:
            self.file_model.setNameFilters([f"*{text}*"])
    def show_new_file_dialog_at_root(self):
        """Muestra el diálogo para crear archivo en la raíz del proyecto"""
        dialog = NewFileDialog(self.project_language, self, self.project_path)
        if dialog.exec_() == QDialog.Accepted:
            self.create_file_from_dialog(dialog, self.project_path)

    def create_new_folder_at_root(self):
        """Crea una nueva carpeta en la raíz del proyecto"""
        folder_name, ok = QInputDialog.getText(
            self, 
            "Nueva Carpeta", 
            "Nombre de la carpeta:",
            text="NuevaCarpeta"
        )
        
        if ok and folder_name:
            new_folder_path = os.path.join(self.project_path, folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=False)
                self.update_file_explorer()
                QMessageBox.information(self, "Éxito", f"Carpeta '{folder_name}' creada correctamente")
            except FileExistsError:
                QMessageBox.warning(self, "Error", f"La carpeta '{folder_name}' ya existe")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear la carpeta: {str(e)}")

    def filter_file_explorer(self, text):
        """Filtra los archivos visibles en el explorador"""
        if not text.strip():
            self.file_model.setNameFilters(["*"])
        else:
            self.file_model.setNameFilters([f"*{text}*"])
    def setup_shortcuts(self):
        """Configura los atajos de teclado globales"""
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_current_file)

        self.save_all_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.save_all_shortcut.activated.connect(self.save_all_files)

        self.close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_tab_shortcut.activated.connect(self.close_current_tab)

        self.new_file_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.new_file_shortcut.activated.connect(self.new_file_with_template)

    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.clear()
        
        file_menu = menubar.addMenu("Archivo")

        new_action = QAction("Nuevo Archivo", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file_with_template)
        file_menu.addAction(new_action)
        
        new_project_action = QAction("Nuevo Proyecto", self)
        new_project_action.setShortcut("Ctrl+Shift+N")
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        file_menu.addSeparator()

        open_action = QAction("Abrir Archivo", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        open_project_action = QAction("Abrir Proyecto", self)
        open_project_action.setShortcut("Ctrl+Shift+O")
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()

        self.save_action = QAction("Guardar", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_current_file)
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)

        self.save_as_action = QAction("Guardar Como...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self.save_file_as)
        self.save_as_action.setEnabled(False)
        file_menu.addAction(self.save_as_action)
 
        save_all_action = QAction("Guardar Todos", self)
        save_all_action.setShortcut("Ctrl+Alt+S")
        save_all_action.triggered.connect(self.save_all_files)
        file_menu.addAction(save_all_action)
        
        file_menu.addSeparator()

        self.close_tab_action = QAction("Cerrar Pestaña", self)
        self.close_tab_action.setShortcut("Ctrl+W")
        self.close_tab_action.triggered.connect(self.close_current_tab)
        self.close_tab_action.setEnabled(False)
        file_menu.addAction(self.close_tab_action)

        close_all_action = QAction("Cerrar Todos", self)
        close_all_action.setShortcut("Ctrl+Shift+W")
        close_all_action.triggered.connect(self.close_all_tabs)
        file_menu.addAction(close_all_action)
        
        file_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("Edicion")
  
        undo_action = QAction("Deshacer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Rehacer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()

        cut_action = QAction("Cortar", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copiar", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
   
        paste_action = QAction("Pegar", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()

        select_all_action = QAction("Seleccionar Todo", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)

        find_action = QAction("Buscar", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find)
        edit_menu.addAction(find_action)

        replace_action = QAction("Reemplazar", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.replace)
        edit_menu.addAction(replace_action)

        view_menu = menubar.addMenu("Ver")

        panels_menu = view_menu.addMenu("Paneles")
     

        self.illustrator_tools_action = QAction("Herramientas Illustrator", self)
        self.illustrator_tools_action.setCheckable(True)
        self.illustrator_tools_action.setChecked(False)
        self.illustrator_tools_action.triggered.connect(self.toggle_illustrator_tools_panel)
        panels_menu.addAction(self.illustrator_tools_action)
        
        self.effects_panel_action = QAction("Efectos Android", self)
        self.effects_panel_action.setCheckable(True)
        self.effects_panel_action.setChecked(False)
        self.effects_panel_action.triggered.connect(self.toggle_effects_panel)
        panels_menu.addAction(self.effects_panel_action)
        
        self.layers_panel_action = QAction("Panel de Capas", self)
        self.layers_panel_action.setCheckable(True)
        self.layers_panel_action.setChecked(False)
        self.layers_panel_action.triggered.connect(self.toggle_layers_panel)
        panels_menu.addAction(self.layers_panel_action)
        
        self.color_panel_action = QAction("Panel de Colores", self)
        self.color_panel_action.setCheckable(True)
        self.color_panel_action.setChecked(False)
        self.color_panel_action.triggered.connect(self.toggle_color_panel)
        panels_menu.addAction(self.color_panel_action)
        
        self.ai_panel_action = QAction("Panel de IA", self)
        self.ai_panel_action.setCheckable(True)
        self.ai_panel_action.setChecked(False)
        self.ai_panel_action.triggered.connect(self.toggle_ai_panel)
        panels_menu.addAction(self.ai_panel_action)
        
        self.explorer_panel_action = QAction("Explorador de Archivos", self)
        self.explorer_panel_action.setCheckable(True)
        self.explorer_panel_action.setChecked(False)
        self.explorer_panel_action.triggered.connect(self.toggle_explorer_panel)
        panels_menu.addAction(self.explorer_panel_action)
        
        view_menu.addSeparator()

        workspace_menu = view_menu.addMenu("Espacios de Trabajo")
        
        default_workspace = QAction("Por Defecto", self)
        default_workspace.triggered.connect(lambda: self.apply_workspace_preset("Default"))
        workspace_menu.addAction(default_workspace)
        
        minimal_workspace = QAction("Minimo", self)
        minimal_workspace.triggered.connect(lambda: self.apply_workspace_preset("Minimal"))
        workspace_menu.addAction(minimal_workspace)
        
        painting_workspace = QAction("Pintura", self)
        painting_workspace.triggered.connect(lambda: self.apply_workspace_preset("Painting"))
        workspace_menu.addAction(painting_workspace)
        
        typography_workspace = QAction("Tipografia", self)
        typography_workspace.triggered.connect(lambda: self.apply_workspace_preset("Typography"))
        workspace_menu.addAction(typography_workspace)
        
        development_workspace = QAction("Desarrollo", self)
        development_workspace.triggered.connect(lambda: self.apply_workspace_preset("Development"))
        workspace_menu.addAction(development_workspace)
        
        view_menu.addSeparator()

        zoom_in_action = QAction("Acercar", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Alejar", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Zoom 100%", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)

        design_menu = menubar.addMenu("Diseno")

        gen_xml_action = QAction("Generar XML", self)
        gen_xml_action.setShortcut("Ctrl+Shift+X")
        gen_xml_action.triggered.connect(self.generate_xml_code)
        design_menu.addAction(gen_xml_action)
        
        gen_java_action = QAction("Generar Java", self)
        gen_java_action.setShortcut("Ctrl+Shift+J")
        gen_java_action.triggered.connect(self.generate_java_code)
        design_menu.addAction(gen_java_action)
        
        design_menu.addSeparator()

        export_action = QAction("Exportar Proyecto", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_project)
        design_menu.addAction(export_action)

        tools_menu = menubar.addMenu("Herramientas")

        android_designer_action = QAction("Disenador Android", self)
        android_designer_action.triggered.connect(self.open_android_designer)
        tools_menu.addAction(android_designer_action)
        
        tools_menu.addSeparator()

        java_editor_action = QAction("Editor Java", self)
        java_editor_action.triggered.connect(self.open_java_editor)
        tools_menu.addAction(java_editor_action)
        
        xml_editor_action = QAction("Editor XML", self)
        xml_editor_action.triggered.connect(self.open_xml_editor)
        tools_menu.addAction(xml_editor_action)
        
        tools_menu.addSeparator()

        ai_chat_action = QAction("Chat IA", self)
        ai_chat_action.setShortcut("Ctrl+I")
        ai_chat_action.triggered.connect(self.open_ai_chat)
        tools_menu.addAction(ai_chat_action)

        project_explorer_action = QAction("Explorador de Proyectos", self)
        project_explorer_action.triggered.connect(self.open_project_explorer)
        tools_menu.addAction(project_explorer_action)

        window_menu = menubar.addMenu("Ventana")

        cascade_action = QAction("Cascada", self)
        cascade_action.triggered.connect(self.cascade_windows)
        window_menu.addAction(cascade_action)
        
        tile_action = QAction("Mosaico", self)
        tile_action.triggered.connect(self.tile_windows)
        window_menu.addAction(tile_action)
        
        window_menu.addSeparator()
        
        close_all_windows_action = QAction("Cerrar Todas las Ventanas", self)
        close_all_windows_action.triggered.connect(self.close_all_windows)
        window_menu.addAction(close_all_windows_action)

        help_menu = menubar.addMenu("Ayuda")

        docs_action = QAction("Documentacion", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)

        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)


    def new_project(self):
        """Crea un nuevo proyecto"""
        QMessageBox.information(self, "Nuevo Proyecto", "Funcionalidad de nuevo proyecto en desarrollo")

    def open_project(self):
        """Abre un proyecto existente"""
        QMessageBox.information(self, "Abrir Proyecto", "Funcionalidad de abrir proyecto en desarrollo")

    def undo(self):
        """Deshacer acción"""
        if self.current_editor:
            self.current_editor.undo()

    def redo(self):
        """Rehacer acción"""
        if self.current_editor:
            self.current_editor.redo()

    def cut(self):
        """Cortar texto"""
        if self.current_editor:
            self.current_editor.cut()

    def copy(self):
        """Copiar texto"""
        if self.current_editor:
            self.current_editor.copy()

    def paste(self):
        """Pegar texto"""
        if self.current_editor:
            self.current_editor.paste()

    def select_all(self):
        """Seleccionar todo el texto"""
        if self.current_editor:
            self.current_editor.selectAll()

    def find(self):
        """Buscar texto"""
        if self.current_editor:
            self.show_find_dialog(self.current_editor)

    def replace(self):
        """Reemplazar texto"""
        if self.current_editor:
            self.show_replace_dialog(self.current_editor)

    def show_replace_dialog(self, editor):
        """Diálogo de reemplazar"""
        QMessageBox.information(self, "Reemplazar", "Funcionalidad de reemplazar en desarrollo")
    def toggle_illustrator_tools_panel(self):
        """Alternar visibilidad del panel de herramientas Illustrator CORREGIDO"""
        if self.illustrator_tools_panel.isVisible():
            self.illustrator_tools_panel.setVisible(False)
            self.illustrator_tools_action.setChecked(False)
        else:
            self.illustrator_tools_panel.setVisible(True)
            self.illustrator_tools_panel.raise_()
            self.illustrator_tools_panel.activateWindow()
            self.illustrator_tools_action.setChecked(True)

    def toggle_effects_panel(self):
        """Alternar visibilidad del panel de efectos CORREGIDO"""
        if self.effects_panel.isVisible():
            self.effects_panel.setVisible(False)
            self.effects_panel_action.setChecked(False)
        else:
            self.effects_panel.setVisible(True)
            self.effects_panel.raise_()
            self.effects_panel.activateWindow()
            self.effects_panel_action.setChecked(True)

    # Actualizar los presets de workspace para incluir los nuevos paneles
    def create_workspace_presets(self):
        self.workspace_presets = {
            "Default": WorkspacePreset("Default", "left", 
                                    ["IllustratorTools", "Layers", "AI Assistant", "Effects"]),
            "Design": WorkspacePreset("Design", "left", 
                                    ["IllustratorTools", "Effects", "Color", "Layers"]),
            "Development": WorkspacePreset("Development", "right", 
                                        ["IllustratorTools", "AI Assistant", "File Explorer"]),
            "Minimal": WorkspacePreset("Minimal", "left", 
                                    ["File Explorer", "AI Assistant"])
        }
    def toggle_tool_panel(self):
        self.tool_panel.setVisible(self.tool_panel_action.isChecked())

    def toggle_layers_panel(self):
        self.layers_panel.setVisible(self.layers_panel_action.isChecked())

    def toggle_color_panel(self):
        self.color_panel.setVisible(self.color_panel_action.isChecked())

    def toggle_ai_panel(self):
        self.ai_panel.setVisible(self.ai_panel_action.isChecked())

    def toggle_explorer_panel(self):
        self.file_explorer_panel.setVisible(self.explorer_panel_action.isChecked())

    def zoom_in(self):
        """Acercar zoom"""
        self.statusBar().showMessage("Zoom: Acercar")

    def zoom_out(self):
        """Alejar zoom"""
        self.statusBar().showMessage("Zoom: Alejar")

    def reset_zoom(self):
        """Resetear zoom"""
        self.statusBar().showMessage("Zoom: 100%")

    def generate_xml_code(self):
        """Generar código XML"""
        if hasattr(self, 'ai_panel'):
            self.ai_panel.generate_xml()

    def generate_java_code(self):
        """Generar código Java"""
        if hasattr(self, 'ai_panel'):
            self.ai_panel.generate_java()

    def export_project(self):
        """Exportar proyecto"""
        if hasattr(self, 'ai_panel'):
            self.ai_panel.export_project()

    def show_documentation(self):
        """Mostrar documentación"""
        QMessageBox.information(self, "Documentación", "Documentación disponible en desarrollo")

    def show_about(self):
        """Mostrar información acerca de"""
        about_text = """
        <h3>Creators Studio</h3>
        <p>Entorno de desarrollo integrado para diseño Android</p>
        <p>Versión 1.0</p>
        <p>Desarrollado con PySide6 y Python</p>
        <p>© 2024 Creators Studio</p>
        """
        QMessageBox.about(self, "Acerca de Creators Studio", about_text)
    def new_file_with_template(self):
        """Crea un nuevo archivo usando el diálogo de plantillas"""
        current_index = self.file_tree.currentIndex()
        if current_index.isValid():
            current_path = self.file_model.filePath(current_index)
            if os.path.isfile(current_path):
                current_path = os.path.dirname(current_path)
        else:
            current_path = self.project_path

        dialog = NewFileDialog(self.project_language, self, current_path)
        if dialog.exec_() == QDialog.Accepted:
            self.create_file_from_dialog(dialog, current_path)

    def save_file_as(self):
        """Guarda el archivo actual con un nombre diferente"""
        if self.current_editor:
            current_path = None
            for path, tab_data in self.open_files.items():
                if tab_data['editor'] == self.current_editor:
                    current_path = path
                    break
            
            if current_path:
                file_path, ok = QFileDialog.getSaveFileName(
                    self, 
                    "Guardar Como", 
                    current_path, 
                    "Todos los archivos (*)"
                )
                
                if ok and file_path:
                    content = self.current_editor.toPlainText()
                    if self.save_file(file_path, content):
                        self.close_current_tab()
                        self.open_file_in_tab(file_path)

    def save_all_files(self):
        """Guarda todos los archivos abiertos"""
        unsaved_files = []
        
        for file_path, tab_data in self.open_files.items():
            if tab_data['editor'].document().isModified():
                unsaved_files.append(file_path)
        
        if not unsaved_files:
            self.statusBar().showMessage("✅ Todos los archivos están guardados", 2000)
            return
        
        saved_count = 0
        for file_path in unsaved_files:
            tab_data = self.open_files[file_path]
            content = tab_data['editor'].toPlainText()
            if self.save_file(file_path, content):
                saved_count += 1
        
        self.statusBar().showMessage(f"✅ {saved_count} archivos guardados", 3000)

    def close_current_tab(self):
        """Cierra la pestaña actual"""
        current_index = self.tab_widget.currentIndex()
        if current_index > 0:
            self.close_tab(current_index)

    def close_all_tabs(self):
        """Cierra todas las pestañas excepto el emulador"""
        for i in range(self.tab_widget.count() - 1, 0, -1):
            self.close_tab(i)

    def on_file_modified(self, file_path, modified):
        """Maneja el evento de modificación de archivo"""
        if file_path in self.open_files:
            tab_data = self.open_files[file_path]
            index = self.tab_widget.indexOf(tab_data['widget'])
            file_name = os.path.basename(file_path)
            
            if modified:
                self.tab_widget.setTabText(index, f"{file_name} *")
                self.save_action.setEnabled(True)
                self.save_as_action.setEnabled(True)
            else:
                self.tab_widget.setTabText(index, file_name)

                any_modified = any(
                    tab_data['editor'].document().isModified() 
                    for tab_data in self.open_files.values()
                )
                if not any_modified:
                    self.save_action.setEnabled(False)
                    self.save_as_action.setEnabled(False)
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
                "Paragraph": self.paragraph_panel,
                "AI Assistant": self.ai_panel,
                "File Explorer": self.file_explorer_panel
            }
            
            for panel_name, panel in all_panels.items():
                if panel:
                    panel.setVisible(False)

            for panel_name in preset.panels:
                if panel_name in all_panels and all_panels[panel_name]:
                    all_panels[panel_name].setVisible(True)
    def set_tool(self, tool_id):
        self.current_tool = tool_id
        for tid, btn in self.tool_buttons.items():
            btn.setChecked(tid == tool_id)
        
        if self.hoja_ai_canvas:
           self.hoja_ai_canvas.setTool(tool_id)

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
        """Versión corregida para abrir archivos - con soporte para XML"""
        if file_path in self.open_files:
            tab_data = self.open_files[file_path]
            index = self.tab_widget.indexOf(tab_data['widget'])
            self.tab_widget.setCurrentIndex(index)
            return
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            tab_widget.setLayout(layout)

            file_name = os.path.basename(file_path)
            tab_index = self.tab_widget.addTab(tab_widget, file_name)
            self.tab_widget.setCurrentIndex(tab_index)
            self.tab_widget.setTabToolTip(tab_index, file_path)
            
            self.open_files[file_path] = {
                'widget': tab_widget,
                'editor': text_edit if not file_path.lower().endswith('.xml') else None,
                'file_path': file_path,
                'is_modified': False,
                'is_xml': file_path.lower().endswith('.xml')
            }
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")
 
    def show_enhanced_context_menu(self, editor, pos):
        """Menú contextual mejorado con opciones de editor"""
        menu = QMenu(self)
        
        # Acciones de edición
        actions = [
            ("📝 Deshacer", "Ctrl+Z", editor.undo, editor.document().isUndoAvailable()),
            ("🔁 Rehacer", "Ctrl+Y", editor.redo, editor.document().isRedoAvailable()),
            ("---", None, None, False),
            ("✂️ Cortar", "Ctrl+X", editor.cut, editor.textCursor().hasSelection()),
            ("📋 Copiar", "Ctrl+C", editor.copy, editor.textCursor().hasSelection()),
            ("📄 Pegar", "Ctrl+V", editor.paste, True),
            ("---", None, None, False),
            ("🔍 Buscar...", "Ctrl+F", lambda: self.show_find_dialog(editor), True),
            ("🔄 Reemplazar...", "Ctrl+H", lambda: self.show_replace_dialog(editor), True),
            ("---", None, None, False),
            ("⭐ Seleccionar todo", "Ctrl+A", editor.selectAll, True),
            ("🎨 Formatear código", "Ctrl+Shift+F", lambda: self.format_code(editor), True),
        ]
        
        for text, shortcut, action, enabled in actions:
            if text == "---":
                menu.addSeparator()
            else:
                action_obj = QAction(text, self)
                if shortcut:
                    action_obj.setShortcut(shortcut)
                if action:
                    action_obj.triggered.connect(action)
                action_obj.setEnabled(enabled)
                menu.addAction(action_obj)
        
        menu.exec_(editor.mapToGlobal(pos))

    def show_find_dialog(self, editor):
        """Diálogo de búsqueda mejorado"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 Buscar")
        dialog.setFixedSize(400, 150)
        
        layout = QVBoxLayout(dialog)
        
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Texto a buscar:"))
        find_input = QLineEdit()
        find_input.setPlaceholderText("Ingrese texto para buscar...")
        find_layout.addWidget(find_input)
        layout.addLayout(find_layout)
        
        options_layout = QHBoxLayout()
        case_sensitive = QCheckBox("Coincidir mayúsculas/minúsculas")
        whole_word = QCheckBox("Palabra completa")
        options_layout.addWidget(case_sensitive)
        options_layout.addWidget(whole_word)
        layout.addLayout(options_layout)

        button_layout = QHBoxLayout()
        find_next_btn = QPushButton("Buscar siguiente")
        find_prev_btn = QPushButton("Buscar anterior")
        close_btn = QPushButton("Cerrar")
        
        find_next_btn.clicked.connect(lambda: self.find_text(editor, find_input.text(), 
                                                        case_sensitive.isChecked(),
                                                        whole_word.isChecked(), True))
        find_prev_btn.clicked.connect(lambda: self.find_text(editor, find_input.text(),
                                                        case_sensitive.isChecked(),
                                                        whole_word.isChecked(), False))
        close_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(find_next_btn)
        button_layout.addWidget(find_prev_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def find_text(self, editor, text, case_sensitive, whole_word, forward=True):
        """Buscar texto en el editor"""
        if not text:
            return
        
        cursor = editor.textCursor()
        document = editor.document()
        
        flags = QTextDocument.FindFlag(0)
        if not forward:
            flags = QTextDocument.FindBackward
        if whole_word:
            flags |= QTextDocument.FindWholeWords
        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively
        
        cursor = document.find(text, cursor, flags)
        
        if not cursor.isNull():
            editor.setTextCursor(cursor)
        else:
            QMessageBox.information(self, "Búsqueda", "Texto no encontrado")

    def format_code(self, editor):
        """Formatear código básico (indentación)"""
        cursor = editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            lines = text.split('\n')
            formatted_lines = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.endswith('}'):
                    indent_level = max(0, indent_level - 1)
                
                formatted_lines.append('    ' * indent_level + stripped)
                
                if stripped.endswith('{'):
                    indent_level += 1
            
            formatted_text = '\n'.join(formatted_lines)
            cursor.insertText(formatted_text)
        else:
            QMessageBox.information(self, "Formatear", "Seleccione texto para formatear")

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

 
