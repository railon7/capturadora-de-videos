"""Carga los scripts (nombres con guion, no importables con `import` normal)
como módulos para poder probar sus funciones puras sin ejecutar main()."""
import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPTS = RAIZ / "scripts"


def cargar_modulo(nombre_fichero: str):
    ruta = SCRIPTS / nombre_fichero
    nombre_modulo = nombre_fichero.replace("-", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(nombre_modulo, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo
