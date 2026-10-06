from _util import cargar_modulo

m = cargar_modulo("generar-borrador-guion.py")


def test_hora_a_segundos_y_vuelta():
    assert m.hora_a_segundos("00:45:20") == 45 * 60 + 20
    assert m.segundos_a_hora(2720) == "00:45:20"


def test_hora_a_segundos_formato_invalido():
    assert m.hora_a_segundos("45:20") is None
    assert m.hora_a_segundos("no es una hora") is None


def test_fusionar_segmentos_junta_si_estan_cerca():
    segmentos = [(0.0, "hola"), (1.0, "que tal"), (10.0, "otro bloque")]
    fusionados = m.fusionar_segmentos(segmentos, pausa_min=1.5)
    assert fusionados == [(0.0, "hola que tal"), (10.0, "otro bloque")]


def test_fusionar_segmentos_vacio():
    assert m.fusionar_segmentos([], pausa_min=1.5) == []


def test_pantalla_mas_cercana_dentro_de_tolerancia():
    catalogo = [(0, "t_000000.jpg", "login"), (45, "t_000045.jpg", "presupuesto")]
    fichero, desc = m.pantalla_mas_cercana(50, catalogo, tolerancia=30)
    assert fichero == "t_000045.jpg"
    assert desc == "presupuesto"


def test_pantalla_mas_cercana_fuera_de_tolerancia():
    catalogo = [(0, "t_000000.jpg", "login")]
    fichero, desc = m.pantalla_mas_cercana(500, catalogo, tolerancia=30)
    assert fichero is None and desc is None


def test_leer_catalogo_parsea_tabla_markdown(tmp_path):
    contenido = (
        "# Catalogo\n\n"
        "| Fichero | Hora | Texto detectado (OCR) | Qué se ve |\n"
        "|---|---|---|---|\n"
        "| t_000000.jpg | 00:00:00 | login | pantalla de login |\n"
        "| t_000045.jpg | 00:00:45 |  |  |\n"
    )
    ruta = tmp_path / "Catalogo de capturas.md"
    ruta.write_text(contenido, encoding="utf-8")
    filas = m.leer_catalogo(ruta)
    assert filas == [(0, "t_000000.jpg", "pantalla de login"), (45, "t_000045.jpg", "")]


def test_leer_catalogo_admite_barras_escapadas_en_el_ocr(tmp_path):
    # catalogar-capturas.py escapa como \| las barras que el OCR lee en pantalla
    contenido = (
        "| Fichero | Hora | Texto detectado (OCR) | Qué se ve |\n"
        "|---|---|---|---|\n"
        "| t_000010.jpg | 00:00:10 | Clientes \\| Artículos | lista de facturas |\n"
    )
    ruta = tmp_path / "Catalogo de capturas.md"
    ruta.write_text(contenido, encoding="utf-8")
    assert m.leer_catalogo(ruta) == [(10, "t_000010.jpg", "lista de facturas")]
