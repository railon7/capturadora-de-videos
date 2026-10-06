import datetime
import sys

from _util import SCRIPTS, cargar_modulo

sys.path.insert(0, str(SCRIPTS))
import biblioteca as bib  # noqa: E402

v = cargar_modulo("validar-biblioteca.py")
HOY = datetime.date(2026, 10, 6)

META_OK = {
    "id": "SOP-HOLD-001", "tipo": "sop", "titulo": "Emitir factura", "idioma": "es", "version": "1.0",
    "estado": "aprobado", "propietario": "Ana", "revisor": "Luis", "cliente": "ClienteX",
    "aplicacion": "Holded", "creado": "2026-01-01", "revisado": "2026-02-01", "proxima_revision": "2027-02-01",
}
CUERPO_OK = "# Emitir factura\n\n## Pasos\n\nHaz esto.\n\n## Historial de cambios\n\n| 1.0 | 2026-02-01 | Aprobado | Ana |\n"


def _doc(carpeta, nombre="SOP-HOLD-001_emitir-factura.es.md", meta=None, cuerpo=CUERPO_OK, **cambios):
    datos = dict(META_OK if meta is None else meta)
    datos.update(cambios)
    datos = {k: val for k, val in datos.items() if val is not None}
    ruta = carpeta / nombre
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(bib.volcar_frontmatter(datos) + "\n" + cuerpo, encoding="utf-8")
    return ruta


def _mensajes(tmp_path, nivel=None):
    _, hallazgos = v.validar_biblioteca(tmp_path, HOY)
    return [h.mensaje for h in hallazgos if nivel in (None, h.nivel)]


def test_documento_correcto_no_da_hallazgos(tmp_path):
    _doc(tmp_path)
    assert _mensajes(tmp_path) == []


def test_nombre_que_no_sigue_la_convencion(tmp_path):
    _doc(tmp_path, nombre="P-02 · Circuito de compra.md")
    assert any("el nombre no sigue" in m for m in _mensajes(tmp_path, "ERROR"))


def test_sin_frontmatter_y_frontmatter_roto(tmp_path):
    (tmp_path / "SOP-HOLD-001_a.es.md").write_text("# Solo texto\n", encoding="utf-8")
    (tmp_path / "SOP-HOLD-002_b.es.md").write_text("---\nesto no es yaml\n---\n", encoding="utf-8")
    msgs = _mensajes(tmp_path, "ERROR")
    assert any("no tiene frontmatter" in m for m in msgs)
    assert any("frontmatter ilegible" in m for m in msgs)


def test_campos_obligatorios_y_coherencia_con_el_nombre(tmp_path):
    _doc(tmp_path, propietario="", aplicacion=None)
    msgs = _mensajes(tmp_path, "ERROR")
    assert any("faltan campos obligatorios" in m and "propietario" in m and "aplicacion" in m for m in msgs)

    otro = tmp_path / "otro"
    _doc(otro, id="SOP-HOLD-009", idioma="en", tipo="guia-usuario")
    msgs = _mensajes(otro, "ERROR")
    assert any("no coincide con el del nombre" in m and "SOP-HOLD-009" in m for m in msgs)
    assert any("idioma" in m and "no coincide" in m for m in msgs)


def test_tipo_debe_corresponder_al_prefijo(tmp_path):
    _doc(tmp_path, tipo="guia-usuario")
    assert any("no corresponde al prefijo SOP" in m for m in _mensajes(tmp_path, "ERROR"))


def test_estado_version_y_fechas(tmp_path):
    _doc(tmp_path, estado="terminado", version="uno", proxima_revision="2027-13-40")
    msgs = _mensajes(tmp_path, "ERROR")
    assert any("estado no válido" in m for m in msgs)
    assert any("mayor.menor" in m for m in msgs)
    assert any("proxima_revision" in m for m in msgs)


def test_aprobado_exige_revisor_fecha_y_version_1_o_mas(tmp_path):
    _doc(tmp_path, revisor="", revisado="", version="0.3")
    msgs = _mensajes(tmp_path, "ERROR")
    assert any("necesita revisor" in m for m in msgs)
    assert any("fecha de revisión" in m for m in msgs)
    assert any("1.0 o superior" in m for m in msgs)


