from _util import cargar_modulo

m = cargar_modulo("consolidar-patrones.py")

# Solo se prueban las funciones puras. main() escribe en el
# conocimiento/patrones-acumulados.md real del repo — no se invoca aquí.

ORIGEN = """# Patrones reutilizables — Proyecto de prueba

## Escandallo base + acabado
**Visto en**: Cliente A, 2026-09
**Se aplica cuando**: fabricante que en realidad ensambla

Un artículo estándar que se stockea y un segundo escandallo de acabado.

## Fabricación y proyecto separados
**Visto en**: Cliente A, 2026-09
**Se aplica cuando**: se factura por certificación

La orden se cierra al montar; las horas posteriores van al proyecto.
"""

ACUMULADO = """# Patrones acumulados

## Del proyecto: Otro cliente

### Escandallo base y de acabado
**Visto en**: Otro cliente, 2026-01

Texto.
"""


def test_normalizar():
    assert m.normalizar("Escandallo base + acabado") == "escandallo base acabado"


def test_extraer_patrones_encuentra_los_dos():
    patrones = m.extraer_patrones(ORIGEN)
    nombres = [n for n, _ in patrones]
    assert nombres == ["Escandallo base + acabado", "Fabricación y proyecto separados"]


def test_extraer_patrones_incluye_el_cuerpo_completo():
    patrones = m.extraer_patrones(ORIGEN)
    _, cuerpo = patrones[0]
    assert cuerpo.startswith("## Escandallo base + acabado")
    assert "artículo estándar" in cuerpo
    assert "Fabricación y proyecto separados" not in cuerpo  # no se cuela el siguiente patrón


def test_nombres_existentes_lee_los_de_nivel_tres():
    assert m.nombres_existentes(ACUMULADO) == ["Escandallo base y de acabado"]


def test_deteccion_de_parecido_via_difflib():
    import difflib
    ratio = difflib.SequenceMatcher(
        None,
        m.normalizar("Escandallo base + acabado"),
        m.normalizar("Escandallo base y de acabado"),
    ).ratio()
    assert ratio >= m.UMBRAL_PARECIDO
