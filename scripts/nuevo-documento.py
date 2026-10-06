#!/usr/bin/env python3
"""Crea un documento nuevo de la biblioteca con su ID, su nombre y su frontmatter.

Calcula el siguiente número libre del ID (TIPO-AMBITO-NNN), genera el nombre
en kebab-case (`<ID>_<slug>.<idioma>.md`), rellena el frontmatter y deja el
cuerpo desde la plantilla de `plantillas/biblioteca/<TIPO>.md`. Con
--titulo-en crea además el esqueleto en inglés, enlazado con el español y
marcado como pendiente de traducir. Nunca sobrescribe un fichero.

Tipos: MAN manual de aplicación · GUI guía de usuario · SOP procedimiento (PNT)
       TUT tutorial · QSG guía rápida · FAQ preguntas y problemas · GLO glosario
       NOV notas de versión · DEC registro de decisión · PAT patrón reutilizable

Dónde está la biblioteca: --biblioteca, o la variable de entorno
BIBLIOTECA_TAZUKE, o conocimiento/biblioteca de este repo. Los documentos de un
cliente van a la biblioteca de ese cliente (--biblioteca "<Cliente>/Biblioteca"
con --cliente "<Cliente>").

Uso:
    python nuevo-documento.py --tipo SOP --aplicacion Holded --titulo "Emitir factura rectificativa" \\
        --titulo-en "Issue a corrective invoice" --cliente ClienteX --biblioteca "ClienteX/Biblioteca"
    python nuevo-documento.py --iniciar comun --biblioteca "D:/Biblioteca Tazuke"
    python nuevo-documento.py --iniciar cliente --biblioteca "ClienteX/Biblioteca"
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import biblioteca as bib  # noqa: E402

# Piezas que comparten nuevo-documento.py, migrar-protocolo.py y patrones-a-biblioteca.py
TIPOS_POR_APLICACION = bib.TIPOS_POR_APLICACION
carpeta_destino = bib.carpeta_destino
construir_meta = bib.construir_meta

CARPETAS_COMUN = ("00-gobierno", "10-aplicaciones", "40-patrones", "90-archivo")
CARPETAS_CLIENTE = ("_img", "entregables", "90-archivo")

LEEME_COMUN = """# Biblioteca común

Documentos reutilizables, sin datos de ningún cliente.

| Carpeta | Contenido |
|---|---|
| `00-gobierno/` | Glosario ES-EN, decisiones de la propia biblioteca y el registro generado |
| `10-aplicaciones/<app>/` | Manuales, tutoriales, guías rápidas, FAQ y notas de versión de cada aplicación |
| `40-patrones/` | Patrones reutilizables aprendidos en proyectos |
| `90-archivo/` | Documentos obsoletos (estado `obsoleto`) |

Reglas, tipos y nombres: `metodologia/biblioteca-de-conocimiento.md` del repositorio de la capturadora.
Crear un documento: `python scripts/nuevo-documento.py --help`.
Comprobar la biblioteca y regenerar el registro: `python scripts/validar-biblioteca.py --registro`.
"""

LEEME_CLIENTE = """# Biblioteca del cliente

Guías, procedimientos y tutoriales propios de este cliente. Enlazan a los manuales
de aplicación de la biblioteca común en vez de copiarlos.

| Carpeta | Contenido |
|---|---|
| (esta carpeta) | GUI, SOP, QSG, FAQ y demás documentos del cliente, con nombre `<ID>_<slug>.<idioma>.md` |
| `_img/` | Capturas ya tapadas y anotadas: `<ID>-<NN>-<descripcion>.png` |
| `entregables/` | HTML y PDF generados para entregar al cliente |
| `90-archivo/` | Documentos obsoletos |

