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


def _linea(*textos):
    """Palabras OCR de una misma línea, cada una con su caja de 10 px de ancho."""
    return [{"texto": t, "linea": (1, 1, 1), "caja": (i * 15, 0, 10, 10)} for i, t in enumerate(textos)]


def test_normalizar_quita_tildes_mayusculas_y_puntuacion():
    assert m.normalizar("Martínez:") == "martinez"
    assert m.normalizar("  JUAN  Pérez, ") == "juan perez"
    assert m.normalizar("Íñigo") == "inigo"


def test_palabras_coinciden_tolera_errores_del_ocr_en_palabras_largas():
    assert m.palabras_coinciden("martine", "martinez")
    assert m.palabras_coinciden("mortines", "martinez")
    assert not m.palabras_coinciden("lawn", "juan")  # cortas: solo iguales
    assert not m.palabras_coinciden("pedido", "martinez")


def test_encontrar_cajas_nombre_sin_tilde_en_el_ocr():
    encontradas = m.encontrar_cajas_a_redactar(_linea("Juan", "Martinez"), ["Juan Martínez"])
    assert encontradas == [((0, 0, 25, 10), "nombre de la lista")]


def test_encontrar_cajas_nombre_con_error_del_ocr():
    encontradas = m.encontrar_cajas_a_redactar(_linea("2", "Juan", "Martine:"), ["Juan Martínez"])
    assert encontradas == [((15, 0, 25, 10), "nombre de la lista")]


def test_encontrar_cajas_nombre_pegado_en_una_palabra():
    encontradas = m.encontrar_cajas_a_redactar(_linea("MANBLANCOPEREZ", "2"), ["Blanco Pérez"])
    assert encontradas == [((0, 0, 10, 10), "nombre de la lista")]


def test_encontrar_cajas_no_duplica_si_varios_nombres_casan_igual():
    encontradas = m.encontrar_cajas_a_redactar(_linea("Novality"), ["Novality", "novality"])
    assert len(encontradas) == 1


def test_no_tapa_palabras_corrientes_parecidas_a_un_nombre_corto():
    # "Marca" y "Material" se parecen a "María" tanto como un error del OCR: en nombres
    # cortos solo vale la coincidencia exacta (sin tildes)
    assert m.encontrar_cajas_a_redactar(_linea("Marca", "Material", "marcas"), ["María"]) == []
    assert len(m.encontrar_cajas_a_redactar(_linea("Maria", "López"), ["María"])) == 1


def test_encontrar_cajas_no_tapa_palabras_que_no_se_parecen():
    assert m.encontrar_cajas_a_redactar(_linea("Pedido", "de", "compra"), ["Juan Martínez"]) == []


def test_elegir_idioma_ocr():
    assert m.elegir_idioma_ocr(["eng", "osd", "spa"]) == "spa+eng"
    assert m.elegir_idioma_ocr(["eng", "osd"]) == "eng"
    assert m.elegir_idioma_ocr([]) == "eng"


def test_escala_ocr_auto_amplia_las_capturas_pequenas():
    assert m.escala_ocr_auto(1077) == 3
    assert m.escala_ocr_auto(1906) == 2
    assert m.escala_ocr_auto(3840) == 1


def test_leer_lista_nombres_ignora_comentarios_y_vacios(tmp_path):
    ruta = tmp_path / "nombres.txt"
    ruta.write_text("Novality\n# comentario\n\nInnovatecnic\n", encoding="utf-8")
    assert m.leer_lista_nombres(str(ruta)) == ["Novality", "Innovatecnic"]


def test_leer_lista_nombres_sin_ruta():
    assert m.leer_lista_nombres(None) == []
