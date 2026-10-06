#!/usr/bin/env python3
"""Comprueba que la biblioteca de conocimiento sigue la convención y genera su registro.

Por cada documento revisa: nombre `<ID>_<slug>.<es|en>.md`, frontmatter con los campos
obligatorios, que ID, tipo e idioma coincidan con el nombre, estado y versión válidos,
fechas, que "aprobado" tenga revisor y versión 1.0 o superior, imágenes y enlaces,
marcadores `{{...}}` y comentarios GUÍA sin quitar, pareja español-inglés enlazada,
revisiones vencidas y documentos obsoletos fuera del archivo.

Errores = la biblioteca no cumple la convención (salida 1). Avisos = conviene mirarlo
(salida 0, o 1 con --estricto).

Con --registro escribe `00_Registro.md` (en 00-gobierno/ si existe): una tabla por tipo con
estado, versión y próxima revisión, y la lista de revisiones vencidas. Se regenera, no se edita.

Uso:
    python validar-biblioteca.py                       # la biblioteca por defecto
    python validar-biblioteca.py "ClienteX/Biblioteca" --registro
    python validar-biblioteca.py --estricto            # los avisos también fallan
"""
import argparse
import datetime
import glob
import re
import sys
from collections import defaultdict, namedtuple
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import biblioteca as bib  # noqa: E402

Hallazgo = namedtuple("Hallazgo", "ruta nivel mensaje")

CAMPOS_OBLIGATORIOS = ("id", "tipo", "titulo", "idioma", "version", "estado", "propietario",
                       "cliente", "aplicacion", "proxima_revision")

RE_COMENTARIO = re.compile(r"<!--.*?-->", re.DOTALL)
RE_CODIGO_BLOQUE = re.compile(r"```.*?```", re.DOTALL)
RE_CODIGO_LINEA = re.compile(r"`[^`\n]*`")
RE_IMAGEN = re.compile(r"!\[[^\]]*\]\(\s*(<[^>\n]+>|[^)\s\n]+)(?:\s+\"[^\"\n]*\")?\s*\)")
RE_IMAGEN_OBSIDIAN = re.compile(r"!\[\[([^\]|\n]+)(?:\|[^\]\n]*)?\]\]")
RE_ENLACE = re.compile(r"(?<!!)\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^)\s\n]+)(?:\s+\"[^\"\n]*\")?\s*\)")
RE_WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#\n]+)(?:#[^\]|\n]*)?(?:\|[^\]\n]*)?\]\]")
RE_MARCADOR = re.compile(r"\{\{[^}\n]*\}\}")
RE_GUIA = re.compile(r"<!--\s*GUÍA:")
RE_H1 = re.compile(r"^# +\S", re.MULTILINE)
RE_HISTORIAL = re.compile(r"^## +(Historial de cambios|Change history)\s*$", re.MULTILINE)


def _limpio(cuerpo: str) -> str:
    """El cuerpo sin comentarios ni código, para buscar enlaces e imágenes reales."""
    return RE_CODIGO_LINEA.sub("", RE_CODIGO_BLOQUE.sub("", RE_COMENTARIO.sub("", cuerpo)))


def _es_externo(ruta: str) -> bool:
    return ruta.startswith(("http://", "https://", "data:", "mailto:", "#", "obsidian://"))


def _existe_en_biblioteca(raiz: Path, nombre: str) -> bool:
    nombre = Path(nombre).name
    return any(raiz.rglob(glob.escape(nombre)))


