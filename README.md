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
