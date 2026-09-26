# Bloque 24 — Proyecto integrador

> Diseñar, modelar, simular, construir y controlar un brazo de 4 GDL que recoge huevos a la salida de una clasificadora y los acomoda en una cubeta de 30.

Este bloque no sigue la plantilla de tema-por-tema del resto del curso (ver `bloques/_plantilla_bloque.md`): es el cierre, y su estructura son los ocho entregables que fija ESTRUCTURA.md. Cada uno reúne herramientas de varios bloques anteriores sobre un solo robot concreto, en vez de introducir un concepto nuevo.

## Por qué este robot

`ESTRUCTURA.md` dejaba pendiente, desde que se documentó la integración con
[`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores)
(ver [docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md)), la decisión de si
este proyecto se diseña desde cero o se apoya en uno de sus brazos de acrílico **ya construidos**:
`tercer_corte_3gdl` (3 GDL) o `prototipo_4gdl` (4 GDL, con pinza). El proyecto pide explícitamente
4 GDL — `prototipo_4gdl` encaja exactamente, sin ajustar nada: es un brazo real, con tabla DH
documentada (`docs/robots.md` de `robotica-manipuladores`) y con pinza, que en su repositorio de
origen solo tenía cinemática directa implementada (`etiquetas=("directa","acrilico")`, sin
inversa ni dinámica). Este bloque completa exactamente lo que faltaba: inversa, Jacobiana,
dinámica, dimensionamiento, CAD/URDF, trayectorias, control y la tarea completa — todo lo que los
Bloques 00-23 construyeron, aplicado a un brazo real en vez de a un caso didáctico.

Tabla DH de `prototipo_4gdl` (`docs/robots.md`, cm convertidos a m):

| Articulación | θ (offset) | d | a | α | Tipo |
|---|---|---|---|---|---|
| 1 | π | 0,03 | 0 | −π/2 | rotacional |
| 2 | −π/2 | 0 | 0,13 | π | rotacional |
| 3 | π/2 | 0 | 0,17 | π/2 | rotacional |
| 4 | 0 | 0 | 0,02 | 0 | rotacional |

`codigo/bloque_24/modelo_proyecto.py` fija esta tabla y unas masas estimadas por eslabón para
dimensionamiento y dinámica (Entregables 3-5); es el módulo que comparten todos los scripts de
este bloque.

## Entregable 1 — Especificación

Los cuatro requisitos del Bloque 21 (Tema 21.1), fijados para esta tarea concreta:

| Requisito | Valor | Justificación |
|---|---|---|
| Alcance | ≈ 0,32 m ($L_2+L_3+L_4$) | Cubre la salida de la clasificadora y una cubeta cercana; el alcance real de `prototipo_4gdl` (Bloque 07, Tema 7.1). |
| Carga | 70 g (huevo de 60 g + 15 % de margen) | Un huevo grande pesa hasta ~70 g; el margen absorbe variabilidad entre huevos (Bloque 16, Tema 16.5). |
| Tiempo de ciclo | < 3 s por huevo (≥ 1200 huevos/hora) | Consistente con clasificadoras de banda de velocidad moderada; verificado en el Entregable 5. |
| Precisión | ± 5 mm en la cubeta | Suficiente para no golpear el huevo contra el borde de una cubeta de 30 (Bloque 07, Tema 7.8: no se necesita repetibilidad de robot industrial). |

## Entregable 2 — Tabla DH, cinemática directa, inversa y Jacobiana

`codigo/bloque_24/cinematica_y_dinamica.py` (función `parte_cinematica`) evalúa la directa en
$\vec q=\vec 0$, genera 8 posturas aleatorias, calcula su pose con `robotica.dh.directa` (Bloque
11), resuelve la inversa con `robotica.inversa.inversa_numerica` (Bloque 12) — este brazo, a
diferencia del 3R plano de los Bloques 12/19/23, no tiene una inversa geométrica cerrada simple
por su geometría espacial, así que se usa el método numérico general, exactamente para lo que se
diseñó — y **cierra el ciclo**: aplica `directa` a la solución encontrada y verifica que reproduce
el objetivo.

**Resultado** (8 posturas aleatorias, semilla fija): las 8 convergieron, con error de cierre de
ciclo de **0,0000 mm** en las 8 (el numérico converge hasta la tolerancia pedida, $10^{-8}$), y
manipulabilidad (Bloque 13, Tema 13.6) entre 0,0006 y 0,0058 — ningún valor cercano a cero, así
que ninguna de las posturas de prueba está cerca de una singularidad.

## Entregable 3 — Modelo dinámico y dimensionamiento de motores

`codigo/bloque_24/cinematica_y_dinamica.py` (función `parte_dinamica`) deduce el modelo con
Lagrange (Bloque 14), con masas puntuales en cada eslabón (la misma simplificación del Bloque 14
para el 2R, aplicada aquí a la geometría 3D real de `prototipo_4gdl` en vez de un caso plano) y
verifica $M(\vec q)$ simétrica y definida positiva (Bloque 14, Tema 14.6) en 30 posturas
aleatorias.

**Resultado:** **941,1 s** (~15,7 min) — comparado con ~1,6 s (2 eslabones) y ~17 s (3 eslabones)
del Bloque 15 (Tema 15.2): el mismo patrón de crecimiento del costo de *construcción* simbólica,
ahora con un cuarto dato real, para un brazo espacial (no solo planar). $M$ resultó simétrica y
definida positiva en las 30 posturas — el modelo es físicamente consistente. El par de gravedad
máximo observado en 200 posturas aleatorias fue de **0,390 N·m** — el punto de partida para elegir
motor y reductor siguiendo el procedimiento del Bloque 16 (Tema 16.6): con el margen de seguridad
habitual (1,3-1,5×, Bloque 16 Tema 16.5) y la carga de 70 g del Entregable 1, un servo de
aficionado de gama media (Bloque 16, Tema 16.3), como los que ya usa `prototipo_4gdl` en
`robotica-manipuladores`, alcanza con margen.

**Nota de verificación:** la primera corrida de este cálculo, con el `separar_gravedad_y_coriolis`
de `robotica.dinamica` tal como quedó en el Bloque 14, falló al evaluar $G(\vec q)$: el vector
devuelto conservaba un término simbólico de $\ddot q_1$ sin sustituir. La causa: esa función
calculaba el resto restando $M(\vec q)\ddot{\vec q}$ (ya obtenida por derivación, Bloque 14 Tema
14.4) de la ecuación completa, y solo aplicaba `sp.expand()` al resultado; para el 2R plano del
Bloque 14 eso bastaba, pero para la geometría espacial de `prototipo_4gdl` el coeficiente real de
$\ddot q_1$ y la entrada correspondiente de $M$ llegan en formas trigonométricas distintas
($\sin^2(q_2)$ frente a $\cos(2q_2)$, iguales por identidad pero no textualmente) — una resta que
`expand()` solo no cancela, y ni siquiera `sp.simplify()` sobre esa resta lo garantiza en general.
La corrección: en vez de restar, evaluar la ecuación directamente en $\ddot{\vec q}=\vec 0$
(`ecuaciones[i].subs({qddot_k: 0 ...})`), exacto por construcción porque cada ecuación es afín en
$\ddot{\vec q}$ (Bloque 14, Tema 14.4) — sin depender de que dos expresiones equivalentes coincidan
como texto. Reejecutar los Bloques 14, 15 y 20 con la corrección reprodujo exactamente los mismos
resultados ya publicados en esos bloques (el 2R plano nunca disparó el caso), confirmando que el
error solo afectaba geometrías donde $\theta$ offset y $\alpha$ son simultáneamente no nulos — el
mismo tipo de caso límite que ya expuso el Entregable 4.

## Entregable 4 — Modelo CAD paramétrico y URDF

`codigo/bloque_24/generar_urdf_proyecto.py` construye cada eslabón como un prisma con build123d
(Bloque 21, Tema 21.2), parametrizado por las longitudes de la tabla DH, calcula sus propiedades
de masa (Tema 21.3) y genera el URDF completo con la reindexación DH-estándar→URDF del Bloque 21
(Tema 21.4) — generalizada aquí: `prototipo_4gdl` es el primer robot del curso con articulaciones
donde el offset de $\theta$ **y** $\alpha$ del eslabón anterior son simultáneamente distintos de
cero, un caso que `curso_3gdl` (Bloque 21) no tenía y que expuso un error real en la primera
versión de la reindexación (ver la nota de verificación más abajo).

`codigo/bloque_24/verificar_pybullet_proyecto.py` carga el URDF en PyBullet (Bloque 21, Tema
21.5) y compara contra `robotica.dh.directa` en 15 posturas aleatorias: **error máximo
2,74×10⁻⁷ m** — coinciden hasta la precisión numérica esperable.

**Nota de verificación:** la primera versión de la reindexación (copiada tal cual del Bloque 21)
daba un error de 0,445 m — enorme. La causa: URDF combina la rotación fija de un joint con la
convención RPY $R=R_z(yaw)R_y(pitch)R_x(roll)$, y `curso_3gdl` (Bloque 21) nunca expuso el problema
porque ahí todos los offsets de $\theta$ eran cero. Aquí, con offset de $\theta$ y $\alpha$ ambos
no nulos, la asignación directa (roll=$\alpha_{prev}$, yaw=$\theta_{offset}$) ya no reproduce la
rotación real $R_x(\alpha_{prev})R_z(\theta_{offset})$ del Bloque 11. La corrección: construir esa
matriz con `robotica.rotaciones` y convertirla a RPY de verdad con `robotica.orientacion.mat2rpy`
(Bloque 09) — el mismo tipo de conversión entre representaciones de orientación que ese bloque ya
enseñó, aplicado aquí a un problema real de exportación a URDF.

## Entregable 5 — Generador de trayectorias y controlador, validados en simulación

`codigo/bloque_24/tarea_proyecto.py` resuelve la cinemática inversa de cinco puntos de enseñanza
(Bloque 23, Tema 23.2) una sola vez —`reposo`, `aprox_recoger`, `recoger`, `aprox_depositar`,
`depositar`— y genera, entre puntos consecutivos, una trayectoria articular sincronizada con
perfil trapezoidal por articulación (Bloque 19, Tema 19.3; Bloque 23, Tema 23.5).

**Resultado:** los cinco puntos convergen y cierran el ciclo con error menor a $10^{-4}$ m; la
duración nominal del ciclo completo (suma de los seis tramos: reposo→aproximar→recoger→levantar→
trasladar→dejar→regresar) es de **6,69 s** — por encima de la especificación de 3 s del Entregable
1. Esto es exactamente el tipo de resultado que un dimensionamiento inicial debe exponer: con las
velocidades y aceleraciones máximas conservadoras usadas aquí (60°/s, 120°/s² por articulación),
no se cumple el tiempo de ciclo pedido, y hace falta revisar el Bloque 16 (motores con más
velocidad disponible) o el Bloque 23 (Tema 23.5: eliminar tramos innecesarios) antes de dar el
diseño por bueno — la especificación no es un formalismo, es una prueba que el diseño falla aquí y
debe iterarse, tal como advierte el Bloque 21 (Tema 21.1) sobre los compromisos de diseño.

Para el controlador: el Bloque 20 (par calculado) aplica directamente sobre el modelo dinámico del
Entregable 3, exactamente como se validó para el 2R plano en ese bloque (error de seguimiento
~0,01°, robusto en movimientos rápidos) — no se repite esa simulación completa aquí (tomaría
varios minutos más de cómputo simbólico, Entregable 3) porque el mecanismo ya quedó verificado a
fondo en el Bloque 20; este bloque reutiliza esa verificación en vez de duplicarla.

## Entregable 6 — Brazo físico calibrado con error de posición medido

Este entregable requiere un brazo físico real, que no existe en esta sesión de trabajo (un
ambiente de desarrollo de software, sin hardware conectado) — a diferencia de los otros siete,
**no se puede completar aquí**, y decirlo explícitamente es más honesto que simularlo como si
fuera equivalente. Lo que sí se deja listo, para cuando exista el brazo físico (por ejemplo,
construyendo `prototipo_4gdl` siguiendo sus propias medidas, ya reales y ya verificadas en el
Entregable 2):

1. El procedimiento completo de calibración del Bloque 22 (Tema 22.3: ceros, sentido de giro,
   relación señal-ángulo) aplica sin cambios.
2. `codigo/bloque_22/calibracion.py` ya está escrito y verificado en simulación (offset recuperado
   con error $<10^{-6}$°); solo hace falta reemplazar `medir_articulacion` (que ahora simula la
   lectura) por la lectura real de un sensor (Bloque 22, Tema 22.4).
3. La "rejilla de puntos" del laboratorio final del Bloque 22 — comandar una cuadrícula de
   posiciones conocidas y medir el error real — es el procedimiento exacto para obtener el "error
   de posición medido" que pide este entregable.

## Entregable 7 — Programa de la tarea como máquina de estados

`codigo/bloque_24/tarea_proyecto.py` (clase `TareaProyecto`) implementa la misma máquina de
estados del Bloque 23 (`ESPERANDO → APROXIMAR_RECOGER → RECOGER → LEVANTAR → TRASLADAR → DEJAR →
REGRESAR → TERMINADO`, con transiciones a `ERROR`), con registro de eventos, sobre los puntos de
enseñanza del Entregable 5.

**Resultado:** un ciclo sin errores simulados completa las nueve transiciones esperadas; sobre 200
ciclos con probabilidad de error 3 % (objeto no encontrado) y 5 % (fallo de agarre, Bloque 23 Tema
23.4), **183 de 200 terminan con éxito** — consistente con $200\times(1-0,03)\times(1-0,05)\approx
184$, la estimación esperada del Bloque 23 (Tema 23.4, Ejercicio B1) aplicada aquí.

## Entregable 8 — Manual de mantenimiento y diagnóstico

Siguiendo la **cadena de diagnóstico** de FILOSOFIA.md (sección 4): ante un error de posición, se
revisa de abajo hacia arriba. Esta tabla reúne los síntomas de "fallas típicas" ya documentados a
lo largo del curso, organizados por esa misma cadena:

| # Cadena | Pregunta | Síntoma típico | Causa probable | Cómo verificar | Bloque |
|---|---|---|---|---|---|
| 1 | ¿Unidades? | El brazo "salta" a una posición sin relación con lo pedido | Grados donde se esperaban radianes, o viceversa | Imprimir el ángulo: ¿del orden de 0-6,28, o de 0-360? | 01 |
| 1 | ¿Unidades? | Posición errática tras invertir el orden de dos rotaciones | Premultiplicar/posmultiplicar confundidos (ejes fijos vs. móviles) | Probar ambos órdenes y comparar | 08 |
| 2 | ¿Marcos de referencia? | Dos partes del sistema dan coordenadas incompatibles del mismo punto | Marcos de referencia distintos sin convertir entre ellos | Preguntar "¿respecto a qué marco?" para cada número | 08, 10 |
| 2 | ¿Marcos de referencia? | Un marco "invertido" sale disparado a una posición absurda | Se invirtió una transformación homogénea transponiéndola en vez de $R^T,-R^T\vec p$ | Comparar $T\cdot T^{-1}$ contra la identidad | 10 |
| 3 | ¿Parámetros DH? | La cinemática directa no coincide con medidas físicas del brazo real | Tabla DH estándar evaluada con la fórmula modificada (o viceversa), o un $\alpha$ con el signo cambiado | Verificar en $\vec q=\vec 0$ contra una postura de referencia conocida | 11 |
| 4 | ¿Rama de la inversa? | El brazo llega "al lado opuesto" del punto pedido | Se tomó la solución codo arriba/abajo equivocada, o sin comparar contra la postura actual | Comparar todas las soluciones contra la postura actual (Bloque 12, Tema 12.6) | 12 |
| 4 | ¿Rama de la inversa? | Un signo de calibración invertido en una articulación | Ver Bloque 22, Tema 22.6: error de 10-20 cm con un solo signo mal | Calibrar signo comandando un cambio pequeño y conocido | 22 |
| 5 | ¿Singularidad? | Velocidades articulares que se disparan cerca de cierta postura | El determinante de la Jacobiana (o la manipulabilidad) se acerca a cero | Graficar la manipulabilidad a lo largo de la trayectoria | 13, 19 |
| 6 | ¿Dinámica? | El brazo real no llega, oscila, o el motor se calienta | Masas/inercias del modelo no coinciden con las reales, o par insuficiente | Comparar el par calculado (Bloque 15) contra el par disponible del motor (Bloque 16) | 14-16 |
| 6 | ¿Dinámica? | Simulación que "explota" (crece sin control) | Paso de integración demasiado grande, o parámetros físicos imposibles (masa negativa) | Reducir el paso; verificar que $M$ sea definida positiva | 05, 15 |
| 6 | ¿Dinámica? | $G(\vec q)$ o $C(\vec q,\dot{\vec q})$ conservan un símbolo de $\ddot{\vec q}$ sin sustituir tras `lambdify` | Se separó el resto restando $M\ddot{\vec q}$ en vez de evaluar directamente en $\ddot{\vec q}=\vec 0$; dos formas trigonométricas equivalentes no cancelan por texto | Revisar `.free_symbols` de $G$ y $C$ antes de `lambdify`: no debe quedar ningún $\ddot q_i$ | 14, 24 |
| 7 | ¿Control? | Sobrepaso grande y lento de corregir tras un escalón grande | Windup de la integral sin anti-windup, actuador saturado | Comparar la respuesta con y sin anti-windup | 18 |
| 7 | ¿Control? | Oscilación que antes no existía, tras mover el control a un microcontrolador real | Periodo de muestreo demasiado grande para la dinámica del lazo | Reducir $T_s$ y comparar | 18 |
| — | ¿Comunicación? | Movimientos erráticos ocasionales sin relación con lo pedido | Tramas corrompidas ejecutándose sin verificación | Confirmar que el protocolo tiene y usa checksum | 22 |
| — | ¿Tarea? | La tarea se "cuelga" tras un error, sin que nadie se entere | Falta manejo explícito de errores en la máquina de estados | Revisar si cada fallo posible tiene una transición a `ERROR` | 23 |

Cada fila de esta tabla es, literalmente, una fila de una tabla de "fallas típicas y diagnóstico"
ya escrita en su bloque de origen — el manual de mantenimiento de un brazo real no es más que
reunir, en un solo lugar, la disciplina de diagnóstico que el curso practicó bloque a bloque.

## Cierre

Con este bloque terminan los 25 (00-24) del curso. Lo que empezó en el Bloque 00 preguntando "¿qué
sé y qué no sé?" termina en un brazo de 4 GDL —real, no inventado— con su cinemática, dinámica,
CAD/URDF, trayectorias, control y programación de tareas, todo verificado contra al menos una
implementación independiente (`roboticstoolbox`, PyBullet, o cerrando el propio ciclo
directa→inversa→directa) antes de darlo por bueno. Lo único que falta —el brazo físico real,
Entregable 6— es, apropiadamente, lo único que este curso no puede completar sin salir de una
sesión de software hacia un taller.
