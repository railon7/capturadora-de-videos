from PIL import Image, ImageDraw, ImageFilter

from _util import cargar_modulo

m = cargar_modulo("detectar-redundantes.py")


def _imagen_con_lineas(semilla: int):
    img = Image.new("RGB", (100, 100), color="white")
    d = ImageDraw.Draw(img)
    for i in range(0, 100, 7 + semilla):
        d.line((i, 0, 100 - i, 100), fill="black", width=2)
    return img


def test_hash_perceptivo_identico_para_imagenes_iguales():
    img = _imagen_con_lineas(1)
    assert m.hash_perceptivo(img) == m.hash_perceptivo(img.copy())


def test_distancia_hamming_cero_para_hashes_iguales():
    assert m.distancia_hamming(0b1010, 0b1010) == 0


def test_distancia_hamming_cuenta_bits_distintos():
    assert m.distancia_hamming(0b0000, 0b1011) == 3


def test_nitidez_detecta_imagen_borrosa():
    nitida = _imagen_con_lineas(1)
    borrosa = nitida.filter(ImageFilter.GaussianBlur(8))
    assert m.puntuacion_nitidez(nitida) > m.puntuacion_nitidez(borrosa)


def test_percentil_casos_basicos():
    valores = [10, 20, 30, 40, 50]
    assert m.percentil(valores, 0) == 10
    assert m.percentil(valores, 100) == 50
    assert m.percentil(valores, 50) == 30


def test_percentil_lista_vacia():
    assert m.percentil([], 50) == 0.0
