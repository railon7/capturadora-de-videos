<#
.SYNOPSIS
    Saca un único fotograma de un vídeo, en máxima calidad, en el momento
    exacto que ya se ha localizado con las hojas de contacto o el índice.

.PARAMETER Video
    Ruta al vídeo de origen.

.PARAMETER Momento
    Momento del vídeo en formato HH:MM:SS (o MM:SS).

.PARAMETER Salida
    Ruta del fichero de imagen a generar (.png o .jpg). Las carpetas
    intermedias se crean si no existen.

.EXAMPLE
    .\extraer-captura-puntual.ps1 -Video "C:\videos\demo.mp4" -Momento "00:45:20" -Salida "C:\proyecto\Capturas\Seleccionadas\pantalla-01.png"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Video,

    [Parameter(Mandatory = $true)]
    [string]$Momento,

    [Parameter(Mandatory = $true)]
    [string]$Salida
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

# -ss antes de -i: ffmpeg salta directamente al punto en lugar de decodificar
# desde el principio, así que tarda igual con un vídeo de 500 MB que de 8 GB.
& ffmpeg -ss $Momento -i $Video -frames:v 1 -q:v 1 -y $Salida

if ($LASTEXITCODE -ne 0) { throw "ffmpeg ha devuelto error al extraer la captura." }
Write-Host "Captura guardada: $Salida" -ForegroundColor Green
