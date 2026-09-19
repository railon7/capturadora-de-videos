<#
.SYNOPSIS
    Copia la skill, los scripts, las plantillas y la metodología de este
    repo a un proyecto de destino, de una sola vez, en vez de la copia
    manual carpeta a carpeta. Reescribe las rutas dentro de la skill
    copiada para que apunten a donde quedan las herramientas en el
    proyecto de destino, así los comandos de SKILL.md funcionan tal cual
    sin editar nada a mano. No copia conocimiento/ (es de este repo, no
    del proyecto) ni tests/ ni .github/.

.PARAMETER Proyecto
    Carpeta raíz del proyecto de destino. Se crea si no existe.

.PARAMETER CarpetaHerramientas
    Ruta (relativa a la raíz del proyecto) donde van scripts/, plantillas/
    y metodologia/ dentro del proyecto de destino. Por defecto
    "_herramientas/capturadora-de-videos", para no mezclarse con las
    herramientas propias del proyecto. Usa siempre barra normal (/),
    aunque el destino esté en Windows.

.EXAMPLE
    .\instalar.ps1 -Proyecto "C:\Proyectos\Cliente X"

.EXAMPLE
    .\instalar.ps1 -Proyecto "C:\Proyectos\Cliente X" -CarpetaHerramientas "herramientas/video"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Proyecto,

    [string]$CarpetaHerramientas = "_herramientas/capturadora-de-videos"
)

$ErrorActionPreference = 'Stop'
$raiz = $PSScriptRoot
$prefijo = $CarpetaHerramientas.Trim('/').Replace('\', '/')

New-Item -ItemType Directory -Force -Path $Proyecto | Out-Null

$destinoSkill = Join-Path $Proyecto ".claude\skills\video-a-manual"
$destinoHerramientas = Join-Path $Proyecto ($prefijo -replace '/', '\')

Write-Host "Instalando en: $Proyecto" -ForegroundColor Cyan

# --------------------------------------------------------- scripts, plantillas, metodologia
foreach ($sub in @("scripts", "plantillas", "metodologia")) {
    $destino = Join-Path $destinoHerramientas $sub
    New-Item -ItemType Directory -Force -Path $destino | Out-Null
    Copy-Item -Path (Join-Path $raiz "$sub\*") -Destination $destino -Recurse -Force
    Write-Host "  $sub ......... $destino" -ForegroundColor Green
}

# ------------------------------------------------------------------------------- skill
New-Item -ItemType Directory -Force -Path $destinoSkill | Out-Null
Copy-Item -Path (Join-Path $raiz ".claude\skills\video-a-manual\*") -Destination $destinoSkill -Recurse -Force

# Las rutas dentro de SKILL.md (scripts/..., plantillas/..., metodologia/...) están
# escritas para ejecutarse desde la raíz de ESTE repo. Se reescriben para que
# apunten a $prefijo dentro del proyecto de destino, y así funcionan tal cual.
$rutaSkillMd = Join-Path $destinoSkill "SKILL.md"
$contenido = Get-Content -LiteralPath $rutaSkillMd -Raw
foreach ($carpeta in @("scripts", "plantillas", "metodologia")) {
    $contenido = $contenido -replace "(?<![\w/])$carpeta/", "$prefijo/$carpeta/"
}
Set-Content -LiteralPath $rutaSkillMd -Value $contenido -NoNewline -Encoding UTF8
Write-Host "  Skill ......... $destinoSkill (rutas reescritas a $prefijo/)" -ForegroundColor Green

Write-Host ""
Write-Host "Hecho. Los comandos de SKILL.md ya apuntan a $prefijo/ dentro" -ForegroundColor White
Write-Host "de este proyecto — se ejecutan tal cual, sin ajustar nada a mano." -ForegroundColor White
