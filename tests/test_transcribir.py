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


def test_tramos_audio_corto_es_un_solo_tramo():
    np = pytest.importorskip("numpy")
    muestras = np.ones(100 * 16, dtype=np.float32)  # 100 s a 16 Hz
    assert m.tramos_por_silencio(muestras, 16, tramo_seg=90) == [(0, 1600)]


def test_tramos_cubren_todo_el_audio_sin_huecos():
    np = pytest.importorskip("numpy")
    muestras = np.random.default_rng(1).uniform(-1, 1, 10_000 * 16).astype(np.float32)
    tramos = m.tramos_por_silencio(muestras, 16, tramo_seg=1800, margen_seg=15)
    assert tramos[0][0] == 0 and tramos[-1][1] == len(muestras)
    assert all(a[1] == b[0] for a, b in zip(tramos, tramos[1:]))
    assert len(tramos) == 6  # 10 000 s en tramos de ~30 min (el último, con lo que sobra)


def test_tramos_cortan_en_el_silencio():
    np = pytest.importorskip("numpy")
    f = 16
    muestras = np.random.default_rng(2).uniform(-1, 1, 4000 * f).astype(np.float32)
    muestras[1808 * f:1810 * f] = 0  # silencio de 2 s, 8 s después del corte nominal
    tramos = m.tramos_por_silencio(muestras, f, tramo_seg=1800, margen_seg=15)
    assert 1808 * f <= tramos[0][1] <= 1810 * f


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
