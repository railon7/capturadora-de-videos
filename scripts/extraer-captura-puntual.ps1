<#
.SYNOPSIS
    Saca un único fotograma de un vídeo, en máxima calidad, en el momento
    exacto que ya se ha localizado con las hojas de contacto, el índice o
    la transcripción con marcas de tiempo.

.PARAMETER Video
    Ruta al vídeo de origen.

.PARAMETER Momento
    Momento del vídeo en formato HH:MM:SS (o MM:SS).

.PARAMETER Salida
    Ruta del fichero de imagen a generar (.png o .jpg). Las carpetas
    intermedias se crean si no existen.

.PARAMETER Preciso
    Búsqueda exacta en lugar de búsqueda rápida. Por defecto, el script
    salta al punto ANTES de decodificar (-ss antes de -i): es casi
    instantáneo incluso en vídeos de varios GB, pero en códecs con pocos
    keyframes (típicamente HEVC/H.265) puede devolver un fotograma un par
    de imágenes antes o después del punto exacto. Con -Preciso, ffmpeg
    decodifica desde el keyframe anterior hasta el punto exacto: siempre
    da el fotograma correcto, pero tarda más cuanto más lejos esté el
    keyframe anterior.

.EXAMPLE
    .\extraer-captura-puntual.ps1 -Video "C:\videos\demo.mp4" -Momento "00:45:20" -Salida "C:\proyecto\Capturas\Seleccionadas\pantalla-01.png"

.EXAMPLE
    .\extraer-captura-puntual.ps1 -Video "C:\videos\demo.mp4" -Momento "00:45:20" -Salida "C:\proyecto\Capturas\Seleccionadas\pantalla-01.png" -Preciso
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Video,

    [Parameter(Mandatory = $true)]
    [string]$Momento,

    [Parameter(Mandatory = $true)]
    [string]$Salida,

    [switch]$Preciso
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Video)) {
    throw "No encuentro el vídeo: $Video"
}

$c = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $c) { throw "ffmpeg no está en el PATH. Ejecuta antes extraer-capturas.ps1, que lo instala, o instálalo a mano." }

$dirSalida = Split-Path $Salida -Parent
if ($dirSalida -and -not (Test-Path -LiteralPath $dirSalida)) {
    New-Item -ItemType Directory -Force -Path $dirSalida | Out-Null
}

if ($Preciso) {
    # -ss despues de -i: ffmpeg decodifica desde el principio del GOP hasta
    # el punto exacto. Mas lento, pero el fotograma es siempre el correcto.
    & ffmpeg -i $Video -ss $Momento -frames:v 1 -q:v 1 -y $Salida
} else {
    # -ss antes de -i: ffmpeg salta directamente al keyframe mas cercano, asi
    # que tarda igual con un video de 500 MB que de 8 GB. En codecs con
    # keyframes espaciados (HEVC) puede quedarse a un par de fotogramas del
    # punto exacto: si la captura no es la esperada, repite con -Preciso.
    & ffmpeg -ss $Momento -i $Video -frames:v 1 -q:v 1 -y $Salida
}

if ($LASTEXITCODE -ne 0) { throw "ffmpeg ha devuelto error al extraer la captura." }
Write-Host "Captura guardada: $Salida" -ForegroundColor Green
