#!/usr/bin/env python3
"""Utilidades compartidas de la biblioteca de conocimiento.

No se ejecuta solo: lo importan nuevo-documento.py, validar-biblioteca.py,
migrar-protocolo.py, patrones-a-biblioteca.py y exportar-manual.py. Solo
usa la librería estándar (el frontmatter YAML se lee con un lector propio
que cubre el subconjunto que usan las plantillas: textos, listas en bloque
y listas en línea), para que los scripts funcionen sin instalar nada.

La convención completa está en metodologia/biblioteca-de-conocimiento.md.
"""
import datetime
import os
import re
import subprocess
import unicodedata
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent
BIBLIOTECA_POR_DEFECTO = RAIZ_REPO / "conocimiento" / "biblioteca"
PLANTILLAS = RAIZ_REPO / "plantillas" / "biblioteca"
VARIABLE_ENTORNO = "BIBLIOTECA_TAZUKE"

# --------------------------------------------------------------------- tipos
# código -> valor del campo `tipo`, nombres ES/EN y cuadrante de Diátaxis
TIPOS = {
    "MAN": {"valor": "manual-aplicacion", "es": "Manual de aplicación", "en": "Application manual",
            "diataxis": "referencia + explicación", "audiencia": ["equipo", "cliente"]},
    "GUI": {"valor": "guia-usuario", "es": "Guía de usuario", "en": "User guide",
            "diataxis": "cómo hacer", "audiencia": ["cliente"]},
    "SOP": {"valor": "sop", "es": "Procedimiento normalizado de trabajo (PNT)", "en": "Standard operating procedure (SOP)",
            "diataxis": "cómo hacer, con control", "audiencia": ["equipo-cliente"]},
    "TUT": {"valor": "tutorial", "es": "Tutorial de formación", "en": "Training tutorial",
            "diataxis": "tutorial", "audiencia": ["usuario-nuevo"]},
    "QSG": {"valor": "guia-rapida", "es": "Guía rápida", "en": "Quick-start guide",
            "diataxis": "tutorial corto", "audiencia": ["usuario-nuevo"]},
    "FAQ": {"valor": "faq", "es": "Preguntas frecuentes y resolución de problemas", "en": "FAQ and troubleshooting",
            "diataxis": "cómo hacer", "audiencia": ["cliente", "equipo"]},
    "GLO": {"valor": "glosario", "es": "Glosario ES-EN", "en": "Glossary",
            "diataxis": "referencia", "audiencia": ["equipo", "cliente"]},
    "NOV": {"valor": "notas-version", "es": "Notas de versión", "en": "Release notes",
            "diataxis": "referencia", "audiencia": ["equipo", "cliente"]},
    "DEC": {"valor": "decision", "es": "Registro de decisión", "en": "Decision record",
            "diataxis": "explicación", "audiencia": ["equipo"]},
    "PAT": {"valor": "patron", "es": "Patrón reutilizable", "en": "Reusable pattern",
            "diataxis": "explicación", "audiencia": ["equipo"]},
}
VALOR_A_CODIGO = {datos["valor"]: codigo for codigo, datos in TIPOS.items()}

ESTADOS = ("borrador", "revision", "aprobado", "obsoleto")
ESTADOS_TRADUCCION = ("pendiente", "borrador-ia", "revisada")
IDIOMAS = ("es", "en")
# Los tres estados del protocolo antiguo (plantilla-protocolo.md) y su equivalente
EMOJI_A_ESTADO = {"🟡": "borrador", "🟠": "revision", "🟢": "aprobado"}

# Carpetas que el recorrido de la biblioteca no mira
CARPETAS_IGNORADAS = {"_img", "entregables", ".obsidian", ".git", ".trash", "node_modules", "__pycache__"}


def es_fichero_de_servicio(nombre: str) -> bool:
    """Ficheros .md que no son documentos de la biblioteca: índices, avisos y registros generados."""
    return nombre.startswith("00_") or nombre.upper() in {"LEEME.MD", "README.MD"}


