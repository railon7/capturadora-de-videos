import sys

import pytest
from PIL import Image, ImageDraw

from _util import cargar_modulo

m = cargar_modulo("recortar-pantalla.py")

PANTALLA = (80, 60, 320, 200)  # x0, y0, x1, y1 de la pantalla compartida


def _fotograma(contenido_oscuro=False, pestana=False):
    """Fotograma de videollamada: fondo oscuro, miniatura de cámara arriba y pantalla clara."""
    img = Image.new("RGB", (400, 230), color=(18, 18, 18))
    d = ImageDraw.Draw(img)
    d.rectangle((170, 8, 230, 50), fill=(200, 160, 150))  # miniatura de cámara, estrecha
    d.rectangle((PANTALLA[0], PANTALLA[1], PANTALLA[2] - 1, PANTALLA[3] - 1), fill="white")
    if contenido_oscuro:
        # Una portada oscura que ocupa casi toda la pantalla compartida
        d.rectangle((PANTALLA[0], PANTALLA[1], PANTALLA[2] - 1, PANTALLA[3] - 30), fill=(30, 20, 40))
    if pestana:
        d.rectangle((190, PANTALLA[1] + 2, 210, PANTALLA[1] + 8), fill=(45, 45, 45))  # ~8 % del ancho, como la real
    d.rectangle((0, 215, 399, 229), fill=(30, 30, 30))  # barra de botones de la aplicación
    return img


def test_tramo_mas_largo_elige_el_mas_largo():
    assert m.tramo_mas_largo([0, 1, 1, 0, 1, 1, 1, 0], 0.5) == (4, 7)


def test_tramo_mas_largo_hasta_el_final():
    assert m.tramo_mas_largo([0, 1, 1], 0.5) == (1, 3)


def test_tramo_mas_largo_sin_valores():
    assert m.tramo_mas_largo([0, 0, 0], 0.5) is None


def test_detecta_la_pantalla_sin_camara_ni_barras():
    assert m.detectar_pantalla(_fotograma()) == PANTALLA


def test_imagen_toda_oscura_no_tiene_pantalla():
    assert m.detectar_pantalla(Image.new("RGB", (400, 230), color=(15, 15, 15))) is None


def test_contenido_oscuro_falla_la_deteccion_aislada():
    # Es el caso que resuelve el consenso: la detección sola no da la caja buena
    assert m.detectar_pantalla(_fotograma(contenido_oscuro=True)) != PANTALLA


def test_consenso_corrige_los_fotogramas_raros_con_el_vecino_estable():
    a, b = (10, 10, 100, 60), (12, 30, 90, 50)
    assert m.consenso([a, a, a, b, None, a]) == [a] * 6


def test_consenso_tolera_diferencias_de_pocos_pixeles():
    a, casi_a = (10, 10, 100, 60), (11, 9, 101, 60)
    assert m.consenso([a, a, a, casi_a]) == [a] * 4


def test_consenso_sin_disposicion_estable_no_cambia_nada():
    cajas = [(0, 0, 10, 10), (5, 5, 50, 50), None]
    assert m.consenso(cajas) == cajas


def test_consenso_respeta_dos_disposiciones_estables():
    con_camara, sin_camara = (350, 170, 1254, 680), (232, 37, 1373, 680)
    cajas = [sin_camara] * 3 + [con_camara] * 3
    assert m.consenso(cajas) == cajas


def test_tapa_la_pestana_de_la_camara():
    recorte = _fotograma(pestana=True).crop(PANTALLA)
    limpio = m.tapar_pestana(recorte)
    zona = limpio.convert("L").crop((190 - PANTALLA[0], 2, 211 - PANTALLA[0], 9))
    assert min(zona.tobytes()) > 200


def test_no_toca_una_fila_de_menu():
    img = Image.new("RGB", (240, 140), color="white")
    d = ImageDraw.Draw(img)
    for x in range(10, 230, 12):  # "letras" repartidas a lo ancho de las primeras filas
        d.rectangle((x, 3, x + 4, 9), fill="black")
    assert m.tapar_pestana(img) is img


def test_sin_pestana_devuelve_la_misma_imagen():
    img = Image.new("RGB", (240, 140), color="white")
    assert m.tapar_pestana(img) is img


def test_parsear_regla():
    assert m.parsear_regla("t_0000*.jpg=232,37,1373,680") == ("t_0000*.jpg", (232, 37, 1373, 680))


@pytest.mark.parametrize("regla", ["t_*.jpg", "t_*.jpg=1,2,3", "=1,2,3,4", "t_*.jpg=10,10,5,20"])
def test_parsear_regla_rechaza_reglas_mal_formadas(regla):
    with pytest.raises(ValueError):
        m.parsear_regla(regla)


def test_carpeta_completa_con_salida_por_defecto(tmp_path, monkeypatch):
    origen = tmp_path / "Rejilla"
    origen.mkdir()
    for i in range(4):
        _fotograma().save(origen / f"t_00000{i}.png")
    _fotograma(contenido_oscuro=True).save(origen / "t_000004.png")
    monkeypatch.setattr(sys, "argv", ["recortar-pantalla.py", str(origen)])
    assert m.main() == 0
    salida = tmp_path / "Rejilla-pantalla"
    tamanos = {Image.open(p).size for p in salida.iterdir()}
    ancho, alto = PANTALLA[2] - PANTALLA[0], PANTALLA[3] - PANTALLA[1]
    assert tamanos == {(ancho, alto)}  # el de contenido oscuro también, por consenso
    assert len(list(origen.iterdir())) == 5  # los originales siguen ahí


def test_forzar_caja_gana_al_consenso(tmp_path, monkeypatch):
    origen = tmp_path / "Rejilla"
    origen.mkdir()
    for i in range(3):
        _fotograma().save(origen / f"t_00000{i}.png")
    monkeypatch.setattr(sys, "argv", ["recortar-pantalla.py", str(origen), "--forzar-caja", "t_000000.png=0,0,50,40"])
    assert m.main() == 0
    assert Image.open(tmp_path / "Rejilla-pantalla" / "t_000000.png").size == (50, 40)


def test_no_pisa_los_originales(tmp_path, monkeypatch):
    img = tmp_path / "captura.png"
    _fotograma().save(img)
    monkeypatch.setattr(sys, "argv", ["recortar-pantalla.py", str(img), str(img)])
    assert m.main() == 1
