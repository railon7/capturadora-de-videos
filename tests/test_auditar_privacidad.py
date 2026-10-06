from _util import cargar_modulo

m = cargar_modulo("auditar-privacidad.py")


def test_dni_valido():
    assert m.dni_valido("12345678", "Z") is True
    assert m.dni_valido("12345678", "A") is False


def test_nie_valido():
    assert m.nie_valido("X", "1234567", "L") is True
    assert m.nie_valido("X", "1234567", "A") is False


def test_luhn_valido():
    assert m.luhn_valido("4111111111111111") is True
    assert m.luhn_valido("4111111111111112") is False
    assert m.luhn_valido("123") is False  # demasiado corto para ser una tarjeta


def test_enmascarar():
    texto = "juan@example.com"
    resultado = m.enmascarar(texto)
    assert resultado == "ju" + "*" * (len(texto) - 4) + "om"
    assert m.enmascarar("ab") == "**"


def test_cif_valido():
    assert m.cif_valido("B", "7654321", "4") is True
    assert m.cif_valido("B", "7654321", "0") is False


def test_buscar_en_texto_detecta_los_cinco_tipos():
    texto = (
        "Contacto: juan.perez@example.com telf 611223344 "
        "DNI 12345678Z tarjeta 4111111111111111 CIF B76543214"
    )
    hallazgos = m.buscar_en_texto(texto, "prueba")
    tipos = {"email", "telefono_es", "DNI (checksum ok)", "tarjeta (Luhn ok)", "CIF (checksum ok)"}
    for tipo in tipos:
        assert any(tipo in h for h in hallazgos), f"no se detectó: {tipo}"


def test_buscar_en_texto_sin_datos():
    assert m.buscar_en_texto("no hay nada identificable aquí", "prueba") == []


def test_buscar_nombres_encuentra_coincidencia_literal():
    hallazgos = m.buscar_nombres("El cliente es Novality, contacto Paco", "prueba", ["Novality"])
    assert len(hallazgos) == 1
    assert "nombre de la lista" in hallazgos[0]


def test_buscar_nombres_sin_coincidencia():
    assert m.buscar_nombres("texto sin ningun nombre de la lista", "prueba", ["Novality"]) == []


def test_buscar_nombres_sin_tildes_en_el_ocr():
    assert len(m.buscar_nombres("2 Juan Martinez 24/03/2025", "ocr", ["Juan Martínez"])) == 1


def test_buscar_nombres_con_error_del_ocr():
    assert len(m.buscar_nombres("2 Juan Martine: 24/03/2025", "ocr", ["Juan Martínez"])) == 1


def test_buscar_nombres_pegado_en_una_palabra():
    assert len(m.buscar_nombres("Cliente MANBLANCOPEREZ 2", "ocr", ["Blanco Pérez"])) == 1


def test_buscar_nombres_un_aviso_por_nombre_aunque_salga_varias_veces():
    texto = "Juan Martinez entra. Juan Martinez sale."
    assert len(m.buscar_nombres(texto, "ocr", ["Juan Martínez"])) == 1


def test_buscar_nombres_no_avisa_de_palabras_que_no_se_parecen():
    assert m.buscar_nombres("Pedido de compra del martes", "ocr", ["Juan Martínez"]) == []


def test_elegir_idioma_ocr():
    assert m.elegir_idioma_ocr(["eng", "spa"]) == "spa+eng"
    assert m.elegir_idioma_ocr(["eng"]) == "eng"


def test_escala_ocr_auto():
    assert m.escala_ocr_auto(1077) == 3
    assert m.escala_ocr_auto(3840) == 1


def test_leer_lista_nombres_ignora_comentarios_y_vacios(tmp_path):
    ruta = tmp_path / "nombres.txt"
    ruta.write_text("Novality\n# comentario\n\nInnovatecnic\n", encoding="utf-8")
    assert m.leer_lista_nombres(str(ruta)) == ["Novality", "Innovatecnic"]


def test_leer_lista_nombres_sin_ruta():
    assert m.leer_lista_nombres(None) == []


def test_buscar_nombres_no_avisa_de_palabras_corrientes_parecidas_a_un_nombre_corto():
    assert m.buscar_nombres("Marca Material marcas", "ocr", ["María"]) == []


def test_buscar_nombres_no_avisa_de_un_nombre_dentro_de_otra_palabra():
    assert m.buscar_nombres("Diarios de usuarios", "ocr", ["Ríos"]) == []
    assert len(m.buscar_nombres("Contacto: Ana Ríos", "ocr", ["Ríos"])) == 1