# ------------------------------------------------------------------ nombres
RE_ID = re.compile(r"^(?P<tipo>[A-Z]{3})-(?P<ambito>[A-Z0-9]{2,8})-(?P<numero>\d{3})$")
RE_NOMBRE = re.compile(
    r"^(?P<id>[A-Z]{3}-[A-Z0-9]{2,8}-\d{3})_(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.(?P<idioma>es|en)\.md$"
)
RE_VERSION = re.compile(r"^\d+\.\d+$")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def slugify(texto: str, maximo: int = 60) -> str:
    """Texto -> kebab-case sin tildes: 'Emitir factura rectificativa' -> 'emitir-factura-rectificativa'."""
    normal = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in normal if not unicodedata.combining(c))
    limpio = re.sub(r"[^a-z0-9]+", "-", sin_tildes.lower()).strip("-")
    if len(limpio) > maximo:
        corte = limpio[:maximo]
        # no cortar una palabra por la mitad si hay un guion cerca del final
        if "-" in corte and limpio[maximo] != "-":
            corte = corte.rsplit("-", 1)[0]
        limpio = corte.strip("-")
    return limpio


def codigo_ambito(texto: str) -> str:
    """Código de 2-8 caracteres para el ID a partir del nombre de una aplicación o área.

    'Holded' -> 'HOLDED', 'Administración' -> 'ADMINIST'. Es una propuesta:
    nuevo-documento.py acepta --ambito para fijar el que se quiera.
    """
    solo = re.sub(r"[^A-Z0-9]", "", slugify(texto).upper())
    return solo[:8] if len(solo) >= 2 else (solo + "XX")[:2]


def nombre_fichero(id_doc: str, slug: str, idioma: str) -> str:
    return f"{id_doc}_{slug}.{idioma}.md"


def partir_nombre(nombre: str):
    """Devuelve {'id','slug','idioma'} o None si el nombre no sigue la convención."""
    m = RE_NOMBRE.match(nombre)
    return m.groupdict() if m else None


def partir_id(id_doc: str):
    m = RE_ID.match(id_doc or "")
    return m.groupdict() if m else None


def tipo_desde_texto(texto: str) -> str:
    """Acepta el código (SOP) o el valor (sop, guia-usuario) y devuelve el código."""
    clave = (texto or "").strip()
    if clave.upper() in TIPOS:
        return clave.upper()
    if clave.lower() in VALOR_A_CODIGO:
        return VALOR_A_CODIGO[clave.lower()]
    raise ValueError(f"Tipo desconocido: {texto!r}. Válidos: {', '.join(TIPOS)}")


# --------------------------------------------------------------- frontmatter
class ErrorFrontmatter(ValueError):
    pass


_RE_CLAVE = re.compile(r"^([A-Za-z_][\w-]*)\s*:(?:\s+(.*))?$")
_RE_ELEMENTO = re.compile(r"^\s+-(?:\s+(.*))?$")


def _quitar_comentario(valor: str) -> str:
    """Quita un ' # comentario' final de un valor sin comillas."""
    if valor[:1] in ('"', "'"):
        return valor
    return re.sub(r"\s+#.*$", "", valor).strip()


def _desescapar(valor: str) -> str:
    valor = valor.strip()
    if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
        return re.sub(r'\\(["\\])', r"\1", valor[1:-1])
    if len(valor) >= 2 and valor[0] == "'" and valor[-1] == "'":
        return valor[1:-1].replace("''", "'")
    return valor


def _partir_lista_en_linea(contenido: str) -> list:
    elementos, actual, comilla = [], "", None
    for c in contenido:
        if comilla:
            actual += c
            if c == comilla:
                comilla = None
        elif c in ('"', "'"):
            comilla = c
            actual += c
        elif c == ",":
            elementos.append(actual)
            actual = ""
        else:
            actual += c
    elementos.append(actual)
    return [_desescapar(e) for e in elementos if e.strip()]


