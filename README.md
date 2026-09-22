# Curso de robótica

Curso propio para diseñar, modelar, simular y controlar un brazo robótico con Python, siguiendo *Fundamentos de Robótica* (Barrientos, Peñín, Balaguer y Aracil) y las reglas fijadas en [FILOSOFIA.md](FILOSOFIA.md).

El mapa completo de los 25 bloques (00–24), organizados en seis partes, está en [ESTRUCTURA.md](ESTRUCTURA.md).

## Estado

En desarrollo. Bloques publicados hasta ahora:

- [Bloque 00 — Cómo usar el curso y preparar el entorno](bloques/bloque_00_bienvenida_y_entorno.md)
- [Bloque 01 — Trigonometría y geometría del plano](bloques/bloque_01_trigonometria_geometria_plano.md)
- [Bloque 02 — Vectores](bloques/bloque_02_vectores.md)

## Empezar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python codigo/bloque_00/verificar_entorno.py
```

Luego se sigue el Bloque 00 en `bloques/bloque_00_bienvenida_y_entorno.md`.

## Exportar a PDF

```bash
./export_pdf.sh                 # cada bloque por separado + el libro completo
./export_pdf.sh bloque_02_vectores   # solo ese bloque
```

Genera los PDF en `pdf/` (carpeta ignorada por git; se recompila desde los `.md` cuando haga falta). Requiere Pandoc, TeX Live con LuaLaTeX, las fuentes DejaVu y Noto Color Emoji, y Graphviz (`dot`) para regenerar los esquemas de `recursos/`.

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `bloques/` | Un archivo Markdown por bloque (`bloque_NN_tema.md`). |
| `codigo/robotica/` | Librería propia del curso, construida bloque a bloque. |
| `codigo/bloque_NN/` | Scripts y laboratorios de cada bloque; cada uno corre solo. |
| `recursos/` | Esquemas e imágenes del curso (ver `recursos/README.md`). |
| `anexos/` | Glosario, notación, entorno, formulario, bibliografía, deducciones largas. |

## Licencia de contenido

Material de estudio personal. Ver [FILOSOFIA.md](FILOSOFIA.md) para las convenciones de escritura y [ESTRUCTURA.md](ESTRUCTURA.md) para la bibliografía completa.
