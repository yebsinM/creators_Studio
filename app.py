import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import QSettings, Qt, QSize, Signal
from PySide6.QtGui import QFont
from ui.auth_window import AuthWindow, RegisterWindow
from ui.main_app import MainApp
from ui.entorno_java import IllustratorWindow
from config.database import SupabaseClient

class AppManager(QMainWindow):
    
    project_opened = Signal(str, str, str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Creators App")
        self.settings = QSettings("MyCompany", "CreatorsApp")
  
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_app = MainApp(self.show_auth, self.show_entorno_java)
        self.auth = AuthWindow(self.stack, self.handle_login_success) 
        self.register = RegisterWindow(self.stack)
        
        
        self.entorno_java = None  

        self.stack.addWidget(self.auth)
        self.stack.addWidget(self.register)
        self.stack.addWidget(self.main_app)

        self.set_auth_window_size()
        self.show_auth()

        self.load_window_state()
    def set_auth_window_size(self):
        """Tamaño pequeño fijo para auth (800x600)"""
        self.setFixedSize(800, 600)

    def set_main_app_size(self):
        """Tamaño mediano redimensionable para main app (1200x800 inicial)"""
        self.setFixedSize(0, 0) 
        self.setMinimumSize(1000, 650)
        self.resize(QSize(1200, 800))
        self.center_window()

    def center_window(self):
        """Centrar la ventana en la pantalla"""
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.size()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def load_window_state(self):
        """Cargar estado anterior de la ventana principal"""
        geometry = self.settings.value("main_window_geometry")
        if geometry:
            self.restoreGeometry(geometry)

    def save_window_state(self):
        """Guardar estado actual de la ventana principal"""
        self.settings.setValue("main_window_geometry", self.saveGeometry())

    def show_auth(self):
        """Mostrar ventana de autenticación (pequeña)"""
        self.set_auth_window_size()
        self.stack.setCurrentIndex(0)

    def show_main_app(self):
        """Mostrar aplicación principal (mediana)"""
        self.set_main_app_size()
        self.stack.setCurrentIndex(2)

    def show_entorno_java(self, name=None, path=None, lang=None):
        """Mostrar entorno Java (pantalla completa)"""
        if not self.entorno_java:
            self.entorno_java = IllustratorWindow(
                project_name=name or "Proyecto",
                project_path=path,
                project_language=lang or "Java"
            )
            self.entorno_java.closed.connect(self.handle_entorno_closed)
        self.hide()
        self.entorno_java.showMaximized()
        self.project_opened.emit(name or "Proyecto", path, lang or "Java")

    def handle_login_success(self):
        """Método que se llama cuando el login es exitoso"""
        self.show_main_app()

    def handle_entorno_closed(self):
        """Cuando se cierra el entorno Java"""
        self.show()
        self.entorno_java = None

    def closeEvent(self, event):
        self.save_window_state()
        super().closeEvent(event)

def main():
    try:
   
        SupabaseClient().get_client()
        
        app = QApplication(sys.argv)
        
      
        font = QFont()
        font.setPointSize(10)
        app.setFont(font)
        
        window = AppManager()
        app.aboutToQuit.connect(window.save_window_state)
        
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error de configuración: {e}")

if __name__ == "__main__":
    main()