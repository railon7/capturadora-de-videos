from PIL import Image

from _util import cargar_modulo

m = cargar_modulo("exportar-manual.py")


def test_incrustar_imagenes_reemplaza_por_data_uri(tmp_path):
    Image.new("RGB", (10, 10), color="red").save(tmp_path / "captura.png")
    md = "Texto antes\n\n![alt](captura.png)\n\nTexto después"

    resultado = m.incrustar_imagenes(md, tmp_path)

    assert "captura.png" not in resultado
    assert "data:image/png;base64," in resultado
    assert "Texto antes" in resultado and "Texto después" in resultado


def test_incrustar_imagenes_deja_urls_externas_igual():
    md = "![alt](https://example.com/imagen.png)"
    resultado = m.incrustar_imagenes(md, __import__("pathlib").Path("."))
    assert resultado == md


def test_incrustar_imagenes_avisa_si_no_encuentra_el_fichero(tmp_path, capsys):
    md = "![alt](no-existe.png)"
    resultado = m.incrustar_imagenes(md, tmp_path)
    assert resultado == md  # se deja tal cual
    assert "no encuentro la imagen" in capsys.readouterr().err.lower()
