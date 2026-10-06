#!/usr/bin/env python3
"""Descarga vídeos de YouTube (u otra web que soporte yt-dlp) para procesarlos aquí.

Todos los demás scripts trabajan con un fichero de vídeo local. Si el vídeo está
en una web, este es el paso 0: lo deja en la carpeta indicada como .mp4, listo
para extraer-capturas.ps1.

Se le pasan enlaces sueltos o un fichero de lista con una línea por vídeo, en
cualquiera de estas dos formas:

    Creación de una ficha de cliente = https://youtu.be/ciHgR9xX1PI?si=sqWS...
    https://youtu.be/VMM_P4AEcuA

Con nombre, el fichero se llama así; sin nombre, como el título del vídeo. El
script corrige lo que suele romper el comando a mano:

  - Comillas tipográficas (” “) y espacios pegados al enlace, típicos al copiar
    desde el móvil, Word o WhatsApp.
  - El parámetro de seguimiento ?si=... de los enlaces compartidos.
  - Caracteres que Windows no admite en un nombre de fichero (: | ? * " < > / \\),
    que cambia por un guion o quita, y emojis de los títulos.

Al final dice qué vídeos se descargaron y cuáles fallaron, y sigue con el
resto aunque uno falle. Los que ya existen en la carpeta se saltan.

**Descarga solo vídeos propios, del cliente o con permiso del autor.** Las
condiciones de YouTube no permiten descargar contenido ajeno sin autorización,
y si el material va a formación o venta cuentan también los derechos de autor.

Requiere: pip install yt-dlp, y ffmpeg (junta vídeo y audio en un .mp4).

Uso:
    python descargar-videos.py "https://youtu.be/ciHgR9xX1PI" --carpeta "C:\\Videos\\FactuSol"
    python descargar-videos.py --lista enlaces.txt --carpeta "C:\\Videos\\FactuSol"
    python descargar-videos.py --lista enlaces.txt --carpeta "..." --calidad 720
"""
import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Comillas y espacios raros que se cuelan al copiar un comando o un enlace
COMILLAS = "\"'“”„‟‘’‚‛«»`"
PARAMETROS_SEGUIMIENTO = {"si", "feature", "pp", "utm_source", "utm_medium", "utm_campaign"}
PROHIBIDOS_WINDOWS = '<>:"/\\|?*'
NOMBRES_RESERVADOS_WINDOWS = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}


def limpiar_url(url: str) -> str:
    """Quita comillas, espacios y parámetros de seguimiento (?si=...) de un enlace."""
    url = url.strip().strip(COMILLAS).strip()
    url = "".join(url.split())  # espacios metidos por error dentro del enlace
    partes = urlsplit(url)
    consulta = [(k, v) for k, v in parse_qsl(partes.query, keep_blank_values=True)
                if k.lower() not in PARAMETROS_SEGUIMIENTO]
    return urlunsplit(partes._replace(query=urlencode(consulta)))


def es_url(texto: str) -> bool:
    return bool(re.match(r"^https?://\S+$", texto.strip().strip(COMILLAS).strip()))


def limpiar_nombre(nombre: str) -> str:
    """Nombre de fichero válido en Windows: sin caracteres prohibidos, sin emojis
    ni espacios sobrantes. Los dos puntos y la barra vertical pasan a ' - '."""
    nombre = re.sub(r"\s+", " ", nombre)  # saltos de línea y tabuladores, a espacio
    nombre = nombre.strip().strip(COMILLAS).strip()
    nombre = re.sub(r"\s*[:|]\s*", " - ", nombre)
    nombre = "".join(
        c for c in nombre
        if c not in PROHIBIDOS_WINDOWS
        and unicodedata.category(c)[0] != "C"     # controles, saltos de línea
        and unicodedata.category(c) != "So"       # emojis y otros símbolos
    )
    nombre = re.sub(r"\s+", " ", nombre).strip(" .-")
    if nombre.upper() in NOMBRES_RESERVADOS_WINDOWS:
        nombre = f"{nombre}_"
    return nombre


def parsear_linea(linea: str):
    """'Nombre = URL' -> (nombre, url); 'URL' -> (None, url); vacía o comentario -> None."""
    linea = linea.strip()
    if not linea or linea.startswith("#"):
        return None
    if es_url(linea):
        return None, limpiar_url(linea)
    # El "=" de un enlace (watch?v=...) no separa: el separador es el que va antes de http
    m = re.match(r"^(?P<nombre>.+?)\s*=\s*(?P<url>[" + re.escape(COMILLAS) + r"\s]*https?://.+)$", linea)
    if not m:
        raise ValueError(f"No reconozco esta línea (formato: Nombre = URL, o solo URL): {linea!r}")
    nombre = limpiar_nombre(m.group("nombre"))
    return (nombre or None), limpiar_url(m.group("url"))


