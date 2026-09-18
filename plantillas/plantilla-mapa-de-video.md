# Mapa del vídeo — plantilla

Copia esta plantilla como `Mapa del video — bloques y pantallas.md` dentro de
la carpeta `Analisis/` de cada vídeo procesado. Es el guion del vídeo,
reconstruido de su transcripción íntegra, **en el orden en que ocurre**.

La columna `t` se rellena en cuanto haya capturas: sirve para saltar al
momento exacto y sacar la pantalla en calidad final con
`extraer-captura-puntual.ps1`.

**Cómo usarlo con las hojas de contacto.** Cada hoja cubre `intervalo × 20`
segundos de vídeo (con el intervalo por defecto de 20 s, son 6 min 40 s por
hoja). La secuencia de bloques de abajo es el guion: se recorre la hoja 01
buscando el bloque 2, la 02 el bloque 5, etc. En cuanto se anota el `t` de
tres o cuatro bloques, el resto se sitúa solo.

Para saber a qué momento corresponde una miniatura de una hoja:

```
índice = (nº de hoja − 1) × 20 + posición
segundo = (índice − 1) × intervalo
```

---

## Acto 1 · <nombre del bloque grande>

| # | Bloque | Señal para localizarlo | Pantalla | Destino | t |
|---|---|---|---|---|---|
| 1 | <qué pasa en este bloque> | *"<fragmento textual literal que se oye, para buscarlo en la transcripción>"* | <qué se ve en pantalla, o — si no se comparte pantalla> | <a qué documento alimenta: un manual, una decisión, nada> | |
| 2 | | | | | |

## Acto 2 · <siguiente bloque grande>

| # | Bloque | Señal para localizarlo | Pantalla | Destino | t |
|---|---|---|---|---|---|
| | | | | | |

---

## Pantallas que NO están en el vídeo y hacen falta igual

Lo que un manual necesita pero el vídeo no mostró — se pide aparte o se saca
de la instalación real cuando esté disponible.

- <pantalla o dato pendiente>

---

## Cómo se construye este mapa

1. **Una pasada completa de la transcripción íntegra**, de principio a fin,
   sin parar a mirar pantallas todavía. El objetivo de esta pasada es
   trocear el vídeo en bloques con sentido propio (un tema, una pantalla,
   una decisión) y agruparlos en actos.
2. **Para cada bloque**, anota una frase textual que se pueda buscar
   literalmente — no un resumen. Un resumen no permite encontrar el
   fragmento después; una cita sí.
3. **No adivines el `t`.** Se rellena después, mirando las hojas de
   contacto o el índice, nunca de memoria ni por proporción estimada.
4. **Marca el destino de cada bloque** en cuanto se sepa: a qué manual, a
   qué decisión, o si no alimenta nada y es solo contexto.
