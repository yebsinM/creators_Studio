from .common_imports import *
from PySide6.QtGui import QTextFormat, QSyntaxHighlighter, QTextCharFormat

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