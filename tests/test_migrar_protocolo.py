import datetime
import sys

import pytest
from PIL import Image

from _util import SCRIPTS, cargar_modulo

sys.path.insert(0, str(SCRIPTS))
import biblioteca as bib  # noqa: E402

m = cargar_modulo("migrar-protocolo.py")
validar = cargar_modulo("validar-biblioteca.py")
HOY = datetime.date(2026, 10, 6)

ANTIGUO = """# P-02 · Circuito de compra

| | |
|---|---|
| **Quién lo hace** | Compras |
| **Cuándo** | Al recibir un pedido |
| **Aplicación** | Holded |
| **Ámbito** | Todas las sociedades |
| **Estado** | 🟢 validado por el destinatario |
| **Última revisión** | 2026-09-30 · Administración |

## Para qué sirve
Registrar la compra.

## Pasos

### 1 · Abrir compras
![](Capturas/Editadas/P02-04-comparativo-proveedores.png)
> ① El botón

### 2 · Comparar
![[otra captura.png]]
![](Capturas/Editadas/no-existe.png)

## Qué NO hacer
No dupliques proveedores.
"""


def _png(ruta):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (4, 4), color="green").save(ruta)


def _protocolo(tmp_path, texto=ANTIGUO):
    carpeta = tmp_path / "08-Formacion"
    _png(carpeta / "Capturas" / "Editadas" / "P02-04-comparativo-proveedores.png")
    _png(carpeta / "otra captura.png")
    ruta = carpeta / "P-02 · Circuito de compra.md"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def test_separar_titulo_con_y_sin_codigo():
    assert m.separar_titulo("# P-02 · Circuito de compra\n\ntexto")[:2] == ("P-02", "Circuito de compra")
    assert m.separar_titulo("# Entrada de factura\n")[:2] == ("", "Entrada de factura")
    assert m.separar_titulo("sin titulo")[:2] == ("", "")


def test_extraer_tabla_de_metadatos():
    _, _, resto = m.separar_titulo(ANTIGUO)
    datos, sin_tabla = m.extraer_tabla_metadatos(resto)
    assert datos["quien"] == "Compras" and datos["aplicacion"] == "Holded"
    assert datos["estado"].startswith("🟢") and datos["revision"] == "2026-09-30 · Administración"
    assert "Quién lo hace" not in sin_tabla and sin_tabla.lstrip().startswith("## Para qué sirve")


def test_una_tabla_posterior_al_primer_encabezado_no_se_toca():
    texto = "## Pasos\n\n| a | b |\n|---|---|\n| **Estado** | x |\n"
    datos, sin = m.extraer_tabla_metadatos(texto)
    assert datos == {} and sin == texto


@pytest.mark.parametrize("estado,revision,esperado", [
    ("🟡 borrador", "", ("borrador", "0.1", "", "")),
    ("🟠 validado internamente", "2026-09-01 · Luis", ("revision", "0.5", "2026-09-01", "Luis")),
    ("🟢 validado por el destinatario", "30/09/2026 · Ana", ("aprobado", "1.0", "2026-09-30", "Ana")),
])
def test_interpretar_estado(estado, revision, esperado):
    assert m.interpretar_estado(estado, revision)[:4] == esperado


def test_aprobado_sin_revisor_baja_a_revision_con_aviso():
    estado, version, revisado, revisor, avisos = m.interpretar_estado("🟢", "2026-09-30")
    assert (estado, version, revisor) == ("revision", "0.9", "") and avisos


def test_recoger_imagenes_renombra_copia_y_avisa(tmp_path):
    ruta = _protocolo(tmp_path)
    _, _, resto = m.separar_titulo(ANTIGUO)
    texto, copias, avisos = m.recoger_imagenes(resto, ruta.parent, "SOP-HOLDED-001")
    assert "![](_img/SOP-HOLDED-001-04-comparativo-proveedores.png)" in texto
    assert "![](_img/SOP-HOLDED-001-01-otra-captura.png)" in texto
    assert [n for _, n in copias] == ["SOP-HOLDED-001-04-comparativo-proveedores.png", "SOP-HOLDED-001-01-otra-captura.png"]
    assert any("no-existe.png" in a for a in avisos) and "no-existe.png" in texto


