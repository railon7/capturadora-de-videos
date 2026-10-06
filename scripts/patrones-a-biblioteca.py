#!/usr/bin/env python3
"""Pasa los patrones acumulados a documentos PAT de la biblioteca.

`conocimiento/patrones-acumulados.md` es la bandeja de entrada: consolidar-patrones.py
añade en él un apartado "## Del proyecto: <origen>" por cada proyecto. Este script
convierte cada apartado en un documento PAT con frontmatter (ID, versión, estado,
aplicación), para que los patrones se puedan filtrar por aplicación, versionar y
revisar como el resto de la biblioteca.

  - Un documento PAT por apartado, con un `##` por patrón.
  - La aplicación sale del apartado ("Software DELSOL — ContaSol (tutoriales oficiales)"
    -> ContaSol) y de ella el código del ID (PAT-CONTASOL-001).
  - Se puede repetir: si ya existe el PAT de ese apartado (campo origen_patrones) y el
    contenido cambió, lo actualiza y sube la versión menor; si no cambió, no toca nada.
  - Los PAT nuevos nacen en borrador: alguien tiene que revisarlos antes de aprobarlos.

Uso:
    python patrones-a-biblioteca.py --propietario "Jorge Herrera"
    python patrones-a-biblioteca.py --origen otro.md --biblioteca "D:/Biblioteca Tazuke" --simular
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import biblioteca as bib  # noqa: E402

RE_SECCION = re.compile(r"^## Del proyecto: (.+?)[ \t]*$", re.MULTILINE)
RE_PATRON = re.compile(r"^### +\S", re.MULTILINE)
RE_HISTORIAL = re.compile(r"\n## Historial de cambios\s*\n")


def dividir_acumulado(texto: str) -> list:
    """[(origen, patrones_en_markdown)] uno por apartado '## Del proyecto: ...'."""
    marcas = list(RE_SECCION.finditer(texto))
    secciones = []
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        cuerpo = texto[m.end():fin].strip("\n")
        # el comentario que deja consolidar-patrones.py no es un patrón
        cuerpo = re.sub(r"<!--.*?-->", "", cuerpo, flags=re.DOTALL).strip("\n")
        secciones.append((m.group(1).strip(), cuerpo))
    return secciones


def aplicacion_de(origen: str) -> str:
    """'Software DELSOL — ContaSol (tutoriales oficiales)' -> 'ContaSol'."""
    base = re.sub(r"\s*\([^)]*\)\s*$", "", origen).strip()
    partes = re.split(r"\s+[—–-]\s+", base)
    return partes[-1].strip() or origen


def subir_encabezados(patrones: str) -> str:
    """Cada patrón pasa de ### a ## dentro de su documento."""
    return re.sub(r"^### ", "## ", patrones, flags=re.MULTILINE)


def construir_cuerpo(origen: str, patrones: str) -> str:
    n = len(RE_PATRON.findall(patrones))
    titulo = f"Patrones de {aplicacion_de(origen)}"
    return (f"# {titulo}\n\n> Origen: «{origen}» · {n} patrones. Cada apartado es un patrón con su «Visto en» y su «Se aplica cuando».\n\n"
            + subir_encabezados(patrones).strip("\n") + "\n")


def _fila_historial(version: str, fecha: str, cambio: str, autor: str) -> str:
    return f"| {version} | {fecha} | {cambio} | {autor} |"


def _tabla_nueva(version, fecha, cambio, autor) -> str:
    return ("\n## Historial de cambios\n\n| Versión | Fecha | Cambio | Autoría |\n|---|---|---|---|\n"
            + _fila_historial(version, fecha, cambio, autor) + "\n")


def _buscar_pat_existente(raiz: Path, origen: str):
    for ruta in bib.documentos_de(raiz):
        try:
            meta, cuerpo = bib.leer_documento(ruta)
        except (bib.ErrorFrontmatter, UnicodeDecodeError):
            continue
        if meta.get("origen_patrones") == origen and meta.get("tipo") == bib.TIPOS["PAT"]["valor"]:
            return ruta, meta, cuerpo
    return None


