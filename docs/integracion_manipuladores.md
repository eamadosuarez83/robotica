# Integración con `robotica-manipuladores`

Análisis de cómo el curso (este repositorio) se apoya en
[`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores),
el port a Python de un curso universitario de robótica de manipuladores: brazos de
acrílico reales con servos y modelos de robots industriales (ABB IRB 6600, KUKA KR6),
con cinemática directa e inversa ya deducida, probada contra MATLAB y verificada con
pytest en cientos de poses aleatorias.

Este documento fija **qué se reutiliza, de dónde, y en qué bloque**, para no perder el
análisis y no tener que rehacerlo cada vez que se retome el curso.

## Qué NO cambia

Las Partes I (Bloques 00–06) son fundamentos matemáticos que `robotica-manipuladores`
da por sabidos — ese repositorio empieza directamente en transformaciones homogéneas,
asumiendo álgebra lineal y cálculo ya dominados. **Los bloques 00 a 04 ya escritos no
se modifican por esta integración.** El tensor de inercia (Bloque 06) es la única
excepción parcial: el notebook `09_tensor_de_inercia.ipynb` de manipuladores sirve como
ejercicio adicional verificado con SymPy, pero no reemplaza el desarrollo propio del
bloque.

La integración empieza a operar recién en el **Bloque 07**.

## Qué SÍ hay en `robotica-manipuladores` y dónde encaja

| Bloque | Módulo/notebook de manipuladores | Qué se porta | Qué falta (se escribe original) |
|---|---|---|---|
| 07 — Morfología | `docs/robots.md`, `docs/especificaciones.md` | 9 robots reales (acrílico, ABB, KUKA) como ejemplos de cada configuración, con medidas de datasheet | — |
| 08 — Rotación | `transformaciones.py` (`rotx/roty/rotz`) | casi 1:1 → `codigo/robotica/rotaciones.py` | — |
| 09 — Orientación | `transformaciones.py` (`rpy2mat/mat2rpy`, `zxz2mat/mat2zxz`) | RPY y Euler ZXZ → `codigo/robotica/orientacion.py` | eje-ángulo (Rodrigues) y cuaterniones: no están en manipuladores, se escriben originales |
| 10 — Homogéneas | `transformaciones.py` (`transl`, `es_homogenea`) | casi 1:1 → `codigo/robotica/homogeneas.py` | — |
| 11 — DH y cinemática directa | `dh.py` (`matriz_dh`, `directa`, `marcos`, `directa_simbolica`), `robots.py` (catálogo) | casi 1:1 → `codigo/robotica/dh.py`, `codigo/robotica/brazo.py`; catálogo de robots reales en vez de inventar uno | — |
| 12 — Cinemática inversa | `inversa/geometrica.py`, `inversa/numerica.py`, `inversa/desacoplo.py` | el más fuerte: geométrica (codo arriba/abajo) + numérica (`fsolve`) + desacoplo (muñeca esférica) para 5 robots reales → `codigo/robotica/inversa.py` | — |
| 13 — Jacobiana | nada | — | **original**: manipuladores no tiene cinemática diferencial |
| 14–16 — Dinámica | `09_tensor_de_inercia.ipynb` (solo tensor de inercia, va al Bloque 06) | — | **original**: Lagrange-Euler, Newton-Euler, dimensionamiento de actuadores |
| 17, 18, 20 — Control | nada | — | **original**: PID, control dinámico, par calculado |
| 19 — Trayectorias | `trayectorias.py` (`interpolador_lineal`, `interpolador_trapezoidal`, `perfil_trapezoidal`, `linea`, `circulo`, `polilinea`) | casi 1:1 → `codigo/robotica/trayectorias.py` | perfil en S (*jerk* limitado): no está, se escribe original |
| 21 — Diseño mecánico | — | — | **original**: build123d, URDF |
| 22 — Hardware | `matlab/extras/serial_arduino`, `matlab/extras/ArduinoIO` (sin portar a Python) | protocolo serie como referencia a adaptar, no código directo | Python + microcontrolador: original |
| 24 — Proyecto integrador | `robots.py`: `tercer_corte_3gdl`, `prototipo_4gdl` (brazos de acrílico **construidos**, no solo diseñados) | precedente de diseño fuerte; decidir en su momento si el proyecto del huevo se basa en uno de estos o se diseña aparte | — |

Módulo `visualizacion.py` de manipuladores (dibujo y animación 3D del brazo) amplía,
sin chocar con él, nuestro `codigo/robotica/graficar.py` (Bloque 03, solo 2D): se puede
portar como `codigo/robotica/visualizacion.py` desde el Bloque 08, cuando aparecen los
primeros marcos 3D.

## Cómo se porta (mecánica, no solo qué)

1. **Repos separados.** `robotica-manipuladores` mantiene su propia historia, tests y
   licencia en GitHub; no se fusiona. Este repo porta código puntual con atribución,
   como se haría con cualquier fuente externa.
2. **Bloque a bloque, no todo de una vez.** El código se adapta recién cuando se
   escribe el bloque correspondiente (ver tabla), no antes — evita mantener código sin
   bloque que lo explique.
3. **El andamiaje pedagógico de [FILOSOFIA.md](../FILOSOFIA.md) no se salta.** El código
   portado entra como la implementación ya verificada de la sección "3. En la vida
   real"; la sección "2. El mecanismo" se sigue deduciendo desde cero, paso a paso,
   como en los Bloques 00–04. Manipuladores es una fuente de código y de datos reales,
   no un atajo para saltarse la deducción.
4. **`docs/correcciones.md` de manipuladores como cantera de "fallas típicas".** Son
   bugs reales de código de estudiantes/profesor, no inventados — mejor material
   posible para esas tablas. Casos ya identificados para reutilizar:
   - Bloque 12: error #1 (tabla DH de la GUI inversa que no correspondía a la de la
     directa — el brazo dibujaba en otra posición) y error #9 (criterio de convergencia
     `fval <= Error` con `fval` vector, que acepta residuos negativos grandes, en vez de
     `norm(fval) <= Error`).
   - Bloque 19: error #5 (los interpoladores lineal y trapezoidal descartaban el último
     punto de cada tramo y no llegaban al destino).
   - Bloque 09: error #6 (`mat2zxz` no recibía la matriz como argumento; usaba `ax` en
     vez de `az`).
5. **Adoptar su disciplina de pruebas.** Desde el Bloque 11 en adelante, cada función
   nueva de `codigo/robotica/` se verifica con pytest: cinemática inversa comprobada
   contra la directa en cientos de poses aleatorias (`inversa(directa(q)) ≈ q`), igual
   que `python/tests/test_inversas.py` de manipuladores. Hasta el Bloque 04 no se había
   adoptado este hábito de forma sistemática (solo scripts de verificación manual); se
   corrige a partir de aquí.
6. **Atribución.** El código de manipuladores es MIT; su documentación, CC BY 4.0.
   Al portar una función se cita en el docstring el archivo de origen (por ejemplo,
   `Adaptado de robotica-manipuladores/python/robotica/dh.py`), igual que sus propios
   docstrings ya citan el `.m` original de MATLAB.

## Convenciones que ya coinciden (sin fricción)

Buena noticia: manipuladores usa exactamente las mismas convenciones de unidades que
[FILOSOFIA.md](../FILOSOFIA.md) — radianes en `directa` y en las rotaciones, grados
solo en las salidas de las inversas y en las funciones de dibujo. No hace falta
traducir nada al portar código.

## Decisión pendiente para más adelante

Cuando se llegue al Bloque 24 (proyecto integrador), decidir si el brazo recolector de
huevos se diseña sobre `tercer_corte_3gdl` o `prototipo_4gdl` (ya construidos y con
medidas reales) o se diseña aparte desde cero. No es una decisión que haga falta tomar
ahora.
