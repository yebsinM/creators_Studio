# modules/workspace.py
import os
import sys

# Agrega la ruta de modules al path para imports relativos
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from .common_imports import *
from .code_generator import CodeGenerator, UIElement
from .highlighter import VSCodeHighlighter, HighlighterFactory
from .ai_panel import EnhancedAIChatPanel
from .file_explorer import FileExplorerContextMenu, FileIconDelegate, NewFileDialog
from .editor import EnhancedCodeEditor, LineNumberArea
from .illustrator_tools import IllustratorToolsPanel, AdvancedIllustratorCanvas, HojaAIPanel
from .effects_panel import EffectsPanel
from .elements_window import ElementsWindow
from .utils import FileType, WorkspacePreset, AIProvider
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
        
        # Configurar objectName para la ventana principal
        self.setObjectName("IllustratorWindow")
        
        self.code_generator = CodeGenerator(project_name)
        self.open_files = {}
        self.open_windows = {}
        self.current_editor = None
        
        self.tool_panel_action = QAction("Panel de Herramientas", self)
        self.tool_panel_action.setCheckable(True)
        self.tool_panel_action.setChecked(False)
        
        self.layers_panel_action = QAction("Panel de Capas", self)
        self.layers_panel_action.setCheckable(True)
        self.layers_panel_action.setChecked(False)
        
        self.color_panel_action = QAction("Panel de Colores", self)
        self.color_panel_action.setCheckable(True)
        self.color_panel_action.setChecked(False)
        
        self.ai_panel_action = QAction("Panel de IA", self)
        self.ai_panel_action.setCheckable(True)
        self.ai_panel_action.setChecked(True)
        
        self.explorer_panel_action = QAction("Explorador de Archivos", self)
        self.explorer_panel_action.setCheckable(True)
        self.explorer_panel_action.setChecked(True)
        
        self.illustrator_tools_action = QAction("Herramientas Illustrator", self)
        self.illustrator_tools_action.setCheckable(True)
        self.illustrator_tools_action.setChecked(False)
        
        self.effects_panel_action = QAction("Efectos Android", self)
        self.effects_panel_action.setCheckable(True)
        self.effects_panel_action.setChecked(False)
        
        # Crear paneles con objectName
        self.create_illustrator_tools_panel()
        self.create_effects_panel()
        
        self.setup_workspace()
        self.create_workspace_presets()
        self.setup_ui()
        self.setup_shortcuts()

        self.setup_initial_layout()
        
        self.create_menu_bar() 
        self.setup_language_specific_features()
        self.setup_context_menu()
        
        # Restaurar estado de la ventana al final de la inicialización
        QTimer.singleShot(100, self.restore_window_state)
    def setup_initial_layout(self):
        """Configura el layout inicial SOLO con paneles que existen"""
        try:
            print("🔧 Configurando layout inicial...")
            
            # ✅ SOLO paneles que sabemos que existen
            panels_to_add = [
                ('illustrator_tools_dock', Qt.LeftDockWidgetArea),
                ('ai_panel', Qt.RightDockWidgetArea),
                ('file_explorer_dock', Qt.LeftDockWidgetArea)
            ]
            
            added_panels = 0
            for panel_name, area in panels_to_add:
                if hasattr(self, panel_name):
                    panel = getattr(self, panel_name)
                    if panel is not None:
                        self.addDockWidget(area, panel)
                        print(f"✅ {panel_name} agregado al área {area}")
                        added_panels += 1
                    else:
                        print(f"⚠️ {panel_name} es None")
                else:
                    print(f"⚠️ {panel_name} no existe")
                    
            print(f"✅ Layout configurado: {added_panels} paneles agregados")
            
        except Exception as e:
            print(f"❌ Error configurando layout: {e}")
     
    def resizeEvent(self, event):
        """Maneja el redimensionamiento de la ventana principal"""
        super().resizeEvent(event)
        
        if hasattr(self, 'central_splitter') and self.central_splitter:
            total_width = self.width()
            if total_width > 0:
                left_width = max(250, min(350, total_width * 0.2))
                right_width = max(250, min(350, total_width * 0.2))
                center_width = total_width - left_width - right_width - self.central_splitter.handleWidth() * 2
                
                if center_width > self.hoja_ai_widget.phone_width:  
                    sizes = [int(left_width), int(center_width), int(right_width)]
                    self.central_splitter.setSizes(sizes)
    def setup_hoja_ai(self):
        """Configura el panel Hoja_AI como centro de la interfaz"""
        if hasattr(self, 'emulator_container'):
            self.tab_widget.removeTab(0)
        
        self.hoja_ai_panel = HojaAIPanel(self)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.hoja_ai_panel)
        self.setCentralWidget(central_widget)
 
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

    def setup_hoja_ai_in_current_class(self):
        """Integra Hoja_AI en la clase IllustratorWindow existente"""
        
        if hasattr(self, 'emulator_layout'):
            for i in reversed(range(self.emulator_layout.count())): 
                self.emulator_layout.itemAt(i).widget().setParent(None)

            self.hoja_ai = AdvancedIllustratorCanvas(self)
            self.emulator_layout.addWidget(self.hoja_ai)

            self.tab_widget.setTabText(0, "Hoja_AI")
            self.tab_widget.setTabToolTip(0, "Lienzo profesional de diseño vectorial")
            
            self.hoja_ai.elementSelected.connect(self.on_canvas_element_selected)

    def on_canvas_element_selected(self, element):
        """Maneja la selección de elementos en el canvas"""

        if hasattr(self, 'properties_panel'):
            self.update_properties_panel(element)

        if hasattr(self, 'effects_panel'):
            self.effects_panel.update_for_element(element)

        if hasattr(self, 'layers_list'):
            self.update_layers_selection(element)
    def create_illustrator_tools_panel(self):
        """Crea el panel de herramientas de Illustrator CORREGIDO"""
        self.illustrator_tools_panel = IllustratorToolsPanel(self)
        self.illustrator_tools_panel.setObjectName("IllustratorToolsPanel")

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
        self.effects_panel.setObjectName("EffectsPanel")
        
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

        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
    
    def show_file_explorer_context_menu(self, position):
        """Muestra el menú contextual en el explorador de archivos"""
        index = self.file_tree.indexAt(position)
        if not index.isValid():
            current_path = self.project_path
        else:
            current_path = self.file_model.filePath(index)

            if os.path.isfile(current_path):
                current_path = os.path.dirname(current_path)

        context_menu = FileExplorerContextMenu(
            self.file_tree, 
            self.file_model, 
            self.project_path, 
            self.project_language, 
            self
        )
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

    # MODIFICAR el método setup_ui para usar el nuevo enfoque
    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # SPLITTER HORIZONTAL PARA CÓDIGO Y DISEÑO (como Android Studio)
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # 1. PARTE IZQUIERDA: PESTAÑAS DE CÓDIGO
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #555555;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #333333;
                color: white;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #BB86FC;
                color: black;
            }
            QTabBar::tab:hover {
                background-color: #555555;
            }
        """)
        
        # 2. PARTE DERECHA: HOJA_AI (DISEÑO)
        self.hoja_ai_panel = HojaAIPanel(self)
        
        # Agregar al splitter
        self.main_splitter.addWidget(self.tab_widget)
        self.main_splitter.addWidget(self.hoja_ai_panel)
        
        # Configurar proporciones (50% código, 50% diseño)
        self.main_splitter.setSizes([600, 600])
        
        # Agregar splitter al layout principal
        self.main_layout.addWidget(self.main_splitter)
        
        # ✅ CORREGIDO: Crear SOLO los paneles esenciales primero
        print("🔧 Creando paneles esenciales...")
        
        # PANELES ESENCIALES (los que sabemos que funcionan)
        self.create_illustrator_tools_panel()  # Panel de herramientas Illustrator
        self.create_ai_panel()                 # Panel de IA
        self.create_file_explorer_panel()      # Explorador de archivos
        
        # ❌ COMENTADO TEMPORALMENTE: Paneles que pueden causar problemas
        # self.create_tool_panel()
        # self.create_layers_panel()
        # self.create_color_panel()
        # self.create_brushes_panel()
        # self.create_character_panel()    # ← POSIBLE PROBLEMA
        # self.create_paragraph_panel()
        # self.create_effects_panel()
        
        # ✅ PRIMERO: Configurar el layout con paneles que existen
        self.setup_initial_layout()
        
        # ✅ LUEGO: Crear menús y conexiones
        self.create_menu_bar()
        self.connect_hoja_ai_signals()
        
        # ✅ FINALMENTE: Limpiar ventanas ocultas
        self.cleanup_hidden_windows()
        
        self.statusBar().showMessage("✅ Ready | Modo Android Studio: Código ←→ Diseño")
        
        print("🎨 Interfaz configurada correctamente")
    
    def cleanup_hidden_windows(self):
        """Limpia ventanas que puedan estar ocultas o en segundo plano"""
        print("🧹 Limpiando ventanas ocultas...")
        
        try:
            # Obtener todas las ventanas hijas
            children = self.findChildren(QDockWidget)
            print(f"🔍 Encontrados {len(children)} dock widgets")
            
            for i, child in enumerate(children):
                print(f"  {i+1}. {child.windowTitle()} - Visible: {child.isVisible()}")
                
            # Buscar y cerrar diálogos ocultos
            dialogs = self.findChildren(QDialog)
            for dialog in dialogs:
                if not dialog.isVisible() or dialog.isHidden():
                    print(f"🗑️ Cerrando diálogo oculto: {dialog.windowTitle()}")
                    dialog.reject()
                    dialog.close()
                    
            print("✅ Limpieza de ventanas completada")
            
        except Exception as e:
            print(f"❌ Error en limpieza de ventanas: {e}")

    def closeEvent(self, event):
        """Maneja el cierre de la ventana - Cierra todas las ventanas hijas"""
        print("🔒 Cerrando ventana Illustrator...")
        
        try:
            # Cerrar todos los dock widgets explícitamente
            docks_to_close = [
                'tools_dock', 'ai_panel', 'properties_dock', 'layers_dock',
                'color_dock', 'brushes_dock', 'character_dock', 'paragraph_dock',
                'file_explorer_dock', 'illustrator_tools_dock', 'effects_dock'
            ]
            
            for dock_name in docks_to_close:
                if hasattr(self, dock_name):
                    dock = getattr(self, dock_name)
                    if dock:
                        print(f"🔒 Cerrando {dock_name}")
                        dock.close()
                        dock.setParent(None)
            
            # Forzar cierre de cualquier ventana restante
            for child in self.findChildren(QWidget):
                if child != self and child.isWindow():
                    child.close()
                    
            print("✅ Ventana Illustrator cerrada correctamente")
            event.accept()
            
        except Exception as e:
            print(f"❌ Error cerrando ventana: {e}")
            event.accept()  # Aceptar el cierre de todas formas
    def create_hoja_ai_panel(self):
        """Crea el panel Hoja_AI como un QDockWidget normal pero con visibilidad forzada"""
        self.hoja_ai_panel = QDockWidget("Hoja_AI - Lienzo Profesional", self)
        self.hoja_ai_panel.setObjectName("HojaAIPanel")
        self.hoja_ai_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | 
                                        Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        
        # Crear el contenido de Hoja_AI
        hoja_ai_content = HojaAIPanel(self)
        self.hoja_ai_panel.setWidget(hoja_ai_content)
        
        # Configurar como los demás paneles pero visible por defecto
        self.hoja_ai_panel.setFeatures(
            QDockWidget.DockWidgetMovable | 
            QDockWidget.DockWidgetClosable |
            QDockWidget.DockWidgetFloatable
        )
        
        # FORZAR VISIBILIDAD INICIAL
        self.hoja_ai_panel.setVisible(True)
        
        # Añadir al área central como un dock normal
        self.addDockWidget(Qt.LeftDockWidgetArea, self.hoja_ai_panel)
    def setup_java_features(self):
        """Configura características específicas para Java"""
        try:
            print("🔧 Configurando características Java...")
            
            # ✅ CORREGIR: Usar self.ai_widget en lugar de self.ai_panel
            if hasattr(self, 'ai_widget') and self.ai_widget:
                welcome_message = """🚀 **MODO JAVA ACTIVADO**

    📋 **Características disponibles:**
    • 📁 Gestión de proyectos Maven/Gradle
    • ☕ Generación de clases Java
    • 🏗️ Patrones de diseño automáticos
    • 🔧 Refactorización inteligente
    • 📊 Análisis de código estático

    💡 **Comandos útiles:**
    • 'crea clase Usuario' - Genera clase Java
    • 'genera getters/setters' - Crea métodos de acceso
    • 'implementa patrón Singleton' - Aplica patrón de diseño
    • 'analiza este código' - Revisa calidad de código

    📂 **Directorio del proyecto:** {}
    """.format(self.project_path)
                
                self.ai_widget.chat_history.setPlainText("")
                self.ai_widget.chat_history.append(welcome_message)
                
            # Configurar otras características Java...
            self.setup_java_templates()
            self.setup_java_shortcuts()
            
            print("✅ Características Java configuradas")
            
        except Exception as e:
            print(f"❌ Error configurando características Java: {e}")
    def setup_java_templates(self):
        """Configura plantillas para Java"""
        try:
            print("🔧 Configurando plantillas Java...")
            # Aquí puedes agregar plantillas específicas para Java
            self.java_templates = {
                "class": "public class {name} {{\n    // TODO: Implementar clase\n}}",
                "interface": "public interface {name} {{\n    // TODO: Definir métodos\n}}",
                "main": "public class {name} {{\n    public static void main(String[] args) {{\n        // TODO: Código principal\n    }}\n}}"
            }
            print("✅ Plantillas Java configuradas")
        except Exception as e:
            print(f"❌ Error configurando plantillas Java: {e}")

    def setup_java_shortcuts(self):
        """Configura atajos para Java"""
        try:
            print("🔧 Configurando atajos Java...")
            # Aquí puedes agregar atajos de teclado específicos para Java
            print("✅ Atajos Java configurados")
        except Exception as e:
            print(f"❌ Error configurando atajos Java: {e}")
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
        """Crea el panel de herramientas"""
        try:
            print("🔧 Creando panel de herramientas...")
            self.tools_dock = QDockWidget("🛠️ Herramientas", self)
            tools_widget = QWidget()
            layout = QVBoxLayout(tools_widget)
            
            # Agregar herramientas básicas
            tools = ["Selección", "Texto", "Formas", "Líneas"]
            for tool in tools:
                btn = QPushButton(tool)
                layout.addWidget(btn)
            
            layout.addStretch()
            self.tools_dock.setWidget(tools_widget)
            self.tools_dock.setMaximumWidth(200)
            print("✅ Panel de herramientas creado")
        except Exception as e:
            print(f"❌ Error creando panel de herramientas: {e}")

    def create_properties_panel(self):
        """Crea el panel de propiedades"""
        try:
            print("🔧 Creando panel de propiedades...")
            self.properties_dock = QDockWidget("📋 Propiedades", self)
            properties_widget = QLabel("Panel de propiedades")
            self.properties_dock.setWidget(properties_widget)
            self.properties_dock.setMaximumWidth(250)
            print("✅ Panel de propiedades creado")
        except Exception as e:
            print(f"❌ Error creando panel de propiedades: {e}")

    def create_layers_panel(self):
        self.layers_panel = QDockWidget("Capas", self)
        self.layers_panel.setObjectName("LayersPanel") 
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
        self.color_panel.setObjectName("ColorPanel")
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
        self.brushes_panel.setObjectName("BrushesPanel")
        brushes_widget = QWidget()
        brushes_widget.setLayout(QVBoxLayout())
        self.brushes_panel.setWidget(brushes_widget)

    def create_character_panel(self):
        self.character_panel = QDockWidget("Carácter", self)
        self.character_panel.setObjectName("CharacterPanel")
        character_widget = QWidget()
        character_widget.setLayout(QVBoxLayout())
        self.character_panel.setWidget(character_widget)
    def create_paragraph_panel(self):
        self.paragraph_panel = QDockWidget("Párrafo", self)
        self.paragraph_panel.setObjectName("ParagraphPanel")
        self.paragraph_panel.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.paragraph_panel.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        
        paragraph_widget = QWidget()
        paragraph_widget.setLayout(QVBoxLayout())
        self.paragraph_panel.setWidget(paragraph_widget)
        
        self.addDockWidget(Qt.RightDockWidgetArea, self.paragraph_panel)
        self.paragraph_panel.setVisible(False)  
    def create_ai_panel(self):
        """Crea y configura el panel de IA como dock widget"""
        try:
            print("🔧 Creando panel de IA...")
            
            # Crear el panel de IA como QWidget normal
            self.ai_widget = EnhancedAIChatPanel(self.code_generator, self)  # ✅ Guardar referencia
            
            # Crear el dock widget contenedor
            self.ai_panel = QDockWidget("🤖 AI Assistant", self)
            self.ai_panel.setWidget(self.ai_widget)  # ✅ Usar la referencia guardada
            self.ai_panel.setFeatures(
                QDockWidget.DockWidgetMovable | 
                QDockWidget.DockWidgetFloatable | 
                QDockWidget.DockWidgetClosable
            )
            self.ai_panel.setMinimumWidth(350)
            self.ai_panel.setMaximumWidth(500)
            
            print("✅ Panel de IA creado correctamente")
            
        except Exception as e:
            print(f"❌ Error creando panel de IA: {e}")
    def create_file_explorer_panel(self):
        """Crea el panel del explorador de archivos con mejoras"""
        self.file_explorer_panel = QDockWidget("Explorador de Archivos", self)
        self.file_explorer_panel.setObjectName("FileExplorerPanel")  # ¡IMPORTANTE!
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

        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
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
     
        self.hoja_ai_action = QAction("Hoja_AI - Lienzo", self)
        self.hoja_ai_action.setCheckable(True)
        self.hoja_ai_action.setChecked(True)  # Visible por defecto
        self.hoja_ai_action.triggered.connect(self.toggle_hoja_ai_panel)
        panels_menu.addAction(self.hoja_ai_action)

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
        self.ai_panel_action.setChecked(True)  # INICIALMENTE ACTIVADO
        self.ai_panel_action.triggered.connect(self.toggle_ai_panel)
        panels_menu.addAction(self.ai_panel_action)
            
        self.explorer_panel_action = QAction("Explorador de Archivos", self)
        self.explorer_panel_action.setCheckable(True)
        self.explorer_panel_action.setChecked(True)  # INICIALMENTE ACTIVADO
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

    # 2. AGREGAR EL MÉTODO TOGGLE PARA HOJA_AI
    def toggle_hoja_ai_panel(self):
        """Alternar visibilidad del panel Hoja_AI"""
        if hasattr(self, 'hoja_ai_panel'):
            if self.hoja_ai_panel.isVisible():
                self.hoja_ai_panel.setVisible(False)
                self.hoja_ai_action.setChecked(False)
            else:
                self.hoja_ai_panel.setVisible(True)
                self.hoja_ai_action.setChecked(True)
                # Asegurar que Hoja_AI ocupe el espacio central
                self.hoja_ai_panel.raise_()
    def dockLocationChanged(self, area):
        """Se llama cuando un dock es movido a otra área"""
        # Asegurar que Hoja_AI siempre tenga espacio para expandirse
        if hasattr(self, 'hoja_ai_panel') and self.hoja_ai_panel.isVisible():
            # Forzar actualización del layout
            QTimer.singleShot(100, self.update_dock_layout)

    def update_dock_layout(self):
        """Actualizar el layout de los docks para optimizar el espacio"""
        # Esta función se puede expandir para lógica más compleja de layout
        pass
    def connect_hoja_ai_signals(self):
        """Conecta las señales de Hoja_AI con otros paneles"""
        if hasattr(self, 'hoja_ai_widget') and hasattr(self.hoja_ai_widget, 'canvas'):
            # Conectar selección de elementos con el panel de efectos
            if hasattr(self, 'effects_panel'):
                try:
                    self.hoja_ai_widget.canvas.elementSelected.connect(self.effects_panel.on_element_selected)
                    print("✅ Hoja_AI conectada con EffectsPanel")
                except Exception as e:
                    print(f"❌ Error conectando Hoja_AI con EffectsPanel: {e}")
            
            # Conectar con herramientas de Illustrator
            if hasattr(self, 'illustrator_tools_panel'):
                try:
                    # Conectar la selección de herramientas
                    pass
                except Exception as e:
                    print(f"❌ Error conectando Hoja_AI con IllustratorTools: {e}")
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
                                    ["Hoja_AI", "File Explorer", "AI Assistant"]),
            "Minimal": WorkspacePreset("Minimal", "left", 
                                    ["Hoja_AI", "File Explorer"]),
            "Design": WorkspacePreset("Design", "left", 
                                    ["Hoja_AI", "IllustratorTools", "Effects", "Color"]),
            "Development": WorkspacePreset("Development", "right", 
                                        ["Hoja_AI", "AI Assistant", "File Explorer"])
        }
    def toggle_tool_panel(self):
        self.tool_panel.setVisible(self.tool_panel_action.isChecked())

    def toggle_layers_panel(self):
        self.layers_panel.setVisible(self.layers_panel_action.isChecked())

    def toggle_color_panel(self):
        self.color_panel.setVisible(self.color_panel_action.isChecked())
    def toggle_explorer_panel(self):
        """Alternar visibilidad del explorador de archivos"""
        if self.file_explorer_panel.isVisible():
            self.file_explorer_panel.setVisible(False)
            self.explorer_panel_action.setChecked(False)
        else:
            self.file_explorer_panel.setVisible(True)
            self.explorer_panel_action.setChecked(True)

    def toggle_ai_panel(self):
        """Alternar visibilidad del panel de IA"""
        if self.ai_panel.isVisible():
            self.ai_panel.setVisible(False)
            self.ai_panel_action.setChecked(False)
        else:
            self.ai_panel.setVisible(True)
            self.ai_panel_action.setChecked(True)
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
                tab_data['is_modified'] = True
            else:
                self.tab_widget.setTabText(index, file_name)
                tab_data['is_modified'] = False
                
                # Verificar si todos los archivos están guardados
                any_modified = any(
                    data.get('is_modified', False) 
                    for data in self.open_files.values()
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
                "File Explorer": self.file_explorer_panel,
                "IllustratorTools": self.illustrator_tools_panel,
                "Effects": self.effects_panel
            }
            
            # Ocultar todos primero (excepto Hoja_AI que es central)
            for panel_name, panel in all_panels.items():
                if panel:
                    panel.setVisible(False)

            # Mostrar solo los del preset
            for panel_name in preset.panels:
                if panel_name in all_panels and all_panels[panel_name]:
                    all_panels[panel_name].setVisible(True)
            
            # Hoja_AI siempre visible en el centro
            if hasattr(self, 'hoja_ai_widget'):
                self.hoja_ai_widget.setVisible(True)
            
            # Actualizar estados de los actions
            self.hoja_ai_action.setChecked(True)  # Siempre checked pues es central
            self.explorer_panel_action.setChecked(self.file_explorer_panel.isVisible())
            self.ai_panel_action.setChecked(self.ai_panel.isVisible())
            self.tool_panel_action.setChecked(self.tool_panel.isVisible())
            self.layers_panel_action.setChecked(self.layers_panel.isVisible())
            self.color_panel_action.setChecked(self.color_panel.isVisible())
            self.illustrator_tools_action.setChecked(self.illustrator_tools_panel.isVisible())
            self.effects_panel_action.setChecked(self.effects_panel.isVisible())
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
        """Maneja el doble click en archivos - CORREGIDO"""
        if not index.isValid():
            return
            
        file_path = self.file_model.filePath(index)
        
        # Verificar que es un archivo y no una carpeta
        if os.path.isfile(file_path):
            print(f"Abriendo archivo: {file_path}")
            self.open_file_in_tab(file_path)
        else:
            # Si es una carpeta, expandir/colapsar
            if self.file_tree.isExpanded(index):
                self.file_tree.collapse(index)
            else:
                self.file_tree.expand(index)

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
        """Guarda un archivo"""
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
        """Actualiza el título de la pestaña"""
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
        """Abre un archivo y si es XML, lo carga en Hoja_AI"""
        # Verificar si el archivo ya está abierto
        if file_path in self.open_files:
            tab_data = self.open_files[file_path]
            index = self.tab_widget.indexOf(tab_data['widget'])
            self.tab_widget.setCurrentIndex(index)
            # Si es XML, actualizar Hoja_AI
            if file_path.lower().endswith('.xml'):
                self.load_xml_to_hoja_ai(file_path)
            return
        
        try:
            # Leer el contenido del archivo
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Crear widget de pestaña
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Crear editor de código
            editor = EnhancedCodeEditor(self, theme="dark")
            editor.setPlainText(content)
            
            # Configurar resaltado de sintaxis
            try:
                editor.set_highlighter(file_path)
            except Exception as e:
                print(f"Error configurando highlighter: {e}")
            
            # Conectar señal de modificación
            editor.document().modificationChanged.connect(
                lambda modified: self.on_file_modified(file_path, modified)
            )
            
            # Conectar cambios en tiempo real para XML
            if file_path.lower().endswith('.xml'):
                editor.textChanged.connect(
                    lambda: self.on_xml_changed(file_path, editor.toPlainText())
                )
            
            layout.addWidget(editor)
            tab_widget.setLayout(layout)

            # Agregar pestaña al tab widget
            file_name = os.path.basename(file_path)
            tab_index = self.tab_widget.addTab(tab_widget, file_name)
            self.tab_widget.setCurrentIndex(tab_index)
            self.tab_widget.setTabToolTip(tab_index, file_path)
            
            # Guardar información del archivo abierto
            tab_data = {
                'widget': tab_widget,
                'editor': editor,
                'file_path': file_path,
                'file_name': file_name,
                'is_modified': False,
                'is_xml': file_path.lower().endswith('.xml')
            }
            
            tab_widget.setProperty("tab_data", tab_data)
            self.open_files[file_path] = tab_data
            
            # Actualizar estado
            self.current_editor = editor
            
            # Si es XML, cargar en Hoja_AI
            if file_path.lower().endswith('.xml'):
                self.load_xml_to_hoja_ai(file_path)
                print(f"✅ XML cargado en Hoja_AI: {file_name}")
            
            print(f"✅ Archivo abierto: {file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")
    def load_xml_to_hoja_ai(self, file_path):
        """Carga el contenido XML en Hoja_AI para diseño visual"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                xml_content = f.read()
            
            # Actualizar Hoja_AI con el XML
            if hasattr(self, 'hoja_ai_panel') and hasattr(self.hoja_ai_panel, 'canvas'):
                self.hoja_ai_panel.canvas.set_xml_content(xml_content)
                self.hoja_ai_panel.setWindowTitle(f"Hoja_AI - {os.path.basename(file_path)}")
                print(f"🎨 XML cargado en lienzo: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"❌ Error cargando XML en Hoja_AI: {e}")

    def on_xml_changed(self, file_path, new_content):
        """Cuando se modifica un XML, actualizar Hoja_AI en tiempo real"""
        if file_path.lower().endswith('.xml'):
            try:
                if hasattr(self, 'hoja_ai_panel') and hasattr(self.hoja_ai_panel, 'canvas'):
                    self.hoja_ai_panel.canvas.set_xml_content(new_content)
                    print("🔄 Hoja_AI actualizada en tiempo real")
            except Exception as e:
                print(f"❌ Error actualizando Hoja_AI: {e}")

    def tab_changed(self, index):
        """Cuando se cambia de pestaña, actualizar Hoja_AI si es XML"""
        if index >= 0:
            widget = self.tab_widget.widget(index)
            if widget:
                tab_data = widget.property("tab_data")
                if tab_data:
                    self.current_editor = tab_data.get('editor')
                    file_path = tab_data.get('file_path', '')
                    
                    # Si es XML, cargar en Hoja_AI
                    if file_path.lower().endswith('.xml'):
                        self.load_xml_to_hoja_ai(file_path)
                        print(f"🔄 Cambiado a XML: {tab_data.get('file_name', '')}")
                    else:
                        # Si no es XML, limpiar Hoja_AI o mostrar mensaje
                        if hasattr(self, 'hoja_ai_panel') and hasattr(self.hoja_ai_panel, 'canvas'):
                            self.hoja_ai_panel.canvas.clear_canvas()
                            self.hoja_ai_panel.setWindowTitle("Hoja_AI - Selecciona un archivo XML")
                            print("🧹 Hoja_AI limpiada (no es XML)")
    def open_binary_file(self, file_path):
        """Abre archivos binarios en modo hexadecimal o muestra información"""
        try:
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Crear pestaña para archivo binario
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            
            info_text = QTextEdit()
            info_text.setReadOnly(True)
            info_text.setPlainText(
                f"Archivo binario: {file_name}\n"
                f"Tamaño: {file_size} bytes\n"
                f"Ruta: {file_path}\n\n"
                "Los archivos binarios no se pueden editar en este editor."
            )
            
            layout.addWidget(info_text)
            
            tab_index = self.tab_widget.addTab(tab_widget, f"🔒 {file_name}")
            self.tab_widget.setCurrentIndex(tab_index)
            
            # Guardar información
            tab_data = {
                'widget': tab_widget,
                'editor': None,  # No hay editor para binarios
                'file_path': file_path,
                'file_name': file_name,
                'is_modified': False,
                'is_binary': True
            }
            
            tab_widget.setProperty("tab_data", tab_data)
            self.open_files[file_path] = tab_data
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo binario:\n{str(e)}")
    def close_tab(self, index):
        """Cierra una pestaña específica"""
        if index < 0 or index >= self.tab_widget.count():
            return
            
        tab_widget = self.tab_widget.widget(index)
        if not tab_widget:
            return
            
        tab_data = tab_widget.property("tab_data")
        
        # VERIFICAR SI HAY CAMBIOS SIN GUARDAR SOLO SI EL EDITOR EXISTE
        if (tab_data and 'editor' in tab_data and 
            'file_path' in tab_data):
            
            editor = tab_data['editor']
            file_path = tab_data['file_path']
            
            # Verificar si hay cambios sin guardar SOLO si el editor existe
            if (editor is not None and 
                hasattr(editor, 'document') and 
                editor.document().isModified()):
                
                # Preguntar si guardar cambios
                reply = QMessageBox.question(
                    self,
                    "Cambios sin guardar",
                    f"¿Quieres guardar los cambios en {tab_data.get('file_name', 'el archivo')}?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save
                )
                
                if reply == QMessageBox.Save:
                    content = editor.toPlainText()
                    self.save_file(file_path, content)
                elif reply == QMessageBox.Cancel:
                    return
        
        # Eliminar de open_files
        for path, data in list(self.open_files.items()):
            if data.get('widget') == tab_widget:
                del self.open_files[path]
                break
        
        # Cerrar la pestaña
        self.tab_widget.removeTab(index)
        
        # Actualizar estado de las acciones
        if not self.open_files:
            self.save_action.setEnabled(False)
            self.save_as_action.setEnabled(False)
            self.close_tab_action.setEnabled(False)
    def show_enhanced_context_menu(self, editor, pos):
        """Menú contextual mejorado para el editor"""
        menu = QMenu(self)
        
        # Acciones básicas de edición
        undo_action = QAction("📝 Deshacer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(editor.undo)
        undo_action.setEnabled(editor.document().isUndoAvailable())
        menu.addAction(undo_action)
        
        redo_action = QAction("🔁 Rehacer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(editor.redo)
        redo_action.setEnabled(editor.document().isRedoAvailable())
        menu.addAction(redo_action)
        
        menu.addSeparator()
        
        cut_action = QAction("✂️ Cortar", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(editor.cut)
        cut_action.setEnabled(editor.textCursor().hasSelection())
        menu.addAction(cut_action)
        
        copy_action = QAction("📋 Copiar", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(editor.copy)
        copy_action.setEnabled(editor.textCursor().hasSelection())
        menu.addAction(copy_action)
        
        paste_action = QAction("📄 Pegar", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(editor.paste)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        select_all_action = QAction("⭐ Seleccionar todo", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(editor.selectAll)
        menu.addAction(select_all_action)
        
        menu.addSeparator()
        
        find_action = QAction("🔍 Buscar...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(lambda: self.show_find_dialog(editor))
        menu.addAction(find_action)
        
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
        if index >= 0:
            widget = self.tab_widget.widget(index)
            if widget:
                tab_data = widget.property("tab_data")
                if tab_data and 'editor' in tab_data:
                    self.current_editor = tab_data['editor']
                    print(f"Pestaña cambiada a: {tab_data.get('file_name', 'Desconocido')}")
                else:
                    self.current_editor = None
        else:
            self.current_editor = None
  
    def closeEvent(self, event):
        """Maneja el cierre de la ventana CORREGIDO"""
        try:
            # Verificar si hay cambios sin guardar
            unsaved_changes = False
            unsaved_files = []
            
            # Revisar todas las pestañas abiertas
            for i in range(self.tab_widget.count()):
                tab_widget = self.tab_widget.widget(i)
                if tab_widget:
                    tab_data = tab_widget.property("tab_data")
                    # VERIFICAR SI EXISTE tab_data Y SI TIENE UN EDITOR VÁLIDO
                    if tab_data and 'editor' in tab_data:
                        editor = tab_data['editor']
                        # VERIFICAR SI EL EDITOR EXISTE Y TIENE EL MÉTODO document()
                        if (editor is not None and 
                            hasattr(editor, 'document') and 
                            editor.document().isModified()):
                            unsaved_changes = True
                            file_name = tab_data.get('file_name', 'Sin nombre')
                            unsaved_files.append(file_name)
            
            if unsaved_changes:
                reply = QMessageBox.question(
                    self,
                    "Archivos sin guardar",
                    f"Los siguientes archivos tienen cambios sin guardar:\n" +
                    "\n".join(f"• {name}" for name in unsaved_files) +
                    "\n\n¿Estás seguro de que quieres salir?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Save:
                    # Guardar todos los archivos modificados
                    for i in range(self.tab_widget.count()):
                        tab_widget = self.tab_widget.widget(i)
                        if tab_widget:
                            tab_data = tab_widget.property("tab_data")
                            if (tab_data and 'editor' in tab_data and 
                                'file_path' in tab_data):
                                editor = tab_data['editor']
                                file_path = tab_data['file_path']
                                if (editor is not None and 
                                    hasattr(editor, 'document') and 
                                    editor.document().isModified()):
                                    content = editor.toPlainText()
                                    self.save_file(file_path, content)
                elif reply == QMessageBox.Cancel:
                    event.ignore()
                    return
            
            # Guardar configuración antes de cerrar (CORREGIDO)
            self.save_window_state()
            
            # Cerrar todos los procesos hijos si existen
            if hasattr(self, 'current_process') and self.current_process:
                try:
                    self.current_process.terminate()
                    self.current_process.waitForFinished(3000)
                except:
                    pass
            
            # Emitir señal de cierre
            self.closed.emit()
            event.accept()
            
        except Exception as e:
            print(f"Error en closeEvent: {e}")
            # En caso de error, aceptar el evento para permitir el cierre
            event.accept()
    def save_window_state(self):
        """Guarda el estado de la ventana CORREGIDO"""
        try:
            settings = QSettings("CreatorsStudio", "Workspace")
            settings.setValue("window_geometry", self.saveGeometry())
            
            # Verificar que todos los docks tengan objectName antes de guardar
            docks = self.findChildren(QDockWidget)
            for dock in docks:
                if not dock.objectName():
                    dock.setObjectName(f"DockWidget_{id(dock)}")  # Nombre temporal
            
            settings.setValue("window_state", self.saveState())
            settings.setValue("current_preset", self.current_preset)
            
        except Exception as e:
            print(f"Error guardando estado de ventana: {e}")

    def restore_window_state(self):
        """Restaura el estado de la ventana"""
        try:
            settings = QSettings("CreatorsStudio", "Workspace")
            
            geometry = settings.value("window_geometry")
            if geometry:
                self.restoreGeometry(geometry)
            
            state = settings.value("window_state")
            if state:
                self.restoreState(state)
            
            preset = settings.value("current_preset", "Default")
            if preset in self.workspace_presets:
                self.apply_workspace_preset(preset)
                
        except Exception as e:
            print(f"Error restaurando estado de ventana: {e}")




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

 