def parsear_frontmatter(texto: str):
    """Devuelve (meta: dict, cuerpo: str). Sin bloque `---` inicial, meta es {}.

    Todos los valores salen como texto (o lista de textos): no se convierten
    números ni fechas, así '1.10' no pasa a ser 1.1. Lanza ErrorFrontmatter
    si el bloque está abierto sin cerrar o tiene una línea que no entiende.
    """
    texto = texto.lstrip("﻿")
    lineas = texto.splitlines()
    if not lineas or lineas[0].strip() != "---":
        return {}, texto
    cierre = next((i for i in range(1, len(lineas)) if lineas[i].strip() == "---"), None)
    if cierre is None:
        raise ErrorFrontmatter("el bloque de frontmatter empieza con --- pero no se cierra")
    meta, clave_abierta = {}, None
    for numero, linea in enumerate(lineas[1:cierre], start=2):
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        elemento = _RE_ELEMENTO.match(linea)
        if elemento and clave_abierta is not None:
            valor = _desescapar(_quitar_comentario((elemento.group(1) or "").strip()))
            if not isinstance(meta[clave_abierta], list):
                meta[clave_abierta] = []
            meta[clave_abierta].append(valor)
            continue
        m = _RE_CLAVE.match(linea)
        if not m:
            raise ErrorFrontmatter(f"línea {numero} no reconocida: {linea.strip()!r}")
        clave, valor = m.group(1), _quitar_comentario((m.group(2) or "").strip())
        if valor.startswith("[") and valor.endswith("]"):
            meta[clave], clave_abierta = _partir_lista_en_linea(valor[1:-1]), None
        elif valor == "":
            meta[clave], clave_abierta = "", clave
        else:
            meta[clave], clave_abierta = _desescapar(valor), None
    cuerpo = "\n".join(lineas[cierre + 1:])
    return meta, cuerpo.lstrip("\n")


_RE_NECESITA_COMILLAS = re.compile(r"""^[\[\]{}&*!|>'"%@`#?,-]|:\s|\s#|:$|^\s|\s$""")
_RE_PARECE_NUMERO = re.compile(r"^[-+]?\d+(\.\d+)?$")
_PALABRAS_RESERVADAS = {"true", "false", "null", "yes", "no", "on", "off", "~"}


def _escalar(valor) -> str:
    valor = "" if valor is None else str(valor)
    if valor == "":
        return ""
    if RE_FECHA.match(valor):
        return valor
    if (_RE_NECESITA_COMILLAS.search(valor) or _RE_PARECE_NUMERO.match(valor)
            or valor.lower() in _PALABRAS_RESERVADAS):
        return '"' + valor.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return valor


def volcar_frontmatter(meta: dict) -> str:
    """Bloque `---` ... `---` con las claves en el orden dado. Listas en bloque, como Obsidian."""
    lineas = ["---"]
    for clave, valor in meta.items():
        if isinstance(valor, (list, tuple)):
            if not valor:
                lineas.append(f"{clave}: []")
            else:
                lineas.append(f"{clave}:")
                lineas.extend(f"  - {_escalar(v)}" for v in valor)
        else:
            lineas.append(f"{clave}: {_escalar(valor)}".rstrip())
    lineas.append("---")
    return "\n".join(lineas) + "\n"


def leer_documento(ruta: Path):
    """(meta, cuerpo) de un fichero de la biblioteca."""
    return parsear_frontmatter(Path(ruta).read_text(encoding="utf-8"))


def escribir_texto(ruta: Path, texto: str) -> None:
    """Escribe en UTF-8 con saltos de línea LF (los de Windows romperían el frontmatter en otros lectores)."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


# --------------------------------------------------------------- biblioteca
def raiz_biblioteca(argumento=None) -> Path:
    """--biblioteca > variable BIBLIOTECA_TAZUKE > conocimiento/biblioteca de este repo."""
    if argumento:
        return Path(argumento)
    if os.environ.get(VARIABLE_ENTORNO):
        return Path(os.environ[VARIABLE_ENTORNO])
    return BIBLIOTECA_POR_DEFECTO


def propietario_por_defecto() -> str:
    """BIBLIOTECA_PROPIETARIO o el nombre configurado en git. Vacío si no hay ninguno."""
    if os.environ.get("BIBLIOTECA_PROPIETARIO"):
        return os.environ["BIBLIOTECA_PROPIETARIO"].strip()
    try:
        return subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def documentos_de(raiz: Path) -> list:
    """Todos los .md de la biblioteca que son documentos (no índices ni registros)."""
    raiz = Path(raiz)
    encontrados = []
    for carpeta, subcarpetas, ficheros in os.walk(raiz):
        subcarpetas[:] = sorted(d for d in subcarpetas if d not in CARPETAS_IGNORADAS)
        for nombre in sorted(ficheros):
            if nombre.lower().endswith(".md") and not es_fichero_de_servicio(nombre):
                encontrados.append(Path(carpeta) / nombre)
    return encontrados


def siguiente_numero(raiz: Path, tipo: str, ambito: str) -> int:
    """Siguiente NNN libre para TIPO-AMBITO-NNN, mirando los nombres de toda la biblioteca (archivo incluido)."""
    maximo = 0
    for ruta in documentos_de(raiz):
        partes = partir_nombre(ruta.name)
        if not partes:
            continue
        datos = partir_id(partes["id"])
        if datos and datos["tipo"] == tipo and datos["ambito"] == ambito:
            maximo = max(maximo, int(datos["numero"]))
    return maximo + 1


def formatear_id(tipo: str, ambito: str, numero: int) -> str:
    return f"{tipo}-{ambito}-{numero:03d}"


def hoy_iso(hoy=None) -> str:
    return (hoy or datetime.date.today()).isoformat()


def sumar_dias(fecha_iso: str, dias: int) -> str:
    return (datetime.date.fromisoformat(fecha_iso) + datetime.timedelta(days=dias)).isoformat()


def fecha_valida(texto: str) -> bool:
    if not RE_FECHA.match(texto or ""):
        return False
    try:
        datetime.date.fromisoformat(texto)
        return True
    except ValueError:
        return False


def subir_version_menor(version: str) -> str:
    """'0.1' -> '0.2', '1.3' -> '1.4'. Si no es mayor.menor, devuelve '0.1'."""
    if not RE_VERSION.match(version or ""):
        return "0.1"
    mayor, menor = version.split(".")
    return f"{mayor}.{int(menor) + 1}"


# --------------------------------------------------- dónde va cada documento y sus metadatos
# Tipos que en la biblioteca común viven en 10-aplicaciones/<aplicación>/
TIPOS_POR_APLICACION = {"MAN", "TUT", "QSG", "FAQ", "NOV"}


def carpeta_destino(raiz: Path, tipo: str, aplicacion: str, cliente: str) -> Path:
    """Dónde va un documento según su tipo y de quién es."""
    raiz = Path(raiz)
    if tipo == "GLO":
        return raiz / "00-gobierno"
    if tipo == "PAT":
        return raiz / "40-patrones"
    if cliente.lower() != "comun":
        return raiz  # la biblioteca de un cliente es plana: el prefijo del ID ya ordena por tipo
    if tipo in TIPOS_POR_APLICACION:
        return raiz / "10-aplicaciones" / slugify(aplicacion)
    return raiz / "00-gobierno"


def construir_meta(*, id_doc, tipo, titulo, idioma, propietario, cliente, aplicacion, fecha,
                   titulo_alt="", traduccion="", traduccion_estado="", origen="", fuente_video="") -> dict:
    datos = TIPOS[tipo]
    meta = {
        "id": id_doc,
        "tipo": datos["valor"],
        "titulo": titulo,
        "aliases": [titulo_alt] if titulo_alt else [],
        "idioma": idioma,
        "version": "0.1",
        "estado": "borrador",
        "propietario": propietario,
        "revisor": "",
        "cliente": cliente,
        "aplicacion": aplicacion,
        "audiencia": list(datos["audiencia"]),
        "creado": fecha,
        "revisado": "",
        "proxima_revision": sumar_dias(fecha, 365),
    }
    if traduccion:
        meta["traduccion"] = traduccion
    if traduccion_estado:
        meta["traduccion_estado"] = traduccion_estado
    if origen:
        meta["origen"] = origen
    if fuente_video:
        meta["fuente_video"] = fuente_video
    meta["tags"] = [f"doc/{datos['valor']}", f"app/{slugify(aplicacion)}",
                    f"cliente/{slugify(cliente)}", f"idioma/{idioma}"]
    return meta


# --------------------------------------------------------------- plantillas
ENCABEZADOS = {
    "proposito": ("Para qué sirve", "Purpose"),
    "alcance": ("Alcance", "Scope"),
    "responsables": ("Responsables", "Responsibilities"),
    "definiciones": ("Definiciones", "Definitions"),
    "antes": ("Antes de empezar", "Before you start"),
    "pasos": ("Pasos", "Steps"),
    "no_hacer": ("Qué NO hacer", "What NOT to do"),
    "si_sale_mal": ("Si algo sale mal", "If something goes wrong"),
    "registros": ("Registros y evidencias", "Records and evidence"),
    "decisiones": ("Decisiones detrás de este procedimiento", "Decisions behind this procedure"),
    "mas_ayuda": ("Más ayuda", "More help"),
    "resumen_app": ("Qué es y para qué se usa", "What it is and what it is for"),
    "conceptos": ("Conceptos clave", "Key concepts"),
    "acceso": ("Acceso y requisitos", "Access and requirements"),
    "pantallas": ("Pantallas y funciones", "Screens and functions"),
    "configuracion": ("Configuración", "Configuration"),
    "integraciones": ("Integraciones", "Integrations"),
    "limites": ("Límites conocidos", "Known limitations"),
    "relacionados": ("Documentos relacionados", "Related documents"),
    "aprenderas": ("Qué vas a aprender", "What you will learn"),
    "requisitos": ("Requisitos", "Requirements"),
    "leccion": ("Lección", "Lesson"),
    "logrado": ("Qué has conseguido", "What you have achieved"),
    "siguientes": ("Siguientes pasos", "Next steps"),
    "objetivo": ("Objetivo", "Goal"),
    "resultado": ("Resultado", "Result"),
    "preguntas": ("Preguntas frecuentes", "Frequently asked questions"),
    "problemas": ("Resolución de problemas", "Troubleshooting"),
    "escalar": ("Cuándo escalar", "When to escalate"),
    "terminos": ("Términos", "Terms"),
    "siglas": ("Siglas", "Acronyms"),
    "resumen_version": ("Resumen de la versión", "Release summary"),
    "novedades": ("Novedades", "What is new"),
    "impacto": ("Cambios que afectan a los procedimientos", "Changes that affect procedures"),
    "correcciones": ("Correcciones", "Fixes"),
    "revisar": ("Documentos a revisar", "Documents to review"),
    "contexto": ("Contexto", "Context"),
    "decision": ("Decisión", "Decision"),
    "alternativas": ("Alternativas descartadas", "Rejected alternatives"),
    "consecuencias": ("Consecuencias", "Consequences"),
    "afectados": ("Documentos afectados", "Affected documents"),
    "se_aplica": ("Se aplica cuando", "Applies when"),
    "patron": ("El patrón", "The pattern"),
    "visto_en": ("Visto en", "Seen in"),
    "evitar": ("Qué evitar", "What to avoid"),
    "historial": ("Historial de cambios", "Change history"),
    "col_version": ("Versión", "Version"),
    "col_fecha": ("Fecha", "Date"),
    "col_cambio": ("Cambio", "Change"),
    "col_autor": ("Autoría", "Author"),
    "col_es": ("Español", "Spanish"),
    "col_en": ("Inglés", "English"),
    "col_def": ("Definición", "Definition"),
    "col_notas": ("Notas", "Notes"),
    "creacion": ("Creación del documento", "Document created"),
    "traducir": ("Pendiente de traducir desde la versión en español.", "Pending translation from the Spanish version."),
}

RE_PLACEHOLDER = re.compile(r"\{\{\s*([\w:]+)\s*\}\}")
RE_GUIA = re.compile(r"<!--\s*GUÍA:.*?-->\n?", re.DOTALL)


def _tabla_historial(idioma: str, valores: dict) -> str:
    i = 0 if idioma == "es" else 1
    cab = [ENCABEZADOS[k][i] for k in ("col_version", "col_fecha", "col_cambio", "col_autor")]
    fila = [valores.get("version", "0.1"), valores.get("fecha", ""), ENCABEZADOS["creacion"][i], valores.get("propietario", "")]
    return (f"## {ENCABEZADOS['historial'][i]}\n\n"
            f"| {' | '.join(cab)} |\n|---|---|---|---|\n| {' | '.join(fila)} |\n")


def renderizar_plantilla(texto: str, valores: dict, idioma: str = "es", con_guia: bool = True) -> str:
    """Rellena una plantilla del cuerpo.

    {{h:clave}} -> encabezado en el idioma pedido · {{historial}} -> sección con la tabla
    de versiones · {{otro}} -> valores['otro']. Un marcador desconocido es un error: mejor
    fallar que dejar un `{{...}}` en un documento.
    """
    if idioma not in IDIOMAS:
        raise ValueError(f"Idioma no soportado: {idioma!r}")
    indice = 0 if idioma == "es" else 1

    def reemplazar(m):
        clave = m.group(1)
        if clave.startswith("h:"):
            return ENCABEZADOS[clave[2:]][indice]
        if clave == "historial":
            return _tabla_historial(idioma, valores).rstrip("\n")
        return str(valores[clave])

    if not con_guia:
        texto = RE_GUIA.sub("", texto)
    return RE_PLACEHOLDER.sub(reemplazar, texto)
