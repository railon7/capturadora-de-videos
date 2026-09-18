import argparse

import pytest
from PIL import Image

from _util import cargar_modulo

m = cargar_modulo("anotar-captura.py")


def test_parsear_marca_valida():
    assert m.parsear_marca("120,80") == (120.0, 80.0)


def test_parsear_marca_invalida():
    with pytest.raises(argparse.ArgumentTypeError):
        m.parsear_marca("no-es-una-coordenada")


def test_dibujar_marcadores_crea_fichero_del_mismo_tamano(tmp_path):
    entrada = tmp_path / "entrada.png"
    salida = tmp_path / "salida.png"
    Image.new("RGB", (200, 150), color="white").save(entrada)

    m.dibujar_marcadores(entrada, salida, [(50, 50), (150, 100)], porcentaje=False,
                          radio=10, color="red", color_texto="white")

    assert salida.exists()
    with Image.open(salida) as img:
        assert img.size == (200, 150)


def test_dibujar_marcadores_con_porcentaje(tmp_path):
    entrada = tmp_path / "entrada.png"
    salida = tmp_path / "salida.png"
    Image.new("RGB", (200, 100), color="white").save(entrada)

    # no debe fallar con coordenadas 0-100 en vez de píxeles
    m.dibujar_marcadores(entrada, salida, [(50, 50)], porcentaje=True,
                          radio=10, color="red", color_texto="white")
    assert salida.exists()
