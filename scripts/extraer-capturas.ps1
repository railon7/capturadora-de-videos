<#
.SYNOPSIS
    Convierte un vídeo en fotogramas navegables: rejilla a intervalo fijo,
    opcionalmente fotogramas extra en cada cambio de escena, hojas de
    contacto para localizar un momento sin reproducir el vídeo, e índice
    tiempo -> fichero.

.PARAMETER Video
    Ruta al vídeo de origen. Obligatorio.

.PARAMETER Trabajo
    Carpeta de trabajo donde se crea la estructura de salida. Por defecto,
    una carpeta "Capturas-<nombre del vídeo>" junto al propio vídeo.

.PARAMETER Intervalo
    Segundos entre fotograma y fotograma de la rejilla a intervalo fijo.
    Por defecto 20.

.PARAMETER AnchoMax
    Ancho máximo de los fotogramas, en píxeles. Por defecto 1600. No afecta
    a la calidad de una captura puntual (ver extraer-captura-puntual.ps1).

.PARAMETER SaltarInicioPct
    Porcentaje de la duración total a saltar al principio (pantallas de
    carga, logotipos). Por defecto 0. Un valor típico si el vídeo empieza
    con una intro es 5-7.

.PARAMETER SaltarFinalPct
    Igual que SaltarInicioPct, pero al final del vídeo. Por defecto 0.

.PARAMETER SoloKeyframes
    Solo decodifica fotogramas clave (I-frames) en la extracción a
    intervalo fijo. Evita fotogramas borrosos por compresión intermedia,
    algo más frecuente en vídeo HEVC/H.265. A cambio, el fotograma que
    sale para cada marca de tiempo puede ser el keyframe más cercano, no
    el instante exacto — el nombre t_HHMMSS.jpg pasa a ser aproximado, no
    exacto. Si la exactitud del instante importa, no actives esta opción
    y usa extraer-captura-puntual.ps1 para la captura final.

.PARAMETER DeteccionEscena
    Además de la rejilla a intervalo fijo, saca un fotograma extra en cada
    cambio de escena real (filtro `scene` de ffmpeg). Pensado para pillar
    transiciones de pantalla que ocurren en menos tiempo que el intervalo
    fijo y que de otro modo se pierden entre fotograma y fotograma. Salen
    con el prefijo e_HHMMSS.jpg y en su propio índice
    (Analisis/indice-escenas.txt): no entran en las hojas de contacto, que
    siguen cubriendo solo el muestreo a intervalo fijo.

.PARAMETER UmbralEscena
    Sensibilidad de la detección de escena, de 0 a 1. Por defecto 0.4
    (cambios de plano claros). Bájalo hacia 0.1-0.3 para pillar también
    transiciones sutiles (un menú desplegable, un scroll brusco); súbelo
    hacia 0.6-0.7 para quedarte solo con los cambios de pantalla completos.
    Sin efecto si no se activa -DeteccionEscena.

.EXAMPLE
    .\extraer-capturas.ps1 -Video "C:\videos\demo.mp4"

.EXAMPLE
    .\extraer-capturas.ps1 -Video "C:\videos\demo.mp4" -Trabajo "C:\proyecto\Capturas" -Intervalo 10 -DeteccionEscena

.EXAMPLE
    .\extraer-capturas.ps1 -Video "C:\videos\demo.mp4" -SaltarInicioPct 5 -SaltarFinalPct 3 -SoloKeyframes
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Video,

    [string]$Trabajo,

    [int]$Intervalo = 20,

    [int]$AnchoMax = 1600,

    [double]$SaltarInicioPct = 0,

    [double]$SaltarFinalPct = 0,

    [switch]$SoloKeyframes,

    [switch]$DeteccionEscena,

    [double]$UmbralEscena = 0.4
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Video)) {
    throw "No encuentro el vídeo: $Video"
}
$Video = (Resolve-Path -LiteralPath $Video).Path

if (-not $Trabajo) {
    $nombreVideo = [System.IO.Path]::GetFileNameWithoutExtension($Video)
    $Trabajo = Join-Path (Split-Path $Video -Parent) "Capturas-$nombreVideo"
}

$Log = Join-Path $Trabajo "_log-extraccion.txt"
New-Item -ItemType Directory -Force -Path $Trabajo | Out-Null
try { Start-Transcript -LiteralPath $Log -Force | Out-Null } catch { }

function Paso  ($t) { Write-Host ""; Write-Host "==> $t" -ForegroundColor Cyan }
function Bien  ($t) { Write-Host "    $t" -ForegroundColor Green }
function Aviso ($t) { Write-Host "    $t" -ForegroundColor Yellow }
function Fallo ($t) { Write-Host "    $t" -ForegroundColor Red }

