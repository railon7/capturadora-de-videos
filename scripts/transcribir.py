#!/usr/bin/env python3
"""Transcribe un vídeo con marca de tiempo por segmento (Whisper).

Con una transcripción de este tipo, el paso "localiza los tiempos con las
hojas de contacto" de metodologia/de-video-a-guion-y-patrones.md pasa a ser
opcional: la cita literal de cada bloque del guion ya trae su segundo exacto,
sin tener que buscarlo a mano en el vídeo.

Requiere: pip install faster-whisper
ffmpeg debe estar en el PATH (lo instala scripts/extraer-capturas.ps1 si hace falta).

Uso:
    python transcribir.py <video> [--salida CARPETA] [--modelo medium] [--idioma es]

Salida (en la carpeta indicada, por defecto "Analisis" junto al vídeo):
    transcripcion.tsv   inicio_seg, fin_seg, hora, texto  (para procesar con otro script)
    transcripcion.md    igual, en formato legible: **HH:MM:SS** texto por línea
"""
import argparse
import sys
from pathlib import Path


def formatear_hora(segundos: float) -> str:
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", help="Ruta al vídeo o audio a transcribir")
    parser.add_argument("--salida", default=None, help="Carpeta de salida (por defecto: Analisis/ junto al vídeo)")
    parser.add_argument("--modelo", default="medium", help="Tamaño del modelo Whisper: tiny, base, small, medium, large-v3 (por defecto: medium)")
    parser.add_argument("--idioma", default=None, help="Código de idioma (es, en, ja...). Si se omite, Whisper lo detecta solo")
    parser.add_argument("--dispositivo", default="auto", help="cpu, cuda o auto (por defecto: auto)")
    args = parser.parse_args()

    video = Path(args.video)
    if not video.exists():
        print(f"No encuentro el vídeo: {video}", file=sys.stderr)
        return 1

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Falta faster-whisper. Instálalo con: pip install faster-whisper", file=sys.stderr)
        return 1

    salida = Path(args.salida) if args.salida else video.parent / "Analisis"
    salida.mkdir(parents=True, exist_ok=True)

    print(f"Cargando modelo Whisper '{args.modelo}' ({args.dispositivo})...")
    compute_type = "int8" if args.dispositivo != "cuda" else "float16"
    modelo = WhisperModel(args.modelo, device=args.dispositivo, compute_type=compute_type)

    print(f"Transcribiendo {video.name} (esto tarda; un vídeo de 90 min puede llevar bastante en CPU)...")
    segmentos, info = modelo.transcribe(str(video), language=args.idioma, vad_filter=True)

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
