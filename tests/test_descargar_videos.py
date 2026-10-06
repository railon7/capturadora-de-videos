import pytest

from _util import cargar_modulo

m = cargar_modulo("descargar-videos.py")


def test_limpiar_url_quita_el_parametro_si():
    assert m.limpiar_url("https://youtu.be/ciHgR9xX1PI?si=sqWSbu6AaLW59K89") == "https://youtu.be/ciHgR9xX1PI"


def test_limpiar_url_conserva_el_id_de_watch():
    url = "https://www.youtube.com/watch?v=inUOx8OycKU&si=abc&t=42"
    assert m.limpiar_url(url) == "https://www.youtube.com/watch?v=inUOx8OycKU&t=42"


def test_limpiar_url_quita_comillas_tipograficas_y_espacios():
    assert m.limpiar_url(' https://youtu.be/VMM_P4AEcuA?si=jmj6”  ') == "https://youtu.be/VMM_P4AEcuA"


def test_limpiar_nombre_cambia_dos_puntos_y_barra_por_guion():
    assert m.limpiar_nombre("Introducción a FACTUSOL: Conoce su interfaz") == "Introducción a FACTUSOL - Conoce su interfaz"
    assert m.limpiar_nombre("Primeros pasos en Factusol | Cómo usar su interfaz") == "Primeros pasos en Factusol - Cómo usar su interfaz"


def test_limpiar_nombre_quita_emojis_saltos_y_espacios_sobrantes():
    assert m.limpiar_nombre(" ✅ Creación de una\nempresa ") == "Creación de una empresa"


def test_limpiar_nombre_quita_caracteres_prohibidos_en_windows():
    assert m.limpiar_nombre('¿Qué es "esto"? <v2> a/b*') == "¿Qué es esto v2 ab"


def test_limpiar_nombre_evita_nombres_reservados():
    assert m.limpiar_nombre("CON") == "CON_"


def test_parsear_linea_nombre_igual_url():
    linea = "Facturación periódica = https://youtu.be/My5x_Qg2pmQ?si=9D2-mV1hSI8sk8CF"
    assert m.parsear_linea(linea) == ("Facturación periódica", "https://youtu.be/My5x_Qg2pmQ")


def test_parsear_linea_url_de_watch_con_igual_en_el_enlace():
    linea = "Demo = https://www.youtube.com/watch?v=inUOx8OycKU"
    assert m.parsear_linea(linea) == ("Demo", "https://www.youtube.com/watch?v=inUOx8OycKU")


def test_parsear_linea_solo_url():
    assert m.parsear_linea("https://youtu.be/wcgfmlr68LI") == (None, "https://youtu.be/wcgfmlr68LI")


def test_parsear_linea_con_espacios_y_comillas_copiadas():
    linea = ' Creación de una ficha de cliente =  " https://youtu.be/ciHgR9xX1PI?si=sqWS”'
    assert m.parsear_linea(linea) == ("Creación de una ficha de cliente", "https://youtu.be/ciHgR9xX1PI")


@pytest.mark.parametrize("linea", ["", "   ", "# comentario"])
def test_parsear_linea_ignora_vacias_y_comentarios(linea):
    assert m.parsear_linea(linea) is None


def test_parsear_linea_rechaza_lo_que_no_es_un_enlace():
    with pytest.raises(ValueError):
        m.parsear_linea("Esto no lleva enlace")


def test_leer_lista(tmp_path):
    lista = tmp_path / "enlaces.txt"
    lista.write_text(
        "# vídeos de FactuSol\n"
        "Emisión de un informe = https://youtu.be/Aw6823kAu94?si=2CZ8\n"
        "\n"
        "https://youtu.be/k5TrdLiDUB8\n",
        encoding="utf-8",
    )
    assert m.leer_lista(lista) == [
        ("Emisión de un informe", "https://youtu.be/Aw6823kAu94"),
        (None, "https://youtu.be/k5TrdLiDUB8"),
    ]


def test_leer_lista_indica_la_linea_que_falla(tmp_path):
    lista = tmp_path / "enlaces.txt"
    lista.write_text("https://youtu.be/a\nsin enlace\n", encoding="utf-8")
    with pytest.raises(ValueError, match="línea 2"):
        m.leer_lista(lista)


def test_comando_ytdlp_con_nombre(tmp_path):
    cmd = m.comando_ytdlp(["yt-dlp"], "https://youtu.be/x", tmp_path, "Mi vídeo", 720)
    assert cmd[0] == "yt-dlp" and cmd[-1] == "https://youtu.be/x"
    assert cmd[cmd.index("-o") + 1] == "Mi vídeo.%(ext)s"
    assert cmd[cmd.index("-P") + 1] == str(tmp_path)
    assert "height<=720" in cmd[cmd.index("-f") + 1]
    assert "--merge-output-format" in cmd and "--windows-filenames" in cmd


def test_comando_ytdlp_sin_nombre_usa_el_titulo(tmp_path):
    cmd = m.comando_ytdlp(["yt-dlp"], "https://youtu.be/x", tmp_path)
    assert cmd[cmd.index("-o") + 1] == "%(title)s.%(ext)s"
