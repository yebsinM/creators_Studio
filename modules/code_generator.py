from .common_imports import *

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
