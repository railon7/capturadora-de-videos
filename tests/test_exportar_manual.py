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


# ---------------------------------------------------------------- biblioteca
import importlib.util  # noqa: E402

import pytest  # noqa: E402

requiere_markdown = pytest.mark.skipif(importlib.util.find_spec("markdown") is None, reason="falta el paquete markdown")

DOC = """---
id: SOP-HOLD-003
tipo: sop
titulo: Emitir factura rectificativa
idioma: en
version: "1.0"
estado: aprobado
revisado: 2026-10-06
---

# Emitir factura rectificativa

<!-- GUÍA: texto interno que no debe salir -->

## Pasos

Haz esto.
"""


def _html(texto, tmp_path, **kwargs):
    return m.convertir_a_html(texto, tmp_path, __import__("pathlib").Path("x.md"), **kwargs)


@requiere_markdown
def test_el_frontmatter_no_sale_en_el_html_y_marca_el_idioma(tmp_path):
    html = _html(DOC, tmp_path)
    assert 'lang="en"' in html
    assert "id: SOP-HOLD-003" not in html and "tipo: sop" not in html
    assert "<title>Emitir factura rectificativa</title>" in html
    assert '<p class="doc-meta">SOP-HOLD-003 · Version 1.0 · Approved · Reviewed 2026-10-06</p>' in html


@requiere_markdown
def test_los_comentarios_guia_no_pasan_al_html(tmp_path):
    html = _html(DOC, tmp_path)
    assert "GUÍA" not in html and "texto interno" not in html


@requiere_markdown
def test_un_bloque_de_codigo_conserva_sus_comentarios(tmp_path):
    texto = DOC + "\n```html\n<!-- ejemplo -->\n```\n"
    assert "ejemplo" in _html(texto, tmp_path)


@requiere_markdown
def test_aprobado_no_lleva_marca_de_agua(tmp_path):
    assert "marca-agua" not in _html(DOC, tmp_path).split("</style>")[1]


@pytest.mark.parametrize("estado,texto_marca", [("borrador", "DRAFT"), ("revision", "IN REVIEW"), ("obsoleto", "OBSOLETE")])
@requiere_markdown
def test_marca_de_agua_segun_estado(tmp_path, estado, texto_marca):
    html = _html(DOC.replace("estado: aprobado", f"estado: {estado}"), tmp_path)
    assert f'<div class="marca-agua">{texto_marca}</div>' in html


@requiere_markdown
def test_marca_de_agua_en_espanol_y_se_puede_quitar(tmp_path):
    borrador = DOC.replace("estado: aprobado", "estado: borrador").replace("idioma: en", "idioma: es")
    assert '<div class="marca-agua">BORRADOR</div>' in _html(borrador, tmp_path)
    assert "<div class=\"marca-agua\">" not in _html(borrador, tmp_path, marca_agua=False)


@requiere_markdown
def test_documento_sin_frontmatter_sigue_funcionando(tmp_path):
    html = _html("# P-01 · Entrada de factura\n\nTexto\n", tmp_path)
    assert "<title>P-01 · Entrada de factura</title>" in html
    assert 'lang="es"' in html and "doc-meta" not in html.split("</style>")[1] and "marca-agua" not in html.split("</style>")[1]


@requiere_markdown
def test_frontmatter_roto_se_exporta_tal_cual_con_aviso(tmp_path, capsys):
    html = _html("---\nesto no es yaml\n---\n# T\n", tmp_path)
    assert "frontmatter ilegible" in capsys.readouterr().err
    assert "<title>" in html


@requiere_markdown
def test_las_imagenes_del_cuerpo_se_incrustan_con_frontmatter(tmp_path):
    _png(tmp_path / "_img" / "a.png")
    html = _html(DOC + "\n![](_img/a.png)\n", tmp_path)
    assert "data:image/png;base64," in html and "_img/a.png" not in html


def test_salida_por_defecto_va_a_entregables_si_existe(tmp_path):
    ruta = tmp_path / "SOP-HOLD-003_x.es.md"
    assert m.salida_por_defecto(ruta, {"id": "SOP-HOLD-003"}) == tmp_path / "SOP-HOLD-003_x.es.html"
    (tmp_path / "entregables").mkdir()
    assert m.salida_por_defecto(ruta, {"id": "SOP-HOLD-003"}) == tmp_path / "entregables" / "SOP-HOLD-003_x.es.html"
    assert m.salida_por_defecto(ruta, {}) == tmp_path / "SOP-HOLD-003_x.es.html"  # sin id: no es de la biblioteca


def test_buscar_navegador_usa_el_primer_candidato_que_existe(tmp_path):
    falso = tmp_path / "chrome.exe"
    falso.write_text("x")
    assert m.buscar_navegador([str(tmp_path / "no-existe.exe"), str(falso)]) == str(falso)


def test_comando_pdf_apunta_al_html_y_usa_un_perfil_propio(tmp_path):
    html = tmp_path / "con espacios.html"
    cmd = m.comando_pdf("chrome", html, tmp_path / "s.pdf", str(tmp_path / "perfil"))
    assert cmd[0] == "chrome" and "--headless=new" in cmd
    assert f"--user-data-dir={tmp_path / 'perfil'}" in cmd
    assert cmd[-1].startswith("file:///") and "%20" in cmd[-1]
    assert any(c.startswith("--print-to-pdf=") and c.endswith("s.pdf") for c in cmd)
