import struct

import pytest

from _util import cargar_modulo

m = cargar_modulo("transcribir.py")


def test_formatear_hora():
    assert m.formatear_hora(0) == "00:00:00"
    assert m.formatear_hora(6860.4) == "01:54:20"


def test_comando_audio_saca_pcm_mono_16k_por_la_salida_estandar():
    cmd = m.comando_audio("ffmpeg", "video con espacios.mp4")
    assert cmd[0] == "ffmpeg"
    assert "video con espacios.mp4" in cmd  # un argumento, sin partir por espacios
    assert cmd[cmd.index("-ac") + 1] == "1"
    assert cmd[cmd.index("-ar") + 1] == "16000"
    assert cmd[cmd.index("-f") + 1] == "s16le"
    assert cmd[-1] == "-"


def test_pcm_a_muestras_escala_entre_menos_uno_y_uno():
    pytest.importorskip("numpy")
    pcm = struct.pack("<3h", 0, 16384, -32768)
    muestras = m.pcm_a_muestras(pcm)
    assert str(muestras.dtype) == "float32"
    assert list(muestras) == [0.0, 0.5, -1.0]


def test_localizar_ffmpeg_manual_que_no_existe(tmp_path):
    assert m.localizar_ffmpeg(str(tmp_path / "no-existe.exe")) is None


def test_localizar_ffmpeg_en_la_copia_portable(tmp_path, monkeypatch):
    monkeypatch.setattr(m.shutil, "which", lambda _: None)
    portable = tmp_path / "_herramientas" / "ffmpeg" / "bin"
    portable.mkdir(parents=True)
    (portable / "ffmpeg.exe").write_bytes(b"")
    assert m.localizar_ffmpeg(None, [tmp_path]) == str(portable / "ffmpeg.exe")


def test_localizar_ffmpeg_sin_ninguno(tmp_path, monkeypatch):
    monkeypatch.setattr(m.shutil, "which", lambda _: None)
    assert m.localizar_ffmpeg(None, [tmp_path]) is None


def test_preparar_dlls_cuda_devuelve_lista():
    # En Linux/macOS no hace nada; en Windows añade las que haya instaladas
    assert isinstance(m.preparar_dlls_cuda(), list)