Reglas, tipos y nombres: `metodologia/biblioteca-de-conocimiento.md` del repositorio de la capturadora.
"""


propietario_por_defecto = bib.propietario_por_defecto


def esqueleto_traduccion(plantilla: str, valores: dict, idioma: str) -> str:
    """Cuerpo de la versión secundaria: solo los encabezados, listos para traducir encima."""
    renderizado = bib.renderizar_plantilla(plantilla, valores, idioma, con_guia=False)
    lineas = ["# " + valores["titulo"], "", f"> {bib.ENCABEZADOS['traducir'][0 if idioma == 'es' else 1]}", ""]
    historial = bib.ENCABEZADOS["historial"][0 if idioma == "es" else 1]
    for linea in renderizado.splitlines():
        if re.match(r"^## ", linea) and linea[3:].strip() != historial:
            lineas += [linea, ""]
    return "\n".join(lineas) + "\n" + bib._tabla_historial(idioma, valores)


def crear_documento(raiz, tipo, titulo, *, ambito="", aplicacion="", cliente="comun", idioma="es",
                    propietario="", titulo_alt="", carpeta=None, origen="", fuente_video="",
                    hoy=None, simular=False) -> dict:
    """Crea el documento (y su pareja en el otro idioma si hay titulo_alt). Devuelve {id, rutas}."""
    raiz = Path(raiz)
    tipo = bib.tipo_desde_texto(tipo)
    if idioma not in bib.IDIOMAS:
        raise ValueError(f"Idioma no válido: {idioma!r}. Válidos: {', '.join(bib.IDIOMAS)}")
    if not titulo.strip():
        raise ValueError("Falta el título.")
    if not propietario.strip():
        raise ValueError("Falta el propietario: pasa --propietario o configura git user.name.")
    if tipo in TIPOS_POR_APLICACION and cliente.lower() == "comun" and not aplicacion.strip():
        raise ValueError(f"Un {tipo} común vive en una carpeta por aplicación: indica --aplicacion.")
    aplicacion = aplicacion.strip() or "general"
    ambito = (ambito or bib.codigo_ambito(aplicacion if aplicacion != "general" else "GEN")).upper()
    if not re.fullmatch(r"[A-Z0-9]{2,8}", ambito):
        raise ValueError(f"Ámbito no válido: {ambito!r}. Usa de 2 a 8 letras o cifras (HOLDED, ADM, FACT).")
    slug = bib.slugify(titulo)
    if not slug:
        raise ValueError("El título no genera un nombre de fichero válido.")

    fecha = bib.hoy_iso(hoy)
    id_doc = bib.formatear_id(tipo, ambito, bib.siguiente_numero(raiz, tipo, ambito))
    destino = Path(carpeta) if carpeta else carpeta_destino(raiz, tipo, aplicacion, cliente)
    otro = "en" if idioma == "es" else "es"

    plantilla_ruta = bib.PLANTILLAS / f"{tipo}.md"
    if not plantilla_ruta.exists():
        raise FileNotFoundError(f"No encuentro la plantilla {plantilla_ruta}")
    plantilla = plantilla_ruta.read_text(encoding="utf-8")
    valores = {"id": id_doc, "titulo": titulo, "fecha": fecha, "propietario": propietario, "version": "0.1"}

    ficheros = []  # (ruta, texto)
    nombre_principal = bib.nombre_fichero(id_doc, slug, idioma)
    nombre_alt = bib.nombre_fichero(id_doc, bib.slugify(titulo_alt), otro) if titulo_alt else ""
    meta = construir_meta(id_doc=id_doc, tipo=tipo, titulo=titulo, idioma=idioma, propietario=propietario,
                          cliente=cliente, aplicacion=aplicacion, fecha=fecha, titulo_alt=titulo_alt,
                          traduccion=nombre_alt, origen=origen, fuente_video=fuente_video)
    cuerpo = bib.renderizar_plantilla(plantilla, valores, idioma, con_guia=True)
    ficheros.append((destino / nombre_principal, bib.volcar_frontmatter(meta) + "\n" + cuerpo.rstrip("\n") + "\n"))

    if titulo_alt:
        if not bib.slugify(titulo_alt):
            raise ValueError("El título alternativo no genera un nombre de fichero válido.")
        meta_alt = construir_meta(id_doc=id_doc, tipo=tipo, titulo=titulo_alt, idioma=otro, propietario=propietario,
                                  cliente=cliente, aplicacion=aplicacion, fecha=fecha, titulo_alt=titulo,
                                  traduccion=nombre_principal, traduccion_estado="pendiente",
                                  origen=origen, fuente_video=fuente_video)
        valores_alt = dict(valores, titulo=titulo_alt)
        ficheros.append((destino / nombre_alt, bib.volcar_frontmatter(meta_alt) + "\n"
                         + esqueleto_traduccion(plantilla, valores_alt, otro)))

    for ruta, _ in ficheros:
        if ruta.exists():
            raise FileExistsError(f"Ya existe {ruta}. No se sobrescribe.")
    if not simular:
        for ruta, texto in ficheros:
            bib.escribir_texto(ruta, texto)
    return {"id": id_doc, "rutas": [r for r, _ in ficheros], "carpeta": destino}


def iniciar_biblioteca(raiz, modo: str, simular: bool = False) -> list:
    """Crea la estructura de carpetas y su LEEME.md. Devuelve lo que ha creado (o crearía)."""
    raiz = Path(raiz)
    if modo not in ("comun", "cliente"):
        raise ValueError("El modo de --iniciar es 'comun' o 'cliente'.")
    carpetas = CARPETAS_COMUN if modo == "comun" else CARPETAS_CLIENTE
    leeme = LEEME_COMUN if modo == "comun" else LEEME_CLIENTE
    creado = []
    for nombre in carpetas:
        carpeta = raiz / nombre
        if not carpeta.exists():
            creado.append(carpeta)
            if not simular:
                carpeta.mkdir(parents=True, exist_ok=True)
    ruta_leeme = raiz / "LEEME.md"
    if not ruta_leeme.exists():
        creado.append(ruta_leeme)
        if not simular:
            bib.escribir_texto(ruta_leeme, leeme)
    return creado


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--biblioteca", help="Carpeta raíz de la biblioteca (por defecto: BIBLIOTECA_TAZUKE o conocimiento/biblioteca)")
    p.add_argument("--iniciar", choices=["comun", "cliente"], help="Crea la estructura de carpetas de una biblioteca nueva y termina")
    p.add_argument("--tipo", help="MAN, GUI, SOP, TUT, QSG, FAQ, GLO, NOV, DEC o PAT")
    p.add_argument("--titulo", help="Título del documento en el idioma principal")
    p.add_argument("--titulo-en", dest="titulo_alt", default="", help="Título en el otro idioma: crea también el esqueleto de la traducción")
    p.add_argument("--idioma", default="es", choices=list(bib.IDIOMAS), help="Idioma principal (por defecto es)")
    p.add_argument("--aplicacion", default="", help="Aplicación o sistema que describe el documento (Holded, FactuSol...)")
    p.add_argument("--ambito", default="", help="Código de 2-8 letras para el ID (por defecto, sale de la aplicación)")
    p.add_argument("--cliente", default="comun", help="Cliente al que pertenece, o 'comun' (por defecto)")
    p.add_argument("--propietario", default="", help="Responsable del documento (por defecto: git user.name)")
    p.add_argument("--carpeta", help="Carpeta de destino, si no se quiere la que corresponde por tipo")
    p.add_argument("--origen", default="", help="De dónde sale: video, reunion, manual-del-fabricante...")
    p.add_argument("--fuente-video", dest="fuente_video", default="", help="Nombre o enlace del vídeo de origen")
    p.add_argument("--simular", action="store_true", help="Muestra lo que haría sin escribir nada")
    args = p.parse_args()

    raiz = bib.raiz_biblioteca(args.biblioteca)
    try:
        if args.iniciar:
            creado = iniciar_biblioteca(raiz, args.iniciar, simular=args.simular)
            etiqueta = "Crearía" if args.simular else "Creado"
            for ruta in creado:
                print(f"{etiqueta}: {ruta}")
            if not creado:
                print(f"No hay nada que crear: {raiz} ya tiene la estructura.")
            return 0
        if not args.tipo or not args.titulo:
            p.error("Faltan --tipo y --titulo (o usa --iniciar).")
        resultado = crear_documento(
            raiz, args.tipo, args.titulo, ambito=args.ambito, aplicacion=args.aplicacion, cliente=args.cliente,
            idioma=args.idioma, propietario=args.propietario or propietario_por_defecto(), titulo_alt=args.titulo_alt,
            carpeta=args.carpeta, origen=args.origen, fuente_video=args.fuente_video, simular=args.simular)
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    etiqueta = "Crearía" if args.simular else "Creado"
    print(f"ID: {resultado['id']}")
    for ruta in resultado["rutas"]:
        print(f"{etiqueta}: {ruta}")
    if not args.simular:
        print("Siguiente: rellena el documento, borra los comentarios GUÍA y comprueba con validar-biblioteca.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