def test_revision_vencida_es_aviso(tmp_path):
    _doc(tmp_path, proxima_revision="2026-09-01")
    assert any("revisión vencida" in m for m in _mensajes(tmp_path, "AVISO"))
    assert _mensajes(tmp_path, "ERROR") == []


def test_marcadores_y_guias_sin_quitar(tmp_path):
    cuerpo = "# T\n\n<!-- GUÍA: borra esto -->\n\nTexto {{pendiente}}\n\n## Historial de cambios\n"
    _doc(tmp_path, cuerpo=cuerpo)
    msgs = _mensajes(tmp_path, "ERROR")
    assert any("marcadores sin rellenar" in m for m in msgs)
    assert any("comentarios GUÍA" in m for m in msgs)

    borrador = tmp_path / "b"
    _doc(borrador, cuerpo=cuerpo, estado="borrador", version="0.1", revisor="", revisado="")
    assert _mensajes(borrador, "ERROR") == []  # en borrador solo avisa


def test_marcador_dentro_de_un_comentario_o_de_codigo_se_ignora(tmp_path):
    cuerpo = CUERPO_OK + "\n<!-- ejemplo {{x}} -->\n\n`{{y}}`\n"
    _doc(tmp_path, cuerpo=cuerpo)
    assert _mensajes(tmp_path) == []


def test_imagen_que_falta_es_error_salvo_en_borrador(tmp_path):
    cuerpo = CUERPO_OK + "\n![](_img/falta.png)\n"
    _doc(tmp_path, cuerpo=cuerpo)
    assert any("imagen que no existe" in m for m in _mensajes(tmp_path, "ERROR"))

    b = tmp_path / "b"
    _doc(b, cuerpo=cuerpo, estado="borrador", version="0.1", revisor="", revisado="")
    assert _mensajes(b, "ERROR") == []
    assert any("imagen que no existe" in m for m in _mensajes(b, "AVISO"))


def test_imagen_que_existe_con_espacios_y_obsidian(tmp_path):
    (tmp_path / "_img").mkdir()
    (tmp_path / "_img" / "con espacio.png").write_bytes(b"x")
    (tmp_path / "_img" / "otra.png").write_bytes(b"x")
    cuerpo = CUERPO_OK + "\n![](_img/con%20espacio.png)\n\n![[otra.png]]\n"
    _doc(tmp_path, cuerpo=cuerpo)
    assert _mensajes(tmp_path) == []


def test_enlace_roto_y_enlace_externo(tmp_path):
    cuerpo = CUERPO_OK + "\n[web](https://example.com) [roto](no-existe.md) [ancla](#pasos)\n"
    _doc(tmp_path, cuerpo=cuerpo)
    msgs = _mensajes(tmp_path, "ERROR")
    assert msgs == ["enlace roto: no-existe.md"]


def test_wikilink_a_otro_documento(tmp_path):
    _doc(tmp_path, cuerpo=CUERPO_OK + "\nVer [[SOP-HOLD-002]] y [[SOP-HOLD-077]].\n")
    _doc(tmp_path, nombre="SOP-HOLD-002_otro.es.md", id="SOP-HOLD-002")
    avisos = _mensajes(tmp_path, "AVISO")
    assert any("[[SOP-HOLD-077]]" in m for m in avisos)
    assert not any("[[SOP-HOLD-002]]" in m for m in avisos)


def test_id_repetido_en_el_mismo_idioma(tmp_path):
    _doc(tmp_path)
    _doc(tmp_path / "otra-carpeta", nombre="SOP-HOLD-001_distinto-slug.es.md")
    assert any("repetido en es" in m for m in _mensajes(tmp_path, "ERROR"))


def test_pareja_enlazada_y_traduccion_inexistente(tmp_path):
    _doc(tmp_path, traduccion="SOP-HOLD-001_invoice.en.md")
    assert any("traducción enlazada no existe" in m for m in _mensajes(tmp_path, "ERROR"))

    b = tmp_path / "b"
    _doc(b, traduccion="SOP-HOLD-001_invoice.en.md")
    _doc(b, nombre="SOP-HOLD-001_invoice.en.md", idioma="en", traduccion="SOP-HOLD-001_emitir-factura.es.md",
         traduccion_estado="revisada")
    assert _mensajes(b) == []


