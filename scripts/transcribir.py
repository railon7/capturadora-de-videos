#!/usr/bin/env python3
"""Transcribe un vídeo con marca de tiempo por segmento (Whisper).

Con una transcripción de este tipo, el paso "localiza los tiempos con las
hojas de contacto" de metodologia/de-video-a-guion-y-patrones.md pasa a ser
opcional: la cita literal de cada bloque del guion ya trae su segundo exacto,
sin tener que buscarlo a mano en el vídeo.

Requiere: pip install faster-whisper
ffmpeg en el PATH o en la copia portable que deja scripts/extraer-capturas.ps1
(_herramientas/ffmpeg). El audio se decodifica con ffmpeg y no con PyAV, cuyas
versiones no siempre casan con las de faster-whisper.

GPU (--dispositivo cuda, mucho más rápido): pip install nvidia-cublas-cu12 nvidia-cudnn-cu12.
En Windows el script añade solo esas librerías a la ruta de búsqueda de DLL.

Uso:
    python transcribir.py <video> [--salida CARPETA] [--modelo medium] [--idioma es]

Salida (en la carpeta indicada, por defecto "Analisis" junto al vídeo):
    transcripcion.tsv   inicio_seg, fin_seg, hora, texto  (para procesar con otro script)
    transcripcion.md    igual, en formato legible: **HH:MM:SS** texto por línea
"""
import argparse
import glob
import os
import shutil
import site
import subprocess
import sys
from pathlib import Path

FRECUENCIA_WHISPER = 16000


def formatear_hora(segundos: float) -> str:
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def localizar_ffmpeg(cmd_manual: str = None, carpetas: list = ()) -> str:
    """ffmpeg indicado, el del PATH o la copia portable que deja
    extraer-capturas.ps1 en <carpeta de trabajo>/_herramientas/ffmpeg."""
    if cmd_manual:
        return cmd_manual if Path(cmd_manual).exists() else None
    en_path = shutil.which("ffmpeg")
    if en_path:
        return en_path
    for carpeta in carpetas:
        for candidato in (Path(carpeta) / "_herramientas" / "ffmpeg" / "bin").glob("ffmpeg*"):
            if candidato.stem == "ffmpeg":
                return str(candidato)
    return None


def preparar_dlls_cuda() -> list:
    """En Windows, las librerías CUDA instaladas con pip (nvidia-cublas-cu12,
    nvidia-cudnn-cu12) viven en site-packages/nvidia/*/bin y Python no las
    encuentra solo: sin esto, --dispositivo cuda falla al cargar cublas/cudnn."""
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return []
    rutas = []
    bases = list(site.getsitepackages()) + [site.getusersitepackages()]
    for base in bases:
        for carpeta in glob.glob(os.path.join(base, "nvidia", "*", "bin")):
            os.add_dll_directory(carpeta)
            os.environ["PATH"] = carpeta + os.pathsep + os.environ.get("PATH", "")
            rutas.append(carpeta)
    return rutas


def comando_audio(ffmpeg: str, video: Path) -> list:
    """ffmpeg que saca el audio en mono a 16 kHz, PCM de 16 bits, por la salida estándar."""
    return [ffmpeg, "-nostdin", "-v", "error", "-i", str(video), "-vn", "-ac", "1",
            "-ar", str(FRECUENCIA_WHISPER), "-f", "s16le", "-"]


def pcm_a_muestras(pcm: bytes):
    """PCM de 16 bits con signo -> muestras float32 entre -1 y 1, como espera Whisper."""
    import numpy as np

    return np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0


def cargar_audio(ffmpeg: str, video: Path):
    """Decodifica el audio con ffmpeg. faster-whisper lo haría con PyAV, pero
    sus versiones no siempre casan (TypeError con 'metadata_errors')."""
    resultado = subprocess.run(comando_audio(ffmpeg, video), capture_output=True, check=True)
    return pcm_a_muestras(resultado.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", help="Ruta al vídeo o audio a transcribir")
    parser.add_argument("--salida", default=None, help="Carpeta de salida (por defecto: Analisis/ junto al vídeo)")
    parser.add_argument("--modelo", default="medium", help="Tamaño del modelo Whisper: tiny, base, small, medium, large-v3 (por defecto: medium)")
    parser.add_argument("--idioma", default=None, help="Código de idioma (es, en, ja...). Si se omite, Whisper lo detecta solo")
    parser.add_argument("--dispositivo", default="auto", help="cpu, cuda o auto (por defecto: auto)")
    parser.add_argument("--ffmpeg", default=None, help="Ruta a ffmpeg, si no está en el PATH ni en _herramientas/ffmpeg de la carpeta de trabajo")
    args = parser.parse_args()

    video = Path(args.video)
    if not video.exists():
        print(f"No encuentro el vídeo: {video}", file=sys.stderr)
        return 1

    if args.dispositivo != "cpu":
        preparar_dlls_cuda()
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Falta faster-whisper. Instálalo con: pip install faster-whisper", file=sys.stderr)
        return 1

    salida = Path(args.salida) if args.salida else video.parent / "Analisis"
    salida.mkdir(parents=True, exist_ok=True)

    ffmpeg = localizar_ffmpeg(args.ffmpeg, [salida.parent, video.parent])
    if ffmpeg:
        print("Extrayendo el audio con ffmpeg...")
        try:
            audio = cargar_audio(ffmpeg, video)
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg no ha podido leer el audio de {video.name}:", file=sys.stderr)
            print(e.stderr.decode(errors="ignore")[-800:], file=sys.stderr)
            return 1
    else:
        print("Aviso: no encuentro ffmpeg; dejo que faster-whisper lea el vídeo con PyAV.", file=sys.stderr)
        audio = str(video)

    print(f"Cargando modelo Whisper '{args.modelo}' ({args.dispositivo})...")
    compute_type = "int8" if args.dispositivo != "cuda" else "float16"
    modelo = WhisperModel(args.modelo, device=args.dispositivo, compute_type=compute_type)

    print(f"Transcribiendo {video.name} (esto tarda; un vídeo de 90 min puede llevar bastante en CPU)...")
    segmentos, info = modelo.transcribe(audio, language=args.idioma, vad_filter=True)

    ruta_tsv = salida / "transcripcion.tsv"
    ruta_md = salida / "transcripcion.md"

    with ruta_tsv.open("w", encoding="utf-8") as f_tsv, ruta_md.open("w", encoding="utf-8") as f_md:
        f_tsv.write("inicio_seg\tfin_seg\thora\ttexto\n")
        f_md.write(f"# Transcripción — {video.name}\n\n")
        f_md.write(f"Idioma detectado: {info.language} (confianza {info.language_probability:.2f})\n\n")
        n = 0
        for seg in segmentos:
            texto = seg.text.strip()
            hora = formatear_hora(seg.start)
            f_tsv.write(f"{seg.start:.2f}\t{seg.end:.2f}\t{hora}\t{texto}\n")
            f_md.write(f"**{hora}** {texto}\n\n")
            n += 1
            if n % 20 == 0:
                print(f"  ... {n} segmentos, en {hora}")

    print(f"\nListo: {n} segmentos")
    print(f"  {ruta_tsv}")
    print(f"  {ruta_md}")
    print("\nPara construir el mapa del vídeo, busca la cita literal de cada bloque")
    print("en transcripcion.md: la marca de tiempo ya viene puesta, no hace falta")
    print("localizarla con las hojas de contacto salvo para verificarla a ojo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