def _comprobar_enlaces(ruta: Path, raiz: Path, cuerpo: str, estado: str, salida: list, nombres: list) -> None:
    limpio = _limpio(cuerpo)
    nivel_imagen = "AVISO" if estado == "borrador" else "ERROR"
    for m in RE_IMAGEN.finditer(limpio):
        destino = m.group(1).strip("<>")
        if _es_externo(destino):
            continue
        if not (ruta.parent / unquote(destino)).exists():
            salida.append((nivel_imagen, f"imagen que no existe: {destino}"))
    for m in RE_IMAGEN_OBSIDIAN.finditer(limpio):
        nombre = m.group(1).strip()
        if not (ruta.parent / nombre).exists() and not _existe_en_biblioteca(raiz, nombre):
            salida.append((nivel_imagen, f"imagen que no existe: {nombre}"))
    for m in RE_ENLACE.finditer(limpio):
        destino = m.group(1).strip("<>")
        if _es_externo(destino):
            continue
        sin_ancla = unquote(destino.split("#", 1)[0])
        if sin_ancla and not (ruta.parent / sin_ancla).exists():
            salida.append(("ERROR", f"enlace roto: {destino}"))
    for m in RE_WIKILINK.finditer(limpio):
        objetivo = m.group(1).strip()
        base = objetivo[:-3] if objetivo.lower().endswith(".md") else objetivo
        encontrado = any(n == objetivo or n[:-3] == base or n.startswith(base + "_") for n in nombres)
        if not encontrado and not _existe_en_biblioteca(raiz, objetivo):
            salida.append(("AVISO", f"enlace [[{objetivo}]] que no apunta a ningún documento de la biblioteca"))


