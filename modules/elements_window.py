from .common_imports import *

class ElementsWindow(QMainWindow):
    """Ventana de elementos predefinidos con buscador"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.project_language = parent.project_language if parent else "Java"
        self.setup_ui()
        self.load_elements()
    
    def setup_ui(self):
        self.setWindowTitle("Elementos Predefinidos")
        self.setGeometry(200, 200, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar elementos...")
        self.search_input.textChanged.connect(self.filter_elements)
        search_layout.addWidget(self.search_input)
        
        clear_btn = QPushButton("X")
        clear_btn.setFixedWidth(30)
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_btn)
        
        layout.addLayout(search_layout)
        
        # Lista de elementos
        self.elements_list = QListWidget()
        self.elements_list.itemDoubleClicked.connect(self.element_double_clicked)
        layout.addWidget(self.elements_list)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Añadir al Diseño")
        add_btn.clicked.connect(self.add_to_design)
        cancel_btn = QPushButton("Cerrar")
        cancel_btn.clicked.connect(self.close)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def load_elements(self):
        """Carga elementos según el lenguaje del proyecto"""
        self.elements_list.clear()
        
        if self.project_language.lower() == "java":
            elements = [
                ("Button", "🔘", "Botón estándar de Android"),
                ("TextView", "🔤", "Texto estático"),
                ("EditText", "📝", "Campo de texto editable"),
                ("ImageView", "🖼️", "Vista de imagen"),
                ("LinearLayout", "📏", "Layout lineal"),
                ("RelativeLayout", "🔗", "Layout relativo"),
                ("ConstraintLayout", "🎯", "Layout con constraints"),
                ("RecyclerView", "📜", "Lista desplazable"),
                ("CardView", "🎴", "Tarjeta con sombra"),
                ("FloatingActionButton", "🔘", "Botón flotante")
            ]
        elif self.project_language.lower() == "kotlin":
            elements = [
                ("Button", "🔘", "Botón estándar"),
                ("Text", "🔤", "Texto en Compose"),
                ("TextField", "📝", "Campo de texto"),
                ("Image", "🖼️", "Imagen en Compose"),
                ("Column", "📏", "Columna en Compose"),
                ("Row", "➡️", "Fila en Compose"),
                ("Box", "📦", "Contenedor en Compose")
            ]
        else:
            elements = [
                ("Button", "🔘", "Botón genérico"),
                ("Text", "🔤", "Texto"),
                ("Input", "📝", "Campo de entrada"),
                ("Image", "🖼️", "Imagen"),
                ("Container", "📦", "Contenedor")
            ]
        
        for name, icon, description in elements:
            item = QListWidgetItem(f"{icon} {name}\n{description}")
            item.setData(Qt.UserRole, name)
            self.elements_list.addItem(item)
    
    def filter_elements(self, text):
        """Filtra elementos basado en la búsqueda"""
        for i in range(self.elements_list.count()):
            item = self.elements_list.item(i)
            item_text = item.text().lower()
            item.setHidden(text.lower() not in item_text)
    
    def clear_search(self):
        """Limpia la búsqueda"""
        self.search_input.clear()
    
    def element_double_clicked(self, item):
        """Maneja doble click en elemento"""
        element_name = item.data(Qt.UserRole)
        self.add_element_to_canvas(element_name)
    
    def add_to_design(self):
        """Añade el elemento seleccionado al diseño"""
        current_item = self.elements_list.currentItem()
        if current_item:
            element_name = current_item.data(Qt.UserRole)
            self.add_element_to_canvas(element_name)
        else:
            QMessageBox.warning(self, "Selección", "Selecciona un elemento primero")
    
    def add_element_to_canvas(self, element_name):
        """Añade el elemento al canvas"""
        if self.parent and hasattr(self.parent, 'hoja_ai_panel'):
            canvas = self.parent.hoja_ai_panel.canvas
            
            # Crear elemento básico en el centro del canvas
            rect = canvas.scene.sceneRect()
            center_x = rect.center().x()
            center_y = rect.center().y()
            
            if "Button" in element_name:
                button = QGraphicsRectItem(center_x - 50, center_y - 25, 100, 50)
                button.setBrush(QBrush(QColor(100, 150, 255)))
                button.setPen(QPen(Qt.blue, 2))
                canvas.scene.addItem(button)
            
            elif "Text" in element_name or "TextView" in element_name:
                text = QGraphicsTextItem(element_name)
                text.setPos(center_x - 30, center_y - 10)
                canvas.scene.addItem(text)
            
            elif "Image" in element_name:
                image_rect = QGraphicsRectItem(center_x - 40, center_y - 40, 80, 80)
                image_rect.setBrush(QBrush(QColor(200, 200, 200)))
                image_rect.setPen(QPen(Qt.gray, 1))
                canvas.scene.addItem(image_rect)
            
            QMessageBox.information(self, "Éxito", f"Elemento '{element_name}' añadido al diseño")
            self.close()