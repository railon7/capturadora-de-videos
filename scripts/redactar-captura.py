#!/usr/bin/env python3
"""Tapa DNI, NIE, CIF, tarjetas y nombres de una lista directamente en la imagen.

Por ley de protección de datos, en las capturas que salen de un vídeo no
pueden aparecer DNI, CIF, ni nombres propios o de empresa. Este script
automatiza lo que `auditar-privacidad.py` solo avisaba: localiza el texto
sensible con OCR (con su caja de posición) y lo tapa sobre una COPIA de la
imagen, nunca sobre la original.

Dos categorías, con una diferencia importante:

  - DNI / NIE / CIF / tarjeta / email / teléfono: detección automática,
    fiable, porque tienen un patrón verificable (dígito de control).
  - Nombres propios y de empresa: **no se detectan solos**. No existe un
    patrón matemático para un nombre — hace falta saber cuáles son. Pásalos
    con --nombres fichero.txt (uno por línea; los conoce quien ha visto el
    vídeo o leído la transcripción — un LLM puede generar esa lista).

**Esto sigue sin ser una garantía legal por sí solo.** Revisa el resultado
antes de entregarlo — es una ayuda que ahorra hacerlo a mano pantalla por
pantalla, no una certificación de cumplimiento.

Requiere: pip install pytesseract pillow
y el binario de Tesseract-OCR: winget install --id UB-Mannheim.TesseractOCR

Uso (un fichero):
    python redactar-captura.py entrada.png salida.png --nombres nombres-a-tapar.txt

Uso (una carpeta entera, mismo nombre de fichero dentro de la salida):
    python redactar-captura.py "Capturas/Editadas" "Capturas/Editadas-redactadas" --carpeta --nombres nombres-a-tapar.txt
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

RUTAS_TESSERACT_WINDOWS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def localizar_tesseract(cmd_manual: str = None) -> str:
    if cmd_manual:
        return cmd_manual if Path(cmd_manual).exists() else None
    en_path = shutil.which("tesseract")
    if en_path:
        return en_path
    for candidato in RUTAS_TESSERACT_WINDOWS:
        if Path(candidato).exists():
            return candidato
    return None


# --- Los mismos validadores de auditar-privacidad.py, duplicados a propósito:
# cada script de este repo es autocontenido y se puede copiar suelto.

RE_TARJETA = re.compile(r"^(?:\d[ -]?){13,19}$")
RE_DNI = re.compile(r"^(\d{8})([A-Za-z])$")
RE_NIE = re.compile(r"^([XYZxyz])(\d{7})([A-Za-z])$")
RE_CIF = re.compile(r"^([ABCDEFGHJKLMNPQRSUVWabcdefghjklmnpqrsuvw])(\d{7})([0-9A-Ja-j])$")
RE_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
RE_TELEFONO = re.compile(r"^(?:\+34|0034)?[6789]\d{8}$")

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"
LETRAS_CIF_CONTROL = "JABCDEFGHI"


def luhn_valido(numero: str) -> bool:
    digitos = [int(c) for c in numero if c.isdigit()]
    if len(digitos) < 13:
        return False
    suma = 0
    for i, d in enumerate(reversed(digitos)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        suma += d
    return suma % 10 == 0


def dni_valido(numero: str, letra: str) -> bool:
    return LETRAS_DNI[int(numero) % 23] == letra.upper()


def nie_valido(prefijo: str, numero: str, letra: str) -> bool:
    mapa = {"X": "0", "Y": "1", "Z": "2"}
    return dni_valido(mapa[prefijo.upper()] + numero, letra)


def cif_valido(letra_inicial: str, digitos: str, control: str) -> bool:
    letra_inicial, control = letra_inicial.upper(), control.upper()
    suma_par = sum(int(d) for d in digitos[1::2])
    suma_impar = 0
    for d in digitos[0::2]:
        doble = int(d) * 2
        suma_impar += doble // 10 + doble % 10
    digito_control = (10 - (suma_par + suma_impar) % 10) % 10
    if letra_inicial in "ABEH":
        return control == str(digito_control)
    if letra_inicial in "KPQS":
        return control == LETRAS_CIF_CONTROL[digito_control]
    if letra_inicial in "CDFGJLMNRUVW":
        return control == str(digito_control) or control == LETRAS_CIF_CONTROL[digito_control]
    return False


def clasificar_palabra(palabra: str) -> str:
    """Devuelve el tipo de dato sensible si la palabra (un token OCR, sin
    espacios) coincide con un patrón verificable, o None si no coincide con
    ninguno."""
    p = palabra.strip()
    if RE_EMAIL.match(p):
        return "email"
    if RE_TELEFONO.match(p):
        return "teléfono"
    m = RE_DNI.match(p)
    if m and dni_valido(*m.groups()):
        return "DNI"
    m = RE_NIE.match(p)
    if m and nie_valido(*m.groups()):
        return "NIE"
    m = RE_CIF.match(p)
    if m and cif_valido(*m.groups()):
        return "CIF"
    if RE_TARJETA.match(p) and luhn_valido(p):
        return "tarjeta"
    return None


def leer_lista_nombres(ruta: str) -> list:
    if not ruta:
        return []
    return [
        linea.strip()
        for linea in Path(ruta).read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    ]


def obtener_palabras_ocr(imagen_path: Path):
    import pytesseract
    from pytesseract import Output
    from PIL import Image

    datos = pytesseract.image_to_data(Image.open(imagen_path), lang="spa+eng", output_type=Output.DICT)
    palabras = []
    for i in range(len(datos["text"])):
        texto = datos["text"][i].strip()
        if not texto:
            continue
        palabras.append({
            "texto": texto,
            "linea": (datos["block_num"][i], datos["par_num"][i], datos["line_num"][i]),
            "caja": (datos["left"][i], datos["top"][i], datos["width"][i], datos["height"][i]),
        })
    return palabras


def caja_union(cajas: list):
    xs0 = [x for x, y, w, h in cajas]
    ys0 = [y for x, y, w, h in cajas]
    xs1 = [x + w for x, y, w, h in cajas]
    ys1 = [y + h for x, y, w, h in cajas]
    return (min(xs0), min(ys0), max(xs1) - min(xs0), max(ys1) - min(ys0))


def encontrar_cajas_a_redactar(palabras: list, nombres: list):
    """Devuelve [(caja, tipo), ...]. Primero por patrón verificable palabra a
    palabra; luego, dentro de cada línea, por coincidencia literal con la
    lista de nombres (que sí puede ocupar varias palabras seguidas)."""
    encontradas = []

    for p in palabras:
        tipo = clasificar_palabra(p["texto"])
        if tipo:
            encontradas.append((p["caja"], tipo))

    if nombres:
        lineas = {}
        for idx, p in enumerate(palabras):
            lineas.setdefault(p["linea"], []).append(idx)

        for indices in lineas.values():
            texto_linea = " ".join(palabras[i]["texto"] for i in indices)
            texto_linea_bajo = texto_linea.lower()
            for nombre in nombres:
                nombre_bajo = nombre.lower().strip()
                if not nombre_bajo or nombre_bajo not in texto_linea_bajo:
                    continue
                # localiza qué palabras de la línea componen la coincidencia
                num_palabras_nombre = len(nombre_bajo.split())
                for inicio in range(len(indices) - num_palabras_nombre + 1):
                    ventana = indices[inicio:inicio + num_palabras_nombre]
                    texto_ventana = " ".join(palabras[i]["texto"] for i in ventana).lower()
                    if texto_ventana == nombre_bajo or nombre_bajo in texto_ventana:
                        caja = caja_union([palabras[i]["caja"] for i in ventana])
                        encontradas.append((caja, "nombre de la lista"))

    return encontradas


def redactar_imagen(imagen_path: Path, salida_path: Path, cajas: list, estilo: str, color: str, margen: int):
    from PIL import Image, ImageDraw, ImageFilter

    img = Image.open(imagen_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    ancho, alto = img.size

    for (x, y, w, h), _tipo in cajas:
        caja = (
            max(0, x - margen), max(0, y - margen),
            min(ancho, x + w + margen), min(alto, y + h + margen),
        )
        if estilo == "difuminado":
            region = img.crop(caja).filter(ImageFilter.GaussianBlur(14))
            img.paste(region, caja)
        else:
            draw.rectangle(caja, fill=color)

    salida_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(salida_path)


def procesar_un_fichero(entrada: Path, salida: Path, nombres: list, estilo: str, color: str, margen: int) -> dict:
    palabras = obtener_palabras_ocr(entrada)
    cajas = encontrar_cajas_a_redactar(palabras, nombres)
    redactar_imagen(entrada, salida, cajas, estilo, color, margen)
    resumen = {}
    for _caja, tipo in cajas:
        resumen[tipo] = resumen.get(tipo, 0) + 1
    return resumen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entrada", help="Imagen o, con --carpeta, carpeta de imágenes")
    parser.add_argument("salida", help="Fichero o carpeta de salida, siempre distinto de la entrada")
    parser.add_argument("--carpeta", action="store_true", help="Trata entrada/salida como carpetas, no como ficheros sueltos")
    parser.add_argument("--nombres", default=None, help="Fichero de texto, un nombre propio o de empresa por línea — esto NO se detecta solo, hace falta la lista")
    parser.add_argument("--estilo", choices=["caja", "difuminado"], default="caja",
                         help="'caja' rellena con un color sólido (recomendado: el difuminado no garantiza que una cadena corta como un DNI no se pueda reconstruir). Por defecto: caja")
    parser.add_argument("--color", default="#2b2b2b", help="Color de la caja sólida (por defecto un gris oscuro discreto)")
    parser.add_argument("--margen", type=int, default=3, help="Píxeles de margen alrededor de cada caja detectada (por defecto 3)")
    parser.add_argument("--tesseract-cmd", default=None, help="Ruta al ejecutable de tesseract, si no está en el PATH ni en su ubicación habitual")
    parser.add_argument("--forzar", action="store_true", help="Permite que entrada y salida sean el mismo fichero/carpeta (no recomendado)")
    args = parser.parse_args()

    entrada = Path(args.entrada)
    salida = Path(args.salida)

    if not entrada.exists():
        print(f"No encuentro: {entrada}", file=sys.stderr)
        return 1
    if entrada.resolve() == salida.resolve() and not args.forzar:
        print("Entrada y salida son el mismo sitio. Usa uno distinto o --forzar.", file=sys.stderr)
        print("La imagen redactada tiene que quedar aparte de la original: si el", file=sys.stderr)
        print("OCR falla y deja algo sin tapar, la original con los datos reales", file=sys.stderr)
        print("todavía tiene que estar disponible para repetirlo.", file=sys.stderr)
        return 1

    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError:
        print("Falta pytesseract y/o pillow. Instala con: pip install pytesseract pillow", file=sys.stderr)
        return 1

    ruta_tesseract = localizar_tesseract(args.tesseract_cmd)
    if not ruta_tesseract:
        print("No encuentro el binario de tesseract.", file=sys.stderr)
        print("Instálalo con: winget install --id UB-Mannheim.TesseractOCR", file=sys.stderr)
        print("o indica la ruta con --tesseract-cmd \"C:\\ruta\\a\\tesseract.exe\"", file=sys.stderr)
        return 1
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = ruta_tesseract

    nombres = leer_lista_nombres(args.nombres)
    if not nombres:
        print("Aviso: sin --nombres, esta pasada solo tapa DNI/NIE/CIF/tarjeta/email/teléfono.", file=sys.stderr)
        print("Los nombres propios y de empresa NO se detectan sin la lista.", file=sys.stderr)

    resumen_total = {}
    if args.carpeta:
        imagenes = sorted(
            [p for p in entrada.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")],
            key=lambda p: p.name,
        )
        if not imagenes:
            print(f"No hay imágenes en {entrada}", file=sys.stderr)
            return 1
        salida.mkdir(parents=True, exist_ok=True)
        for i, imagen in enumerate(imagenes, 1):
            resumen = procesar_un_fichero(imagen, salida / imagen.name, nombres, args.estilo, args.color, args.margen)
            for tipo, n in resumen.items():
                resumen_total[tipo] = resumen_total.get(tipo, 0) + n
            if i % 10 == 0:
                print(f"  ... {i}/{len(imagenes)}")
        print(f"{len(imagenes)} imágenes procesadas -> {salida}")
    else:
        resumen_total = procesar_un_fichero(entrada, salida, nombres, args.estilo, args.color, args.margen)
        print(f"Redactada: {salida}")

    if resumen_total:
        print("Tapado por tipo:", ", ".join(f"{t}: {n}" for t, n in sorted(resumen_total.items())))
    else:
        print("No se ha encontrado nada que tapar con los patrones/lista actuales.")
    print("Esto no es una garantía legal por sí solo — revisa el resultado antes de entregarlo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
