import datetime
import sys

import pytest

from _util import SCRIPTS, cargar_modulo

sys.path.insert(0, str(SCRIPTS))
import biblioteca as bib  # noqa: E402

m = cargar_modulo("nuevo-documento.py")
HOY = datetime.date(2026, 10, 6)


def _crear(raiz, **kwargs):
    base = dict(ambito="HOLD", aplicacion="Holded", propietario="Ana", hoy=HOY)
    base.update(kwargs)
    return m.crear_documento(raiz, base.pop("tipo", "SOP"), base.pop("titulo", "Emitir factura rectificativa"), **base)


def test_crea_documento_con_nombre_id_y_frontmatter(tmp_path):
    r = _crear(tmp_path, cliente="ClienteX")
    assert r["id"] == "SOP-HOLD-001"
    ruta = r["rutas"][0]
    assert ruta.name == "SOP-HOLD-001_emitir-factura-rectificativa.es.md"
    assert ruta.parent == tmp_path  # un cliente: biblioteca plana
    meta, cuerpo = bib.leer_documento(ruta)
    assert meta["id"] == "SOP-HOLD-001" and meta["tipo"] == "sop" and meta["idioma"] == "es"
    assert meta["estado"] == "borrador" and meta["version"] == "0.1"
    assert meta["creado"] == "2026-10-06" and meta["proxima_revision"] == "2027-10-06"
    assert meta["cliente"] == "ClienteX" and "cliente/clientex" in meta["tags"]
    assert cuerpo.startswith("# Emitir factura rectificativa")
    assert "{{" not in cuerpo and "<!-- GUÍA:" in cuerpo


def test_el_numero_avanza_y_no_sobrescribe(tmp_path):
    assert _crear(tmp_path)["id"] == "SOP-HOLD-001"
    assert _crear(tmp_path, titulo="Otro procedimiento")["id"] == "SOP-HOLD-002"
    assert _crear(tmp_path, ambito="FACT")["id"] == "SOP-FACT-001"


def test_no_sobrescribe_un_fichero_existente(tmp_path):
    r = _crear(tmp_path)
    # simula que alguien ha creado a mano el siguiente con el mismo nombre
    destino = r["rutas"][0].parent / "SOP-HOLD-002_emitir-factura-rectificativa.es.md"
    destino.write_text("mio", encoding="utf-8")
    # el siguiente número libre es 003: no choca, y el fichero de la mano sigue intacto
    assert _crear(tmp_path)["id"] == "SOP-HOLD-003"
    assert destino.read_text(encoding="utf-8") == "mio"


def test_pareja_en_ingles_enlazada_y_pendiente(tmp_path):
    r = _crear(tmp_path, titulo_alt="Issue a corrective invoice")
    es, en = r["rutas"]
    assert en.name == "SOP-HOLD-001_issue-a-corrective-invoice.en.md"
    meta_es, _ = bib.leer_documento(es)
    meta_en, cuerpo_en = bib.leer_documento(en)
    assert meta_es["traduccion"] == en.name and meta_en["traduccion"] == es.name
    assert meta_en["traduccion_estado"] == "pendiente" and "traduccion_estado" not in meta_es
    assert meta_es["aliases"] == ["Issue a corrective invoice"]
    assert meta_en["aliases"] == ["Emitir factura rectificativa"]
    assert "## Purpose" in cuerpo_en and "## Change history" in cuerpo_en
    assert "GUÍA" not in cuerpo_en and "Pending translation" in cuerpo_en


def test_carpeta_destino_por_tipo(tmp_path):
    f = m.carpeta_destino
    assert f(tmp_path, "MAN", "Holded", "comun") == tmp_path / "10-aplicaciones" / "holded"
    assert f(tmp_path, "FAQ", "Fact Sol", "comun") == tmp_path / "10-aplicaciones" / "fact-sol"
    assert f(tmp_path, "GLO", "general", "comun") == tmp_path / "00-gobierno"
    assert f(tmp_path, "PAT", "Holded", "comun") == tmp_path / "40-patrones"
    assert f(tmp_path, "SOP", "Holded", "comun") == tmp_path / "00-gobierno"
    assert f(tmp_path, "SOP", "Holded", "ClienteX") == tmp_path
    assert f(tmp_path, "MAN", "Holded", "ClienteX") == tmp_path


def test_manual_comun_exige_aplicacion(tmp_path):
    with pytest.raises(ValueError, match="aplicacion"):
        _crear(tmp_path, tipo="MAN", aplicacion="", ambito="HOLD")


def test_ambito_se_deduce_de_la_aplicacion(tmp_path):
    r = _crear(tmp_path, tipo="MAN", ambito="", aplicacion="Holded")
    assert r["id"] == "MAN-HOLDED-001"
    assert r["rutas"][0].parent == tmp_path / "10-aplicaciones" / "holded"


@pytest.mark.parametrize("kwargs,mensaje", [
    ({"titulo": "  "}, "título"),
    ({"propietario": ""}, "propietario"),
    ({"ambito": "H"}, "Ámbito"),
    ({"titulo": "¿¡?!"}, "nombre de fichero"),
    ({"idioma": "fr"}, "Idioma"),
    ({"tipo": "XYZ"}, "Tipo desconocido"),
])
def test_entradas_no_validas(tmp_path, kwargs, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        _crear(tmp_path, **kwargs)


def test_simular_no_escribe_nada(tmp_path):
    r = _crear(tmp_path, simular=True)
    assert r["id"] == "SOP-HOLD-001"
    assert not any(tmp_path.iterdir())


def test_todos_los_tipos_se_pueden_crear_y_pasan_el_validador(tmp_path):
    validar = cargar_modulo("validar-biblioteca.py")
    for codigo in bib.TIPOS:
        _crear(tmp_path / "comun", tipo=codigo, titulo=f"Documento de prueba {codigo}", titulo_alt=f"Test document {codigo}")
    docs, hallazgos = validar.validar_biblioteca(tmp_path / "comun", HOY)
    assert len(docs) == 2 * len(bib.TIPOS)
    assert [h for h in hallazgos if h.nivel == "ERROR"] == []


def test_iniciar_biblioteca_comun_y_cliente(tmp_path):
    creado = m.iniciar_biblioteca(tmp_path / "comun", "comun")
    nombres = {p.name for p in creado}
    assert {"00-gobierno", "10-aplicaciones", "40-patrones", "90-archivo", "LEEME.md"} <= nombres
    assert (tmp_path / "comun" / "LEEME.md").exists()
    assert m.iniciar_biblioteca(tmp_path / "comun", "comun") == []  # idempotente

    m.iniciar_biblioteca(tmp_path / "cliente", "cliente")
    assert (tmp_path / "cliente" / "_img").is_dir() and (tmp_path / "cliente" / "entregables").is_dir()
    with pytest.raises(ValueError):
        m.iniciar_biblioteca(tmp_path, "otro")


def test_iniciar_en_simulacion_no_crea(tmp_path):
    creado = m.iniciar_biblioteca(tmp_path / "x", "comun", simular=True)
    assert creado and not (tmp_path / "x").exists()