def test_la_misma_imagen_dos_veces_usa_un_solo_nombre(tmp_path):
    ruta = _protocolo(tmp_path)
    resto = "![](otra captura.png)\n\n![](otra%20captura.png)\n"
    texto, copias, _ = m.recoger_imagenes(resto, ruta.parent, "SOP-X-001")
    assert len(copias) == 1 and texto.count("_img/SOP-X-001-01-otra-captura.png") == 2


def test_migracion_completa_pasa_el_validador(tmp_path):
    ruta = _protocolo(tmp_path)
    original = ruta.read_text(encoding="utf-8")
    biblioteca = tmp_path / "ClienteX" / "Biblioteca"

    r = m.migrar_protocolo(ruta, biblioteca, tipo="SOP", cliente="ClienteX", propietario="Jorge", hoy=HOY)

    assert r["id"] == "SOP-HOLDED-001" and r["estado"] == "aprobado"
    assert r["ruta"] == biblioteca / "SOP-HOLDED-001_circuito-de-compra.es.md"
    assert (biblioteca / "_img" / "SOP-HOLDED-001-04-comparativo-proveedores.png").exists()
    assert ruta.read_text(encoding="utf-8") == original  # el original no se toca
    assert (ruta.parent / "Capturas" / "Editadas" / "P02-04-comparativo-proveedores.png").exists()

    meta, cuerpo = bib.leer_documento(r["ruta"])
    assert meta["titulo"] == "Circuito de compra" and meta["aliases"] == ["P-02 · Circuito de compra"]
    assert meta["estado"] == "aprobado" and meta["version"] == "1.0" and meta["revisor"] == "Administración"
    assert meta["revisado"] == "2026-09-30" and meta["proxima_revision"] == "2027-09-30"
    assert meta["origen"] == "protocolo-antiguo" and meta["aplicacion"] == "Holded" and meta["propietario"] == "Jorge"
    assert cuerpo.startswith("# Circuito de compra")
    assert "## Alcance" in cuerpo and "- **Quién lo hace:** Compras" in cuerpo
    assert "Quién lo hace** | Compras" not in cuerpo  # la tabla antigua ya no está
    assert "## Qué NO hacer" in cuerpo and "## Historial de cambios" in cuerpo
    assert "Migrado desde el protocolo P-02 · Circuito de compra" in cuerpo

    _, hallazgos = validar.validar_biblioteca(biblioteca, HOY)
    # la única incidencia permitida es la imagen que ya faltaba en el protocolo antiguo
    assert [h.mensaje for h in hallazgos if h.nivel == "ERROR"] == ["imagen que no existe: Capturas/Editadas/no-existe.png"]


def test_simular_no_escribe_nada(tmp_path):
    ruta = _protocolo(tmp_path)
    biblioteca = tmp_path / "bib"
    r = m.migrar_protocolo(ruta, biblioteca, cliente="X", propietario="Jorge", hoy=HOY, simular=True)
    assert r["imagenes"] and not biblioteca.exists()


def test_no_sobrescribe_y_el_segundo_protocolo_coge_otro_numero(tmp_path):
    ruta = _protocolo(tmp_path)
    biblioteca = tmp_path / "bib"
    a = m.migrar_protocolo(ruta, biblioteca, cliente="X", propietario="Jorge", hoy=HOY)
    b = m.migrar_protocolo(ruta, biblioteca, cliente="X", propietario="Jorge", hoy=HOY, carpeta=biblioteca / "otra")
    assert a["id"] == "SOP-HOLDED-001" and b["id"] == "SOP-HOLDED-002"


def test_errores_de_entrada(tmp_path):
    with pytest.raises(FileNotFoundError):
        m.migrar_protocolo(tmp_path / "no.md", tmp_path, propietario="J")
    ruta = _protocolo(tmp_path)
    with pytest.raises(ValueError, match="propietario"):
        m.migrar_protocolo(ruta, tmp_path / "bib", propietario="")


def test_protocolo_sin_tabla_ni_codigo(tmp_path):
    ruta = tmp_path / "Entrada de factura.md"
    ruta.write_text("# Entrada de factura\n\n## Pasos\n\nHaz esto.\n", encoding="utf-8")
    r = m.migrar_protocolo(ruta, tmp_path / "bib", aplicacion="Holded", cliente="X", propietario="Jorge", hoy=HOY)
    meta, cuerpo = bib.leer_documento(r["ruta"])
    assert meta["estado"] == "borrador" and meta["version"] == "0.1" and meta["aliases"] == ["Entrada de factura"]
    assert "## Alcance" not in cuerpo and "## Historial de cambios" in cuerpo