try {

Write-Host ""
Write-Host "  Extraccion de capturas de video" -ForegroundColor White
Write-Host "  --------------------------------" -ForegroundColor DarkGray
Write-Host "  PowerShell $($PSVersionTable.PSVersion)"

# --------------------------------------------------------------- 1 · carpetas
Paso "Creando la estructura de carpetas"
foreach ($c in @("Capturas\Rejilla","Capturas\Seleccionadas","Capturas\Editadas","Hojas de contactos","Analisis")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Trabajo $c) | Out-Null
}
Bien "Listo en: $Trabajo"

$gb = [math]::Round((Get-Item -LiteralPath $Video).Length / 1GB, 2)
Bien "Video ($gb GB): $(Split-Path $Video -Leaf)"

# ----------------------------------------------------------------- 2 · ffmpeg
Paso "Comprobando ffmpeg"
function Buscar-FFmpeg {
    $c = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    $local = Join-Path $Trabajo "_herramientas\ffmpeg\bin\ffmpeg.exe"
    if (Test-Path -LiteralPath $local) { return $local }
    return $null
}
$FFmpeg = Buscar-FFmpeg

if (-not $FFmpeg) {
    Aviso "No esta instalado. Intento instalarlo con winget..."
    try {
        winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements --silent | Out-Null
        $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
        $FFmpeg = Buscar-FFmpeg
    } catch { Aviso "winget no ha podido instalarlo." }
}

if (-not $FFmpeg) {
    Aviso "Descargo una copia portable de ffmpeg en la carpeta de trabajo..."
    $dirH = Join-Path $Trabajo "_herramientas"
    New-Item -ItemType Directory -Force -Path $dirH | Out-Null
    $zip  = Join-Path $dirH "ffmpeg.zip"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile $zip -UseBasicParsing
    Expand-Archive -LiteralPath $zip -DestinationPath $dirH -Force
    Remove-Item -LiteralPath $zip -Force
    $ext = Get-ChildItem -Path $dirH -Directory | Where-Object { $_.Name -like 'ffmpeg-*' } | Select-Object -First 1
    if ($ext) { Rename-Item -LiteralPath $ext.FullName -NewName "ffmpeg" -Force }
    $FFmpeg = Buscar-FFmpeg
}

if (-not $FFmpeg) { throw "No he conseguido tener ffmpeg disponible. Instalalo a mano y vuelve a lanzar el script." }

$FFprobe = Join-Path (Split-Path $FFmpeg -Parent) "ffprobe.exe"
if (-not (Test-Path -LiteralPath $FFprobe)) { $FFprobe = "ffprobe" }
Bien "ffmpeg: $FFmpeg"

# ------------------------------------------------------------ 3 · info del video
Paso "Leyendo la informacion del video"
$argsProbe = @('-v','error','-select_streams','v:0','-show_entries','format=duration:stream=width,height,r_frame_rate,codec_name','-of','default=noprint_wrappers=1','--',$Video)
$info = & $FFprobe @argsProbe 2>&1
$info | Out-File -LiteralPath (Join-Path $Trabajo "Analisis\video-info.txt") -Encoding UTF8
$dur = ($info | Select-String '^duration=' | Select-Object -First 1) -replace 'duration=',''
$segundos = [int][double]$dur
$ts = [TimeSpan]::FromSeconds($segundos)
$previstos = [math]::Floor($segundos / $Intervalo) + 1
Bien ("Duracion: {0:hh\:mm\:ss}  -  fotogramas previstos: ~{1}" -f $ts, $previstos)

$inicioSeg = [math]::Round($segundos * $SaltarInicioPct / 100, 2)
$finSeg    = [math]::Round($segundos * $SaltarFinalPct / 100, 2)
$duracionUtil = $segundos - $inicioSeg - $finSeg
if ($duracionUtil -le 0) { throw "SaltarInicioPct + SaltarFinalPct deja 0 o menos segundos de video util." }
if ($inicioSeg -gt 0 -or $finSeg -gt 0) {
    Bien ("Saltando {0}s al inicio y {1}s al final -> {2}s utiles" -f $inicioSeg, $finSeg, $duracionUtil)
}

# ------------------------------------------------------------ 4 · extraccion
Paso "Extrayendo un fotograma cada $Intervalo segundos"
Aviso "Esto recorre el video entero. Puede tardar - dejalo corriendo."
$dirRej = Join-Path $Trabajo "Capturas\Rejilla"
Get-ChildItem -LiteralPath $dirRej -Filter *.jpg -ErrorAction SilentlyContinue | Remove-Item -Force