def test_pareja_sin_enlace_y_versiones_distintas(tmp_path):
    _doc(tmp_path)
    _doc(tmp_path, nombre="SOP-HOLD-001_invoice.en.md", idioma="en", version="1.1")
    avisos = _mensajes(tmp_path, "AVISO")
    assert any("falta el campo traduccion" in m for m in avisos)
    assert any("traducción desfasada" in m for m in avisos)


def test_aprobado_con_traduccion_sin_revisar(tmp_path):
    _doc(tmp_path, traduccion="SOP-HOLD-001_invoice.en.md")
    _doc(tmp_path, nombre="SOP-HOLD-001_invoice.en.md", idioma="en", traduccion="SOP-HOLD-001_emitir-factura.es.md",
         traduccion_estado="borrador-ia")
    assert any("traducción sin revisar" in m for m in _mensajes(tmp_path, "AVISO"))


def test_obsoletos_y_archivo(tmp_path):
    _doc(tmp_path, estado="obsoleto")
    assert any("no está en 90-archivo" in m for m in _mensajes(tmp_path, "AVISO"))

    b = tmp_path / "b"
    _doc(b / "90-archivo", estado="aprobado")
    assert any("está en 90-archivo/ pero su estado es aprobado" in m for m in _mensajes(b, "AVISO"))

    c = tmp_path / "c"
    _doc(c / "90-archivo", estado="obsoleto")
    assert _mensajes(c) == []


def test_registro_generado(tmp_path):
    _doc(tmp_path)
    _doc(tmp_path, nombre="GUI-HOLD-001_guia.es.md", id="GUI-HOLD-001", tipo="guia-usuario", proxima_revision="2026-01-01")
    docs, hallazgos = v.validar_biblioteca(tmp_path, HOY)
    texto = v.generar_registro(tmp_path, docs, hallazgos, HOY)
    assert "# Registro de la biblioteca" in texto
    assert "## SOP · Procedimiento normalizado de trabajo (PNT)" in texto
    assert "## GUI · Guía de usuario / User guide" in texto
    assert "[[SOP-HOLD-001_emitir-factura.es\\|SOP-HOLD-001]]" in texto
    assert "## Revisiones vencidas" in texto
    meta, _ = bib.parsear_frontmatter(texto)
    assert meta["tipo"] == "registro-generado"


def test_ruta_del_registro(tmp_path):
    assert v.ruta_registro(tmp_path) == tmp_path / "00_Registro.md"
    (tmp_path / "00-gobierno").mkdir()
    assert v.ruta_registro(tmp_path) == tmp_path / "00-gobierno" / "00_Registro.md"


def test_el_registro_y_el_leeme_no_cuentan_como_documentos(tmp_path):
    (tmp_path / "00-gobierno").mkdir()
    (tmp_path / "00-gobierno" / "00_Registro.md").write_text("generado", encoding="utf-8")
    (tmp_path / "LEEME.md").write_text("hola", encoding="utf-8")
    docs, hallazgos = v.validar_biblioteca(tmp_path, HOY)
    assert docs == [] and hallazgos == []


def test_el_registro_no_se_reescribe_si_solo_cambia_la_fecha(tmp_path):
    _doc(tmp_path)
    docs, hallazgos = v.validar_biblioteca(tmp_path, HOY)
    destino = tmp_path / "00_Registro.md"
    assert v.escribir_registro(destino, v.generar_registro(tmp_path, docs, hallazgos, HOY)) is True
    manana = HOY + datetime.timedelta(days=1)
    assert v.escribir_registro(destino, v.generar_registro(tmp_path, docs, hallazgos, manana)) is False
    assert "generado: 2026-10-06" in destino.read_text(encoding="utf-8")  # sigue con la fecha de la última escritura real
    _doc(tmp_path, nombre="SOP-HOLD-002_otro.es.md", id="SOP-HOLD-002")
    docs, hallazgos = v.validar_biblioteca(tmp_path, HOY)
    assert v.escribir_registro(destino, v.generar_registro(tmp_path, docs, hallazgos, manana)) is True
    assert "SOP-HOLD-002" in destino.read_text(encoding="utf-8")
