from .common_imports import *

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
        """Configura el resaltador de sintaxis para el archivo - CORREGIDO"""
        if self.highlighter:
            self.highlighter.setDocument(None)
        
        try:
            from .highlighter import HighlighterFactory
            self.highlighter = HighlighterFactory.create_highlighter(file_path, self.document(), self.theme)
        except ImportError:
            self.create_basic_highlighter(file_path)
        except Exception as e:
            print(f"Error creando highlighter: {e}")
            self.create_basic_highlighter(file_path)
    
    def create_basic_highlighter(self, file_path):
        """Crea un resaltador básico cuando HighlighterFactory no está disponible"""
        try:
            from .highlighter import VSCodeHighlighter
            self.highlighter = VSCodeHighlighter(self.document(), self.theme)
        except ImportError:
    
            self.highlighter = BasicHighlighter(self.document())
            print("Usando resaltador básico")

class BasicHighlighter(QSyntaxHighlighter):
    """Resaltador básico de sintaxis como fallback"""
    
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((QRegExp("//[^\n]*"), comment_format))
        self.highlighting_rules.append((QRegExp("/\\*.*\\*/"), comment_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((QRegExp("\".*\""), string_format))
        self.highlighting_rules.append((QRegExp("'.*'"), string_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((QRegExp("\\b\\d+\\b"), number_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)