def validar_documento(ruta: Path, raiz: Path, hoy: datetime.date, nombres=None):
    """Devuelve (meta, [(nivel, mensaje), ...]) de un documento."""
    ruta, raiz = Path(ruta), Path(raiz)
    if nombres is None:
        nombres = [p.name for p in bib.documentos_de(raiz)]
    h = []
    partes = bib.partir_nombre(ruta.name)
    if not partes:
        h.append(("ERROR", f"el nombre no sigue <ID>_<slug-kebab>.<es|en>.md: {ruta.name}"))
    try:
        meta, cuerpo = bib.leer_documento(ruta)
    except bib.ErrorFrontmatter as e:
        return {}, h + [("ERROR", f"frontmatter ilegible: {e}")]
    except UnicodeDecodeError:
        return {}, h + [("ERROR", "el fichero no está en UTF-8")]
    if not meta:
        return {}, h + [("ERROR", "no tiene frontmatter (bloque --- al principio del fichero)")]

    faltan = [c for c in CAMPOS_OBLIGATORIOS if not str(meta.get(c, "")).strip()]
    if faltan:
        h.append(("ERROR", "faltan campos obligatorios: " + ", ".join(faltan)))

    id_doc = meta.get("id", "")
    datos_id = bib.partir_id(id_doc) if id_doc else None
    if id_doc and not datos_id:
        h.append(("ERROR", f"el id {id_doc!r} no tiene la forma TIPO-AMBITO-NNN"))
    if partes and id_doc and id_doc != partes["id"]:
        h.append(("ERROR", f"el id del frontmatter ({id_doc}) no coincide con el del nombre ({partes['id']})"))
    if partes and meta.get("idioma") and meta["idioma"] != partes["idioma"]:
        h.append(("ERROR", f"el idioma del frontmatter ({meta['idioma']}) no coincide con el del nombre (.{partes['idioma']}.md)"))
    if meta.get("idioma") and meta["idioma"] not in bib.IDIOMAS:
        h.append(("ERROR", f"idioma no válido: {meta['idioma']} (válidos: {', '.join(bib.IDIOMAS)})"))
    if datos_id and meta.get("tipo"):
        if datos_id["tipo"] not in bib.TIPOS:
            h.append(("ERROR", f"el prefijo {datos_id['tipo']} del id no es un tipo conocido"))
        elif meta["tipo"] != bib.TIPOS[datos_id["tipo"]]["valor"]:
            h.append(("ERROR", f"el tipo {meta['tipo']!r} no corresponde al prefijo {datos_id['tipo']} "
                               f"(debería ser {bib.TIPOS[datos_id['tipo']]['valor']!r})"))

    estado, version = meta.get("estado", ""), meta.get("version", "")
    if estado and estado not in bib.ESTADOS:
        h.append(("ERROR", f"estado no válido: {estado} (válidos: {', '.join(bib.ESTADOS)})"))
    if version and not bib.RE_VERSION.match(version):
        h.append(("ERROR", f"la versión {version!r} no es del tipo mayor.menor (por ejemplo 1.0)"))
    for campo in ("creado", "revisado", "proxima_revision"):
        if meta.get(campo) and not bib.fecha_valida(meta[campo]):
            h.append(("ERROR", f"{campo} no es una fecha AAAA-MM-DD válida: {meta[campo]}"))
    if meta.get("traduccion_estado") and meta["traduccion_estado"] not in bib.ESTADOS_TRADUCCION:
        h.append(("ERROR", f"traduccion_estado no válido: {meta['traduccion_estado']} (válidos: {', '.join(bib.ESTADOS_TRADUCCION)})"))

    if estado == "aprobado":
        if not str(meta.get("revisor", "")).strip():
            h.append(("ERROR", "un documento aprobado necesita revisor"))
        if not bib.fecha_valida(meta.get("revisado", "")):
            h.append(("ERROR", "un documento aprobado necesita la fecha de revisión (revisado)"))
        if bib.RE_VERSION.match(version or "") and version.startswith("0."):
            h.append(("ERROR", f"un documento aprobado sale como 1.0 o superior, no {version}"))
        if bib.fecha_valida(meta.get("proxima_revision", "")) and meta["proxima_revision"] < hoy.isoformat():
            h.append(("AVISO", f"revisión vencida desde {meta['proxima_revision']}"))
        if meta.get("traduccion_estado", "revisada") not in ("", "revisada"):
            h.append(("AVISO", f"aprobado con la traducción sin revisar ({meta['traduccion_estado']})"))

    try:
        en_archivo = "90-archivo" in ruta.relative_to(raiz).parts[:-1]
    except ValueError:
        en_archivo = False
    if estado == "obsoleto" and not en_archivo:
        h.append(("AVISO", "está obsoleto pero no está en 90-archivo/"))
    if estado and estado != "obsoleto" and en_archivo:
        h.append(("AVISO", f"está en 90-archivo/ pero su estado es {estado}"))

    marcadores = RE_MARCADOR.findall(_limpio(cuerpo))
    if marcadores:
        h.append(("ERROR" if estado == "aprobado" else "AVISO", f"quedan marcadores sin rellenar: {marcadores[0]}"))
    if RE_GUIA.search(cuerpo) and estado in ("revision", "aprobado"):
        h.append(("ERROR" if estado == "aprobado" else "AVISO", "quedan comentarios GUÍA de la plantilla por borrar"))
    if not RE_H1.search(cuerpo):
        h.append(("AVISO", "falta el título como encabezado # en el cuerpo"))
    if estado == "aprobado" and not RE_HISTORIAL.search(cuerpo):
        h.append(("AVISO", "falta la sección Historial de cambios"))

    _comprobar_enlaces(ruta, raiz, cuerpo, estado, h, nombres)
    return meta, h


