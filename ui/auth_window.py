import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                              QPushButton, QMessageBox, QHBoxLayout, QStackedWidget,
                              QSpacerItem, QSizePolicy, QStyle, QFrame)
from PySide6.QtGui import (QFont, QPixmap, QIcon, QCursor, QLinearGradient, 
                          QPainter, QColor, QBrush)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QRadialGradient 
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent
from config.database import SupabaseClient
from datetime import datetime

import re




class PasswordLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.Password)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #0078D7;
            }
        """)
        self.toggle_password_btn = QPushButton(self)
        self.toggle_password_btn.setIcon(QIcon(os.path.join("assets", "eye-closed.png")))
        self.toggle_password_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_mode)
        self.update_button_position()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_button_position()
        
    def update_button_position(self):
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        button_size = self.toggle_password_btn.sizeHint()
        self.toggle_password_btn.move(
            self.rect().right() - frame_width - button_size.width() - 5,
            (self.rect().bottom() - button_size.height()) // 2
        )
        
    def toggle_password_mode(self):
        if self.echoMode() == QLineEdit.Password:
            self.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setIcon(QIcon(os.path.join("assets", "eye-open.png")))
        else:
            self.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setIcon(QIcon(os.path.join("assets", "eye-closed.png")))


class GradientWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            center = self.rect().center()
            radius = max(self.width(), self.height()) * 1.2 

            gradient = QRadialGradient(center, radius)

            gradient.setColorAt(0, QColor(50, 50, 50))   
            gradient.setColorAt(0.7, QColor(15, 15, 15))
            gradient.setColorAt(1, QColor(0, 0, 0))     

            painter.setRenderHint(QPainter.Antialiasing)
            painter.fillRect(self.rect(), QBrush(gradient))
        finally:
            painter.end()

class AuthWindow(QWidget):
    def __init__(self, stacked_widget, on_login_success):
        super().__init__()
        self.setFixedSize(800, 600)
        self.on_login_success = on_login_success  
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumSize(400, 500)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
 
        background = GradientWidget()
        background_layout = QVBoxLayout(background)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)

        center_container = QWidget()
        center_container.setFixedWidth(400) 
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(40, 40, 40, 40)
        center_layout.setSpacing(20)
        
       
        logo = QLabel("CREATORS")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            font-family: 'Arial';
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        

        title = QLabel("INICIO DE SESION")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-family: 'Arial';
            font-size: 18px;
            color: white;
            margin-bottom: 30px;
            letter-spacing: 1px;
        """)

        field_style = """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 1px solid white;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.7);
            }
        """
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo o usuario")
        self.email_input.setStyleSheet(field_style)
        self.email_input.setFixedHeight(45)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(field_style)
        self.password_input.setFixedHeight(45)
        
        self.email_input.installEventFilter(self)
        self.password_input.installEventFilter(self)
        login_btn = QPushButton("INICIO DE SESION")
        login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
                min-width: 300px;
              
            }
            QPushButton:hover {
                background-color: black;
                color: white;
                border: 1px solid black;
            }
        """)
        login_btn.setFixedHeight(45)
        login_btn.clicked.connect(self.handle_login)

        register_link = QLabel("¿No tienes una cuenta? <a href='#' style='color:white;text-decoration:none;'>Registrate</a>")
        register_link.setAlignment(Qt.AlignCenter)
        register_link.setStyleSheet("""
            font-size: 13px; 
            color: rgba(255, 255, 255, 0.7);
        """)
        register_link.setOpenExternalLinks(False)
        register_link.linkActivated.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        center_layout.addWidget(logo, 0, Qt.AlignCenter)
        center_layout.addWidget(title, 0, Qt.AlignCenter)
        center_layout.addWidget(self.email_input, 0, Qt.AlignCenter)
        center_layout.addWidget(self.password_input, 0, Qt.AlignCenter)
        center_layout.addWidget(login_btn, 0, Qt.AlignCenter)
        center_layout.addWidget(register_link, 0, Qt.AlignCenter)
        center_layout.addStretch()

        background_layout.addStretch()
        background_layout.addWidget(center_container, 0, Qt.AlignCenter)
        background_layout.addStretch()
        
        main_layout.addWidget(background)
    def email_key_press_event(self, event: QKeyEvent):
        if event.key() == Qt.Key_Down:
            self.password_input.setFocus()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handle_login()
        else:
            QLineEdit.keyPressEvent(self.email_input, event)
            
    def password_key_press_event(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up:
            self.email_input.setFocus()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handle_login()
        else:
            QLineEdit.keyPressEvent(self.password_input, event)
    def eventFilter(self, source, event):

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Down:
                if source is self.email_input:
                    self.password_input.setFocus()
                    return True
            elif event.key() == Qt.Key_Up:
                if source is self.password_input:
                    self.email_input.setFocus()
                    return True
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.handle_login()
                return True
        return super().eventFilter(source, event)
    
    def handle_login(self):
        username_or_email = self.email_input.text().strip()
        password = self.password_input.text()

        if not username_or_email or not password:
            self.show_message("Error", "Por favor completa todos los campos")
            return

        try:
            supabase = SupabaseClient().get_client()
            

            try:
                response = supabase.auth.sign_in_with_password({
                    "email": username_or_email,
                    "password": password
                })
                
                if response.user:

                    user_record = supabase.table("users").select("*").eq("id", response.user.id).execute()
                    
                    if not user_record.data or not user_record.data[0].get('is_active', True):
                        self.show_message("Error", "Cuenta desactivada")
                        supabase.auth.sign_out()
                        return
                    
                
                    supabase.table("users").update({
                        "last_login": datetime.now().isoformat()
                    }).eq("id", response.user.id).execute()
                    
                    self.on_login_success()
                    return
                    
            except Exception as email_err:
                print(f"Error al iniciar con email: {str(email_err)}")

            try:
                user_data = supabase.table("users").select("email, is_active").eq("username", username_or_email).execute()
                
                if not user_data.data:
                    self.show_message("Error", "Usuario no encontrado")
                    return
                    
                user_info = user_data.data[0]
                
                if not user_info.get('is_active', True):
                    self.show_message("Error", "Cuenta desactivada")
                    return
                    
                user_email = user_info['email']
                response = supabase.auth.sign_in_with_password({
                    "email": user_email,
                    "password": password
                })
                
                if response.user:

                    supabase.table("users").update({
                        "last_login": datetime.now().isoformat()
                    }).eq("id", response.user.id).execute()
                    
                    self.on_login_success()
                    return
                else:
                    self.show_message("Error", "Contraseña incorrecta")
                    
            except Exception as username_err:
                print(f"Error al iniciar con username: {str(username_err)}")
                self.show_message("Error", "Credenciales incorrectas")
                
        except Exception as e:
            print(f"Error general: {str(e)}")
            self.show_message("Error", f"Error al conectar con el servidor: {str(e)}")
    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #333333;
                font-family: 'Arial';
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #000000;
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        msg.exec()

class RegisterWindow(QWidget):
    def __init__(self, stacked_widget=None, on_register_success=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.on_register_success = on_register_success
        self.setFixedSize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumSize(400, 600) 

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        background = GradientWidget()
        background_layout = QVBoxLayout(background)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)

        center_container = QWidget()
        center_container.setFixedWidth(400) 
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(40, 40, 40, 40)
        center_layout.setSpacing(20)
   
        logo = QLabel("CREATORS")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            font-family: 'Arial';
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)

        title = QLabel("REGISTRO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-family: 'Arial';
            font-size: 18px;
            color: white;
            margin-bottom: 30px;
            letter-spacing: 1px;
        """)

        field_style = """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 1px solid white;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.7);
            }
        """

        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Nombre completo")
        self.fullname_input.setStyleSheet(field_style)
        self.fullname_input.setFixedHeight(45)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setStyleSheet(field_style)
        self.email_input.setFixedHeight(45)
        
        self.password_input = PasswordLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setStyleSheet(field_style)
        self.password_input.setFixedHeight(45)
        
        self.confirm_password_input = PasswordLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar contraseña")
        self.confirm_password_input.setStyleSheet(field_style)
        self.confirm_password_input.setFixedHeight(45)
 
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        back_btn = QPushButton("VOLVER")
        back_btn.setCursor(QCursor(Qt.PointingHandCursor))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid black;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: black;
                color: white;
                border: 1px solid white;
            }
        """)
        back_btn.setFixedHeight(45)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        register_btn = QPushButton("REGISTRARSE")
        register_btn.setCursor(QCursor(Qt.PointingHandCursor))
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: black;
                color: white;
                border: 1px solid white;
            }
        """)
        register_btn.setFixedHeight(45)
        register_btn.clicked.connect(self.handle_register)
        
        button_layout.addWidget(back_btn)
        button_layout.addWidget(register_btn)
    
        center_layout.addWidget(logo, 0, Qt.AlignCenter)
        center_layout.addWidget(title, 0, Qt.AlignCenter)
        center_layout.addWidget(self.fullname_input, 0, Qt.AlignCenter)
        center_layout.addWidget(self.email_input, 0, Qt.AlignCenter)
        center_layout.addWidget(self.password_input, 0, Qt.AlignCenter)
        center_layout.addWidget(self.confirm_password_input, 0, Qt.AlignCenter)
        center_layout.addLayout(button_layout)
        center_layout.addStretch()

        background_layout.addStretch()
        background_layout.addWidget(center_container, 0, Qt.AlignCenter)
        background_layout.addStretch()
    
        main_layout.addWidget(background)
    
    def validate_inputs(self):
        errors = []
        fullname = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if not fullname:
            errors.append("El nombre completo es requerido")
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Ingrese un email válido")
            
        if len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres")
            
        if password != confirm_password:
            errors.append("Las contraseñas no coinciden")
            
        return errors
    
    def handle_register(self):
        errors = self.validate_inputs()
        if errors:
            self.show_message("Error de Validación", "\n".join(errors))
            return
        
        try:
            supabase = SupabaseClient().get_client()
            email = self.email_input.text().strip()
            password = self.password_input.text()
            fullname = self.fullname_input.text().strip()
            
            base_username = email.split('@')[0]
            username = base_username

            counter = 1
            while True:
                existing = supabase.table("users").select("username").eq("username", username).execute()
                if not existing.data:
                    break
                username = f"{base_username}{counter}"
                counter += 1

            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                
                user_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "full_name": fullname,
                    "username": username,
                    "is_verified": False,
                    "role": "user"
                }
                
                supabase.table("users").insert(user_data).execute()
                
                self.show_message("Éxito", "Registro completado. Por favor verifica tu email.")
                if self.on_register_success:
                    self.on_register_success()
                self.stacked_widget.setCurrentIndex(0)
        
        except Exception as e:
            error_msg = str(e)
            if "User already registered" in error_msg:
                self.show_message("Error", "Este email ya está registrado")
            elif "duplicate key value violates unique constraint" in error_msg:
                self.show_message("Error", "El nombre de usuario ya está en uso")
            else:
                self.show_message("Error", f"Error en el registro: {error_msg}")
    
    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #333333;
                font-family: 'Arial';
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #000000;
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        msg.exec()