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


def _png(ruta):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (4, 4), color="blue").save(ruta)


def test_incrustar_imagenes_ruta_con_espacios(tmp_path):
    _png(tmp_path / "Capturas con espacios" / "P01 paso 1.png")
    resultado = m.incrustar_imagenes("![paso](Capturas con espacios/P01 paso 1.png)", tmp_path)
    assert resultado.startswith("![paso](data:image/png;base64,")
    assert resultado.endswith(")")


def test_incrustar_imagenes_ruta_entre_angulos(tmp_path):
    _png(tmp_path / "mis capturas" / "a.png")
    resultado = m.incrustar_imagenes("![a](<mis capturas/a.png>)", tmp_path)
    assert "data:image/png;base64," in resultado and "<" not in resultado


def test_incrustar_imagenes_ruta_con_porcentaje_20(tmp_path):
    _png(tmp_path / "mis capturas" / "a.png")
    assert "data:image/png;base64," in m.incrustar_imagenes("![a](mis%20capturas/a.png)", tmp_path)


def test_incrustar_imagenes_conserva_el_titulo(tmp_path):
    _png(tmp_path / "a.png")
    resultado = m.incrustar_imagenes('![a](a.png "Pantalla de compras")', tmp_path)
    assert resultado.endswith(' "Pantalla de compras")')
    assert "data:image/png;base64," in resultado


def test_incrustar_imagenes_formato_obsidian(tmp_path):
    _png(tmp_path / "img" / "captura 1.png")
    resultado = m.incrustar_imagenes("Antes ![[img/captura 1.png]] después", tmp_path)
    assert "![captura 1](data:image/png;base64," in resultado
    assert resultado.startswith("Antes ") and resultado.endswith(" después")


def test_incrustar_imagenes_obsidian_busca_por_nombre_en_subcarpetas(tmp_path):
    _png(tmp_path / "Capturas" / "Editadas" / "P02 pantalla.png")
    resultado = m.incrustar_imagenes("![[P02 pantalla.png|300]]", tmp_path)
    assert "data:image/png;base64," in resultado


def test_incrustar_imagenes_avisa_si_no_encuentra_el_fichero(tmp_path, capsys):
    md = "![alt](no-existe.png)"
    resultado = m.incrustar_imagenes(md, tmp_path)
    assert resultado == md  # se deja tal cual
    assert "no encuentro la imagen" in capsys.readouterr().err.lower()
