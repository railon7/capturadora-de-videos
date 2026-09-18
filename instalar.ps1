<#
.SYNOPSIS
    Copia la skill, los scripts y las plantillas de este repo a un proyecto
    de destino, de una sola vez, en vez de la copia manual carpeta a
    carpeta. No copia conocimiento/ (es de este repo, no del proyecto) ni
    tests/ ni .github/.

.PARAMETER Proyecto
    Carpeta raíz del proyecto de destino. Se crea si no existe.

.PARAMETER CarpetaHerramientas
    Nombre de la subcarpeta donde van scripts/ y plantillas/ dentro del
    proyecto de destino. Por defecto "_herramientas/capturadora-de-videos",
    para no mezclarse con las herramientas propias del proyecto.

.EXAMPLE
    .\instalar.ps1 -Proyecto "C:\Proyectos\Cliente X"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Proyecto,

    [string]$CarpetaHerramientas = "_herramientas\capturadora-de-videos"
)

$ErrorActionPreference = 'Stop'
$raiz = $PSScriptRoot

New-Item -ItemType Directory -Force -Path $Proyecto | Out-Null

$destinoSkill = Join-Path $Proyecto ".claude\skills\video-a-manual"
$destinoHerramientas = Join-Path $Proyecto $CarpetaHerramientas

Write-Host "Instalando en: $Proyecto" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $destinoSkill | Out-Null
Copy-Item -Path (Join-Path $raiz ".claude\skills\video-a-manual\*") -Destination $destinoSkill -Recurse -Force
Write-Host "  Skill ......... $destinoSkill" -ForegroundColor Green

foreach ($sub in @("scripts", "plantillas")) {
    $destino = Join-Path $destinoHerramientas $sub
    New-Item -ItemType Directory -Force -Path $destino | Out-Null
    Copy-Item -Path (Join-Path $raiz "$sub\*") -Destination $destino -Recurse -Force
    Write-Host "  $sub ......... $destino" -ForegroundColor Green
}

Write-Host ""
Write-Host "Hecho. La skill referencia scripts/ y plantillas/ como rutas relativas" -ForegroundColor White
Write-Host "al propio repo: si el proyecto usa una ubicación distinta a" -ForegroundColor White
Write-Host "'$CarpetaHerramientas', ajusta las rutas dentro de SKILL.md." -ForegroundColor White
