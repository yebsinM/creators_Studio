from .common_imports import *

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

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.setup_animation_effects(scroll_layout)

        self.setup_view_effects(scroll_layout)

        self.setup_transition_effects(scroll_layout)
 
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