$t0 = Get-Date
$filtro = "fps=1/$Intervalo,scale='min($AnchoMax,iw)':-2"
$argsExtraer = @('-hide_banner','-loglevel','warning','-stats')
if ($SoloKeyframes) { $argsExtraer += @('-skip_frame','nokey') }
if ($inicioSeg -gt 0) { $argsExtraer += @('-ss', $inicioSeg) }
$argsExtraer += @('-y','-i',$Video)
if ($inicioSeg -gt 0 -or $finSeg -gt 0) { $argsExtraer += @('-t', $duracionUtil) }
$argsExtraer += @('-vf',$filtro,'-vsync','vfr','-q:v','3',(Join-Path $dirRej '_tmp_%04d.jpg'))
& $FFmpeg @argsExtraer
if ($LASTEXITCODE -ne 0) { throw "ffmpeg ha devuelto error al extraer los fotogramas." }
$n = (Get-ChildItem -LiteralPath $dirRej -Filter "_tmp_*.jpg").Count
Bien ("{0} capturas en {1:mm\:ss}" -f $n, ((Get-Date) - $t0))
if ($SoloKeyframes) {
    Aviso "SoloKeyframes activo: el instante de cada t_HHMMSS.jpg es aproximado (el keyframe mas cercano), no exacto."
}

# --------------------------------------------------- 5 · hojas de contactos
Paso "Montando las hojas de contactos"
$dirHojas = Join-Path $Trabajo "Hojas de contactos"
Get-ChildItem -LiteralPath $dirHojas -Filter *.jpg -ErrorAction SilentlyContinue | Remove-Item -Force
$argsHojas = @('-hide_banner','-loglevel','error','-y','-i',(Join-Path $dirRej '_tmp_%04d.jpg'),'-vf','scale=520:-2,tile=5x4:margin=8:padding=8:color=0x1b1b1b','-vsync','vfr','-q:v','3',(Join-Path $dirHojas 'hoja_%02d.jpg'))
& $FFmpeg @argsHojas
$h = (Get-ChildItem -LiteralPath $dirHojas -Filter "hoja_*.jpg" -ErrorAction SilentlyContinue).Count
Bien "$h hojas de contactos (20 fotogramas cada una, 5x4, $([math]::Round($Intervalo * 20 / 60, 1)) min por hoja)"
Aviso "Las hojas de contacto solo cubren el muestreo a intervalo fijo, no los fotogramas de cambio de escena."

# ------------------------------------------------------------ 6 · renombrado
Paso "Renombrando las capturas por su minuto"
$i = 0
$lineas = New-Object System.Collections.Generic.List[string]
$lineas.Add("indice`thora`tfichero")
$tiemposIntervalo = New-Object System.Collections.Generic.List[int]
Get-ChildItem -LiteralPath $dirRej -Filter "_tmp_*.jpg" | Sort-Object Name | ForEach-Object {
    $seg   = [int]$inicioSeg + ($i * $Intervalo)
    $sp    = [TimeSpan]::FromSeconds($seg)
    # Floor, no [int]: [int] redondea (1:54 = 1,9 h saldría como hora 2)
    $horas = [int][math]::Floor($sp.TotalHours)
    $sello = '{0:00}{1:00}{2:00}' -f $horas, $sp.Minutes, $sp.Seconds
    $hora  = '{0:00}:{1:00}:{2:00}' -f $horas, $sp.Minutes, $sp.Seconds
    $nuevo = "t_$sello.jpg"
    Rename-Item -LiteralPath $_.FullName -NewName $nuevo -Force
    $lineas.Add(("{0}`t{1}`t{2}" -f ($i + 1), $hora, $nuevo))
    $tiemposIntervalo.Add($seg)
    $i++
}
$lineas | Out-File -LiteralPath (Join-Path $Trabajo "Analisis\indice-capturas.txt") -Encoding UTF8
Bien "$i capturas renombradas a t_HHMMSS.jpg"

