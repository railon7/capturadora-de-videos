from _util import cargar_modulo

m = cargar_modulo("redactar-captura.py")


def test_cif_valido_letra_digito():
    assert m.cif_valido("B", "7654321", "4") is True
    assert m.cif_valido("B", "7654321", "0") is False


def test_cif_valido_letra_ambigua_acepta_digito_o_letra():
    assert m.cif_valido("K", "7654321", "D") is True  # letra de control
    assert m.cif_valido("C", "7654321", "4") is True  # digito, letra ambigua


def test_clasificar_palabra_dni():
    assert m.clasificar_palabra("12345678Z") == "DNI"
    assert m.clasificar_palabra("12345678A") is None  # checksum incorrecto


def test_clasificar_palabra_email_y_no_dato():
    assert m.clasificar_palabra("juan.perez@example.com") == "email"
    assert m.clasificar_palabra("Pedido") is None
    assert m.clasificar_palabra("P26-2600168") is None


def test_clasificar_palabra_tarjeta():
    assert m.clasificar_palabra("4111111111111111") == "tarjeta"
    assert m.clasificar_palabra("4111111111111112") is None


def test_caja_union():
    cajas = [(10, 10, 5, 5), (20, 12, 5, 5)]
    assert m.caja_union(cajas) == (10, 10, 15, 7)


def test_encontrar_cajas_dato_verificable():
    palabras = [
        {"texto": "DNI", "linea": (1, 1, 1), "caja": (0, 0, 10, 10)},
        {"texto": "12345678Z", "linea": (1, 1, 1), "caja": (15, 0, 30, 10)},
    ]
    encontradas = m.encontrar_cajas_a_redactar(palabras, [])
    assert encontradas == [((15, 0, 30, 10), "DNI")]


def test_encontrar_cajas_nombre_de_dos_palabras():
    palabras = [
        {"texto": "Cliente:", "linea": (1, 1, 1), "caja": (0, 0, 20, 10)},
        {"texto": "Juan", "linea": (1, 1, 1), "caja": (25, 0, 10, 10)},
        {"texto": "Perez", "linea": (1, 1, 1), "caja": (40, 0, 10, 10)},
    ]
    encontradas = m.encontrar_cajas_a_redactar(palabras, ["Juan Perez"])
    assert len(encontradas) == 1
    caja, tipo = encontradas[0]
    assert tipo == "nombre de la lista"
    assert caja == (25, 0, 25, 10)  # une las cajas de "Juan" y "Perez"


def test_leer_lista_nombres_ignora_comentarios_y_vacios(tmp_path):
    ruta = tmp_path / "nombres.txt"
    ruta.write_text("Novality\n# comentario\n\nInnovatecnic\n", encoding="utf-8")
    assert m.leer_lista_nombres(str(ruta)) == ["Novality", "Innovatecnic"]


def test_leer_lista_nombres_sin_ruta():
    assert m.leer_lista_nombres(None) == []
