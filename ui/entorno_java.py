import os
import subprocess
import platform
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
    QPlainTextEdit, QListWidgetItem, QStyledItemDelegate 
)


from PySide6.QtGui import (
    QIcon, QAction, QCursor, QColor, QBrush, QTextCursor, QFont,
    QPen, QPainter, QTextFormat, QSyntaxHighlighter, QTextCharFormat, QPalette,
    QShortcut, QKeySequence, 
)
from PySide6.QtCore import (
    Qt, QSize, QPoint, Signal, QDir, QRectF, QSettings, QThread, 
    Signal as pyqtSignal, QEvent, QTimer, QRect, QRegularExpression, QDateTime
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
    """Panel de IA mejorado con acceso total al sistema de archivos y ejecución de código"""
    
    def __init__(self, code_generator, parent=None):
        super().__init__("AI Assistant - Programación Total", parent)
        self.code_generator = code_generator
        self.parent_window = parent
        self.conversation_history = []
        self.current_provider = None
        self.available_providers = []
        self.current_worker = None
        self.project_path = getattr(parent, 'project_path', os.getcwd())
        self.setupUI()
        self.load_api_keys()
        self.detect_available_providers()

    def setupUI(self):
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        
        # Panel de proveedores
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
        
        # Historial de chat mejorado
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Conversa con la IA sobre programación, archivos, ejecución de código...")
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
        
        # Panel de entrada mejorado
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Escribe tu mensaje, pide crear/modificar archivos, ejecutar código...")
        self.user_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.user_input)
        
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        # Botones de acciones rápidas
        quick_actions_layout = QHBoxLayout()
        
        self.file_actions_btn = QPushButton("📁 Archivos")
        self.file_actions_btn.clicked.connect(self.show_file_actions_menu)
        
        self.code_actions_btn = QPushButton("⚡ Ejecutar")
        self.code_actions_btn.clicked.connect(self.show_code_actions_menu)
        
        self.project_actions_btn = QPushButton("📦 Proyecto")
        self.project_actions_btn.clicked.connect(self.show_project_actions_menu)
        
        quick_actions_layout.addWidget(self.file_actions_btn)
        quick_actions_layout.addWidget(self.code_actions_btn)
        quick_actions_layout.addWidget(self.project_actions_btn)
        quick_actions_layout.addStretch()
        
        layout.addLayout(input_layout)
        layout.addLayout(quick_actions_layout)
        
        chat_widget.setLayout(layout)
        self.setWidget(chat_widget)
        
        # Mensaje de bienvenida mejorado
        self.add_system_message("🚀 **Asistente de Programación Total Iniciado**")
        self.add_system_message("**Capacidades disponibles:**")
        self.add_system_message("• 📁 Gestión completa de archivos (crear, modificar, eliminar)")
        self.add_system_message("• ⚡ Ejecución de código (Java, Kotlin, Python, etc.)")
        self.add_system_message("• 🔍 Análisis y búsqueda en proyectos")
        self.add_system_message("• 📊 Generación de código inteligente")
        self.add_system_message("• 🛠️ Debugging y optimización")
    
    def change_ai_provider(self, provider_name):
        """Cambia el proveedor de IA seleccionado"""
        self.current_provider = provider_name

    def show_api_config_dialog(self):
        """Muestra el diálogo de configuración de API (pendiente de implementar)"""
        QMessageBox.information(self, "Configurar API", "Funcionalidad de configuración de API en desarrollo.")    
    
    def show_file_actions_menu(self):
        """Menú de acciones rápidas para archivos"""
        menu = QMenu(self)
        
        actions = [
            ("📄 Crear Archivo", self.quick_create_file),
            ("📁 Crear Carpeta", self.quick_create_folder),
            ("🔍 Listar Archivos", self.list_project_files),
            ("📊 Analizar Proyecto", self.analyze_project),
            ("📝 Editar Archivo", self.quick_edit_file),
            ("🗑️ Eliminar Archivo", self.quick_delete_file),
        ]
        
        for text, action in actions:
            act = QAction(text, self)
            act.triggered.connect(action)
            menu.addAction(act)
        
        menu.exec_(self.file_actions_btn.mapToGlobal(QPoint(0, self.file_actions_btn.height())))

    def show_code_actions_menu(self):
        """Menú de acciones rápidas para código"""
        menu = QMenu(self)
        
        actions = [
            ("▶️ Ejecutar Proyecto", self.run_project),
            ("🔨 Compilar", self.compile_project),
            ("🐛 Debug", self.debug_project),
            ("📋 Analizar Sintaxis", self.check_syntax),
            ("⚡ Ejecutar Snippet", self.run_code_snippet),
        ]
        
        for text, action in actions:
            act = QAction(text, self)
            act.triggered.connect(action)
            menu.addAction(act)
        
        menu.exec_(self.code_actions_btn.mapToGlobal(QPoint(0, self.code_actions_btn.height())))

    def show_project_actions_menu(self):
        """Menú de acciones rápidas para proyectos"""
        menu = QMenu(self)
        
        actions = [
            ("📊 Estadísticas", self.project_stats),
            ("🔍 Buscar en Código", self.search_in_code),
            ("📋 Dependencias", self.show_dependencies),
            ("🔄 Refactorizar", self.refactor_project),
            ("📦 Exportar", self.export_project_quick),
        ]
        
        for text, action in actions:
            act = QAction(text, self)
            act.triggered.connect(action)
            menu.addAction(act)
        
        menu.exec_(self.project_actions_btn.mapToGlobal(QPoint(0, self.project_actions_btn.height())))

    # ===== FUNCIONES DE GESTIÓN DE ARCHIVOS =====
    
    def list_project_files(self):
        """Lista todos los archivos del proyecto"""
        try:
            files_info = []
            for root, dirs, files in os.walk(self.project_path):
                level = root.replace(self.project_path, '').count(os.sep)
                indent = ' ' * 2 * level
                files_info.append(f"{indent}📁 {os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    size = os.path.getsize(os.path.join(root, file))
                    files_info.append(f"{subindent}📄 {file} ({size} bytes)")
            
            file_tree = "\n".join(files_info[:50])  # Limitar a 50 elementos
            self.add_system_message(f"**Estructura del proyecto:**\n```\n{file_tree}\n```")
            
            # Estadísticas
            total_files = sum([len(files) for r, d, files in os.walk(self.project_path)])
            total_size = sum([os.path.getsize(os.path.join(r, f)) 
                            for r, d, files in os.walk(self.project_path) 
                            for f in files])
            
            self.add_system_message(f"**Estadísticas:** {total_files} archivos, {total_size} bytes totales")
            
        except Exception as e:
            self.add_error_message(f"Error al listar archivos: {str(e)}")

    def quick_create_file(self):
        """Crea un archivo rápidamente"""
        file_name, ok = QInputDialog.getText(self, "Crear Archivo", "Nombre del archivo:")
        if ok and file_name:
            file_path = os.path.join(self.project_path, file_name)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.add_success_message(f"✅ Archivo '{file_name}' creado exitosamente")
                
                # Abrir el archivo en el editor si está disponible
                if hasattr(self.parent_window, 'open_file_in_tab'):
                    self.parent_window.open_file_in_tab(file_path)
                    
            except Exception as e:
                self.add_error_message(f"❌ Error al crear archivo: {str(e)}")

    def quick_create_folder(self):
        """Crea una carpeta rápidamente"""
        folder_name, ok = QInputDialog.getText(self, "Crear Carpeta", "Nombre de la carpeta:")
        if ok and folder_name:
            folder_path = os.path.join(self.project_path, folder_name)
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.add_success_message(f"✅ Carpeta '{folder_name}' creada exitosamente")
            except Exception as e:
                self.add_error_message(f"❌ Error al crear carpeta: {str(e)}")

    def quick_edit_file(self):
        """Edita un archivo existente"""
        files = []
        for root, dirs, filenames in os.walk(self.project_path):
            for file in filenames:
                files.append(os.path.join(root, file))
        
        if not files:
            self.add_warning_message("No hay archivos en el proyecto")
            return
            
        file_path, ok = QInputDialog.getItem(self, "Editar Archivo", "Selecciona un archivo:", 
                                           files, 0, False)
        if ok and file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Mostrar diálogo de edición
                self.show_file_editor(file_path, content)
                
            except Exception as e:
                self.add_error_message(f"❌ Error al leer archivo: {str(e)}")

    def show_file_editor(self, file_path, content):
        """Muestra un editor para modificar archivos"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editando: {os.path.basename(file_path)}")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Editor de código
        editor = QPlainTextEdit()
        editor.setPlainText(content)
        editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(editor)
        
        # Botones
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Guardar")
        save_btn.clicked.connect(lambda: self.save_edited_file(file_path, editor.toPlainText(), dialog))
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def save_edited_file(self, file_path, content, dialog):
        """Guarda el archivo editado"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.add_success_message(f"✅ Archivo '{os.path.basename(file_path)}' guardado exitosamente")
            dialog.accept()
            
            # Actualizar en el editor principal si está abierto
            if hasattr(self.parent_window, 'open_files'):
                for path, tab_data in self.parent_window.open_files.items():
                    if path == file_path and tab_data['editor']:
                        tab_data['editor'].setPlainText(content)
                        tab_data['editor'].document().setModified(False)
                        
        except Exception as e:
            self.add_error_message(f"❌ Error al guardar archivo: {str(e)}")

    # ===== FUNCIONES DE EJECUCIÓN DE CÓDIGO =====
    def quick_delete_file(self):
        """Elimina un archivo rápidamente"""
        files = []
        for root, dirs, filenames in os.walk(self.project_path):
            for file in filenames:
                files.append(os.path.join(root, file))
        if not files:
            self.add_warning_message("No hay archivos en el proyecto")
            return
        file_path, ok = QInputDialog.getItem(self, "Eliminar Archivo", "Selecciona un archivo:", files, 0, False)
        if ok and file_path:
            try:
                os.remove(file_path)
                self.add_success_message(f"✅ Archivo '{os.path.basename(file_path)}' eliminado exitosamente")
            except Exception as e:
                self.add_error_message(f"❌ Error al eliminar archivo: {str(e)}")
    def run_project(self):
        """Ejecuta el proyecto actual"""
        project_language = getattr(self.parent_window, 'project_language', 'Java').lower()
        
        try:
            if project_language == 'java':
                self.run_java_project()
            elif project_language == 'kotlin':
                self.run_kotlin_project()
            elif project_language == 'python':
                self.run_python_project()
            else:
                self.add_warning_message(f"Ejecución para {project_language} no implementada")
                
        except Exception as e:
            self.add_error_message(f"❌ Error al ejecutar proyecto: {str(e)}")

    def run_java_project(self):
        """Ejecuta proyecto Java"""
        # Buscar archivo principal
        main_files = []
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.java'):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'public static void main' in content:
                            main_files.append(os.path.join(root, file))
        
        if not main_files:
            self.add_error_message("❌ No se encontró archivo principal con main()")
            return
        
        if len(main_files) > 1:
            file_path, ok = QInputDialog.getItem(self, "Seleccionar Archivo Principal", 
                                               "Múltiples archivos main encontrados:", main_files, 0, False)
            if not ok:
                return
        else:
            file_path = main_files[0]
        
        # Compilar y ejecutar
        try:
            self.add_system_message("🔨 Compilando proyecto Java...")
            
            # Compilar
            compile_process = subprocess.run(['javac', file_path], 
                                          cwd=os.path.dirname(file_path),
                                          capture_output=True, text=True)
            
            if compile_process.returncode != 0:
                self.add_error_message(f"❌ Error de compilación:\n```\n{compile_process.stderr}\n```")
                return
            
            # Ejecutar
            class_name = os.path.basename(file_path).replace('.java', '')
            self.add_system_message("▶️ Ejecutando...")
            
            run_process = subprocess.run(['java', class_name], 
                                      cwd=os.path.dirname(file_path),
                                      capture_output=True, text=True)
            
            output = f"**Salida:**\n```\n{run_process.stdout}\n```"
            if run_process.stderr:
                output += f"\n**Errores:**\n```\n{run_process.stderr}\n```"
            
            self.add_system_message(output)
            
        except Exception as e:
            self.add_error_message(f"❌ Error en ejecución: {str(e)}")

    def run_python_project(self):
        """Ejecuta proyecto Python"""
        main_files = []
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    main_files.append(os.path.join(root, file))
        
        if not main_files:
            self.add_error_message("❌ No se encontraron archivos .py")
            return
        
        if len(main_files) > 1:
            file_path, ok = QInputDialog.getItem(self, "Seleccionar Archivo", 
                                               "Selecciona archivo Python:", main_files, 0, False)
            if not ok:
                return
        else:
            file_path = main_files[0]
        
        try:
            self.add_system_message(f"▶️ Ejecutando {os.path.basename(file_path)}...")
            
            process = subprocess.run(['python', file_path], 
                                  cwd=self.project_path,
                                  capture_output=True, text=True)
            
            output = f"**Salida:**\n```\n{process.stdout}\n```"
            if process.stderr:
                output += f"\n**Errores:**\n```\n{process.stderr}\n```"
            
            self.add_system_message(output)
            
        except Exception as e:
            self.add_error_message(f"❌ Error en ejecución: {str(e)}")
    def run_kotlin_project(self):
        """Ejecuta proyecto Kotlin (pendiente de implementar)"""
        self.add_warning_message("Ejecución de proyectos Kotlin no implementada aún.")

    def compile_project(self):
        """Compila el proyecto actual (solo Java/Kotlin)"""
        project_language = getattr(self.parent_window, 'project_language', 'Java').lower()
        try:
            if project_language == 'java':
                self.add_system_message("🔨 Compilando proyecto Java...")
                # Implementa compilación aquí si lo deseas
            elif project_language == 'kotlin':
                self.add_system_message("🔨 Compilando proyecto Kotlin...")
                # Implementa compilación aquí si lo deseas
            else:
                self.add_warning_message(f"Compilación para {project_language} no implementada")
        except Exception as e:
            self.add_error_message(f"❌ Error al compilar proyecto: {str(e)}")

    def debug_project(self):
        """Debug del proyecto (pendiente de implementar)"""
        self.add_warning_message("Funcionalidad de debug no implementada aún.")

    def check_syntax(self):
        """Analiza la sintaxis del proyecto (pendiente de implementar)"""
        self.add_warning_message("Análisis de sintaxis no implementado aún.")

    def run_code_snippet(self):
        """Ejecuta un snippet de código (pendiente de implementar)"""
        self.add_warning_message("Ejecución de snippets no implementada aún.")

    def project_stats(self):
        """Muestra estadísticas del proyecto"""
        self.analyze_project()

    def show_dependencies(self):
        """Muestra dependencias del proyecto (pendiente de implementar)"""
        self.add_warning_message("Visualización de dependencias no implementada aún.")

    def refactor_project(self):
        """Refactoriza el proyecto (pendiente de implementar)"""
        self.add_warning_message("Refactorización no implementada aún.")

    def export_project_quick(self):
        """Exporta el proyecto rápidamente"""
        if hasattr(self.parent_window, "export_project"):
            self.parent_window.export_project()
        else:
            self.add_warning_message("Exportación rápida no disponible.")
    # ===== FUNCIONES DE ANÁLISIS =====
    
    def analyze_project(self):
        """Analiza el proyecto y muestra estadísticas"""
        try:
            stats = {
                'total_files': 0,
                'total_size': 0,
                'by_extension': {},
                'largest_files': []
            }
            
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    stats['total_files'] += 1
                    
                    # Tamaño
                    size = os.path.getsize(file_path)
                    stats['total_size'] += size
                    
                    # Extensión
                    ext = os.path.splitext(file)[1].lower() or 'sin extensión'
                    stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
                    
                    # Archivos más grandes
                    stats['largest_files'].append((file_path, size))
            
            # Ordenar archivos por tamaño
            stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
            
            # Generar reporte
            report = f"**📊 Análisis del Proyecto**\n\n"
            report += f"• **Archivos totales:** {stats['total_files']}\n"
            report += f"• **Tamaño total:** {stats['total_size'] / 1024:.2f} KB\n\n"
            
            report += "**📁 Por extensión:**\n"
            for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True):
                report += f"• `{ext}`: {count} archivos\n"
            
            report += f"\n**🏆 Archivos más grandes:**\n"
            for file_path, size in stats['largest_files'][:5]:
                name = os.path.basename(file_path)
                report += f"• `{name}`: {size / 1024:.2f} KB\n"
            
            self.add_system_message(report)
            
        except Exception as e:
            self.add_error_message(f"❌ Error en análisis: {str(e)}")

    # ===== FUNCIONES DE BÚSQUEDA =====
    
    def search_in_code(self):
        """Busca texto en todos los archivos del proyecto"""
        search_text, ok = QInputDialog.getText(self, "Buscar en Código", "Texto a buscar:")
        if ok and search_text:
            try:
                results = []
                for root, dirs, files in os.walk(self.project_path):
                    for file in files:
                        if file.endswith(('.java', '.kt', '.py', '.xml', '.txt', '.md')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    if search_text in content:
                                        # Contar ocurrencias
                                        count = content.count(search_text)
                                        results.append((file_path, count))
                            except:
                                continue
                
                if results:
                    result_text = f"**🔍 Resultados para '{search_text}':**\n\n"
                    for file_path, count in sorted(results, key=lambda x: x[1], reverse=True):
                        rel_path = os.path.relpath(file_path, self.project_path)
                        result_text += f"• `{rel_path}`: {count} ocurrencias\n"
                    
                    self.add_system_message(result_text)
                else:
                    self.add_warning_message(f"❌ No se encontró '{search_text}' en el proyecto")
                    
            except Exception as e:
                self.add_error_message(f"❌ Error en búsqueda: {str(e)}")
    def search_in_code_specific(self, search_text):
        """Busca texto específico en todos los archivos del proyecto"""
        try:
            results = []
            for root, dirs, files in os.walk(self.project_path):
                for file in files:
                    if file.endswith(('.java', '.kt', '.py', '.xml', '.txt', '.md')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if search_text in content:
                                    count = content.count(search_text)
                                    results.append((file_path, count))
                        except:
                            continue
            if results:
                result_text = f"**🔍 Resultados para '{search_text}':**\n\n"
                for file_path, count in sorted(results, key=lambda x: x[1], reverse=True):
                    rel_path = os.path.relpath(file_path, self.project_path)
                    result_text += f"• `{rel_path}`: {count} ocurrencias\n"
                self.add_system_message(result_text)
            else:
                self.add_warning_message(f"❌ No se encontró '{search_text}' en el proyecto")
        except Exception as e:
            self.add_error_message(f"❌ Error en búsqueda: {str(e)}")

    # ===== FUNCIONES MEJORADAS DE MENSAJES =====
    
    def add_system_message(self, message):
        """Añade un mensaje del sistema formateado"""
        self._add_formatted_message("🤖 **Sistema**", message, "#2d2d30")

    def add_success_message(self, message):
        """Añade un mensaje de éxito"""
        self._add_formatted_message("✅ **Éxito**", message, "#4CAF50")

    def add_warning_message(self, message):
        """Añade un mensaje de advertencia"""
        self._add_formatted_message("⚠️ **Advertencia**", message, "#FF9800")

    def add_error_message(self, message):
        """Añade un mensaje de error"""
        self._add_formatted_message("❌ **Error**", message, "#F44336")

    def add_code_message(self, message, language=""):
        """Añade un mensaje con código formateado"""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Encabezado del mensaje
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        cursor.insertHtml(f'''
            <div style="background-color: #1e1e1e; padding: 10px; margin: 5px; border-radius: 8px; border-left: 4px solid #569CD6;">
                <div style="color: #569CD6; font-weight: bold;">💻 **Código** <span style="color: #666; font-size: 0.8em;">[{timestamp}]</span></div>
        ''')
        
        # Código con botón de copiar
        code_id = f"code_{hash(message) % 10000}"
        cursor.insertHtml(f'''
            <div style="position: relative;">
                <pre style="background-color: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 5px; overflow-x: auto; margin: 10px 0; border: 1px solid #3e3e42;">
{message}
                </pre>
                <button id="{code_id}" onclick="copyCode('{code_id}')" style="position: absolute; top: 5px; right: 5px; background: #569CD6; color: white; border: none; border-radius: 3px; padding: 2px 8px; font-size: 10px; cursor: pointer;">
                    📋 Copiar
                </button>
            </div>
        ''')
        
        cursor.insertHtml('</div><br>')
        self.chat_history.ensureCursorVisible()

    def _add_formatted_message(self, sender, message, color):
        """Añade un mensaje formateado"""
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        
        # Detectar si el mensaje contiene código
        if '```' in message:
            parts = message.split('```')
            formatted_message = ""
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Parte de código
                    formatted_message += f'<pre style="background-color: #1e1e1e; color: #d4d4d4; padding: 10px; border-radius: 5px; overflow-x: auto; margin: 5px 0;">{part}</pre>'
                else:
                    formatted_message += part.replace('\n', '<br>')
            message = formatted_message
        else:
            message = message.replace('\n', '<br>')
        
        cursor.insertHtml(f'''
            <div style="background-color: {color}; padding: 10px; margin: 5px; border-radius: 8px; border-left: 4px solid {color};">
                <div style="color: white; font-weight: bold;">{sender} <span style="color: #ccc; font-size: 0.8em;">[{timestamp}]</span></div>
                <div style="color: white; margin-top: 5px;">{message}</div>
            </div>
        ''')
        
        cursor.insertHtml('<br>')
        self.chat_history.ensureCursorVisible()


    def send_message(self):
        """Envía un mensaje con procesamiento de comandos especiales"""
        user_text = self.user_input.text().strip()
        if not user_text:
            return
            
        self._add_formatted_message("👤 **Tú**", user_text, "#1976D2")  # <-- CORREGIDO
        self.user_input.clear()
        
        # Procesar comandos especiales
        if user_text.startswith('/'):
            self.process_command(user_text)
        else:
            # Procesamiento normal con IA
            self.process_with_ai(user_text)
    # ...existing code...

    def process_command(self, command):
        """Procesa comandos especiales"""
        cmd = command.lower().strip()
        
        if cmd == '/archivos' or cmd == '/files':
            self.list_project_files()
        elif cmd == '/estadisticas' or cmd == '/stats':
            self.analyze_project()
        elif cmd == '/ejecutar' or cmd == '/run':
            self.run_project()
        elif cmd == '/buscar' or cmd.startswith('/buscar '):
            search_text = command[7:].strip()
            if search_text:
                self.search_in_code_specific(search_text)
            else:
                self.search_in_code()
        elif cmd == '/help' or cmd == '/ayuda':
            self.show_help()
        elif cmd.startswith('/crear_carpeta '):
            folder_name = command[15:].strip()
            self.create_specific_folder(folder_name)
        elif cmd.startswith('/crear_archivo '):
            file_path = command[15:].strip()
            self.create_specific_file(file_path)

        else:
            self.add_warning_message(f"Comando no reconocido: {command}")
    def create_specific_folder(self, folder_name):
        """Crea una carpeta específica"""
        try:
            folder_path = os.path.join(self.project_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            self.add_success_message(f"✅ Carpeta '{folder_name}' creada/verificada")
            if hasattr(self.parent_window, 'update_file_explorer'):
                self.parent_window.update_file_explorer()
        except Exception as e:
            self.add_error_message(f"❌ Error: {str(e)}")

    def create_specific_file(self, file_path):
        """Crea un archivo específico con contenido básico"""
        try:
            full_path = os.path.join(self.project_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Contenido según extensión
            if file_path.endswith('.py'):
                content = '# Archivo Python\nprint("Hola Mundo")'
            elif file_path.endswith('.java'):
                content = '// Archivo Java\npublic class Test {\n    public static void main(String[] args) {\n        System.out.println("Hola Mundo");\n    }\n}'
            elif file_path.endswith('.kt'):
                content = '// Archivo Kotlin\nfun main() {\n    println("Hola Mundo")\n}'
            else:
                content = f'// Archivo {file_path}'
                
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.add_success_message(f"✅ Archivo '{file_path}' creado")
            
        except Exception as e:
            self.add_error_message(f"❌ Error: {str(e)}")
    def show_help(self):
        """Muestra ayuda de comandos"""
        help_text = """
        **🛠️ Comandos Disponibles:**

        **📁 Archivos:**
        • `/archivos` - Lista la estructura del proyecto
        • `/estadisticas` - Muestra estadísticas del proyecto
        • `/buscar [texto]` - Busca texto en los archivos

        **⚡ Ejecución:**
        • `/ejecutar` - Ejecuta el proyecto actual
        • `/compilar` - Compila el proyecto

        **🔧 Utilidades:**
        • `/help` - Muestra esta ayuda

        **💬 IA:**
        • Escribe normalmente para conversar con la IA
        • Pide crear, modificar o analizar archivos
                """
        self.add_system_message(help_text)

    # Mantener las funciones existentes de IA pero mejorarlas
    def process_with_ai(self, user_text):
        """Procesa el mensaje con IA"""
        # Aquí integrarías con DeepSeek/StarCoder como antes
        # Pero ahora con más contexto del proyecto
        
        # Por ahora, respuesta local mejorada
        self.enhanced_local_response(user_text)
    def process_advanced_command(self, command):
        """Procesa comandos avanzados de creación de archivos y carpetas"""
        lower_cmd = command.lower()
        
        # Detectar patrones de creación múltiple
        if any(word in lower_cmd for word in ['crea estos', 'crear varios', 'multiple archivos']):
            self.handle_multiple_file_creation(command)
        elif 'crear carpeta' in lower_cmd or 'crea la carpeta' in lower_cmd:
            self.handle_folder_creation(command)
        else:
            self.enhanced_local_response(command)

    def handle_multiple_file_creation(self, command):
        """Maneja la creación de múltiples archivos"""
        try:
            # Extraer nombres y tipos de archivo del comando
            if 'prueba_process' in command:
                base_name = 'prueba_process'
                extensions = ['.py', '.java', '.kt']
                folder_name = 'Logica'
                
                # Crear carpeta si no existe
                folder_path = os.path.join(self.project_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                # Crear archivos
                created_files = []
                for ext in extensions:
                    file_path = os.path.join(folder_path, f"{base_name}{ext}")
                    
                    # Contenido básico según extensión
                    if ext == '.py':
                        content = f'# Archivo {base_name}{ext}\nprint("Hola desde Python")'
                    elif ext == '.java':
                        content = f'// Archivo {base_name}{ext}\npublic class {base_name} {{\n    public static void main(String[] args) {{\n        System.out.println("Hola desde Java");\n    }}\n}}'
                    elif ext == '.kt':
                        content = f'// Archivo {base_name}{ext}\nclass {base_name} {{\n    fun main() {{\n        println("Hola desde Kotlin")\n    }}\n}}'
                    else:
                        content = f'// Archivo {base_name}{ext}'
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created_files.append(f"{base_name}{ext}")
                
                self.add_success_message(f"✅ Carpeta '{folder_name}' y archivos creados exitosamente:")
                for file in created_files:
                    self.add_system_message(f"• 📄 {file}")
                    
                # Actualizar explorador
                if hasattr(self.parent_window, 'update_file_explorer'):
                    self.parent_window.update_file_explorer()
                    
            else:
                self.add_warning_message("No se pudo procesar el comando de creación múltiple")
                
        except Exception as e:
            self.add_error_message(f"❌ Error al crear archivos múltiples: {str(e)}")

    def handle_folder_creation(self, command):
        """Maneja la creación de carpetas específicas"""
        try:
            # Extraer nombre de carpeta del comando
            if 'logica' in command.lower():
                folder_name = 'Logica'
                folder_path = os.path.join(self.project_path, folder_name)
                
                os.makedirs(folder_path, exist_ok=True)
                self.add_success_message(f"✅ Carpeta '{folder_name}' creada/verificada exitosamente")
                
                # Actualizar explorador
                if hasattr(self.parent_window, 'update_file_explorer'):
                    self.parent_window.update_file_explorer()
                    
        except Exception as e:
            self.add_error_message(f"❌ Error al crear carpeta: {str(e)}")
    def enhanced_local_response(self, user_text):
        """Respuesta local mejorada con conocimiento del proyecto"""
        lower_msg = user_text.lower()
        
        # Comandos avanzados primero
        if any(word in lower_msg for word in ['crea estos', 'crear varios', 'multiple archivos', 'crear carpeta']):
            self.process_advanced_command(user_text)
        # Detectar intenciones relacionadas con archivos (mantener existentes)
        elif any(word in lower_msg for word in ['crear archivo', 'nuevo archivo', 'new file']):
            self.quick_create_file()
        elif any(word in lower_msg for word in ['listar archivos', 'ver archivos', 'ls']):
            self.list_project_files()
        # ... resto de comandos existentes

    def generate_enhanced_response(self, user_text):
        """Genera una respuesta mejorada basada en el contexto del proyecto"""
        # Aquí podrías integrar más inteligencia contextual
        return f"He procesado tu solicitud: '{user_text}'. Puedo ayudarte con gestión de archivos, ejecución de código, análisis de proyectos y más. Usa los botones de acción rápida o escribe comandos como '/help'."

    def add_ai_response(self, response):
        """Añade respuesta de IA formateada"""
        self._add_formatted_message("🤖 **IA**", response, "#388E3C")

    # Añadir esta función auxiliar para copiar código
    def add_copy_functionality(chat_history):
        """Añade funcionalidad JavaScript para copiar código"""
        js_code = """
        <script>
        function copyCode(elementId) {
            var codeElement = document.getElementById(elementId).previousElementSibling;
            var textArea = document.createElement("textarea");
            textArea.value = codeElement.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("copy");
            document.body.removeChild(textArea);
            
            var button = document.getElementById(elementId);
            button.textContent = "✅ Copiado";
            setTimeout(function() {
                button.textContent = "📋 Copiar";
            }, 2000);
        }
        </script>
        """
        # Esto sería más efectivo en una aplicación web, pero para Qt necesitamos un enfoque diferente
        pass
    def load_api_keys(self):
        """Carga las API keys de los proveedores de IA"""
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.starcoder_api_key = os.getenv("HUGGINGFACE_API_KEY", "")

    def detect_available_providers(self):
        """Detecta proveedores de IA disponibles y actualiza el combo"""
        self.available_providers = AIProvider.get_available_providers()
        self.provider_combo.clear()
        for provider in self.available_providers:
            self.provider_combo.addItem(provider)
        if self.available_providers:
            self.current_provider = self.available_providers[0]
            self.provider_combo.setCurrentText(self.current_provider)

    def generate_xml(self):
        """Genera código XML del proyecto (pendiente de implementar)"""
        self.add_system_message("Funcionalidad de generación XML en desarrollo.")

    def generate_java(self):
        """Genera código Java del proyecto (pendiente de implementar)"""
        self.add_system_message("Funcionalidad de generación Java en desarrollo.")

    def export_project(self):
        """Exporta el proyecto (pendiente de implementar)"""
        self.add_system_message("Funcionalidad de exportación en desarrollo.")
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
        self.open_windowa = {}
        self.current_editor = None
        
      
        self.current_tool = "select"
        self.current_color = "#FFFFFF"
        self.tool_buttons = {}
        
        self.setup_workspace()
        self.create_workspace_presets()
        self.setup_ui()
        self.setup_shortcuts()

        self.setup_enhanced_docks()

        self.create_menu_bar()
        self.setup_language_specific_features()
        self.setup_context_menu()

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
        
        self.tool_panel_action = QAction("Panel de Herramientas", self)
        self.tool_panel_action.setCheckable(True)
        self.tool_panel_action.setChecked(False)
        self.tool_panel_action.triggered.connect(self.toggle_tool_panel)
        panels_menu.addAction(self.tool_panel_action)
        
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

            if file_path.lower().endswith('.xml'):
                self.show_xml_designer(tab_widget, content, file_path)
            else:
                text_edit = EnhancedCodeEditor(theme="dark")
                text_edit.setPlainText(content)
                text_edit.set_highlighter(file_path)
                layout.addWidget(text_edit)
            
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
 
    def show_xml_designer(self, parent_widget, xml_content, file_path):
        """Muestra el diseñador para archivos XML"""
        layout = parent_widget.layout()

        splitter = QSplitter(Qt.Horizontal)

        xml_editor = EnhancedCodeEditor(theme="dark")
        xml_editor.setPlainText(xml_content)
        xml_editor.set_highlighter(file_path)

        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        preview_label = QLabel("Vista previa del layout XML\n(Emulador Android)")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setStyleSheet("font-size: 14px; color: #666; padding: 50px; background-color: #2C2C2C; color: white;")
        preview_layout.addWidget(preview_label)
        
        splitter.addWidget(xml_editor)
        splitter.addWidget(preview_widget)
        splitter.setSizes([400, 400]) 
        
        layout.addWidget(splitter)

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

 
