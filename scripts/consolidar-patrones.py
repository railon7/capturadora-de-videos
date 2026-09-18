#!/usr/bin/env python3
"""Funde los patrones reutilizables de un proyecto en el conocimiento acumulado.

Lee un `Patrones reutilizables.md` (ver plantillas/plantilla-patrones.md,
cada patrón es un encabezado `##`) y lo añade a
`conocimiento/patrones-acumulados.md` de este repo, bajo su propio
apartado "Del proyecto: <nombre>". No fusiona automáticamente patrones
que sean el mismo visto en dos proyectos — eso es una decisión humana —
pero SÍ avisa cuando el nombre de un patrón nuevo se parece a uno que ya
existe, para que se revise a mano.

Uso:
    python consolidar-patrones.py "<proyecto>/Analisis/Patrones reutilizables.md" --proyecto "Distrito K"
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

UMBRAL_PARECIDO = 0.6  # ratio de difflib.SequenceMatcher, 0-1

# En el fichero de origen (plantilla-patrones.md) cada patrón es un "##".
# Dentro del acumulado se anida un nivel para dejar sitio al "## Del
# proyecto: X", así que ahí un patrón ya consolidado es un "###".
RE_PATRON_ORIGEN = re.compile(r"^## +(.+?)\s*$", re.MULTILINE)
RE_PATRON_ACUMULADO = re.compile(r"^### +(.+?)\s*$", re.MULTILINE)

RAIZ_REPO = Path(__file__).resolve().parent.parent
FICHERO_ACUMULADO = RAIZ_REPO / "conocimiento" / "patrones-acumulados.md"


def normalizar(nombre: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", nombre.lower()).strip()


def extraer_patrones(texto: str) -> list:
    """Devuelve [(nombre, cuerpo_completo_incluido_el_encabezado), ...]."""
    posiciones = [(m.start(), m.group(1).strip()) for m in RE_PATRON_ORIGEN.finditer(texto)]
    patrones = []
    for i, (inicio, nombre) in enumerate(posiciones):
        fin = posiciones[i + 1][0] if i + 1 < len(posiciones) else len(texto)
        patrones.append((nombre, texto[inicio:fin].rstrip() + "\n"))
    return patrones


def nombres_existentes(acumulado_texto: str) -> list:
    return [m.group(1).strip() for m in RE_PATRON_ACUMULADO.finditer(acumulado_texto)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("patrones", help="Fichero 'Patrones reutilizables.md' del proyecto a consolidar")
    parser.add_argument("--proyecto", default=None, help="Nombre del proyecto/cliente para el apartado (por defecto, el nombre de su carpeta)")
    args = parser.parse_args()

    ruta_origen = Path(args.patrones)
    if not ruta_origen.exists():
        print(f"No encuentro el fichero: {ruta_origen}", file=sys.stderr)
        return 1

    texto_origen = ruta_origen.read_text(encoding="utf-8")
    patrones_nuevos = extraer_patrones(texto_origen)
    if not patrones_nuevos:
        print("No he encontrado ningún '## Nombre del patrón' en el fichero.", file=sys.stderr)
        return 1

    proyecto = args.proyecto or ruta_origen.resolve().parent.parent.name

    FICHERO_ACUMULADO.parent.mkdir(parents=True, exist_ok=True)
    if not FICHERO_ACUMULADO.exists():
        FICHERO_ACUMULADO.write_text("# Patrones acumulados\n\n", encoding="utf-8")

    acumulado_texto = FICHERO_ACUMULADO.read_text(encoding="utf-8")
    existentes = nombres_existentes(acumulado_texto)

    cabecera_proyecto = f"## Del proyecto: {proyecto}\n\n"
    if cabecera_proyecto in acumulado_texto:
        print(f"Aviso: ya hay un apartado 'Del proyecto: {proyecto}'. Se añade otra vez debajo; revisa duplicados a mano.", file=sys.stderr)

    bloque = [cabecera_proyecto]
    avisos = []
    for nombre, cuerpo in patrones_nuevos:
        # el patrón de origen usa '##'; se anida a '###' bajo su "## Del proyecto"
        cuerpo_anidado = re.sub(r"^## ", "### ", cuerpo, count=1)
        bloque.append(cuerpo_anidado + "\n")
        clave = normalizar(nombre)
        mejor_existente, mejor_ratio = None, 0.0
        for existente in existentes:
            ratio = difflib.SequenceMatcher(None, clave, normalizar(existente)).ratio()
            if ratio > mejor_ratio:
                mejor_existente, mejor_ratio = existente, ratio
        if mejor_existente and mejor_existente != nombre and mejor_ratio >= UMBRAL_PARECIDO:
            avisos.append((nombre, mejor_existente, mejor_ratio))

    with FICHERO_ACUMULADO.open("a", encoding="utf-8") as f:
        f.write("\n" + "".join(bloque))

    print(f"{len(patrones_nuevos)} patrón(es) añadidos de '{proyecto}' a {FICHERO_ACUMULADO}")
    for nuevo, parecido, ratio in avisos:
        print(f"  revisar posible duplicado ({ratio:.0%} parecido): \"{nuevo}\" ~ \"{parecido}\" ya existente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
