#!/usr/bin/env python3
"""Pasa un protocolo del formato antiguo a un documento de la biblioteca.

El formato antiguo (plantilla-protocolo.md hasta la v1.6 de la skill) se llamaba
`P-02 · Circuito de compra.md`, llevaba una tabla de metadatos en Markdown
(Quién lo hace, Cuándo, Aplicación, Ámbito, Estado con 🟡🟠🟢, Última revisión) y sus
imágenes se llamaban `P02-04-comparativo.png`.

Este script crea el documento nuevo con frontmatter, ID y nombre kebab-case:
  - el título sale del `# P-02 · Nombre`, y el nombre antiguo se guarda como alias;
  - la tabla de metadatos pasa al frontmatter (estado, revisor, fecha) y a un apartado Alcance;
  - 🟡 borrador (0.1) · 🟠 revisión (0.5) · 🟢 aprobado (1.0, solo si hay fecha y revisor;
    si no, queda en revisión, porque un aprobado sin revisor no pasa el validador);
  - las imágenes se copian a `_img/` con el nombre `<ID>-<NN>-<descripcion>.<ext>` y los
    enlaces se reescriben;
  - se añade el Historial de cambios.
El protocolo original y sus imágenes NO se tocan: se migra una copia. Con --simular solo
muestra lo que haría.

Uso:
    python migrar-protocolo.py "08-Formacion/P-02 · Circuito de compra.md" --tipo SOP \\
        --aplicacion Holded --cliente ClienteX --biblioteca "ClienteX/Biblioteca" --propietario "Ana"
"""
import argparse
import datetime
import glob
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import biblioteca as bib  # noqa: E402

RE_H1 = re.compile(r"^#[ \t]+(.+?)[ \t]*$", re.MULTILINE)
RE_TITULO_CON_CODIGO = re.compile(r"^(?P<codigo>[A-Za-z]{1,3}-?\d{1,3})\s*[·\-–—:]\s*(?P<titulo>.+)$")
RE_IMAGEN_MD = re.compile(r'!\[([^\]]*)\]\(\s*(<[^>\n]+>|[^)\n]+?)(?:\s+"[^"\n]*")?\s*\)')
RE_IMAGEN_OBSIDIAN = re.compile(r"!\[\[([^\]|\n]+)(?:\|[^\]\n]*)?\]\]")
RE_NOMBRE_ANTIGUO = re.compile(r"^[Pp]-?\d+-(\d{1,3})-(.+)$")
RE_FECHA_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
RE_FECHA_ES = re.compile(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})")

CLAVES = {"quien-lo-hace": "quien", "cuando": "cuando", "aplicacion": "aplicacion", "ambito": "ambito",
          "estado": "estado", "ultima-revision": "revision"}
VERSION_POR_ESTADO = {"borrador": "0.1", "revision": "0.5", "aprobado": "1.0"}


def separar_titulo(texto: str):
    """(codigo, titulo, resto): '# P-02 · Circuito de compra' -> ('P-02', 'Circuito de compra', ...)."""
    m = RE_H1.search(texto)
    if not m:
        return "", "", texto
    h1 = m.group(1).strip()
    con_codigo = RE_TITULO_CON_CODIGO.match(h1)
    codigo, titulo = (con_codigo["codigo"], con_codigo["titulo"].strip()) if con_codigo else ("", h1)
    resto = (texto[:m.start()] + texto[m.end():]).lstrip("\n")
    return codigo, titulo, resto


def extraer_tabla_metadatos(texto: str):
    """(datos, texto_sin_la_tabla). Solo mira la primera tabla, y solo si está antes del primer '## '."""
    lineas = texto.splitlines()
    limite = next((i for i, l in enumerate(lineas) if l.startswith("## ")), len(lineas))
    inicio = next((i for i in range(limite) if lineas[i].lstrip().startswith("|")), None)
    if inicio is None:
        return {}, texto
    fin = inicio
    while fin < len(lineas) and lineas[fin].lstrip().startswith("|"):
        fin += 1
    datos = {}
    for linea in lineas[inicio:fin]:
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 2 or set(celdas[0]) <= set("-: ") or not celdas[0]:
            continue
        clave = CLAVES.get(bib.slugify(celdas[0].replace("*", "")))
        if clave:
            datos[clave] = celdas[1].replace("**", "").strip()
    sin = lineas[:inicio] + lineas[fin:]
    return datos, "\n".join(sin).strip("\n") + "\n"


def fecha_desde_texto(texto: str) -> str:
    m = RE_FECHA_ISO.search(texto or "")
    if m:
        iso = "-".join(m.groups())
    else:
        m = RE_FECHA_ES.search(texto or "")
        iso = f"{m[3]}-{int(m[2]):02d}-{int(m[1]):02d}" if m else ""
    return iso if bib.fecha_valida(iso) else ""