def sincronizar(texto_acumulado: str, raiz, *, propietario: str, hoy=None, simular=False) -> list:
    """Crea o actualiza un PAT por apartado. Devuelve [{'origen','accion','ruta','patrones'}]."""
    raiz = Path(raiz)
    hoy = hoy or datetime.date.today()
    fecha = bib.hoy_iso(hoy)
    if not propietario.strip():
        raise ValueError("Falta el propietario: pasa --propietario o configura git user.name.")
    resultado = []
    for origen, patrones in dividir_acumulado(texto_acumulado):
        n = len(RE_PATRON.findall(patrones))
        if n == 0:
            resultado.append({"origen": origen, "accion": "sin patrones", "ruta": None, "patrones": 0})
            continue
        cuerpo_nuevo = construir_cuerpo(origen, patrones)
        existente = _buscar_pat_existente(raiz, origen)

        if existente is None:
            aplicacion = aplicacion_de(origen)
            ambito = bib.codigo_ambito(aplicacion)
            id_doc = bib.formatear_id("PAT", ambito, bib.siguiente_numero(raiz, "PAT", ambito))
            titulo = f"Patrones de {aplicacion}"
            meta = bib.construir_meta(id_doc=id_doc, tipo="PAT", titulo=titulo, idioma="es", propietario=propietario,
                                      cliente="comun", aplicacion=aplicacion, fecha=fecha, origen="patrones-acumulados")
            etiquetas = meta.pop("tags")
            meta["origen_patrones"] = origen
            meta["tags"] = etiquetas
            ruta = bib.carpeta_destino(raiz, "PAT", aplicacion, "comun") / bib.nombre_fichero(id_doc, bib.slugify(titulo), "es")
            texto = (bib.volcar_frontmatter(meta) + "\n" + cuerpo_nuevo
                     + _tabla_nueva("0.1", fecha, "Creado desde patrones-acumulados.md", propietario))
            if not simular:
                bib.escribir_texto(ruta, texto)
            resultado.append({"origen": origen, "accion": "creado", "ruta": ruta, "patrones": n})
            continue

        ruta, meta, cuerpo_viejo = existente
        texto_viejo = "\n" + cuerpo_viejo
        corte = RE_HISTORIAL.search(texto_viejo)
        previo, historial = (texto_viejo[:corte.start()], texto_viejo[corte.end():]) if corte else (texto_viejo, "")
        if previo.strip() == cuerpo_nuevo.strip():
            resultado.append({"origen": origen, "accion": "sin cambios", "ruta": ruta, "patrones": n})
            continue
        version = bib.subir_version_menor(meta.get("version", "0.1"))
        meta["version"] = version
        fila = _fila_historial(version, fecha, "Actualizado desde patrones-acumulados.md", propietario)
        if historial.strip():
            historial_nuevo = "\n## Historial de cambios\n\n" + historial.strip("\n") + "\n" + fila + "\n"
        else:
            historial_nuevo = _tabla_nueva(version, fecha, "Actualizado desde patrones-acumulados.md", propietario)
        if not simular:
            bib.escribir_texto(ruta, bib.volcar_frontmatter(meta) + "\n" + cuerpo_nuevo + historial_nuevo)
        resultado.append({"origen": origen, "accion": "actualizado", "ruta": ruta, "patrones": n})
    return resultado


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--origen", default=str(bib.RAIZ_REPO / "conocimiento" / "patrones-acumulados.md"),
                   help="Fichero de patrones acumulados (por defecto el de este repo)")
    p.add_argument("--biblioteca", help="Carpeta raíz de la biblioteca (por defecto: BIBLIOTECA_TAZUKE o conocimiento/biblioteca)")
    p.add_argument("--propietario", default="", help="Responsable (por defecto: BIBLIOTECA_PROPIETARIO o git user.name)")
    p.add_argument("--simular", action="store_true", help="Muestra lo que haría sin escribir nada")
    args = p.parse_args()

    origen = Path(args.origen)
    if not origen.exists():
        print(f"No encuentro el fichero: {origen}", file=sys.stderr)
        return 1
    try:
        resultado = sincronizar(origen.read_text(encoding="utf-8"), bib.raiz_biblioteca(args.biblioteca),
                                propietario=args.propietario or bib.propietario_por_defecto(), simular=args.simular)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    if not resultado:
        print("No hay ningún apartado '## Del proyecto: ...' en el fichero.", file=sys.stderr)
        return 1
    for r in resultado:
        destino = f" -> {r['ruta']}" if r["ruta"] else ""
        print(f"{r['accion']:<12} {r['patrones']:>3} patrones · {r['origen']}{destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