def validar_biblioteca(raiz: Path, hoy=None):
    """Devuelve (documentos, hallazgos). documentos = [{'ruta','meta'}], hallazgos = [Hallazgo]."""
    raiz = Path(raiz)
    hoy = hoy or datetime.date.today()
    documentos, hallazgos = [], []
    rutas = bib.documentos_de(raiz)
    nombres = [r.name for r in rutas]
    for ruta in rutas:
        meta, lista = validar_documento(ruta, raiz, hoy, nombres)
        documentos.append({"ruta": ruta, "meta": meta})
        hallazgos.extend(Hallazgo(ruta, nivel, msg) for nivel, msg in lista)

    # Cruces entre documentos: ID repetido en un idioma y parejas ES-EN
    por_id = defaultdict(list)
    for d in documentos:
        partes = bib.partir_nombre(d["ruta"].name)
        if partes:
            por_id[partes["id"]].append((partes["idioma"], d))
    for id_doc, entradas in por_id.items():
        vistos = {}
        for idioma, d in entradas:
            if idioma in vistos:
                hallazgos.append(Hallazgo(d["ruta"], "ERROR", f"el id {id_doc} está repetido en {idioma}: ya lo usa {vistos[idioma].name}"))
            else:
                vistos[idioma] = d["ruta"]
        idiomas = {i: d for i, d in entradas}
        for idioma, d in idiomas.items():
            meta, ruta = d["meta"], d["ruta"]
            enlace = meta.get("traduccion", "")
            otro = "en" if idioma == "es" else "es"
            if enlace:
                destino = ruta.parent / enlace
                if not destino.exists():
                    hallazgos.append(Hallazgo(ruta, "ERROR", f"la traducción enlazada no existe: {enlace}"))
                elif otro in idiomas and idiomas[otro]["meta"].get("traduccion") != ruta.name:
                    hallazgos.append(Hallazgo(ruta, "AVISO", "la pareja no enlaza de vuelta a este fichero en su campo traduccion"))
            elif otro in idiomas:
                hallazgos.append(Hallazgo(ruta, "AVISO", f"existe la versión .{otro}.md pero falta el campo traduccion"))
            if otro in idiomas:
                estado_otro = idiomas[otro]["meta"].get("traduccion_estado", "")
                if meta.get("estado") == "aprobado" and estado_otro in ("pendiente", "borrador-ia"):
                    hallazgos.append(Hallazgo(ruta, "AVISO", f"aprobado, pero su versión .{otro}.md sigue {estado_otro}"))
                v1, v2 = meta.get("version"), idiomas[otro]["meta"].get("version")
                if v1 and v2 and v1 != v2 and "borrador" not in (meta.get("estado"), idiomas[otro]["meta"].get("estado")):
                    hallazgos.append(Hallazgo(ruta, "AVISO", f"versión {v1} distinta de la de su pareja {otro} ({v2}): traducción desfasada"))
    return documentos, hallazgos


def _celda(texto) -> str:
    return str(texto or "").replace("|", "\\|").replace("\n", " ")


def generar_registro(raiz: Path, documentos: list, hallazgos: list, hoy=None) -> str:
    hoy = hoy or datetime.date.today()
    errores = sum(1 for h in hallazgos if h.nivel == "ERROR")
    avisos = sum(1 for h in hallazgos if h.nivel == "AVISO")
    lineas = [
        "---", "tipo: registro-generado", "titulo: Registro de la biblioteca", f"generado: {hoy.isoformat()}",
        "tags:", "  - doc/registro", "---", "",
        "# Registro de la biblioteca", "",
        "> Generado por `scripts/validar-biblioteca.py --registro`. No se edita a mano: se regenera.", "",
        f"{len(documentos)} documentos · {errores} errores · {avisos} avisos · generado el {hoy.isoformat()}", "",
    ]
    por_tipo = defaultdict(list)
    for d in documentos:
        partes = bib.partir_nombre(d["ruta"].name)
        codigo = bib.partir_id(partes["id"])["tipo"] if partes and bib.partir_id(partes["id"]) else "?"
        por_tipo[codigo].append(d)
    for codigo in list(bib.TIPOS) + ["?"]:
        docs = por_tipo.get(codigo)
        if not docs:
            continue
        nombre = f"{bib.TIPOS[codigo]['es']} / {bib.TIPOS[codigo]['en']}" if codigo in bib.TIPOS else "Sin clasificar"
        lineas += [f"## {codigo} · {nombre}", "",
                   "| ID | Título | Idioma | Versión | Estado | Aplicación | Cliente | Próxima revisión | Traducción |",
                   "|---|---|---|---|---|---|---|---|---|"]
        for d in sorted(docs, key=lambda x: x["ruta"].name):
            m, ruta = d["meta"], d["ruta"]
            lineas.append("| " + " | ".join([
                f"[[{ruta.stem}\\|{_celda(m.get('id', ruta.stem))}]]", _celda(m.get("titulo")), _celda(m.get("idioma")),
                _celda(m.get("version")), _celda(m.get("estado")), _celda(m.get("aplicacion")), _celda(m.get("cliente")),
                _celda(m.get("proxima_revision")), _celda(m.get("traduccion_estado") or ("sí" if m.get("traduccion") else "")),
            ]) + " |")
        lineas.append("")
    vencidas = [d for d in documentos if d["meta"].get("estado") == "aprobado"
                and bib.fecha_valida(d["meta"].get("proxima_revision", "")) and d["meta"]["proxima_revision"] < hoy.isoformat()]
    if vencidas:
        lineas += ["## Revisiones vencidas", ""]
        lineas += [f"- [[{d['ruta'].stem}\\|{d['meta'].get('id')}]] · {d['meta'].get('proxima_revision')} · {_celda(d['meta'].get('propietario'))}"
                   for d in vencidas]
        lineas.append("")
    return "\n".join(lineas) + "\n"


