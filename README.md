# AAJC26 Cairo

Web para seguir en el móvil el **All Africa Junior Championships 2026 (Individual)**, del 30 de septiembre al 3 de octubre en El Cairo: partidos, pistas, jugadores, países, cuadros y estadísticas. Los datos llegan en directo del mismo feed de la BWF que usa bwfbadminton.com.

Basada en [ESC26](https://github.com/cvpcvp/esc26) de cvpcvp, con su permiso.

## Usarla para otro torneo

Todo lo que depende del torneo está en el bloque `CFG`, al principio del `<script>` de `index.html`:

| Campo | Qué poner |
|---|---|
| `name`, `subtitle`, `event`, `city` | Textos de la cabecera, del texto al compartir y del pie |
| `tmtId` | El número del enlace de bwfbadminton.com: `bwfbadminton.com/tournament/`**`5796`**`/...` |
| `code` | El identificador largo del enlace de tournamentsoftware: `bwf.tournamentsoftware.com/tournament/`**`78E3A435-...`** |
| `days` | Los días de competición, en formato `'AAAA-MM-DD'` |
| `tz` | Zona horaria local, p. ej. `'Africa/Cairo'` o `'Europe/Madrid'` |
| `venues` | Pabellones y sus pistas. Si solo hay uno, se le añaden solas las pistas que vengan en el feed |
| `ages` | `'U'` para torneos junior (U15, U17, U19) y `'+'` para veteranos (35+, 40+...) |
| `storage`, `counter` | Pon un nombre distinto para cada torneo |

## Publicar

En GitHub ve a Settings → Pages → Source: *Deploy from a branch* → `main` / `(root)`. La web queda en `https://javiigaar.github.io/torneo-bwf/`.

---

# Torneos nacionales (badminton.es) — carpeta `fesba/`

Versión para torneos de [badminton.es](https://www.badminton.es). Ahora mismo está configurada para el **Castilla y León TOP TTR Valladolid Absoluto-Sénior** (3 de octubre de 2026).

badminton.es no tiene una API de datos y el navegador no puede leerla directamente, así que funciona en dos partes:

1. **`fesba/scrape.py`** lee de badminton.es la vista de partidos de cada día (hora, cuadro, ronda, pista, duración, marcador, walkover o retirada y el club de cada jugador), la lista de clubes y la de cuadros. Son 3 peticiones más 1 por día, con 3 segundos entre cada una, y lo guarda todo en `fesba/data.json`.
2. **La Action `.github/workflows/fesba.yml`** ejecuta el script cada 10 minutos (de 08:00 a 23:59, hora de Madrid) y hace commit de `data.json` si ha cambiado. Fuera de los días del torneo no hace nada. Desde la pestaña *Actions* → *badminton.es data* → *Run workflow* se puede lanzar a mano.

La web queda en `https://javiigaar.github.io/torneo-bwf/fesba/`.

## Cambiar de torneo

Solo hay que editar `fesba/config.json`:

```json
{ "id": "BD151966-B76B-4B1B-A591-E8DBDFB16D76", "days": ["2026-10-03"], "tz": "Europe/Madrid" }
```

- `id`: el identificador del enlace del torneo, `badminton.es/sport/tournament?id=`**`BD151966-...`**
- `days`: los días del torneo.

Luego conviene cambiar también los textos del bloque `CFG` de `fesba/index.html` (`name`, `subtitle`, `event`, `city`, `tid` y el pabellón en `venues`) y lanzar la Action a mano una vez.

Diferencias con la versión BWF: hay clubes en vez de países, niveles (Absoluto, A1, B2…) en vez de edades, los cuadros se abren en badminton.es y no está la estadística de "puntos seguidos". Mientras un partido tiene pista asignada y no tiene resultado, sale como "en pista".
