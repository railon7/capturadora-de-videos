import datetime
import sys

import pytest

from _util import SCRIPTS, cargar_modulo

sys.path.insert(0, str(SCRIPTS))
import biblioteca as bib  # noqa: E402

m = cargar_modulo("patrones-a-biblioteca.py")
validar = cargar_modulo("validar-biblioteca.py")
HOY = datetime.date(2026, 10, 6)

ACUMULADO = """# Patrones acumulados

Texto de cabecera que no es un patrón.

<!-- consolidar-patrones.py añade aquí un apartado -->

## Del proyecto: Software DELSOL — ContaSol (tutoriales oficiales)

### Maestros antes del primer asiento
**Visto en**: Tutorial A, 2026-10-06
**Se aplica cuando**: se arranca la contabilidad

Dar de alta cuentas antes de contabilizar.

### Ficha de tercero
**Visto en**: Tutorial A, 2026-10-06
**Se aplica cuando**: hay que crear una subcuenta

Crear desde Clientes.

## Del proyecto: Proyecto B

### Escandallo base
**Visto en**: Proyecto B, 2026-09

Texto.
"""


def test_dividir_acumulado_separa_por_proyecto_y_quita_el_comentario():
    secciones = m.dividir_acumulado(ACUMULADO)
    assert [o for o, _ in secciones] == ["Software DELSOL — ContaSol (tutoriales oficiales)", "Proyecto B"]
    assert "consolidar-patrones" not in secciones[0][1]
    assert secciones[0][1].startswith("### Maestros antes del primer asiento")


@pytest.mark.parametrize("origen,esperado", [
    ("Software DELSOL — ContaSol (tutoriales oficiales)", "ContaSol"),
    ("Proyecto B", "Proyecto B"),
    ("Cliente A - FactuSol", "FactuSol"),
])
def test_aplicacion_de(origen, esperado):
    assert m.aplicacion_de(origen) == esperado


def test_crea_un_pat_por_apartado(tmp_path):
    r = m.sincronizar(ACUMULADO, tmp_path, propietario="Jorge", hoy=HOY)
    assert [(x["accion"], x["patrones"]) for x in r] == [("creado", 2), ("creado", 1)]
    ruta = r[0]["ruta"]
    assert ruta == tmp_path / "40-patrones" / "PAT-CONTASOL-001_patrones-de-contasol.es.md"
    meta, cuerpo = bib.leer_documento(ruta)
    assert meta["tipo"] == "patron" and meta["estado"] == "borrador" and meta["aplicacion"] == "ContaSol"
    assert meta["origen_patrones"] == "Software DELSOL — ContaSol (tutoriales oficiales)"
    assert meta["tags"][0] == "doc/patron"
    assert "## Maestros antes del primer asiento" in cuerpo and "### " not in cuerpo
    assert "2 patrones" in cuerpo and "## Historial de cambios" in cuerpo
    assert r[1]["ruta"].name.startswith("PAT-PROYECTO-001_")


def test_los_pat_generados_pasan_el_validador(tmp_path):
    m.sincronizar(ACUMULADO, tmp_path, propietario="Jorge", hoy=HOY)
    _, hallazgos = validar.validar_biblioteca(tmp_path, HOY)
    assert [h for h in hallazgos if h.nivel == "ERROR"] == []


def test_repetir_sin_cambios_no_toca_nada(tmp_path):
    m.sincronizar(ACUMULADO, tmp_path, propietario="Jorge", hoy=HOY)
    antes = {p: p.read_text(encoding="utf-8") for p in bib.documentos_de(tmp_path)}
    r = m.sincronizar(ACUMULADO, tmp_path, propietario="Jorge", hoy=HOY)
    assert [x["accion"] for x in r] == ["sin cambios", "sin cambios"]
    assert {p: p.read_text(encoding="utf-8") for p in bib.documentos_de(tmp_path)} == antes


def test_un_patron_nuevo_actualiza_sube_version_y_conserva_el_historial(tmp_path):
    m.sincronizar(ACUMULADO, tmp_path, propietario="Jorge", hoy=HOY)
    ampliado = ACUMULADO.replace("## Del proyecto: Proyecto B",
                                 "### Tercer patrón\n**Visto en**: Tutorial A\n\nMás texto.\n\n## Del proyecto: Proyecto B")
    r = m.sincronizar(ampliado, tmp_path, propietario="Ana", hoy=datetime.date(2026, 11, 1))
    assert [x["accion"] for x in r] == ["actualizado", "sin cambios"]
    meta, cuerpo = bib.leer_documento(r[0]["ruta"])
    assert meta["version"] == "0.2" and "## Tercer patrón" in cuerpo and "3 patrones" in cuerpo
    assert "| 0.1 | 2026-10-06 | Creado desde patrones-acumulados.md | Jorge |" in cuerpo
    assert "| 0.2 | 2026-11-01 | Actualizado desde patrones-acumulados.md | Ana |" in cuerpo
    assert len(list((tmp_path / "40-patrones").glob("PAT-CONTASOL-*"))) == 1  # no crea otro


def test_simular_no_escribe(tmp_path):
    r = m.sincronizar(ACUMULADO, tmp_path, propietario="Jorge", hoy=HOY, simular=True)
    assert [x["accion"] for x in r] == ["creado", "creado"] and not any(tmp_path.iterdir())


def test_apartado_sin_patrones_y_propietario_obligatorio(tmp_path):
    r = m.sincronizar("## Del proyecto: Vacío\n\nNada.\n", tmp_path, propietario="J", hoy=HOY)
    assert r[0]["accion"] == "sin patrones"
    with pytest.raises(ValueError, match="propietario"):
        m.sincronizar(ACUMULADO, tmp_path, propietario="")
