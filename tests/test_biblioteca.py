import datetime
import sys

import pytest

from _util import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
import biblioteca as bib  # noqa: E402


def test_slugify_quita_tildes_y_enes():
    assert bib.slugify("Emitir factura rectificativa") == "emitir-factura-rectificativa"
    assert bib.slugify("Configuración de año: señales (ñ)") == "configuracion-de-ano-senales-n"


def test_slugify_trunca_sin_cortar_palabras():
    largo = "una frase muy larga " * 10
    slug = bib.slugify(largo, maximo=30)
    assert len(slug) <= 30
    assert not slug.endswith("-")
    assert all(p in {"una", "frase", "muy", "larga"} for p in slug.split("-"))


def test_slugify_vacio_si_no_hay_letras():
    assert bib.slugify("¿¡?!") == ""


def test_codigo_ambito():
    assert bib.codigo_ambito("Holded") == "HOLDED"
    assert bib.codigo_ambito("Administración") == "ADMINIST"
    assert bib.codigo_ambito("a") == "AX"


def test_partir_nombre_valido_y_no_valido():
    ok = bib.partir_nombre("SOP-HOLD-003_emitir-factura.es.md")
    assert ok == {"id": "SOP-HOLD-003", "slug": "emitir-factura", "idioma": "es"}
    for malo in ["P-02 · Circuito de compra.md", "SOP-HOLD-3_x.es.md", "sop-hold-003_x.es.md",
                 "SOP-HOLD-003_Mayusculas.es.md", "SOP-HOLD-003_x.fr.md", "SOP-HOLD-003_x.md"]:
        assert bib.partir_nombre(malo) is None


def test_tipo_desde_texto_acepta_codigo_y_valor():
    assert bib.tipo_desde_texto("sop") == "SOP"
    assert bib.tipo_desde_texto("guia-usuario") == "GUI"
    assert bib.tipo_desde_texto("MAN") == "MAN"
    with pytest.raises(ValueError):
        bib.tipo_desde_texto("informe")


def test_cada_tipo_tiene_plantilla():
    for codigo in bib.TIPOS:
        assert (bib.PLANTILLAS / f"{codigo}.md").exists(), f"falta plantillas/biblioteca/{codigo}.md"


def test_frontmatter_ida_y_vuelta():
    meta = {
        "id": "SOP-HOLD-003", "titulo": "Cierre: IVA # trimestral", "aliases": ["Quarterly VAT close"],
        "version": "1.10", "estado": "aprobado", "revisor": "", "creado": "2026-10-06",
        "tags": ["doc/sop", "app/holded"], "vacia": [],
    }
    texto = bib.volcar_frontmatter(meta) + "\n# Cuerpo\n"
    leido, cuerpo = bib.parsear_frontmatter(texto)
    assert leido["titulo"] == "Cierre: IVA # trimestral"
    assert leido["version"] == "1.10"          # no se convierte en 1.1
    assert leido["revisor"] == ""
    assert leido["aliases"] == ["Quarterly VAT close"]
    assert leido["tags"] == ["doc/sop", "app/holded"]
    assert leido["vacia"] == []
    assert cuerpo.startswith("# Cuerpo")


def test_frontmatter_admite_listas_en_linea_comentarios_y_crlf():
    texto = ('---\r\nid: PAT-GEN-001\r\naliases: [uno, "dos, con coma"]  # un comentario\r\n'
             "estado: borrador # otro\r\n---\r\n\r\nCuerpo\r\n")
    meta, cuerpo = bib.parsear_frontmatter(texto)
    assert meta["aliases"] == ["uno", "dos, con coma"]
    assert meta["estado"] == "borrador"
    assert cuerpo.strip() == "Cuerpo"


def test_frontmatter_ausente_devuelve_meta_vacia():
    meta, cuerpo = bib.parsear_frontmatter("# Solo texto\n")
    assert meta == {} and cuerpo == "# Solo texto\n"


def test_frontmatter_sin_cerrar_o_roto_da_error():
    with pytest.raises(bib.ErrorFrontmatter):
        bib.parsear_frontmatter("---\nid: X\nsin cerrar\n")
    with pytest.raises(bib.ErrorFrontmatter):
        bib.parsear_frontmatter("---\nesto no es yaml\n---\n")


