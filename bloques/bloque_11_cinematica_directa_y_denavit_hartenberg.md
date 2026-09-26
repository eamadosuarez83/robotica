# Bloque 11 — Cinemática directa y Denavit-Hartenberg

> **Problema que abre el bloque:** se conocen los ángulos de todos los motores. ¿Dónde está la pinza y hacia dónde apunta?
>
> **Necesitas antes:** Bloque 10. · **Lectura:** Barrientos, cap. 4 (cinemática directa); Spong, Hutchinson & Vidyasagar, *Robot Modeling and Control*, capítulo de cinemática directa.

Este bloque porta `dh.py` de [`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores)
(`matriz_dh`, `directa`, `marcos`, `directa_simbolica`) casi sin cambios — su convención de
radianes ya coincide con la de este curso — y usa su **catálogo de robots reales**
(`python/robotica/robots.py`) como ejemplos en vez de inventar tablas DH. Ver
[docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md).

## Tema 11.1 — Cinemática directa por geometría: por qué no escala

### 1. El problema

El Bloque 01 (Tema 1.4) calculó la posición de la punta de un brazo 2R a mano, razonando geometría directamente: $x=L_1\cos\theta_1+L_2\cos(\theta_1+\theta_2)$. Funciona perfecto para dos eslabones planos. Para seis eslabones en 3D, con orientación además de posición, la misma estrategia —razonar geométricamente caso por caso— se vuelve inviable: no hay una fórmula "a ojo" para un brazo antropomórfico de 6 GDL.

### 2. El mecanismo

Lo que sí escala es la idea del Bloque 10: encadenar transformaciones homogéneas, marco tras marco, desde la base hasta la pinza. El problema deja de ser "encontrar la geometría de este brazo en particular" y pasa a ser "encontrar, de forma sistemática y repetible, la transformación entre cada eslabón y el siguiente" — exactamente lo que la convención de Denavit-Hartenberg (Tema 11.2) resuelve de una vez para cualquier cadena cinemática abierta.

### 3. En la vida real

El Bloque 01 escribió $x,y$ a mano; este bloque escribe la misma cinemática del 2R como producto de dos matrices homogéneas $A_1A_2$ (Tema 11.4), y comprueba que da el mismo resultado — la garantía de que el método sistemático no es "otra cosa", es la generalización de lo ya conocido.

### 4. Limitaciones

Ninguna nueva.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Se intenta deducir a mano la cinemática de un brazo de más de 3 GDL y el álgebra se vuelve inmanejable | Se está usando el método geométrico del Bloque 01 fuera de su alcance | Contar los GDL: más de 2-3 en 3D ya es señal de usar DH | Usar la convención DH (Tema 11.2) en vez de razonar geometría caso por caso |

### 6. Dónde más aparece la idea

Cualquier sistematización que reemplaza "resolver cada caso a mano" por "aplicar el mismo procedimiento siempre": el propio Bloque 03 (matrices en vez de geometría ad hoc), el algoritmo de Newton-Euler del Bloque 15 frente a Lagrange del Bloque 14.

### 7. Ejemplos resueltos

**Ejemplo:** el 2R del Bloque 01 tiene la tabla DH (adelanto del Tema 11.2) `[[0,0,L1,0,0],[0,0,L2,0,0]]`; se verifica en el laboratorio que `directa(dh, [θ1,θ2])` reproduce exactamente $x,y$ del Bloque 01.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué "cuántas ecuaciones distintas hay que deducir a mano" crece muy rápido con el número de eslabones si no se usa un método sistemático.

**Serie B — Cálculo a mano**
- B1. Contar cuántos términos tendría, a mano, la expresión de $x$ para un brazo 3R plano (tres eslabones), siguiendo el patrón del 2R.

**Serie C — Laboratorio**
- C1. Nada nuevo todavía: este tema se verifica en el Tema 11.4 una vez definida la matriz DH.

---

## Tema 11.2 — La convención de Denavit-Hartenberg

### 1. El problema

Para poder automatizar la cinemática directa hace falta una regla fija —no una elegida a mano para cada brazo— para poner un marco de referencia en cada articulación, de modo que la transformación entre marcos consecutivos siempre tenga la misma forma con solo cuatro números.

### 2. El mecanismo

Denavit-Hartenberg fija un marco $i$ en cada articulación siguiendo cuatro reglas geométricas (el eje $z_i$ a lo largo del eje de la articulación $i+1$; el eje $x_i$ a lo largo de la perpendicular común entre $z_{i-1}$ y $z_i$; etc. — el detalle completo, con dibujos, está en Barrientos cap. 4 y se practica en el laboratorio). El resultado de seguir esas reglas es que la transformación de un marco al siguiente queda descrita por **solo cuatro parámetros**, con significado físico exacto:

| Parámetro | Significado |
|---|---|
| $\theta_i$ | ángulo alrededor de $z_{i-1}$ entre $x_{i-1}$ y $x_i$ |
| $d_i$ | distancia a lo largo de $z_{i-1}$ entre $x_{i-1}$ y $x_i$ |
| $a_i$ | distancia a lo largo de $x_i$ entre $z_{i-1}$ y $z_i$ |
| $\alpha_i$ | ángulo alrededor de $x_i$ entre $z_{i-1}$ y $z_i$ |

Uno de los cuatro es la **variable articular** (lo único que cambia cuando el robot se mueve): $\theta_i$ si la articulación $i$ es rotacional, $d_i$ si es prismática (Bloque 07, Tema 7.1) — los otros tres son constantes geométricas del brazo, fijadas por su diseño mecánico. Reducir *cualquier* par de eslabones consecutivos, en *cualquier* brazo, a solo cuatro números es la razón por la que DH sistematiza lo que el Tema 11.1 no podía escalar.

### 3. En la vida real

Una **tabla DH** es una matriz de $n\times5$: una fila por articulación, columnas $[\theta,d,a,\alpha,\text{tipo}]$ (tipo 0 = rotacional, 1 = prismática) — exactamente la convención de `robotica-manipuladores` (`docs/convenciones.md`), que este curso adopta sin cambios.

### 4. Limitaciones

DH no es la única forma de describir una cadena cinemática (el producto de exponenciales de Lynch & Park es otra, mencionada más abajo), y existen dos variantes de la propia convención DH (estándar y modificada, Tema 11.6) que no son intercambiables sin cuidado.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Dos personas arman tablas DH distintas para el mismo brazo físico | La asignación de marcos DH no es única cuando hay ejes paralelos o que se cruzan (hay libertad de elección en esos casos) | Verificar que ambas tablas, al calcular la cinemática directa, den la misma pose final para los mismos ángulos | Cualquier asignación válida sirve, siempre que sea consistente y se calcule la directa correctamente con ella |

### 6. Dónde más aparece la idea

Es el estándar de facto en robótica industrial para documentar la geometría de un brazo; aparece en cualquier datasheet o manual técnico de un robot manipulador.

### 7. Ejemplos resueltos

**Ejemplo:** el 2R plano del Bloque 01, en DH: articulación 1 en el origen ($\theta_1$ variable, $d=0,a=L_1,\alpha=0$), articulación 2 en la punta del primer eslabón ($\theta_2$ variable, $d=0,a=L_2,\alpha=0$) — fila por fila, `[[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, sin fórmulas, por qué hacen falta exactamente cuatro parámetros (y no tres, ni cinco) para describir la transformación entre dos marcos consecutivos con las reglas de DH.

**Serie B — Cálculo a mano**
- B1. Para un brazo con un solo eslabón prismático a lo largo de su propio eje z, ¿qué parámetro DH es la variable articular?

**Serie C — Laboratorio**
- C1. Consultar la tabla DH de `curso_3gdl` en `robotica-manipuladores/docs/robots.md` e identificar, fila por fila, cuál parámetro es la variable articular.

---

## Tema 11.3 — El algoritmo paso a paso: de los dibujos a los números

### 1. El problema

Las reglas de DH (Tema 11.2) son geométricas: "el eje z a lo largo de..." Traducir eso a números concretos para un brazo específico, sistemáticamente y sin saltarse pasos, es lo que Barrientos organiza en un procedimiento de sub-pasos (DH1 a DH16 en su notación).

### 2. El mecanismo

El procedimiento, resumido: numerar articulaciones de la base (1) a la pinza (n); para cada una, identificar su eje de movimiento y llamarlo $z_{i-1}$; ubicar el origen $O_i$ donde la perpendicular común entre $z_{i-1}$ y $z_i$ corta a $z_i$ (o, si son paralelos, con un criterio de conveniencia); fijar $x_i$ a lo largo de esa perpendicular común, apuntando de $z_{i-1}$ a $z_i$; fijar $y_i$ para completar un sistema dextrógiro (Bloque 08: $y_i=z_i\times x_i$). Los casos particulares (ejes paralelos, que se cortan, prismáticas) tienen reglas específicas que Barrientos detalla y que se practican mejor con dibujos en papel, brazo por brazo, que memorizando el algoritmo en abstracto.

Este tema se apoya deliberadamente en el laboratorio y en la lectura de Barrientos (con sus figuras) más que en la deducción algebraica: es un procedimiento de *dibujo y convención*, no una fórmula a deducir.

### 3. En la vida real

`robotica-manipuladores/python/notebooks/02_denavit_hartenberg.ipynb` (ver [docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md)) trabaja el algoritmo sobre las tablas DH de los brazos de acrílico reales del curso, con las figuras de la asignación de marcos.

### 4. Limitaciones

El procedimiento asume una cadena cinemática abierta (Bloque 07); cadenas cerradas necesitan un tratamiento aparte, fuera del alcance de este curso.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La tabla DH de un brazo real, armada a mano, da una cinemática directa que no coincide con las medidas físicas | Error en algún paso del algoritmo (eje mal identificado, signo de $\alpha$ invertido, Tema 11.6) | Comparar la posición calculada contra una medición física directa, para una postura simple de verificar (por ejemplo, brazo estirado) | Revisar la asignación de marcos paso a paso, empezando por la primera articulación donde aparece la discrepancia |

### 6. Dónde más aparece la idea

Cualquier procedimiento de ingeniería con pasos fijos y verificables (una checklist de vuelo, un protocolo de laboratorio): el valor está en la repetibilidad, no en la creatividad de cada aplicación.

### 7. Ejemplos resueltos

**Ejemplo:** ver la deducción completa, paso a paso con figuras, del 3R antropomórfico (`curso_3gdl`) en el notebook 02 de `robotica-manipuladores`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el algoritmo pide fijar $x_i$ a lo largo de la perpendicular común, en vez de en cualquier otra dirección conveniente.

**Serie B — Cálculo a mano**
- B1. Dibujar (a mano, en papel) la asignación de marcos DH de un brazo 2R plano, siguiendo el procedimiento, y comparar con la tabla del Tema 11.2.

**Serie C — Laboratorio**
- C1. Reproducir en Python la tabla DH de `tercer_corte_3gdl` (`docs/robots.md` de `robotica-manipuladores`) y verificar, con el laboratorio del Tema 11.5, que un ángulo de prueba da una posición físicamente razonable.

---

## Tema 11.4 — La matriz $^{i-1}A_i$ y la cadena completa

### 1. El problema

Con los cuatro parámetros DH de cada articulación (Tema 11.2), falta la fórmula concreta que los convierte en la transformación homogénea (Bloque 10) entre un marco y el siguiente, y la forma de encadenarlas todas.

### 2. El mecanismo

Cada fila de la tabla DH se traduce en una transformación homogénea $^{i-1}A_i$ como la composición de cuatro transformaciones elementales, en este orden:

$$^{i-1}A_i = R_z(\theta_i)\;T_z(d_i)\;T_x(a_i)\;R_x(\alpha_i)$$

(rotar $\theta_i$ en z, trasladar $d_i$ en z, trasladar $a_i$ en x, rotar $\alpha_i$ en x — cada una respecto a ejes móviles, Bloque 08 Tema 8.5, porque se van aplicando sobre el marco recién transformado por la anterior). Multiplicando resulta la matriz cerrada:

$$^{i-1}A_i = \begin{pmatrix} \cos\theta_i & -\cos\alpha_i\sin\theta_i & \sin\alpha_i\sin\theta_i & a_i\cos\theta_i \\ \sin\theta_i & \cos\alpha_i\cos\theta_i & -\sin\alpha_i\cos\theta_i & a_i\sin\theta_i \\ 0 & \sin\alpha_i & \cos\alpha_i & d_i \\ 0&0&0&1 \end{pmatrix}$$

Y, exactamente como en el Bloque 10 (Tema 10.4), la cinemática directa completa es la cadena de todas las $A_i$, marco tras marco desde la base hasta la pinza:

$$T = {}^0A_1\,{}^1A_2\cdots{}^{n-1}A_n$$

La posición de la pinza es la cuarta columna de $T$; su orientación, el bloque $3\times3$ superior izquierdo (Bloque 08).

### 3. En la vida real

`robotica/dh.py` implementa `matriz_dh(theta,d,a,alpha)` (la fórmula cerrada de arriba) y `directa(dh,q)` (la cadena completa), portadas casi 1:1 de `dh.py` de `robotica-manipuladores`; `directa_simbolica` hace lo mismo con SymPy, para *ver* la fórmula antes de evaluarla numéricamente (el mismo patrón "a mano, propio, con librería" de FILOSOFIA.md).

```python
from robotica.dh import matriz_dh, directa
T = directa(dh, q)   # q en radianes
```

### 4. Limitaciones

Ninguna nueva: es la aplicación directa de los Bloques 08 y 10 con parámetros organizados según DH.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La cadena de matrices no reproduce la posición esperada | Se multiplicaron las $A_i$ en el orden equivocado, o se usó la variable articular en el parámetro que no correspondía (Tema 11.2: $\theta$ para rotacional, $d$ para prismática) | Evaluar la directa en $q=\vec 0$ y comparar contra la postura "de referencia" conocida del brazo | Revisar el orden de la cadena y qué parámetro recibe la variable articular en cada fila |

### 6. Dónde más aparece la idea

Cualquier librería profesional de robótica (Robotics Toolbox, ROS/MoveIt) calcula la cinemática directa exactamente así internamente.

### 7. Ejemplos resueltos

**Ejemplo:** con la tabla DH del 2R del Tema 11.2 y $\theta_1=40°,\theta_2=30°$, `directa(dh,[rad(40),rad(30)])` debe reproducir $(0.298,0.381)$ del Bloque 01 (con $L_1=0.30,L_2=0.20$ en metros).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la cuarta columna de $T$ es directamente la posición de la pinza, retomando la lectura de una matriz homogénea del Bloque 10.

**Serie B — Cálculo a mano**
- B1. Multiplicar a mano $^0A_1\,^1A_2$ para el 2R del Tema 11.2 con $\theta_1=90°,\theta_2=0°$ y verificar la posición resultante.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_11/dh_2r_3r.py`: verifica el Ejemplo resuelto contra el Bloque 01, y calcula la cinemática directa del brazo `curso_3gdl` (3R antropomórfico real, `robotica-manipuladores`) para varias posturas, comparando contra `roboticstoolbox.DHRobot`.

---

## Tema 11.5 — Casos resueltos: del 2R a un catálogo de robots reales

### 1. El problema

La teoría de los Temas 11.2–11.4 se vuelve concreta solo al aplicarla a brazos reales, con sus propias particularidades geométricas (ejes desplazados, ángulos $\alpha$ no triviales) — el objetivo de este tema es practicar con casos que no sean el 2R idealizado.

### 2. El mecanismo

En vez de inventar geometrías de ejemplo, este curso reutiliza el catálogo real de `robotica-manipuladores` (`python/robotica/robots.py`): `curso_3gdl` (3R antropomórfico ideal, usado para el método geométrico del Bloque 12), `tercer_corte_3gdl` y `b3grados_3gdl` (brazos de acrílico realmente construidos), y `abb_6gdl`/`kuka_6gdl` (modelos basados en datasheets industriales, Bloque 07). Cada uno tiene su tabla DH documentada en `docs/robots.md`, con las medidas exactas.

Trabajar sobre estos casos, en vez de sobre geometrías idealizadas, es lo que expone las particularidades que un ejemplo de libro de texto suele ocultar: offsets de $\theta$ distintos de cero (porque el "cero" mecánico del servo no coincide con el "cero" matemático conveniente), signos de $\alpha$ que dependen de la orientación exacta de cada eje, y la razón por la que dos tablas DH del *mismo* robot pueden verse distintas (Tema 11.6).

### 3. En la vida real

```python
from robotica.dh import directa
dh_curso_3gdl = [[0, 15, 0, np.pi/2, 0], [0, 0, 12, 0, 0], [0, 0, 10, 0, 0]]
T = directa(dh_curso_3gdl, [np.radians(30), np.radians(45), np.radians(-20)])
```

(la tabla completa de cada robot, con sus unidades, está en `docs/robots.md` de `robotica-manipuladores`).

### 4. Limitaciones

Los modelos industriales (`abb_6gdl`, `kuka_6gdl`) son **simplificados** respecto al robot real (ver `docs/especificaciones.md`): no capturan cada detalle mecánico del datasheet, pero sí su geometría esencial para practicar cinemática.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La cinemática directa de un robot del catálogo da una posición que "se ve mal" comparada con fotos o diagramas del robot real | Se confundieron las unidades (cm contra mm: `abb_6gdl` está en cm, `kuka_6gdl` en mm, según `docs/robots.md`) | Revisar la unidad documentada de cada robot antes de usar sus medidas | Convertir explícitamente a una unidad consistente antes de mezclar robots o compararlos |

### 6. Dónde más aparece la idea

Cualquier "banco de pruebas" de robots reales para practicar algoritmos antes de aplicarlos al hardware propio.

### 7. Ejemplos resueltos

**Ejemplo:** `curso_3gdl` en $q=(0,0,0)$: con su tabla DH, la pinza queda en $(L_2+L_3,0,L_1)=(22,0,15)$ cm — el brazo completamente extendido horizontalmente a la altura del hombro.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué comparar la cinemática directa de dos robots requiere primero llevar ambos a la misma unidad de longitud.

**Serie B — Cálculo a mano**
- B1. Con la tabla DH de `curso_3gdl` del Tema 11.5, calcular a mano la posición de la pinza en $q=(0,90°,0)$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `codigo/bloque_11/dh_2r_3r.py` y explorar, con el animador de deslizadores (`codigo/bloque_11/animar_deslizadores.py`), cómo se mueve `curso_3gdl` al variar cada articulación.

---

## Tema 11.6 — DH estándar contra DH modificado (Craig)

### 1. El problema

Dos libros de robótica —Barrientos y Craig— dan tablas DH *distintas* para el *mismo* robot físico. No es un error de ninguno de los dos: son dos convenciones diferentes de dónde exactamente poner cada marco, y mezclarlas sin darse cuenta produce una cinemática directa incorrecta con números que "casi" tienen sentido.

### 2. El mecanismo

La convención **estándar** (la de este curso y de Barrientos, Tema 11.2) asocia el marco $i$ a la articulación $i+1$, y su matriz es $A_i=R_z(\theta_i)T_z(d_i)T_x(a_i)R_x(\alpha_i)$ (Tema 11.4). La convención **modificada** (Craig) asocia el marco $i$ a la articulación $i$ misma, y su matriz cambia el orden de las transformaciones elementales:

$$^{i-1}A_i^{\text{mod}} = R_x(\alpha_{i-1})\,T_x(a_{i-1})\,R_z(\theta_i)\,T_z(d_i)$$

El resultado neto: las mismas cuatro cantidades ($\theta,d,a,\alpha$) tienen **valores numéricos distintos** entre las dos convenciones para el mismo robot físico, porque están midiendo desplazamientos entre marcos que están ubicados en sitios distintos del brazo. No hay forma de "arreglarlo" cambiando solo un signo: hay que usar la fórmula de la matriz que corresponde a la convención de la tabla que se tiene, sin mezclar.

### 3. En la vida real

Antes de usar cualquier tabla DH de un libro, manual o librería ajena, **verificar explícitamente qué convención usa** (a menudo se indica en el propio documento); `robotica-manipuladores` y este curso usan siempre la convención estándar.

### 4. Limitaciones

Este bloque no desarrolla en profundidad la convención modificada más allá de señalar que existe y por qué importa distinguirla — su tratamiento completo está en Craig, *Introduction to Robotics*.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una tabla DH tomada de un manual o paper da una cinemática directa incorrecta al usarse con `matriz_dh`/`directa` de este curso | La tabla está en convención modificada (Craig) y se está evaluando con la fórmula estándar | Revisar si la fuente indica la convención; probar la fórmula modificada de la sección 2 y comparar | Usar la fórmula que corresponda a la convención real de la tabla, no asumir siempre la estándar |

### 6. Dónde más aparece la idea

Cualquier situación donde dos fuentes usan la misma notación con significados distintos (unidades, signos de convención, sistemas de referencia) — el mismo tipo de error, en esencia, que confundir ejes fijos con móviles (Bloque 08, Tema 8.5).

### 7. Ejemplos resueltos

**Ejemplo:** para un brazo simple de un eslabón, la tabla estándar y la modificada pueden coincidir numéricamente si el robot es lo bastante simple (un solo eslabón sin offset); la diferencia se vuelve evidente recién con dos o más eslabones con $\alpha\neq0$, como se explora en el laboratorio.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, sin calcular, por qué "asociar el marco $i$ a la articulación $i$" (modificado) contra "a la articulación $i+1$" (estándar) obliga a que los parámetros numéricos sean distintos.

**Serie B — Cálculo a mano**
- B1. Escribir la matriz $^{i-1}A_i^{\text{mod}}$ completa multiplicando las cuatro transformaciones elementales de la sección 2, en su orden.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_11/romper_convencion_dh.py`: toma una tabla DH modificada y la evalúa por error con la fórmula estándar (`matriz_dh`), comparando la pose resultante contra la correcta (evaluada con la fórmula modificada) — y, por separado, invierte el signo de un $\alpha$ en una tabla estándar válida para ver cómo cambia la postura del brazo.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/dh.py`: `matriz_dh`, `directa`, `marcos`, `matriz_dh_simbolica`, `directa_simbolica` (portadas de `robotica-manipuladores`). `robotica/brazo.py`: clase `Brazo`, que guarda la tabla DH de un robot junto con su nombre y sus límites articulares.

## Glosario del bloque

| Término | Definición |
|---|---|
| Tabla de Denavit-Hartenberg (DH) | Matriz $n\times5$ con una fila $[\theta,d,a,\alpha,\text{tipo}]$ por articulación, que describe geométricamente un brazo. |
| Variable articular | El parámetro DH ($\theta$ o $d$) que cambia cuando el robot se mueve; los otros tres son constantes del diseño. |
| $^{i-1}A_i$ | Matriz de transformación homogénea entre los marcos DH consecutivos $i-1$ e $i$. |
| DH estándar / modificado | Dos convenciones distintas de asignar los marcos DH (Barrientos y Craig, respectivamente); no son intercambiables sin traducir la fórmula. |