# --------------------------------------------- 7 · deteccion de escena (opcional)
$numEscenas = 0
if ($DeteccionEscena) {
    Paso "Detectando cambios de escena (umbral $UmbralEscena)"
    Get-ChildItem -LiteralPath $dirRej -Filter "_esc_*.jpg" -ErrorAction SilentlyContinue | Remove-Item -Force
    $filtroEsc = "select='gt(scene,$UmbralEscena)',scale='min($AnchoMax,iw)':-2,showinfo"
    $argsEsc = @('-hide_banner','-loglevel','info','-y','-i',$Video,'-vf',$filtroEsc,'-vsync','vfr','-q:v','3',(Join-Path $dirRej '_esc_%04d.jpg'))
    $salidaEsc = & $FFmpeg @argsEsc 2>&1

    $tiemposEsc = New-Object System.Collections.Generic.List[double]
    foreach ($linea in $salidaEsc) {
        if ($linea -match 'pts_time:(?<t>[\d\.]+)') { $tiemposEsc.Add([double]$Matches['t']) }
    }

    $archivosEsc = Get-ChildItem -LiteralPath $dirRej -Filter "_esc_*.jpg" | Sort-Object Name
    if ($archivosEsc.Count -ne $tiemposEsc.Count) {
        Aviso "No he podido emparejar todos los tiempos de escena con sus fotogramas (ffmpeg cambio su formato de aviso). Reviso solo los que coincidan."
    }

    $lineasEsc = New-Object System.Collections.Generic.List[string]
    $lineasEsc.Add("hora`tfichero")
    for ($k = 0; $k -lt [math]::Min($archivosEsc.Count, $tiemposEsc.Count); $k++) {
        $seg = [int][math]::Round($tiemposEsc[$k])
        # Si cae a menos de 2s de un fotograma ya sacado por intervalo fijo, es redundante
        $esRedundante = $false
        foreach ($tExistente in $tiemposIntervalo) {
            if ([math]::Abs($seg - $tExistente) -le 2) { $esRedundante = $true; break }
        }
        if ($esRedundante) {
            Remove-Item -LiteralPath $archivosEsc[$k].FullName -Force
            continue
        }
        $sp    = [TimeSpan]::FromSeconds($seg)
        $horas = [int][math]::Floor($sp.TotalHours)
        $sello = '{0:00}{1:00}{2:00}' -f $horas, $sp.Minutes, $sp.Seconds
        $hora  = '{0:00}:{1:00}:{2:00}' -f $horas, $sp.Minutes, $sp.Seconds
        # Dos cambios de escena en el mismo segundo darían el mismo nombre, y
        # Rename-Item no sobrescribe aunque lleve -Force: sufijo _2, _3...
        $nuevo = "e_$sello.jpg"
        $n = 2
        while (Test-Path -LiteralPath (Join-Path $dirRej $nuevo)) {
            $nuevo = "e_${sello}_$n.jpg"
            $n++
        }
        Rename-Item -LiteralPath $archivosEsc[$k].FullName -NewName $nuevo
        $lineasEsc.Add(("{0}`t{1}" -f $hora, $nuevo))
        $numEscenas++
    }
    # Sobrantes sin tiempo emparejado: fuera, para no dejar basura _esc_ en la carpeta
    Get-ChildItem -LiteralPath $dirRej -Filter "_esc_*.jpg" -ErrorAction SilentlyContinue | Remove-Item -Force

    $lineasEsc | Out-File -LiteralPath (Join-Path $Trabajo "Analisis\indice-escenas.txt") -Encoding UTF8
    Bien "$numEscenas fotogramas de cambio de escena (e_HHMMSS.jpg), tras descartar los redundantes con la rejilla"
}

Write-Host ""
Write-Host "  TERMINADO" -ForegroundColor Green
Write-Host "  ---------" -ForegroundColor DarkGray
Write-Host "  Capturas ............ $dirRej"
Write-Host "  Hojas de contactos .. $dirHojas"
Write-Host "  Indice .............. $(Join-Path $Trabajo 'Analisis\indice-capturas.txt')"
if ($DeteccionEscena) {
Write-Host "  Indice de escenas ... $(Join-Path $Trabajo 'Analisis\indice-escenas.txt') ($numEscenas)"
}
Write-Host ""
Write-Host "  Para el mapa del video y las capturas del manual, sigue" -ForegroundColor White
Write-Host "  metodologia/de-video-a-guion-y-patrones.md y de-capturas-a-manual.md" -ForegroundColor White

}
catch {
    Write-Host ""
    Write-Host "  ERROR" -ForegroundColor Red
    Write-Host "  -----" -ForegroundColor DarkGray
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Linea: $($_.InvocationInfo.ScriptLineNumber)" -ForegroundColor DarkGray
    Write-Host "  $($_.InvocationInfo.Line.Trim())" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "  Todo esto ha quedado guardado en _log-extraccion.txt" -ForegroundColor Yellow
    exit 1
}
finally {
    try { Stop-Transcript | Out-Null } catch { }
}