def interpretar_estado(estado_txt: str, revision_txt: str):
    """(estado, version, revisado, revisor, avisos) a partir de las dos celdas de la tabla antigua."""
    avisos = []
    estado = next((e for emoji, e in bib.EMOJI_A_ESTADO.items() if emoji in (estado_txt or "")), "")
    if not estado:
        bajo = bib.slugify(estado_txt or "")
        estado = ("aprobado" if "destinatario" in bajo else "revision" if "interna" in bajo else "borrador")
        if estado_txt:
            avisos.append(f"estado no reconocido ({estado_txt!r}): se toma como {estado}")
    revisado = fecha_desde_texto(revision_txt)
    resto = RE_FECHA_ISO.sub("", RE_FECHA_ES.sub("", revision_txt or ""))
    revisor = re.sub(r"^[\s·\-–—:,]+|[\s·\-–—:,]+$", "", resto)
    if estado == "aprobado" and not (revisado and revisor):
        avisos.append("estaba validado (🟢) pero falta la fecha o quién lo revisó: queda en revisión")
        return "revision", "0.9", revisado, revisor, avisos
    return estado, VERSION_POR_ESTADO[estado], revisado, revisor, avisos


def recoger_imagenes(texto: str, base_dir: Path, id_doc: str):
    """Reescribe los enlaces a `_img/<ID>-<NN>-<desc>.<ext>`. Devuelve (texto, copias, avisos)."""
    base_dir = Path(base_dir)
    asignadas, usados, copias, avisos = {}, set(), [], []
    secuencia = [0]

    def nombre_nuevo(origen: Path) -> str:
        if origen in asignadas:
            return asignadas[origen]
        m = RE_NOMBRE_ANTIGUO.match(origen.stem)
        if m:
            numero, desc = int(m.group(1)), bib.slugify(m.group(2)) or "captura"
        else:
            numero, desc = None, bib.slugify(origen.stem) or "captura"
        while True:
            if numero is None:
                secuencia[0] += 1
            n = numero if numero is not None else secuencia[0]
            nombre = f"{id_doc}-{n:02d}-{desc}{origen.suffix.lower()}"
            if nombre not in usados:
                break
            numero = None  # colisión: pasa a la numeración correlativa
        usados.add(nombre)
        asignadas[origen] = nombre
        copias.append((origen, nombre))
        return nombre

    def por_markdown(m):
        destino = m.group(2).strip().strip("<>")
        if destino.startswith(("http://", "https://", "data:")):
            return m.group(0)
        origen = (base_dir / unquote(destino)).resolve()
        if not origen.exists():
            avisos.append(f"no encuentro la imagen {destino}: se deja el enlace tal cual")
            return m.group(0)
        return f"![{m.group(1)}](_img/{nombre_nuevo(origen)})"

    def por_obsidian(m):
        nombre = m.group(1).strip()
        origen = (base_dir / nombre).resolve()
        if not origen.exists():
            origen = next(base_dir.rglob(glob.escape(Path(nombre).name)), None)
        if origen is None or not origen.exists():
            avisos.append(f"no encuentro la imagen {nombre}: se deja la incrustación tal cual")
            return m.group(0)
        return f"![]({'_img/' + nombre_nuevo(origen.resolve())})"

    texto = RE_IMAGEN_MD.sub(por_markdown, texto)
    texto = RE_IMAGEN_OBSIDIAN.sub(por_obsidian, texto)
    return texto, copias, avisos


def convertir_protocolo(texto: str, base_dir: Path, *, id_doc: str, tipo: str, aplicacion: str, cliente: str,
                        propietario: str, idioma: str, hoy: datetime.date, nombre_antiguo: str = ""):
    """Devuelve (meta, cuerpo, copias_de_imagenes, avisos). No escribe nada."""
    codigo, titulo, resto = separar_titulo(texto)
    datos, resto = extraer_tabla_metadatos(resto)
    titulo = titulo or nombre_antiguo
    estado, version, revisado, revisor, avisos = interpretar_estado(datos.get("estado", ""), datos.get("revision", ""))
    aplicacion = aplicacion or datos.get("aplicacion", "") or "general"

    resto, copias, avisos_img = recoger_imagenes(resto, base_dir, id_doc)
    avisos += avisos_img

    fecha = bib.hoy_iso(hoy)
    meta = bib.construir_meta(id_doc=id_doc, tipo=tipo, titulo=titulo, idioma=idioma, propietario=propietario,
                              cliente=cliente, aplicacion=aplicacion, fecha=fecha, origen="protocolo-antiguo")
    if nombre_antiguo:
        meta["aliases"] = [nombre_antiguo]
    meta.update({"version": version, "estado": estado, "revisor": revisor, "revisado": revisado,
                 "proxima_revision": bib.sumar_dias(revisado or fecha, 365)})

    partes = [f"# {titulo}", ""]
    alcance = [("Quién lo hace", datos.get("quien")), ("Cuándo", datos.get("cuando")), ("Ámbito", datos.get("ambito"))]
    alcance = [f"- **{k}:** {v}" for k, v in alcance if v]
    if alcance and not re.search(r"^## +Alcance\b", resto, re.MULTILINE):
        partes += ["## Alcance", ""] + alcance + [""]
    partes.append(resto.strip("\n"))
    cuerpo = "\n".join(partes).rstrip("\n") + "\n"
    if not re.search(r"^## +(Historial de cambios|Change history)\s*$", cuerpo, re.MULTILINE):
        origen = f"Migrado desde el protocolo {nombre_antiguo or codigo}".strip()
        cuerpo += (f"\n## Historial de cambios\n\n| Versión | Fecha | Cambio | Autoría |\n|---|---|---|---|\n"
                   f"| {version} | {fecha} | {origen} | {propietario} |\n")
    return meta, cuerpo, copias, avisos


