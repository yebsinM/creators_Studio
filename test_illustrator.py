# test_illustrator.py
import sys
import os
from pathlib import Path

# Añadir el directorio actual al path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

print("=== DIAGNÓSTICO IllustratorWindow ===")

# Verificar archivos existentes
print("\n📁 Archivos Python en el directorio:")
for file in current_dir.glob("*.py"):
    print(f"  - {file.name}")

print("\n📁 Archivos en modules/:")
modules_dir = current_dir / "modules"
if modules_dir.exists():
    for file in modules_dir.glob("*.py"):
        print(f"  - modules/{file.name}")
else:
    print("  ❌ La carpeta modules/ no existe")

# Intentar importar IllustratorWindow
print("\n🔍 Buscando IllustratorWindow...")
import_sources = [
    ("modules.workspace", "modules/workspace.py"),
    ("entorno_java_main", "entorno_java_main.py"), 
    ("entorno_java", "entorno_java.py")
]

IllustratorWindow_class = None
source = None

for module_name, file_path in import_sources:
    try:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path} existe")
            module = __import__(module_name, fromlist=['IllustratorWindow'])
            if hasattr(module, 'IllustratorWindow'):
                IllustratorWindow_class = module.IllustratorWindow
                source = module_name
                print(f"  ✅ IllustratorWindow encontrado en {module_name}")
                break
            else:
                print(f"  ❌ {module_name} no tiene IllustratorWindow")
        else:
            print(f"  ❌ {file_path} no existe")
    except ImportError as e:
        print(f"  ❌ Error importando {module_name}: {e}")

# Mostrar métodos si se encontró la clase
if IllustratorWindow_class:
    print(f"\n🔧 Métodos de IllustratorWindow desde {source}:")
    methods = [method for method in dir(IllustratorWindow_class) if not method.startswith('_')]
    for method in methods:
        print(f"  - {method}")
        
    # Verificar señales específicas
    print(f"\n📡 Señales:")
    print(f"  - closed: {'✅' if hasattr(IllustratorWindow_class, 'closed') else '❌'}")
else:
    print("\n❌ No se pudo encontrar IllustratorWindow en ninguna ubicación")

print("\n=== FIN DIAGNÓSTICO ===")