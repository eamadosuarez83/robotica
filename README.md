# Curso de robótica

Curso propio para diseñar, modelar, simular y controlar un brazo robótico con Python, siguiendo *Fundamentos de Robótica* (Barrientos, Peñín, Balaguer y Aracil) y las reglas fijadas en [FILOSOFIA.md](FILOSOFIA.md).

El mapa completo de los 25 bloques (00–24), organizados en seis partes, está en [ESTRUCTURA.md](ESTRUCTURA.md).

## Proyecto hermano

Desde el Bloque 07 en adelante, el curso se apoya en
[`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores):
un port a Python, ya probado contra MATLAB y con pytest, de un curso universitario con
brazos de acrílico reales y modelos de robots industriales (ABB, KUKA). Qué se porta,
de dónde y en qué bloque está en
[docs/integracion_manipuladores.md](docs/integracion_manipuladores.md). Los Bloques
00–06 (fundamentos matemáticos) son independientes de esa integración.

## Estado

En desarrollo. Bloques publicados hasta ahora:

- [Bloque 00 — Cómo usar el curso y preparar el entorno](bloques/bloque_00_bienvenida_y_entorno.md)
- [Bloque 01 — Trigonometría y geometría del plano](bloques/bloque_01_trigonometria_geometria_plano.md)
- [Bloque 02 — Vectores](bloques/bloque_02_vectores.md)
- [Bloque 03 — Matrices como transformaciones](bloques/bloque_03_matrices_transformaciones.md)
- [Bloque 04 — Cálculo para cosas que se mueven](bloques/bloque_04_calculo_para_cosas_que_se_mueven.md)
- [Bloque 05 — Ecuaciones diferenciales y simulación](bloques/bloque_05_ecuaciones_diferenciales_y_simulacion.md)
- [Bloque 06 — Mecánica del sólido rígido](bloques/bloque_06_mecanica_del_solido_rigido.md) (cierra la Parte I)
- [Bloque 07 — Morfología del robot](bloques/bloque_07_morfologia_del_robot.md) (abre la Parte II)
- [Bloque 08 — Localización espacial I: posición y rotación](bloques/bloque_08_localizacion_espacial_i_posicion_y_rotacion.md)
- [Bloque 09 — Localización espacial II: otras formas de decir la orientación](bloques/bloque_09_localizacion_espacial_ii_orientacion.md)
- [Bloque 10 — Matrices de transformación homogénea](bloques/bloque_10_matrices_transformacion_homogenea.md) (cierra la localización espacial)
- [Bloque 11 — Cinemática directa y Denavit-Hartenberg](bloques/bloque_11_cinematica_directa_y_denavit_hartenberg.md) (abre la Parte III)
- [Bloque 12 — Cinemática inversa](bloques/bloque_12_cinematica_inversa.md)
- [Bloque 13 — Cinemática diferencial: la matriz Jacobiana](bloques/bloque_13_cinematica_diferencial_jacobiana.md) (cierra la Parte III)
- [Bloque 14 — Dinámica por Lagrange-Euler](bloques/bloque_14_dinamica_lagrange_euler.md) (abre la Parte IV)
- [Bloque 15 — Dinámica por Newton-Euler y simulación](bloques/bloque_15_dinamica_newton_euler_y_simulacion.md)
- [Bloque 16 — Actuadores, transmisiones y dimensionamiento](bloques/bloque_16_actuadores_transmisiones_dimensionamiento.md) (cierra la Parte IV)
- [Bloque 17 — Sistemas y realimentación](bloques/bloque_17_sistemas_y_realimentacion.md) (abre la Parte V)
- [Bloque 18 — Control PID de una articulación](bloques/bloque_18_control_pid_de_una_articulacion.md)

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