def migrar_protocolo(origen, raiz, *, tipo="SOP", ambito="", aplicacion="", cliente="comun", propietario="",
                     idioma="es", carpeta=None, hoy=None, simular=False) -> dict:
    origen, raiz = Path(origen), Path(raiz)
    tipo = bib.tipo_desde_texto(tipo)
    if not origen.exists():
        raise FileNotFoundError(f"No encuentro el protocolo: {origen}")
    if not propietario.strip():
        raise ValueError("Falta el propietario: pasa --propietario o configura git user.name.")
    hoy = hoy or datetime.date.today()
    texto = origen.read_text(encoding="utf-8")

    datos, _ = extraer_tabla_metadatos(separar_titulo(texto)[2])
    app = aplicacion.strip() or datos.get("aplicacion", "").strip() or "general"
    ambito = (ambito or bib.codigo_ambito(app if app != "general" else "GEN")).upper()
    id_doc = bib.formatear_id(tipo, ambito, bib.siguiente_numero(raiz, tipo, ambito))
    destino = Path(carpeta) if carpeta else bib.carpeta_destino(raiz, tipo, app, cliente)

    meta, cuerpo, copias, avisos = convertir_protocolo(
        texto, origen.parent, id_doc=id_doc, tipo=tipo, aplicacion=app, cliente=cliente,
        propietario=propietario, idioma=idioma, hoy=hoy, nombre_antiguo=origen.stem)
    slug = bib.slugify(meta["titulo"])
    if not slug:
        raise ValueError("El título no genera un nombre de fichero válido.")
    ruta = destino / bib.nombre_fichero(id_doc, slug, idioma)
    if ruta.exists():
        raise FileExistsError(f"Ya existe {ruta}. No se sobrescribe.")
    for _, nombre in copias:
        if (destino / "_img" / nombre).exists():
            raise FileExistsError(f"Ya existe la imagen {destino / '_img' / nombre}. No se sobrescribe.")

    if not simular:
        for fuente, nombre in copias:
            (destino / "_img").mkdir(parents=True, exist_ok=True)
            shutil.copy2(fuente, destino / "_img" / nombre)
        bib.escribir_texto(ruta, bib.volcar_frontmatter(meta) + "\n" + cuerpo)
    return {"id": id_doc, "ruta": ruta, "imagenes": [n for _, n in copias], "avisos": avisos, "estado": meta["estado"]}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("protocolo", help="Protocolo en el formato antiguo (.md)")
    p.add_argument("--biblioteca", help="Carpeta raíz de la biblioteca destino (por defecto: BIBLIOTECA_TAZUKE o conocimiento/biblioteca)")
    p.add_argument("--tipo", default="SOP", help="Tipo del documento nuevo: SOP (por defecto) o GUI para una guía de cliente")
    p.add_argument("--aplicacion", default="", help="Aplicación (por defecto, la de la tabla antigua)")
    p.add_argument("--ambito", default="", help="Código de 2-8 letras para el ID (por defecto, sale de la aplicación)")
    p.add_argument("--cliente", default="comun", help="Cliente al que pertenece, o 'comun'")
    p.add_argument("--propietario", default="", help="Responsable (por defecto: BIBLIOTECA_PROPIETARIO o git user.name)")
    p.add_argument("--idioma", default="es", choices=list(bib.IDIOMAS))
    p.add_argument("--carpeta", help="Carpeta de destino, si no se quiere la que corresponde por tipo")
    p.add_argument("--simular", action="store_true", help="Muestra lo que haría sin escribir nada")
    args = p.parse_args()

    try:
        r = migrar_protocolo(args.protocolo, bib.raiz_biblioteca(args.biblioteca), tipo=args.tipo, ambito=args.ambito,
                             aplicacion=args.aplicacion, cliente=args.cliente, propietario=args.propietario or bib.propietario_por_defecto(),
                             idioma=args.idioma, carpeta=args.carpeta, simular=args.simular)
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    etiqueta = "Crearía" if args.simular else "Creado"
    print(f"ID: {r['id']} · estado: {r['estado']}")
    print(f"{etiqueta}: {r['ruta']}")
    for nombre in r["imagenes"]:
        print(f"  imagen: _img/{nombre}")
    for aviso in r["avisos"]:
        print(f"Aviso: {aviso}", file=sys.stderr)
    print("El protocolo original no se ha tocado. Revisa el resultado y pásalo por validar-biblioteca.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