def test_escalares_que_necesitan_comillas():
    volcado = bib.volcar_frontmatter({"a": "1.0", "b": "true", "c": "dos: puntos", "d": "normal", "e": "2026-10-06"})
    assert 'a: "1.0"' in volcado
    assert 'b: "true"' in volcado
    assert 'c: "dos: puntos"' in volcado
    assert "d: normal" in volcado
    assert "e: 2026-10-06" in volcado


def _crear(raiz, ruta):
    f = raiz / ruta
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("x", encoding="utf-8")
    return f


def test_siguiente_numero_cuenta_tambien_el_archivo_y_el_otro_idioma(tmp_path):
    _crear(tmp_path, "SOP-HOLD-001_a.es.md")
    _crear(tmp_path, "SOP-HOLD-001_a.en.md")
    _crear(tmp_path, "90-archivo/SOP-HOLD-004_b.es.md")
    _crear(tmp_path, "SOP-OTRO-009_c.es.md")
    _crear(tmp_path, "GUI-HOLD-020_d.es.md")
    assert bib.siguiente_numero(tmp_path, "SOP", "HOLD") == 5
    assert bib.siguiente_numero(tmp_path, "SOP", "NUEVO") == 1
    assert bib.siguiente_numero(tmp_path, "GUI", "HOLD") == 21


def test_documentos_de_ignora_servicio_e_imagenes(tmp_path):
    _crear(tmp_path, "SOP-HOLD-001_a.es.md")
    _crear(tmp_path, "00_Registro.md")
    _crear(tmp_path, "LEEME.md")
    _crear(tmp_path, "_img/nota.md")
    _crear(tmp_path, "entregables/x.md")
    assert [p.name for p in bib.documentos_de(tmp_path)] == ["SOP-HOLD-001_a.es.md"]


def test_raiz_biblioteca_prioridad(monkeypatch, tmp_path):
    monkeypatch.delenv(bib.VARIABLE_ENTORNO, raising=False)
    assert bib.raiz_biblioteca() == bib.BIBLIOTECA_POR_DEFECTO
    monkeypatch.setenv(bib.VARIABLE_ENTORNO, str(tmp_path / "entorno"))
    assert bib.raiz_biblioteca() == tmp_path / "entorno"
    assert bib.raiz_biblioteca(str(tmp_path / "arg")) == tmp_path / "arg"


def test_fechas_y_versiones():
    assert bib.fecha_valida("2026-10-06")
    assert not bib.fecha_valida("2026-13-01")
    assert not bib.fecha_valida("06/10/2026")
    assert bib.sumar_dias("2026-10-06", 365) == "2027-10-06"
    assert bib.subir_version_menor("0.1") == "0.2"
    assert bib.subir_version_menor("1.9") == "1.10"
    assert bib.subir_version_menor("raro") == "0.1"
    assert bib.hoy_iso(datetime.date(2026, 1, 2)) == "2026-01-02"


def test_renderizar_plantilla_en_los_dos_idiomas():
    texto = "# {{titulo}}\n\n<!-- GUÍA: texto de ayuda -->\n## {{h:proposito}}\n\n{{historial}}\n"
    valores = {"titulo": "T", "fecha": "2026-10-06", "propietario": "Ana", "version": "0.1"}
    es = bib.renderizar_plantilla(texto, valores, "es")
    assert "## Para qué sirve" in es and "## Historial de cambios" in es and "GUÍA" in es
    assert "| 0.1 | 2026-10-06 | Creación del documento | Ana |" in es
    en = bib.renderizar_plantilla(texto, valores, "en", con_guia=False)
    assert "## Purpose" in en and "## Change history" in en and "GUÍA" not in en
    assert "| Version | Date | Change | Author |" in en


def test_renderizar_plantilla_falla_con_marcador_desconocido():
    with pytest.raises(KeyError):
        bib.renderizar_plantilla("{{no_existe}}", {}, "es")
    with pytest.raises(KeyError):
        bib.renderizar_plantilla("{{h:no_existe}}", {}, "es")


def test_todas_las_plantillas_se_renderizan():
    valores = {"id": "SOP-X-001", "titulo": "T", "fecha": "2026-10-06", "propietario": "Ana", "version": "0.1"}
    for codigo in bib.TIPOS:
        texto = (bib.PLANTILLAS / f"{codigo}.md").read_text(encoding="utf-8")
        for idioma in bib.IDIOMAS:
            salida = bib.renderizar_plantilla(texto, valores, idioma)
            assert "{{" not in salida, f"{codigo} deja marcadores sin resolver en {idioma}"