def _sin_fecha_de_generacion(texto: str) -> str:
    """El registro sin las líneas que solo cambian con la fecha de hoy."""
    return "\n".join(l for l in texto.splitlines() if not l.startswith("generado:") and "generado el " not in l)


def escribir_registro(destino: Path, texto: str) -> bool:
    """Escribe el registro solo si algo más que la fecha ha cambiado: así no mueve la fecha del fichero
    (y no avisa de un cambio a quien vigile la carpeta, como la sincronización nocturna del vault). True si escribió."""
    destino = Path(destino)
    if destino.exists() and _sin_fecha_de_generacion(destino.read_text(encoding="utf-8")) == _sin_fecha_de_generacion(texto):
        return False
    bib.escribir_texto(destino, texto)
    return True


def ruta_registro(raiz: Path) -> Path:
    gobierno = Path(raiz) / "00-gobierno"
    return (gobierno if gobierno.is_dir() else Path(raiz)) / "00_Registro.md"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("biblioteca", nargs="?", help="Carpeta raíz de la biblioteca (por defecto: BIBLIOTECA_TAZUKE o conocimiento/biblioteca)")
    p.add_argument("--registro", action="store_true", help="Escribe también 00_Registro.md")
    p.add_argument("--estricto", action="store_true", help="Los avisos también hacen fallar (salida 1)")
    p.add_argument("--hoy", help="Fecha de hoy AAAA-MM-DD (solo para pruebas)")
    args = p.parse_args()

    raiz = bib.raiz_biblioteca(args.biblioteca)
    if not raiz.is_dir():
        print(f"No encuentro la biblioteca: {raiz}", file=sys.stderr)
        return 2
    hoy = datetime.date.fromisoformat(args.hoy) if args.hoy else datetime.date.today()

    documentos, hallazgos = validar_biblioteca(raiz, hoy)
    for h in sorted(hallazgos, key=lambda x: (str(x.ruta), x.nivel)):
        print(f"{h.nivel:<6} {h.ruta.relative_to(raiz)}: {h.mensaje}")
    errores = sum(1 for h in hallazgos if h.nivel == "ERROR")
    avisos = sum(1 for h in hallazgos if h.nivel == "AVISO")
    print(f"{len(documentos)} documentos · {errores} errores · {avisos} avisos  ({raiz})")

    if args.registro:
        destino = ruta_registro(raiz)
        escrito = escribir_registro(destino, generar_registro(raiz, documentos, hallazgos, hoy))
        print(f"Registro: {destino}" + ("" if escrito else " (sin cambios)"))
    return 1 if errores or (args.estricto and avisos) else 0


if __name__ == "__main__":
    raise SystemExit(main())