def leer_lista(ruta: Path) -> list:
    entradas = []
    for n, linea in enumerate(ruta.read_text(encoding="utf-8-sig").splitlines(), 1):
        try:
            entrada = parsear_linea(linea)
        except ValueError as e:
            raise ValueError(f"{ruta.name}, línea {n}: {e}") from None
        if entrada:
            entradas.append(entrada)
    return entradas


def comando_ytdlp(base: list, url: str, carpeta: Path, nombre: str = None, calidad: int = 1080) -> list:
    """Orden de yt-dlp: mejor vídeo hasta `calidad` + mejor audio, unidos en .mp4."""
    plantilla = f"{nombre}.%(ext)s" if nombre else "%(title)s.%(ext)s"
    return base + [
        "-f", f"bv*[height<={calidad}]+ba/b[height<={calidad}]/b",
        "--merge-output-format", "mp4",
        "--windows-filenames",
        "--no-playlist",
        "--no-overwrites",
        "-P", str(carpeta),
        "-o", plantilla,
        url,
    ]


def obtener_titulo(base: list, url: str) -> str:
    """Título del vídeo, sin descargarlo. None si no se puede leer."""
    r = subprocess.run(base + ["--print", "%(title)s", "--skip-download", "--no-playlist", url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    lineas = [l for l in r.stdout.splitlines() if l.strip()]
    return lineas[-1].strip() if r.returncode == 0 and lineas else None


def localizar_ytdlp() -> list:
    """['yt-dlp'] si está en el PATH, [python, -m, yt_dlp] si solo está el módulo, o []."""
    exe = shutil.which("yt-dlp")
    if exe:
        return [exe]
    try:
        import yt_dlp  # noqa: F401
        return [sys.executable, "-m", "yt_dlp"]
    except ImportError:
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("enlaces", nargs="*", help="Uno o varios enlaces (o 'Nombre = URL' entre comillas)")
    parser.add_argument("--lista", default=None, help="Fichero de texto con una línea por vídeo: 'Nombre = URL' o solo 'URL'")
    parser.add_argument("--carpeta", default=".", help="Carpeta donde dejar los vídeos (por defecto, la actual)")
    parser.add_argument("--calidad", type=int, default=1080, help="Altura máxima en píxeles (por defecto 1080: sobra para leer pantallas y pesa mucho menos)")
    args = parser.parse_args()

    try:
        entradas = [parsear_linea(e) for e in args.enlaces]
        entradas = [e for e in entradas if e]
        if args.lista:
            ruta_lista = Path(args.lista)
            if not ruta_lista.exists():
                print(f"No encuentro la lista: {ruta_lista}", file=sys.stderr)
                return 1
            entradas += leer_lista(ruta_lista)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    if not entradas:
        print("No hay nada que descargar: pasa enlaces o --lista fichero.txt", file=sys.stderr)
        return 1

    base = localizar_ytdlp()
    if not base:
        print("Falta yt-dlp. Instálalo con: pip install yt-dlp", file=sys.stderr)
        return 1
    if not shutil.which("ffmpeg"):
        print("Aviso: no encuentro ffmpeg en el PATH. Sin él, yt-dlp no puede juntar vídeo y", file=sys.stderr)
        print("audio en un .mp4 y bajará una calidad peor. Instálalo con: winget install Gyan.FFmpeg", file=sys.stderr)

    carpeta = Path(args.carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    print(f"Descargando {len(entradas)} vídeo(s) en {carpeta.resolve()}\n")

    fallos = []
    for i, (nombre, url) in enumerate(entradas, 1):
        if not nombre:
            # Sin nombre, el título del vídeo, limpio como uno escrito a mano
            # (--windows-filenames de yt-dlp deja pasar emojis como el ✅)
            titulo = obtener_titulo(base, url)
            nombre = limpiar_nombre(titulo) if titulo else None
        etiqueta = nombre or url
        if nombre and (carpeta / f"{nombre}.mp4").exists():
            print(f"[{i}/{len(entradas)}] YA ESTABA  {etiqueta}")
            continue
        print(f"[{i}/{len(entradas)}] {etiqueta} ...", flush=True)
        r = subprocess.run(comando_ytdlp(base, url, carpeta, nombre, args.calidad),
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        errores = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("ERROR")]
        if r.returncode != 0 or errores:
            fallos.append(etiqueta)
            print(f"    FALLO: {errores[-1] if errores else 'yt-dlp terminó con código ' + str(r.returncode)}")
        else:
            print("    OK")

    print(f"\n{len(entradas) - len(fallos)} de {len(entradas)} descargados en {carpeta.resolve()}")
    if fallos:
        print("Fallaron:", *fallos, sep="\n  - ")
        print("Si es un vídeo privado o con restricción de edad, prueba a lanzar yt-dlp a mano")
        print("con --cookies-from-browser edge (o chrome) para usar tu sesión.")
        return 1
    print("\nSiguiente paso: scripts/extraer-capturas.ps1 -Video \"<vídeo>\" -Trabajo \"<carpeta de trabajo>\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
