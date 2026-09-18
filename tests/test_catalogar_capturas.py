from _util import cargar_modulo

m = cargar_modulo("catalogar-capturas.py")


def test_hora_desde_nombre_intervalo():
    assert m.hora_desde_nombre("t_004520.jpg") == "00:45:20"


def test_hora_desde_nombre_escena():
    assert m.hora_desde_nombre("e_013045.jpg") == "01:30:45"


def test_hora_desde_nombre_sin_patron():
    assert m.hora_desde_nombre("hoja_03.jpg") == ""


def test_localizar_tesseract_con_ruta_manual_inexistente():
    assert m.localizar_tesseract(r"C:\ruta\que\no\existe\tesseract.exe") is None
