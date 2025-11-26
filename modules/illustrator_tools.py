from .common_imports import *

class IllustratorToolsPanel(QDockWidget):
    """Panel de herramientas de Illustrator profesional"""
    
    def __init__(self, parent=None):
        super().__init__("Herramientas Illustrator", parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        tool_widget = QWidget()
        layout = QVBoxLayout(tool_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        
        # 🖱 HERRAMIENTAS DE SELECCIÓN
        selection_label = QLabel("🖱 Herramientas de Selección")
        selection_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #333;")
        layout.addWidget(selection_label)
        
        selection_tools = [
            ("🔍", "Selección (V)", "selection", 
             "Selecciona objetos completos. Actúa sobre bounding box para traslación, rotación y escala"),
            ("🎯", "Selección directa (A)", "direct_selection", 
             "Accede a nodos y segmentos. Manipula coordenadas y manejadores Bézier"),
            ("✨", "Varita mágica (Y)", "magic_wand", 
             "Selecciona por atributos (color, grosor, opacidad) con tolerancia definida"),
            ("👥", "Selección de grupo", "group_selection", 
             "Selecciona elementos anidados en grupos jerárquicos sin desagrupar")
        ]
        
        for icon, name, tool_id, tooltip in selection_tools:
            btn = self.create_tool_button(icon, name, tool_id, tooltip)
            layout.addWidget(btn)
        
        # ✏️ HERRAMIENTAS DE DIBUJO
        drawing_label = QLabel("✏️ Herramientas de Dibujo")
        drawing_label.setStyleSheet("font-weight: bold; margin-top: 15px; color: #333;")
        layout.addWidget(drawing_label)
        
        drawing_tools = [
            ("🖋️", "Pluma (P)", "pen", 
             "Crea paths vectoriales con puntos de anclaje y curvas Bézier cúbicas"),
            ("✏️", "Lápiz (N)", "pencil", 
             "Genera paths libres interpolados y suavizados con algoritmos de simplificación"),
            ("🖌️", "Pincel (B)", "brush", 
             "Aplica perfiles de trazo predefinidos con variaciones de grosor y textura"),
            ("📏", "Plumilla/Anchura", "width_tool", 
             "Modifica dinámicamente el perfil de grosor del trazo a lo largo del path"),
            ("🧽", "Borrador (Shift+E)", "eraser", 
             "Elimina partes del trazado mediante operaciones booleanas vectoriales")
        ]
        
        for icon, name, tool_id, tooltip in drawing_tools:
            btn = self.create_tool_button(icon, name, tool_id, tooltip)
            layout.addWidget(btn)
        
        layout.addStretch()

        # Botón de configuración avanzada
        settings_btn = QPushButton("⚙️ Configuración Avanzada")
        settings_btn.setFixedHeight(35)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        settings_btn.clicked.connect(self.show_advanced_settings)
        layout.addWidget(settings_btn)
        
        tool_widget.setLayout(layout)
        self.setWidget(tool_widget)
        
        # Configurar propiedades del dock
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setMinimumWidth(200)
        self.setMaximumWidth(250)
        
        # Seleccionar herramienta por defecto
        self.select_default_tool()

    def create_tool_button(self, icon, name, tool_id, tooltip):
        """Crea un botón de herramienta profesional"""
        btn = QPushButton(f"{icon} {name}")
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        btn.setFixedHeight(45)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                text-align: left;
                padding: 8px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f8f8;
                margin: 2px;
            }
            QPushButton:checked {
                background-color: #007acc;
                color: white;
                border: 1px solid #005a9e;
            }
            QPushButton:hover:!checked {
                background-color: #e8f4ff;
                border: 1px solid #007acc;
            }
            QPushButton:pressed {
                background-color: #d0e8ff;
            }
        """)
        
        btn.clicked.connect(lambda: self.tool_selected(tool_id))
        self.tool_group.addButton(btn)
        
        return btn
    
    def select_default_tool(self):
        """Selecciona la herramienta por defecto (Selección)"""
        for btn in self.tool_group.buttons():
            if btn.text().startswith("🔍"):
                btn.setChecked(True)
                self.tool_selected("selection")
                break
    
    def tool_selected(self, tool_id):
        """Maneja la selección de una herramienta profesional"""
        print(f"Herramienta seleccionada: {tool_id}")
        
        if self.parent and hasattr(self.parent, 'hoja_ai_panel'):
            canvas = self.parent.hoja_ai_panel.canvas
            canvas.set_tool(tool_id)
            
            # Mostrar información de la herramienta en status bar
            tool_info = {
                "selection": "Selección (V) - Selecciona objetos completos para traslación, rotación y escala",
                "direct_selection": "Selección directa (A) - Edita nodos y segmentos a nivel de geometría",
                "magic_wand": "Varita mágica (Y) - Selecciona objetos por atributos compartidos",
                "group_selection": "Selección de grupo - Navega jerarquías sin desagrupar",
                "pen": "Pluma (P) - Crea paths Bézier precisos con puntos de anclaje",
                "pencil": "Lápiz (N) - Dibujo libre interpolado con suavizado automático",
                "brush": "Pincel (B) - Trazos con perfiles y texturas personalizadas",
                "width_tool": "Plumilla - Ajusta grosor de trazo dinámicamente",
                "eraser": "Borrador - Elimina secciones vectoriales con operaciones booleanas"
            }
            
            info = tool_info.get(tool_id, f"Herramienta: {tool_id}")
            if hasattr(self.parent, 'statusBar'):
                self.parent.statusBar().showMessage(f"🎯 {info}", 3000)

    def show_advanced_settings(self):
        """Muestra configuración avanzada de herramientas"""
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Configuración Avanzada de Herramientas")
        settings_dialog.setFixedSize(450, 350)
        
        layout = QVBoxLayout(settings_dialog)
        
        # Pestañas para diferentes categorías
        tab_widget = QTabWidget()
        
        # Configuración de selección
        selection_tab = QWidget()
        selection_layout = QVBoxLayout(selection_tab)
        
        selection_layout.addWidget(QLabel("Tolerancia de Varita Mágica:"))
        tolerance_slider = QSlider(Qt.Horizontal)
        tolerance_slider.setRange(1, 100)
        tolerance_slider.setValue(10)
        selection_layout.addWidget(tolerance_slider)
        
        tolerance_label = QLabel("10%")
        tolerance_slider.valueChanged.connect(lambda v: tolerance_label.setText(f"{v}%"))
        selection_layout.addWidget(tolerance_label)
        
        selection_layout.addWidget(QLabel("Comportamiento de Selección:"))
        selection_combo = QComboBox()
        selection_combo.addItems(["Selección simple", "Selección múltiple (Ctrl)", "Selección por toque"])
        selection_layout.addWidget(selection_combo)
        
        snap_checkbox = QCheckBox("Ajustar a cuadrícula")
        snap_checkbox.setChecked(True)
        selection_layout.addWidget(snap_checkbox)
        
        selection_layout.addStretch()
        tab_widget.addTab(selection_tab, "🖱 Selección")
        
        # Configuración de dibujo
        drawing_tab = QWidget()
        drawing_layout = QVBoxLayout(drawing_tab)
        
        drawing_layout.addWidget(QLabel("Suavizado de Lápiz:"))
        smooth_slider = QSlider(Qt.Horizontal)
        smooth_slider.setRange(0, 100)
        smooth_slider.setValue(50)
        drawing_layout.addWidget(smooth_slider)
        
        smooth_label = QLabel("Medio")
        smooth_slider.valueChanged.connect(lambda v: smooth_label.setText(
            "Bajo" if v < 33 else "Medio" if v < 66 else "Alto"
        ))
        drawing_layout.addWidget(smooth_label)
        
        drawing_layout.addWidget(QLabel("Fidelidad de Pincel:"))
        fidelity_combo = QComboBox()
        fidelity_combo.addItems(["Alta precisión", "Rendimiento", "Equilibrado"])
        drawing_layout.addWidget(fidelity_combo)
        
        pressure_checkbox = QCheckBox("Simular presión de tableta")
        pressure_checkbox.setChecked(False)
        drawing_layout.addWidget(pressure_checkbox)
        
        drawing_layout.addStretch()
        tab_widget.addTab(drawing_tab, "✏️ Dibujo")
        
        # Configuración general
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        general_layout.addWidget(QLabel("Tamaño de cursor:"))
        cursor_slider = QSlider(Qt.Horizontal)
        cursor_slider.setRange(1, 5)
        cursor_slider.setValue(2)
        general_layout.addWidget(cursor_slider)
        
        cursor_label = QLabel("Normal")
        cursor_slider.valueChanged.connect(lambda v: cursor_label.setText(
            ["Muy pequeño", "Pequeño", "Normal", "Grande", "Muy grande"][v-1]
        ))
        general_layout.addWidget(cursor_label)
        
        general_layout.addWidget(QLabel("Atajos de teclado:"))
        shortcuts_text = QTextEdit()
        shortcuts_text.setPlainText("""
            Selección (V) - V
            Selección directa (A) - A
            Varita mágica (Y) - Y
            Pluma (P) - P
            Lápiz (N) - N
            Pincel (B) - B
            Borrador (E) - E
                    """)
        shortcuts_text.setReadOnly(True)
        shortcuts_text.setMaximumHeight(120)
        general_layout.addWidget(shortcuts_text)
        
        general_layout.addStretch()
        tab_widget.addTab(general_tab, "⚙️ General")
        
        layout.addWidget(tab_widget)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Guardar Configuración")
        reset_btn = QPushButton("🔄 Restablecer")
        cancel_btn = QPushButton("❌ Cerrar")
        
        save_btn.clicked.connect(lambda: self.save_settings(settings_dialog))
        reset_btn.clicked.connect(lambda: self.reset_settings(tolerance_slider, smooth_slider, cursor_slider))
        cancel_btn.clicked.connect(settings_dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        settings_dialog.exec_()
    
    def save_settings(self, dialog):
        """Guarda la configuración"""
        QMessageBox.information(self, "Configuración", "Configuración guardada correctamente")
        dialog.accept()
    
    def reset_settings(self, tolerance_slider, smooth_slider, cursor_slider):
        """Restablece la configuración por defecto"""
        tolerance_slider.setValue(10)
        smooth_slider.setValue(50)
        cursor_slider.setValue(2)
        QMessageBox.information(self, "Configuración", "Configuración restablecida a valores por defecto")
    
    def get_current_tool(self):
        """Retorna la herramienta actualmente seleccionada"""
        for btn in self.tool_group.buttons():
            if btn.isChecked():
                # Extraer el tool_id del texto del botón
                text = btn.text()
                if "Selección (V)" in text:
                    return "selection"
                elif "Selección directa (A)" in text:
                    return "direct_selection"
                elif "Varita mágica (Y)" in text:
                    return "magic_wand"
                elif "Selección de grupo" in text:
                    return "group_selection"
                elif "Pluma (P)" in text:
                    return "pen"
                elif "Lápiz (N)" in text:
                    return "pencil"
                elif "Pincel (B)" in text:
                    return "brush"
                elif "Plumilla/Anchura" in text:
                    return "width_tool"
                elif "Borrador (Shift+E)" in text:
                    return "eraser"
        return "selection"
    
    def set_tool(self, tool_id):
        """Establece una herramienta específica"""
        for btn in self.tool_group.buttons():
            if tool_id == "selection" and "Selección (V)" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
            elif tool_id == "direct_selection" and "Selección directa (A)" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
            elif tool_id == "magic_wand" and "Varita mágica (Y)" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
            elif tool_id == "group_selection" and "Selección de grupo" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
            elif tool_id == "pen" and "Pluma (P)" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
            elif tool_id == "pencil" and "Lápiz (N)" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
            elif tool_id == "brush" and "Pincel (B)" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
            elif tool_id == "width_tool" and "Plumilla/Anchura" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
            elif tool_id == "eraser" and "Borrador (Shift+E)" in btn.text():
                btn.setChecked(True)
                self.tool_selected(tool_id)
                break
class AdvancedIllustratorCanvas(QGraphicsView):
    """Lienzo avanzado con herramientas profesionales de Illustrator"""
    
    elementSelected = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setStyleSheet("""
            QGraphicsView {
                background: #1e1e1e;
                border: 1px solid #555;
            }
        """)

        # Herramientas profesionales
        self.current_tool = "selection"
        
        # Propiedades para SELECCIÓN Y TRANSFORMACIÓN
        self.selected_items = []
        self.selection_rect = None
        self.dragging = False
        self.drag_start = None
        self.multi_select = False
        self.transform_handles = []
        self.transform_mode = None  # 'move', 'rotate', 'scale'
        self.transform_origin = None
        
        # Propiedades para control de transformación
        self.scale_handles = []
        self.rotate_handle = None
        self.selection_border = None
        
        # Propiedades para SELECCIÓN DIRECTA
        self.direct_selection_mode = False
        self.selected_nodes = []
        self.node_handles = []
        self.active_path_item = None
        
        # Propiedades para PLUMA
        self.pen_path = None
        self.pen_points = []
        self.current_pen_item = None
        self.pen_temp_lines = []
        self.pen_temp_points = []
        
        # Propiedades para LÁPIZ
        self.pencil_path = None
        self.pencil_points = []
        self.current_pencil_item = None
        self.pencil_drawing = False
        
        # Propiedades para PINCEL
        self.brush_path = None
        self.current_brush_item = None
        self.brush_drawing = False
        self.brush_size = 5
        self.brush_color = QColor("#3498db")
        
        # Propiedades para BORRADOR
        self.erasing = False
        self.eraser_size = 20
        self.eraser_cursor = None
        
        # Propiedades para VARITA MÁGICA
        self.magic_wand_tolerance = 10
        
        # Propiedades generales
        self.snap_to_grid = True
        self.grid_size = 10

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Crear cursor de borrador
        self.update_eraser_cursor()

    def set_tool(self, tool_id):
        """Establece la herramienta actual"""
        self.current_tool = tool_id
        
        # Limpiar estados anteriores
        self.clear_selection_state()
        self.clear_drawing_state()
        self.clear_transform_handles()
        
        # Configurar cursor según herramienta
        cursors = {
            "selection": Qt.ArrowCursor,
            "direct_selection": Qt.CrossCursor,
            "magic_wand": Qt.PointingHandCursor,
            "group_selection": Qt.ArrowCursor,
            "pen": Qt.CrossCursor,
            "pencil": Qt.CrossCursor,
            "brush": Qt.CrossCursor,
            "width_tool": Qt.SizeHorCursor,
            "eraser": self.eraser_cursor if self.eraser_cursor else Qt.CrossCursor
        }
        
        self.setCursor(cursors.get(tool_id, Qt.ArrowCursor))
        
        # Modos especiales
        self.direct_selection_mode = (tool_id == "direct_selection")
        
        # Si es herramienta de selección, mostrar handles de transformación
        if tool_id == "selection" and self.selected_items:
            self.show_transform_handles()
        
        # Actualizar escena
        self.scene.update()

    def clear_selection_state(self):
        """Limpia el estado de selección"""
        # Limpiar manijas de nodos
        for handle in self.node_handles:
            if handle in self.scene.items():
                self.scene.removeItem(handle)
        self.node_handles = []
        self.selected_nodes = []
        self.active_path_item = None
        
        # Limpiar rectángulo de selección
        if self.selection_rect:
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None
        
        self.dragging = False
        self.drag_start = None

    def clear_transform_handles(self):
        """Limpia los handles de transformación"""
        for handle in self.transform_handles:
            if handle in self.scene.items():
                self.scene.removeItem(handle)
        self.transform_handles = []
        
        for handle in self.scale_handles:
            if handle in self.scene.items():
                self.scene.removeItem(handle)
        self.scale_handles = []
        
        if self.rotate_handle and self.rotate_handle in self.scene.items():
            self.scene.removeItem(self.rotate_handle)
        self.rotate_handle = None
        
        if self.selection_border and self.selection_border in self.scene.items():
            self.scene.removeItem(self.selection_border)
        self.selection_border = None
        
        self.transform_mode = None
        self.transform_origin = None
    def clear_drawing_state(self):
            """Limpia el estado de dibujo"""
            # Limpiar elementos temporales de pluma
            for line in self.pen_temp_lines:
                if line in self.scene.items():
                    self.scene.removeItem(line)
            for point in self.pen_temp_points:
                if point in self.scene.items():
                    self.scene.removeItem(point)
            
            self.pen_temp_lines = []
            self.pen_temp_points = []
            self.pen_points = []
            self.pen_path = None
            
            # Limpiar estado de lápiz
            self.pencil_points = []
            self.pencil_drawing = False
            
            # Limpiar estado de pincel
            self.brush_drawing = False
    def handle_mouse_release(self, event, handle):
        """Maneja la liberación de un handle de transformación"""
        self.transform_mode = None
        self.transform_origin = None
        event.accept()

    def handle_scale_transform(self, handle, new_pos):
        """Maneja la transformación de escala"""
        handle_type = handle.data(0)
        original_pos = handle.data(1)
        original_bbox = handle.data(2)
        
        # Calcular factores de escala
        scale_x = 1.0
        scale_y = 1.0
        
        if "scale_0" in handle_type:  # Superior izquierda
            scale_x = (original_bbox.right() - new_pos.x()) / original_bbox.width()
            scale_y = (original_bbox.bottom() - new_pos.y()) / original_bbox.height()
        elif "scale_1" in handle_type:  # Superior derecha
            scale_x = (new_pos.x() - original_bbox.left()) / original_bbox.width()
            scale_y = (original_bbox.bottom() - new_pos.y()) / original_bbox.height()
        elif "scale_2" in handle_type:  # Inferior derecha
            scale_x = (new_pos.x() - original_bbox.left()) / original_bbox.width()
            scale_y = (new_pos.y() - original_bbox.top()) / original_bbox.height()
        elif "scale_3" in handle_type:  # Inferior izquierda
            scale_x = (original_bbox.right() - new_pos.x()) / original_bbox.width()
            scale_y = (new_pos.y() - original_bbox.top()) / original_bbox.height()
        
        # Aplicar escala a los items seleccionados
        for item in self.selected_items:
            current_transform = item.transform()
            current_transform.scale(scale_x, scale_y)
            item.setTransform(current_transform)

    def handle_rotate_transform(self, handle, new_pos):
        """Maneja la transformación de rotación"""
        if not self.selected_items:
            return
        
        # Calcular centro del bounding box combinado
        if len(self.selected_items) == 1:
            center = self.selected_items[0].boundingRect().center()
            scene_center = self.selected_items[0].mapToScene(center)
        else:
            scene_bbox = QRectF()
            for item in self.selected_items:
                item_bbox = item.mapToScene(item.boundingRect()).boundingRect()
                scene_bbox = scene_bbox.united(item_bbox)
            scene_center = scene_bbox.center()
        
        # Calcular ángulo de rotación
        original_vector = self.transform_origin - scene_center
        new_vector = new_pos - scene_center
        
        if original_vector.manhattanLength() > 0 and new_vector.manhattanLength() > 0:
            dot_product = original_vector.x() * new_vector.x() + original_vector.y() * new_vector.y()
            cross_product = original_vector.x() * new_vector.y() - original_vector.y() * new_vector.x()
            
            angle_rad = math.atan2(cross_product, dot_product)
            angle_deg = math.degrees(angle_rad)
            
            # Aplicar rotación a los items seleccionados
            for item in self.selected_items:
                item.setRotation(item.rotation() + angle_deg)

    def handle_mouse_press(self, event, handle):
        """Maneja el press en un handle de transformación"""
        self.transform_mode = handle.data(0)
        self.transform_origin = handle.scenePos()
        event.accept()
    def show_transform_handles(self):
            """Muestra los handles de transformación para los items seleccionados"""
            self.clear_transform_handles()
            
            if not self.selected_items:
                return
            
            # Calcular bounding box unificado de todos los items seleccionados
            if len(self.selected_items) == 1:
                bbox = self.selected_items[0].boundingRect()
                pos = self.selected_items[0].pos()
                scene_bbox = self.selected_items[0].mapToScene(bbox).boundingRect()
            else:
                # Para múltiples items, calcular el bounding box combinado
                scene_bbox = QRectF()
                for item in self.selected_items:
                    item_bbox = item.mapToScene(item.boundingRect()).boundingRect()
                    scene_bbox = scene_bbox.united(item_bbox)
                pos = scene_bbox.topLeft()
                bbox = QRectF(0, 0, scene_bbox.width(), scene_bbox.height())
            
            # Crear borde de selección
            self.selection_border = QGraphicsRectItem(bbox)
            self.selection_border.setPos(pos)
            self.selection_border.setPen(QPen(QColor(0, 120, 215), 1, Qt.DashLine))
            self.selection_border.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.selection_border.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.scene.addItem(self.selection_border)
            
            # Crear handles de escala en las esquinas
            corners = [
                bbox.topLeft(),      # Esquina superior izquierda
                bbox.topRight(),     # Esquina superior derecha
                bbox.bottomRight(),  # Esquina inferior derecha
                bbox.bottomLeft()    # Esquina inferior izquierda
            ]
            
            for i, corner in enumerate(corners):
                handle = QGraphicsEllipseItem(corner.x() - 4, corner.y() - 4, 8, 8)
                handle.setBrush(QBrush(Qt.white))
                handle.setPen(QPen(Qt.black, 1))
                handle.setFlag(QGraphicsItem.ItemIsMovable, True)
                handle.setFlag(QGraphicsItem.ItemIsSelectable, True)
                handle.setData(0, f"scale_{i}")
                handle.setData(1, pos)  # Posición original
                handle.setData(2, bbox)  # Bounding box original
                
                # Conectar eventos
                handle.mousePressEvent = lambda event, h=handle: self.handle_mouse_press(event, h)
                handle.mouseMoveEvent = lambda event, h=handle: self.handle_mouse_move(event, h)
                handle.mouseReleaseEvent = lambda event, h=handle: self.handle_mouse_release(event, h)
                
                self.scene.addItem(handle)
                self.scale_handles.append(handle)
            
            # Crear handle de rotación (arriba del centro)
            center_top = QPointF(bbox.center().x(), bbox.top() - 20)
            self.rotate_handle = QGraphicsEllipseItem(center_top.x() - 4, center_top.y() - 4, 8, 8)
            self.rotate_handle.setBrush(QBrush(Qt.blue))
            self.rotate_handle.setPen(QPen(Qt.white, 1))
            self.rotate_handle.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.rotate_handle.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.rotate_handle.setData(0, "rotate")
            self.rotate_handle.setData(1, pos)  # Posición original
            
            # Conectar eventos
            self.rotate_handle.mousePressEvent = lambda event: self.handle_mouse_press(event, self.rotate_handle)
            self.rotate_handle.mouseMoveEvent = lambda event: self.handle_mouse_move(event, self.rotate_handle)
            self.rotate_handle.mouseReleaseEvent = lambda event: self.handle_mouse_release(event, self.rotate_handle)
            
            self.scene.addItem(self.rotate_handle)
    def handle_mouse_move(self, event, handle):
        """Maneja el movimiento de un handle de transformación"""
        if not self.transform_mode:
            return
        
        current_pos = handle.scenePos()
        new_pos = current_pos + event.scenePos() - handle.scenePos()
        
        if self.transform_mode.startswith("scale"):
            self.handle_scale_transform(handle, new_pos)
        elif self.transform_mode == "rotate":
            self.handle_rotate_transform(handle, new_pos)
        
        # Actualizar posición del handle
        handle.setPos(handle.pos() + event.scenePos() - handle.scenePos())
        event.accept()
    def update_eraser_cursor(self):
        """Actualiza el cursor del borrador"""
        pixmap = QPixmap(self.eraser_size, self.eraser_size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.red, 2))
        painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
        painter.drawEllipse(0, 0, self.eraser_size, self.eraser_size)
        painter.end()
        
        self.eraser_cursor = QCursor(pixmap)

    def mousePressEvent(self, event):
        """Maneja el evento de presión del mouse"""
        scene_pos = self.mapToScene(event.pos())
        
        # Ajustar a cuadrícula si está activado
        if self.snap_to_grid:
            scene_pos = self.snap_to_grid_point(scene_pos)
        
        # Modo multi-selección con Ctrl
        self.multi_select = (event.modifiers() & Qt.ControlModifier)
        
        if event.button() == Qt.LeftButton:
            if self.current_tool == "selection":
                self.start_selection(scene_pos, event)
            elif self.current_tool == "direct_selection":
                self.start_direct_selection(scene_pos)
            elif self.current_tool == "magic_wand":
                self.magic_wand_selection(scene_pos)
            elif self.current_tool == "group_selection":
                self.group_selection(scene_pos)
            elif self.current_tool == "pen":
                self.add_pen_point(scene_pos)
            elif self.current_tool == "pencil":
                self.start_pencil_drawing(scene_pos)
            elif self.current_tool == "brush":
                self.start_brush_drawing(scene_pos)
            elif self.current_tool == "eraser":
                self.start_erasing(scene_pos)
            elif self.current_tool == "width_tool":
                self.start_width_adjustment(scene_pos)
    def mouseMoveEvent(self, event):
        """Maneja el movimiento del mouse"""
        scene_pos = self.mapToScene(event.pos())
        
        if self.snap_to_grid:
            scene_pos = self.snap_to_grid_point(scene_pos)
        
        if self.current_tool == "selection" and self.dragging:
            self.update_selection_rect(scene_pos)
        elif self.current_tool == "pencil" and self.pencil_drawing:
            self.update_pencil_drawing(scene_pos)
        elif self.current_tool == "brush" and self.brush_drawing:
            self.update_brush_drawing(scene_pos)
        elif self.current_tool == "eraser" and self.erasing:
            self.update_erasing(scene_pos)
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Maneja la liberación del mouse"""
        if self.current_tool == "selection" and self.dragging:
            self.finish_selection()
        elif self.current_tool == "pencil" and self.pencil_drawing:
            self.finish_pencil_drawing()
        elif self.current_tool == "brush" and self.brush_drawing:
            self.finish_brush_drawing()
        elif self.current_tool == "eraser" and self.erasing:
            self.finish_erasing()
        
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """Maneja eventos de teclado para atajos"""
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        elif event.key() == Qt.Key_Escape:
            self.clear_selection()
        elif event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_A:
                self.select_all_items()
            elif event.key() == Qt.Key_G:
                self.group_selected_items()
            elif event.key() == Qt.Key_ShiftModifier:
                self.multi_select = True
        
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        """Maneja liberación de teclas"""
        if event.key() == Qt.Key_Control:
            self.multi_select = False
        
        super().keyReleaseEvent(event)

    def snap_to_grid_point(self, point):
        """Ajusta un punto a la cuadrícula"""
        x = round(point.x() / self.grid_size) * self.grid_size
        y = round(point.y() / self.grid_size) * self.grid_size
        return QPointF(x, y)

    # 🖱 HERRAMIENTAS DE SELECCIÓN
    def start_selection(self, pos, event):
        """Inicia selección de objetos"""
        # Verificar si se hizo click en un handle de transformación
        items = self.scene.items(pos)
        transform_handle_clicked = False
        
        for item in items:
            if item in self.scale_handles or item == self.rotate_handle:
                transform_handle_clicked = True
                break
        
        if transform_handle_clicked:
            return  # Dejar que el handle maneje el evento
        
        # Selección normal de objetos
        items = self.scene.items(pos)
        
        if items and not self.multi_select:
            # Buscar el primer item que no sea un handle de transformación
            for item in items:
              if (item not in self.scale_handles and 
                  item != self.rotate_handle and 
                  item != self.selection_border and
                  isinstance(item, (QGraphicsPathItem, QGraphicsRectItem, 
                                QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem))):
                    self.select_item(item, clear_previous=not self.multi_select)
                    break
        else:
            # Iniciar selección por rectángulo
            self.dragging = True
            self.drag_start = pos
            self.selection_rect = QGraphicsRectItem(QRectF(pos, pos))
            self.selection_rect.setPen(QPen(QColor(0, 120, 215), 1, Qt.DashLine))
            self.selection_rect.setBrush(QBrush(QColor(0, 120, 215, 30)))
            self.scene.addItem(self.selection_rect)

    def update_selection_rect(self, pos):
        """Actualiza el rectángulo de selección"""
        if self.selection_rect and self.drag_start:
            rect = QRectF(self.drag_start, pos).normalized()
            self.selection_rect.setRect(rect)

    def finish_selection(self):
        """Finaliza la selección por rectángulo"""
        if self.selection_rect:
            # Seleccionar items dentro del rectángulo
            rect = self.selection_rect.rect()
            items_in_rect = self.scene.items(rect, Qt.IntersectsItemShape)
            
            for item in items_in_rect:
                if isinstance(item, (QGraphicsPathItem, QGraphicsRectItem, 
                                QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem)):
                    # Ignorar elementos temporales y handles
                    if (item not in self.pen_temp_points and 
                        item not in self.pen_temp_lines and
                        item not in self.scale_handles and
                        item != self.rotate_handle and
                        item != self.selection_rect):
                        self.select_item(item, clear_previous=False)
            
            self.scene.removeItem(self.selection_rect)
            self.selection_rect = None
        
        self.dragging = False
        self.drag_start = None
    def select_item(self, item, clear_previous=True):
        """Selecciona un item y muestra sus propiedades"""
        if clear_previous and not self.multi_select:
            # Limpiar selección anterior
            self.clear_selection()
        
        # Resaltar item seleccionado
        if hasattr(item, 'setPen'):
            original_pen = item.pen()
            highlight_pen = QPen(QColor(255, 0, 0), 2)
            item.setPen(highlight_pen)
        
        # Habilitar movimiento y selección
        item.setFlag(QGraphicsItem.ItemIsMovable, True)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        if item not in self.selected_items:
            self.selected_items.append(item)
        
        # Mostrar handles de transformación
        self.show_transform_handles()
        
        # Emitir señal de elemento seleccionado
        self.elementSelected.emit(item)

    def clear_selection(self):
        """Limpia toda la selección"""
        for item in self.selected_items:
            if hasattr(item, 'setPen'):
                # Restaurar pen original (simulado)
                item.setPen(QPen(Qt.black, 1))
            item.setFlag(QGraphicsItem.ItemIsMovable, False)
        
        self.selected_items = []
        self.clear_transform_handles()
        self.elementSelected.emit(None)

    def delete_selected_items(self):
        """Elimina los items seleccionados"""
        for item in self.selected_items:
            self.scene.removeItem(item)
        self.selected_items = []

    def select_all_items(self):
        """Selecciona todos los items en la escena"""
        self.clear_selection()
        for item in self.scene.items():
            if isinstance(item, (QGraphicsPathItem, QGraphicsRectItem, 
                               QGraphicsEllipseItem, QGraphicsPolygonItem,
                               QGraphicsLineItem, QGraphicsTextItem)):
                self.select_item(item, clear_previous=False)

    # SELECCIÓN DIRECTA
    def start_direct_selection(self, pos):
        """Inicia selección directa de nodos"""
        items = self.scene.items(pos)
        if items:
            item = items[0]
            if isinstance(item, (QGraphicsPathItem, QGraphicsPolygonItem)):
                self.show_node_handles(item)

    def show_node_handles(self, item):
        """Muestra manijas para los nodos del item"""
        self.clear_selection_state()
        self.active_path_item = item
        
        if isinstance(item, QGraphicsPathItem):
            path = item.path()
            for i in range(path.elementCount()):
                element = path.elementAt(i)
                handle = self.create_node_handle(QPointF(element.x, element.y), i, item)
                self.node_handles.append(handle)
        
        elif isinstance(item, QGraphicsPolygonItem):
            polygon = item.polygon()
            for i, point in enumerate(polygon):
                handle = self.create_node_handle(point, i, item)
                self.node_handles.append(handle)

    def create_node_handle(self, position, index, parent_item):
        """Crea una manija de nodo"""
        handle = QGraphicsEllipseItem(position.x()-4, position.y()-4, 8, 8)
        handle.setBrush(QBrush(Qt.yellow))
        handle.setPen(QPen(Qt.black, 1))
        handle.setFlag(QGraphicsItem.ItemIsMovable, True)
        handle.setFlag(QGraphicsItem.ItemIsSelectable, True)
        handle.setData(0, index)  # Índice del nodo
        handle.setData(1, parent_item)  # Item padre
        
        self.scene.addItem(handle)
        return handle

    def node_moved(self, handle, event):
        """Maneja el movimiento de un nodo (se conecta en mouseMove)"""
        parent_item = handle.data(1)
        node_index = handle.data(0)
        new_pos = handle.scenePos() + QPointF(4, 4)  # Ajustar al centro
        
        if self.snap_to_grid:
            new_pos = self.snap_to_grid_point(new_pos)
        
        if isinstance(parent_item, QGraphicsPolygonItem):
            polygon = parent_item.polygon()
            polygon[node_index] = new_pos
            parent_item.setPolygon(polygon)
        
        QGraphicsEllipseItem.mouseMoveEvent(handle, event)

    # VARITA MÁGICA
    def magic_wand_selection(self, pos):
        """Selección por atributos con varita mágica"""
        items = self.scene.items(pos)
        if items:
            target_item = items[0]
            target_color = target_item.brush().color() if hasattr(target_item, 'brush') else QColor()
            
            # Seleccionar items con color similar
            for item in self.scene.items():
                if (hasattr(item, 'brush') and 
                    isinstance(item, (QGraphicsPathItem, QGraphicsRectItem, 
                                    QGraphicsEllipseItem, QGraphicsPolygonItem))):
                    item_color = item.brush().color()
                    if self.colors_similar(target_color, item_color, self.magic_wand_tolerance):
                        self.select_item(item, clear_previous=False)

    def colors_similar(self, color1, color2, tolerance):
        """Compara si dos colores son similares"""
        if not color1.isValid() or not color2.isValid():
            return False
            
        diff = (abs(color1.red() - color2.red()) +
                abs(color1.green() - color2.green()) +
                abs(color1.blue() - color2.blue()))
        return diff <= tolerance

    # SELECCIÓN DE GRUPO
    def group_selection(self, pos):
        """Selección de elementos en grupos"""
        items = self.scene.items(pos)
        if items:
            # Por ahora, selecciona el primer item (simulación de grupo)
            self.select_item(items[0])

    def group_selected_items(self):
        """Agrupa los items seleccionados"""
        if len(self.selected_items) > 1:
            # Crear un grupo (por ahora solo selección múltiple)
            QMessageBox.information(self.parent(), "Grupo", 
                                  f"{len(self.selected_items)} elementos agrupados")

    # ✏️ HERRAMIENTAS DE DIBUJO
    def add_pen_point(self, pos):
        """Añade punto con herramienta pluma"""
        self.pen_points.append(pos)
        
        # Dibujar punto visual
        point = QGraphicsEllipseItem(pos.x()-2, pos.y()-2, 4, 4)
        point.setBrush(QBrush(Qt.blue))
        point.setPen(QPen(Qt.NoPen))
        self.scene.addItem(point)
        self.pen_temp_points.append(point)
        
        # Conectar puntos con líneas
        if len(self.pen_points) > 1:
            prev_pos = self.pen_points[-2]
            line = QGraphicsLineItem(prev_pos.x(), prev_pos.y(), pos.x(), pos.y())
            line.setPen(QPen(QColor(0, 100, 200), 1))
            self.scene.addItem(line)
            self.pen_temp_lines.append(line)
        
        # Cerrar automáticamente si está cerca del primer punto
        if len(self.pen_points) > 2:
            first_point = self.pen_points[0]
            distance = math.sqrt((pos.x() - first_point.x())**2 + (pos.y() - first_point.y())**2)
            if distance < 15:  # Umbral para cerrar
                self.complete_pen_path()

    def complete_pen_path(self):
        """Completa el path de la pluma"""
        if len(self.pen_points) >= 2:
            # Crear path permanente
            path = QPainterPath()
            path.moveTo(self.pen_points[0])
            
            for point in self.pen_points[1:]:
                path.lineTo(point)
            
            # Cerrar el path si hay suficientes puntos
            if len(self.pen_points) >= 3:
                path.closeSubpath()
            
            path_item = QGraphicsPathItem(path)
            path_item.setPen(QPen(QColor(0, 100, 200), 2))
            path_item.setBrush(QBrush(QColor(0, 100, 200, 50)))
            path_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            path_item.setFlag(QGraphicsItem.ItemIsMovable, True)
            
            self.scene.addItem(path_item)
            
            # Limpiar elementos temporales
            self.clear_pen_temp_items()

    def clear_pen_temp_items(self):
        """Limpia elementos temporales de la pluma"""
        for line in self.pen_temp_lines:
            if line in self.scene.items():
                self.scene.removeItem(line)
        for point in self.pen_temp_points:
            if point in self.scene.items():
                self.scene.removeItem(point)
        
        self.pen_temp_lines = []
        self.pen_temp_points = []
        self.pen_points = []

    def start_pencil_drawing(self, pos):
        """Inicia dibujo con lápiz"""
        self.pencil_drawing = True
        self.pencil_path = QPainterPath()
        self.pencil_path.moveTo(pos)
        
        self.current_pencil_item = QGraphicsPathItem()
        pen = QPen(QColor(255, 100, 0), 3)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.current_pencil_item.setPen(pen)
        self.current_pencil_item.setPath(self.pencil_path)
        
        self.scene.addItem(self.current_pencil_item)

    def update_pencil_drawing(self, pos):
        """Actualiza dibujo con lápiz"""
        if self.pencil_path and self.current_pencil_item:
            self.pencil_path.lineTo(pos)
            self.current_pencil_item.setPath(self.pencil_path)

    def finish_pencil_drawing(self):
        """Finaliza dibujo con lápiz"""
        self.pencil_drawing = False
        if self.current_pencil_item:
            self.current_pencil_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.current_pencil_item.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        self.current_pencil_item = None
        self.pencil_path = None

    def start_brush_drawing(self, pos):
        """Inicia dibujo con pincel"""
        self.brush_drawing = True
        self.brush_path = QPainterPath()
        self.brush_path.moveTo(pos)
        
        self.current_brush_item = QGraphicsPathItem()
        pen = QPen(self.brush_color, self.brush_size)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.current_brush_item.setPen(pen)
        self.current_brush_item.setPath(self.brush_path)
        
        self.scene.addItem(self.current_brush_item)

    def update_brush_drawing(self, pos):
        """Actualiza dibujo con pincel"""
        if self.brush_path and self.current_brush_item:
            self.brush_path.lineTo(pos)
            self.current_brush_item.setPath(self.brush_path)

    def finish_brush_drawing(self):
        """Finaliza dibujo con pincel"""
        self.brush_drawing = False
        if self.current_brush_item:
            self.current_brush_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.current_brush_item.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        self.current_brush_item = None
        self.brush_path = None

    def start_erasing(self, pos):
        """Inicia borrado"""
        self.erasing = True
        self.erase_at_position(pos)

    def update_erasing(self, pos):
        """Actualiza borrado durante movimiento"""
        if self.erasing:
            self.erase_at_position(pos)

    def erase_at_position(self, pos):
        """Borra elementos en la posición dada"""
        # Crear área de borrado
        eraser_rect = QRectF(pos.x() - self.eraser_size/2, pos.y() - self.eraser_size/2,
                           self.eraser_size, self.eraser_size)
        
        items = self.scene.items(eraser_rect, Qt.IntersectsItemShape)
        for item in items:
            if isinstance(item, (QGraphicsPathItem, QGraphicsLineItem)):
                self.scene.removeItem(item)
                if item in self.selected_items:
                    self.selected_items.remove(item)

    def finish_erasing(self):
        """Finaliza borrado"""
        self.erasing = False

    def start_width_adjustment(self, pos):
        """Inicia ajuste de grosor de trazo"""
        items = self.scene.items(pos)
        if items:
            item = items[0]
            if hasattr(item, 'pen'):
                current_pen = item.pen()
                new_width = current_pen.width() + 1
                if new_width > 10:  # Límite máximo
                    new_width = 1
                
                new_pen = QPen(current_pen.color(), new_width)
                item.setPen(new_pen)

    def wheelEvent(self, event):
        """Maneja el zoom con la rueda del mouse"""
        factor = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    # MÉTODOS UTILITARIOS
    def get_selected_items(self):
        """Retorna la lista de items seleccionados"""
        return self.selected_items

    def clear_canvas(self):
        """Limpia todo el canvas"""
        self.scene.clear()
        self.selected_items = []
        self.clear_selection_state()
        self.clear_drawing_state()

    def set_brush_properties(self, size=None, color=None):
        """Configura propiedades del pincel"""
        if size is not None:
            self.brush_size = size
        if color is not None:
            self.brush_color = color

    def set_eraser_size(self, size):
        """Configura el tamaño del borrador"""
        self.eraser_size = size
        self.update_eraser_cursor()
        if self.current_tool == "eraser":
            self.setCursor(self.eraser_cursor)

    def set_magic_wand_tolerance(self, tolerance):
        """Configura la tolerancia de la varita mágica"""
        self.magic_wand_tolerance = tolerance

    def set_snap_to_grid(self, enabled):
        """Activa/desactiva el ajuste a cuadrícula"""
        self.snap_to_grid = enabled

    def set_grid_size(self, size):
        """Configura el tamaño de la cuadrícula"""
        self.grid_size = size
        # EN AdvancedIllustratorCanvas, agregar:
    def setup_android_coordinates(self):
        """Configura el sistema de coordenadas Android"""
        self.android_density = 3.0
        self.android_width_dp = 411
        self.android_height_dp = 731
        
    def snap_to_android_grid(self, point):
        """Ajusta a grid de 8dp como Android Studio"""
        grid_size_dp = 8
        grid_size_px = grid_size_dp * self.android_density
        
        x = round(point.x() / grid_size_px) * grid_size_px
        y = round(point.y() / grid_size_px) * grid_size_px
        return QPointF(x, y)
class HojaAIPanel(QDockWidget):
    """Panel Hoja_AI - Canvas blanco con dimensiones de celular y controles de zoom"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # DIMENSIONES POR DEFECTO DE CELULAR (Pixel 4)
        self.device_config = {
            'width_dp': 411,
            'height_dp': 731,  
            'density': 3.0
        }
        
        self.android_width_px = int(self.device_config['width_dp'] * self.device_config['density'])
        self.android_height_px = int(self.device_config['height_dp'] * self.device_config['density'])
        
        # Configuración de zoom
        self.zoom_level = 1.0
        self.zoom_step = 0.2
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)  
        layout.setSpacing(0)

        # CONTENEDOR PRINCIPAL CON FONDO BLANCO
        container = QWidget()
        container.setStyleSheet("background-color: white; border: none;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.setAlignment(Qt.AlignCenter)

        # CANVAS BLANCO CON DIMENSIONES DE CELULAR
        self.canvas = AdvancedIllustratorCanvas(self)
        
        # Contenedor del canvas con scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 12px;
                margin: 0px;
            }
        """)
        
        # Widget central para el canvas
        self.canvas_widget = QWidget()
        self.canvas_widget.setFixedSize(self.android_width_px, self.android_height_px)
        self.canvas_widget.setStyleSheet("background-color: white; border: 1px solid #e0e0e0;")
        
        canvas_layout = QVBoxLayout(self.canvas_widget)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.addWidget(self.canvas)
        
        self.scroll_area.setWidget(self.canvas_widget)
        container_layout.addWidget(self.scroll_area)

        # BOTONES DE ZOOM EN ESQUINA INFERIOR DERECHA
        self.setup_zoom_controls(container)

        layout.addWidget(container)
        main_widget.setLayout(layout)
        self.setWidget(main_widget)

        # CONFIGURACIÓN INICIAL
        self.setup_canvas()
        
        # Conectar eventos de rueda del mouse para zoom
        self.canvas.wheelEvent = self.canvas_zoom_event

    def setup_zoom_controls(self, parent):
        """Configura los botones de zoom en la esquina inferior derecha"""
        # Contenedor flotante para los botones de zoom
        self.zoom_container = QWidget(parent)
        self.zoom_container.setFixedSize(100, 40)
        self.zoom_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
        """)
        
        zoom_layout = QHBoxLayout(self.zoom_container)
        zoom_layout.setContentsMargins(5, 5, 5, 5)
        zoom_layout.setSpacing(5)

        # Botón de zoom out (-)
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setFixedSize(30, 30)
        self.zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f8f8;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border: 1px solid #aaaaaa;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #aaaaaa;
            }
        """)
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        # Label de porcentaje de zoom
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedSize(40, 30)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        self.zoom_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 11px;
                font-weight: bold;
                color: #333333;
            }
        """)

        # Botón de zoom in (+)
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(30, 30)
        self.zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f8f8;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border: 1px solid #aaaaaa;
            }
            QPushButton:pressed {
                background-color: #d8d8d8;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #aaaaaa;
            }
        """)
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.zoom_in_btn)

        # Posicionar en esquina inferior derecha
        self.update_zoom_controls_position()

    def update_zoom_controls_position(self):
        """Actualiza la posición de los controles de zoom"""
        if hasattr(self, 'zoom_container'):
            # Posicionar en esquina inferior derecha con margen
            margin = 10
            x_pos = self.width() - self.zoom_container.width() - margin
            y_pos = self.height() - self.zoom_container.height() - margin
            self.zoom_container.move(x_pos, y_pos)

    def resizeEvent(self, event):
        """Maneja el redimensionamiento de la ventana"""
        super().resizeEvent(event)
        self.update_zoom_controls_position()

    def setup_canvas(self):
        """Configura el canvas con dimensiones de celular"""
        # Fondo blanco
        self.canvas.setStyleSheet("background-color: white; border: none;")
        
        # Configurar grid para diseño mobile
        self.canvas.snap_to_grid = True
        self.canvas.grid_size = 8 * self.device_config['density']  # 8dp grid
        
        # Configurar coordenadas Android si existe el método
        if hasattr(self.canvas, 'setup_android_coordinates'):
            self.canvas.setup_android_coordinates()
        
        # Agregar guidelines de Material Design
        self.add_mobile_guidelines()
        
        # Actualizar estado de botones de zoom
        self.update_zoom_buttons()

    def add_mobile_guidelines(self):
        """Agrega guidelines para diseño mobile"""
        guideline_style = QPen(QColor(200, 200, 200, 100), 1, Qt.DashLine)
        
        # Guidelines de 16dp (márgenes estándar)
        margin_16dp = 16 * self.device_config['density']
        
        # Vertical izquierda
        line_left = QGraphicsLineItem(margin_16dp, 0, margin_16dp, self.android_height_px)
        line_left.setPen(guideline_style)
        self.canvas.scene.addItem(line_left)
        
        # Vertical derecha  
        line_right = QGraphicsLineItem(
            self.android_width_px - margin_16dp, 0, 
            self.android_width_px - margin_16dp, self.android_height_px
        )
        line_right.setPen(guideline_style)
        self.canvas.scene.addItem(line_right)
        
        # Guidelines horizontales
        line_top = QGraphicsLineItem(0, margin_16dp, self.android_width_px, margin_16dp)
        line_top.setPen(guideline_style)
        self.canvas.scene.addItem(line_top)
        
        line_bottom = QGraphicsLineItem(
            0, self.android_height_px - margin_16dp, 
            self.android_width_px, self.android_height_px - margin_16dp
        )
        line_bottom.setPen(guideline_style)
        self.canvas.scene.addItem(line_bottom)

    def zoom_in(self):
        """Aumenta el zoom"""
        if self.zoom_level < self.max_zoom:
            self.zoom_level += self.zoom_step
            self.apply_zoom()

    def zoom_out(self):
        """Disminuye el zoom"""
        if self.zoom_level > self.min_zoom:
            self.zoom_level -= self.zoom_step
            self.apply_zoom()

    def apply_zoom(self):
        """Aplica el nivel de zoom actual"""
        # Aplicar transformación de escala al canvas
        transform = QTransform()
        transform.scale(self.zoom_level, self.zoom_level)
        self.canvas.setTransform(transform)
        
        # Actualizar label
        zoom_percentage = int(self.zoom_level * 100)
        self.zoom_label.setText(f"{zoom_percentage}%")
        
        # Actualizar estado de botones
        self.update_zoom_buttons()
        
        # Ajustar el tamaño del widget del canvas para el scroll
        scaled_width = int(self.android_width_px * self.zoom_level)
        scaled_height = int(self.android_height_px * self.zoom_level)
        self.canvas_widget.setFixedSize(scaled_width, scaled_height)

    def update_zoom_buttons(self):
        """Actualiza el estado de los botones de zoom según los límites"""
        self.zoom_out_btn.setEnabled(self.zoom_level > self.min_zoom)
        self.zoom_in_btn.setEnabled(self.zoom_level < self.max_zoom)

    def canvas_zoom_event(self, event):
        """Maneja el zoom con la rueda del mouse + Ctrl"""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom con Ctrl + Rueda
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Comportamiento normal de scroll
            super(AdvancedIllustratorCanvas, self.canvas).wheelEvent(event)

    def reset_zoom(self):
        """Restablece el zoom al 100%"""
        self.zoom_level = 1.0
        self.apply_zoom()

    def fit_to_screen(self):
        """Ajusta el zoom para que quepa en pantalla"""
        viewport_size = self.scroll_area.viewport().size()
        width_ratio = viewport_size.width() / self.android_width_px
        height_ratio = viewport_size.height() / self.android_height_px
        self.zoom_level = min(width_ratio, height_ratio) * 0.9  # 90% para margen
        self.apply_zoom()

    def set_device_dimensions(self, width_dp, height_dp, density=3.0):
        """Cambia las dimensiones del dispositivo"""
        self.device_config.update({
            'width_dp': width_dp,
            'height_dp': height_dp,
            'density': density
        })
        
        self.android_width_px = int(width_dp * density)
        self.android_height_px = int(height_dp * density)
        
        # Actualizar tamaño del canvas
        self.canvas_widget.setFixedSize(self.android_width_px, self.android_height_px)
        
        # Limpiar y recrear guidelines
        self.canvas.scene.clear()
        self.add_mobile_guidelines()
        
        # Resetear zoom
        self.reset_zoom()

    def get_current_zoom(self):
        """Retorna el nivel de zoom actual"""
        return self.zoom_level

    def on_element_selected(self, element):
        """Maneja la selección de elementos"""
        if element:
            x_dp = element.x() / self.device_config['density']
            y_dp = element.y() / self.device_config['density']
            print(f"📍 Elemento en: {x_dp:.1f}dp x {y_dp:.1f}dp")

    def sizeHint(self):
        return QSize(800, 600)
    
    def minimumSizeHint(self):
        return QSize(400, 300)