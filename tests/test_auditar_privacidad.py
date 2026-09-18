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


def test_buscar_en_texto_detecta_los_cuatro_tipos():
    texto = (
        "Contacto: juan.perez@example.com telf 611223344 "
        "DNI 12345678Z tarjeta 4111111111111111"
    )
    hallazgos = m.buscar_en_texto(texto, "prueba")
    tipos = {"email", "telefono_es", "DNI (checksum ok)", "tarjeta (Luhn ok)"}
    for tipo in tipos:
        assert any(tipo in h for h in hallazgos), f"no se detectó: {tipo}"


def test_buscar_en_texto_sin_datos():
    assert m.buscar_en_texto("no hay nada identificable aquí", "prueba") == []
