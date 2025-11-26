from .common_imports import *
from .utils import FileType
from .editor import EnhancedCodeEditor, LineNumberArea


class FileExplorerContextMenu(QMenu):
    """Menú contextual personalizado para el explorador de archivos"""
    
    def __init__(self, file_tree, file_model, project_path, project_language, parent=None):
        super().__init__("Explorador", parent)
        self.file_tree = file_tree
        self.file_model = file_model
        self.project_path = project_path
        self.project_language = project_language
        self.parent_widget = parent
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
        index = self.file_tree.currentIndex()
        if index.isValid():
            current_path = self.file_model.filePath(index)
            
            if os.path.isfile(current_path):
                current_path = os.path.dirname(current_path)
            
            dialog = NewFileDialog(
                self.project_language, 
                self.parent_widget, 
                current_path
            )
            
            if dialog.exec_() == QDialog.Accepted:
                self.create_file_from_dialog(dialog, current_path)
    
    def open_file(self):
        """Abre el archivo seleccionado en el editor"""
        index = self.file_tree.currentIndex()
        if index.isValid():
            file_path = self.file_model.filePath(index)
            
            if os.path.isfile(file_path):
                try:
                    if hasattr(self.parent_widget, 'code_editor'):
                        self.open_in_existing_editor(file_path)
  
                    else:
                        self.open_in_new_editor(file_path)
                        
                except Exception as e:
                    QMessageBox.critical(self.parent_widget, "Error", f"No se pudo abrir el archivo: {str(e)}")
            else:
                QMessageBox.information(self.parent_widget, "Información", "Seleccione un archivo, no una carpeta")
    
    def open_in_existing_editor(self, file_path):
        """Abre el archivo en un editor existente"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            self.parent_widget.code_editor.setPlainText(content)

            if hasattr(self.parent_widget.code_editor, 'set_highlighter'):
                self.parent_widget.code_editor.set_highlighter(file_path)
            
            # Opcional: Actualizar la ruta del archivo actual
            if hasattr(self.parent_widget, 'current_file_path'):
                self.parent_widget.current_file_path = file_path
            
            # Opcional: Mostrar nombre del archivo en la ventana
            file_name = os.path.basename(file_path)
            self.parent_widget.setWindowTitle(f"{file_name} - Tu IDE")
            
            print(f"Archivo abierto: {file_path}")
            
        except UnicodeDecodeError:
            # Manejar archivos binarios
            QMessageBox.warning(self.parent_widget, "Advertencia", 
                              "No se pueden abrir archivos binarios en el editor de texto")
        except PermissionError:
            QMessageBox.critical(self.parent_widget, "Error", 
                               "No tiene permisos para leer este archivo")
        except Exception as e:
            raise e
    
    def open_in_new_editor(self, file_path):
        """Abre el archivo en una nueva ventana de editor"""
        try:
            # Crear nuevo editor
            editor = EnhancedCodeEditor(self.parent_widget, theme="dark")
            
            # Leer el contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Establecer el contenido
            editor.setPlainText(content)
            
            # Configurar resaltado de sintaxis
            editor.set_highlighter(file_path)
            
            # Crear una ventana para el editor
            editor_window = QMainWindow(self.parent_widget)
            editor_window.setCentralWidget(editor)
            editor_window.setWindowTitle(f"{os.path.basename(file_path)} - Editor")
            editor_window.resize(800, 600)
            editor_window.show()
            
            print(f"Archivo abierto en nueva ventana: {file_path}")
            
        except UnicodeDecodeError:
            QMessageBox.warning(self.parent_widget, "Advertencia", 
                              "No se pueden abrir archivos binarios en el editor de texto")
        except Exception as e:
            raise e

    
    
    def create_file_from_dialog(self, dialog, current_path):
        """Crea el archivo basado en la selección del diálogo"""
        try:
            file_type = dialog.selected_type
            filename = dialog.selected_filename
            
            # Asegurar que el archivo tenga la extensión correcta
            if not any(filename.endswith(ext) for ext in file_type.extensions):
                filename += file_type.extensions[0]
            
            full_path = os.path.join(current_path, filename)
            
            # Crear el archivo con el contenido de la plantilla
            with open(full_path, 'w', encoding='utf-8') as f:
                # Procesar la plantilla para reemplazar placeholders
                content = file_type.template
                class_name = filename.replace(" ", "_").split('.')[0]
                content = content.replace("{class_name}", class_name)
                content = content.replace("{interface_name}", class_name)
                content = content.replace("{layout_name}", class_name.lower())
                
                f.write(content)
            
            # Actualizar el modelo de archivos
            self.file_model.setRootPath(self.project_path)
            QMessageBox.information(self.parent_widget, "Éxito", f"Archivo '{filename}' creado correctamente")
            
        except Exception as e:
            QMessageBox.critical(self.parent_widget, "Error", f"No se pudo crear el archivo: {str(e)}")
    
    def create_new_folder(self):
        """Crea una nueva carpeta en la ubicación actual"""
        index = self.file_tree.currentIndex()
        if index.isValid():
            current_path = self.file_model.filePath(index)

            if os.path.isfile(current_path):
                current_path = os.path.dirname(current_path)
            
            folder_name, ok = QInputDialog.getText(
                self.parent_widget, 
                "Nueva Carpeta", 
                "Nombre de la carpeta:",
                text="NuevaCarpeta"
            )
            
            if ok and folder_name:
                new_folder_path = os.path.join(current_path, folder_name)
                try:
                    os.makedirs(new_folder_path, exist_ok=False)
                    self.file_model.setRootPath(self.project_path)
                    QMessageBox.information(self.parent_widget, "Éxito", f"Carpeta '{folder_name}' creada correctamente")
                except FileExistsError:
                    QMessageBox.warning(self.parent_widget, "Error", f"La carpeta '{folder_name}' ya existe")
                except Exception as e:
                    QMessageBox.critical(self.parent_widget, "Error", f"No se pudo crear la carpeta: {str(e)}")
    
    def rename_item(self):
        """Renombra el archivo o carpeta seleccionado"""
        index = self.file_tree.currentIndex()
        if index.isValid():
            current_path = self.file_model.filePath(index)
            current_name = os.path.basename(current_path)
            
            new_name, ok = QInputDialog.getText(
                self.parent_widget, 
                "Renombrar", 
                "Nuevo nombre:",
                text=current_name
            )
            
            if ok and new_name and new_name != current_name:
                new_path = os.path.join(os.path.dirname(current_path), new_name)
                try:
                    os.rename(current_path, new_path)
                    self.file_model.setRootPath(self.project_path)
                    QMessageBox.information(self.parent_widget, "Éxito", "Elemento renombrado correctamente")
                except Exception as e:
                    QMessageBox.critical(self.parent_widget, "Error", f"No se pudo renombrar: {str(e)}")
    
    def delete_item(self):
        """Elimina el archivo o carpeta seleccionado"""
        index = self.file_tree.currentIndex()
        if index.isValid():
            current_path = self.file_model.filePath(index)
            item_name = os.path.basename(current_path)
            item_type = "archivo" if os.path.isfile(current_path) else "carpeta"
            
            reply = QMessageBox.question(
                self.parent_widget,
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
                    
                    self.file_model.setRootPath(self.project_path)
                    QMessageBox.information(self.parent_widget, "Éxito", f"{item_type.capitalize()} eliminado correctamente")
                except Exception as e:
                    QMessageBox.critical(self.parent_widget, "Error", f"No se pudo eliminar: {str(e)}")
    
    def copy_path(self):
        """Copia la ruta del archivo/carpeta al portapapeles"""
        index = self.file_tree.currentIndex()
        if index.isValid():
            current_path = self.file_model.filePath(index)
            QApplication.clipboard().setText(current_path)
            QMessageBox.information(self.parent_widget, "Portapapeles", "Ruta copiada al portapapeles")
    
    def open_in_system_explorer(self):
        """Abre la ubicación en el explorador del sistema"""
        index = self.file_tree.currentIndex()
        if index.isValid():
            current_path = self.file_model.filePath(index)

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
                QMessageBox.warning(self.parent_widget, "Error", f"No se pudo abrir el explorador: {str(e)}")

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

class NewFileDialog(QDialog):
    def __init__(self, project_language, parent=None, current_path=None):
        super().__init__(parent)
        self.project_language = project_language
        self.current_path = current_path 
        self.selected_type = None
        self.selected_filename = None
        
        # Inicializar atributos que se usarán en los métodos
        self.file_types_list = None
        self.filename_input = None
        self.preview_editor = None
        self.create_btn = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario del diálogo"""
        # Configuración básica del diálogo
        self.setWindowTitle("Nuevo Archivo")
        self.setModal(True)
        self.resize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Crear y configurar widgets
        self.setup_file_selection(main_layout)
        self.setup_preview(main_layout)
        self.setup_buttons(main_layout)
        
        # Cargar tipos de archivo después de que todos los widgets estén inicializados
        self.load_file_types()
        
    def setup_file_selection(self, main_layout):
        """Configura la sección de selección de tipo de archivo"""
        # Frame para selección de archivo
        selection_frame = QGroupBox("Seleccionar Tipo de Archivo")
        selection_layout = QHBoxLayout(selection_frame)
        
        # Lista de tipos de archivo
        self.file_types_list = QListWidget()
        self.file_types_list.setFixedWidth(300)
        self.file_types_list.currentItemChanged.connect(self.update_preview)
        selection_layout.addWidget(self.file_types_list)
        
        # Controles de nombre de archivo
        name_layout = QVBoxLayout()
        
        filename_label = QLabel("Nombre del archivo:")
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("ej: MiArchivo.java")
        self.filename_input.textChanged.connect(self.update_preview)
        
        name_layout.addWidget(filename_label)
        name_layout.addWidget(self.filename_input)
        name_layout.addStretch()
        
        selection_layout.addLayout(name_layout)
        main_layout.addWidget(selection_frame)
    
    def setup_preview(self, main_layout):
        """Configura la sección de vista previa"""
        preview_frame = QGroupBox("Vista Previa")
        preview_layout = QVBoxLayout(preview_frame)
        
        self.preview_editor = QTextEdit()
        self.preview_editor.setReadOnly(True)
        self.preview_editor.setFont(QFont("Courier New", 10))
        
        preview_layout.addWidget(self.preview_editor)
        main_layout.addWidget(preview_frame)
    
    def setup_buttons(self, main_layout):
        """Configura los botones de acción"""
        button_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("Crear Archivo")
        self.create_btn.clicked.connect(self.accept_selection)
        self.create_btn.setDefault(True)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def load_file_types(self):
        """Carga los tipos de archivo disponibles según el lenguaje del proyecto"""
        if not self.file_types_list:
            return
            
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
        # Verificar que los widgets estén inicializados
        if not hasattr(self, 'preview_editor') or not self.preview_editor:
            return
            
        current_item = self.file_types_list.currentItem()
        if not current_item:
            self.preview_editor.setPlainText("")
            return
            
        file_type = current_item.data(Qt.UserRole)
        filename = self.filename_input.text().strip() if self.filename_input else ""
        
        if not filename:
            self.preview_editor.setPlainText("")
            return

        preview = file_type.template

        class_name = filename.replace(" ", "_").replace(".java", "").replace(".kt", "").replace(".dart", "")
        preview = preview.replace("{class_name}", class_name)
        preview = preview.replace("{interface_name}", class_name)
        preview = preview.replace("{layout_name}", class_name.lower())
        
        self.preview_editor.setPlainText(preview)