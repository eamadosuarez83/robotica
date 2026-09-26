# Bloque 19 — Generación de trayectorias

> **Problema que abre el bloque:** si se le manda al brazo "ve a este punto" de golpe, arranca con aceleración infinita, sacude la estructura y el huevo sale volando.
>
> **Necesitas antes:** Bloque 18. · **Lectura:** Barrientos, cap. 6; Lynch & Park, cap. 9.

Este bloque porta `trayectorias.py` de [`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores)
(`interpolador_lineal`, `perfil_trapezoidal`, `interpolador_trapezoidal`, `linea`, `circulo`,
`polilinea`) casi 1:1 — esas funciones son agnósticas a la unidad de $q$, así que no hace falta
adaptar nada — y adapta `resolver_trayectoria` a que las inversas de este curso (Bloque 12)
devuelven radianes. El polinomio cúbico, el quíntico y el perfil en S son originales: no están en
`robotica-manipuladores`. Ver [docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md).

## Tema 19.1 — Espacio articular contra espacio cartesiano

### 1. El problema

Hay dos formas de decir "muévete de aquí hasta allá": especificar cómo cambian los **ángulos de las articulaciones** en el tiempo, o especificar cómo se mueve la **posición de la pinza** en el espacio (una línea recta, por ejemplo). No son lo mismo, y elegir mal produce un movimiento que no es el esperado.

### 2. El mecanismo

- **Espacio articular**: se interpola cada $q_i(t)$ directamente (Temas 19.2-19.3). Es barato de calcular (no necesita cinemática inversa en cada instante, Bloque 12) y garantiza que cada articulación se mueva suavemente, pero la trayectoria de la **pinza** en el espacio puede ser una curva complicada, no una línea recta — para muchas tareas (seguir el borde de una pieza, evitar un obstáculo) eso no sirve.
- **Espacio cartesiano**: se especifica la curva que debe seguir la pinza (Temas 19.4-19.5: una línea, un círculo), y en **cada instante** se resuelve la cinemática inversa (Bloque 12) para obtener los ángulos correspondientes. Garantiza la forma exacta del movimiento de la pinza, a costa de resolver la inversa repetidamente (más costoso, Bloque 12 Tema 12.5) y de poder toparse con puntos fuera de alcance o cerca de una singularidad (Bloque 13, Tema 19.5) en cualquier punto del camino.

### 3. En la vida real

`robotica.trayectorias` separa ambos casos: `interpolador_lineal`/`perfil_trapezoidal` (espacio articular, Temas 19.2-19.3) contra `linea`/`circulo` + `resolver_trayectoria` (espacio cartesiano, Temas 19.4-19.5).

### 4. Limitaciones

Ninguna es "mejor" en general: la elección depende de la tarea (Bloque 24 tendrá que decidir cuál usar para cada fase de recoger y depositar un huevo).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un movimiento pensado para ser "en línea recta" resulta en una trayectoria curva de la pinza | Se interpoló en espacio articular cuando la tarea necesitaba espacio cartesiano | Graficar la trayectoria de la pinza (no solo los ángulos) y comparar contra la línea esperada | Usar `linea` + `resolver_trayectoria` (espacio cartesiano) cuando la forma del camino de la pinza importa |

### 6. Dónde más aparece la idea

Cualquier robot industrial que suelda o pinta en línea recta usa interpolación cartesiana; uno que solo necesita llegar de un punto a otro sin importar el camino usa interpolación articular, más simple y rápida.

### 7. Ejemplos resueltos

**Ejemplo:** mover el 2R del hombro en 0° a 90° manteniendo el codo fijo en 0° (interpolación articular) traza un arco; mover la pinza en línea recta de $(0.30,0.10)$ a $(0.20,0.30)$ (interpolación cartesiana) exige que los dos ángulos cambien de forma coordinada y no lineal.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué interpolar cada articulación linealmente casi nunca produce una línea recta de la pinza, salvo casos particulares.

**Serie B — Cálculo a mano**
- B1. Para el 2R, describir cualitativamente la forma de la trayectoria de la pinza si solo se interpola $\theta_1$ (espacio articular) de 0° a 90° con $\theta_2=0$ fijo.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_19/comparar_espacios.py`: grafica la trayectoria de la pinza del 2R para el mismo movimiento hecho en espacio articular y en espacio cartesiano, lado a lado.

---

## Tema 19.2 — Interpoladores: lineal, cúbico, quíntico

### 1. El problema

El problema que abre el bloque: pedir un ángulo nuevo "de golpe" (un escalón, Bloque 17) implica velocidad y aceleración infinitas en el instante del cambio — físicamente imposible, y en la práctica produce un tirón violento.

### 2. El mecanismo

- **Interpolación lineal**: $q(t)$ cambia a velocidad constante entre dos puntos — ya mejor que un escalón, pero la velocidad **salta** de golpe al principio y al final del tramo (aceleración infinita en esos dos instantes, aunque no en el resto).
- **Polinomio cúbico**: $q(t)=a_0+a_1t+a_2t^2+a_3t^3$, con cuatro condiciones de frontera —posición y **velocidad** en $t=0$ y $t=T$— que fijan los cuatro coeficientes (Bloque 03, Tema 3.6: un sistema lineal de 4 ecuaciones). Eligiendo velocidad cero en ambos extremos, el movimiento arranca y termina suave, sin el salto de velocidad de la interpolación lineal.
- **Polinomio de quinto orden (quíntico)**: seis coeficientes, seis condiciones de frontera —posición, velocidad **y aceleración** en ambos extremos. Con aceleración cero en los extremos además de velocidad cero, el arranque y la parada son todavía más suaves (ni siquiera hay un salto de aceleración) — el punto de partida del perfil en S (Tema 19.3).

`robotica.trayectorias` resuelve los coeficientes de cualquiera de estos dos casos con un sistema lineal general (`_resolver_polinomio`, Bloque 03), en vez de memorizar fórmulas cerradas propensas a error de transcripción.

### 3. En la vida real

```python
from robotica.trayectorias import interpolador_cubico, interpolador_quintico
t, q, qd, qdd = interpolador_cubico(q0=0, q1=90, qd0=0, qd1=0, T=2.0)
t, q, qd, qdd = interpolador_quintico(q0=0, q1=90, qd0=0, qd1=0, qdd0=0, qdd1=0, T=2.0)
```

### 4. Limitaciones

Ni el cúbico ni el quíntico limitan explícitamente la velocidad o aceleración **máxima** alcanzada a mitad del tramo (a diferencia del perfil trapezoidal, Tema 19.3, que sí las fija de antemano) — hay que verificar después que esos máximos sean físicamente alcanzables (Bloque 16).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un polinomio cúbico/quíntico produce una velocidad pico mucho mayor de lo esperado a mitad de camino | El polinomio no limita la velocidad máxima directamente; para distancias grandes en poco tiempo, la velocidad pico puede ser mucho mayor que el promedio | Graficar $\dot q(t)$ completo, no solo verificar los extremos | Aumentar $T$, o usar un perfil que sí limite la velocidad máxima explícitamente (trapezoidal, Tema 19.3) |

### 6. Dónde más aparece la idea

Animación por computadora (interpolación "ease-in/ease-out" es, esencialmente, un polinomio cúbico o quíntico con velocidad cero en los extremos), diseño de levas mecánicas.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_19/comparar_perfiles.py`, que grafica posición, velocidad y aceleración de lineal, cúbico y quíntico para el mismo movimiento de 0° a 90° en 2 s.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué elegir velocidad y aceleración cero en los extremos del quíntico produce un movimiento más suave que el cúbico, en términos de qué deja de "saltar" en cada caso.

**Serie B — Cálculo a mano**
- B1. Plantear (sin resolver) el sistema de 4 ecuaciones para los coeficientes del interpolador cúbico de 0° a 90° en $T=2$ s con velocidad cero en ambos extremos.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_19/comparar_perfiles.py` y verificar B1 comparando contra `interpolador_cubico`.

---

## Tema 19.3 — Perfil trapezoidal y perfil en S

### 1. El problema

Ni el cúbico ni el quíntico (Tema 19.2) dejan elegir directamente "la velocidad máxima debe ser esta" — un requisito común en la práctica (no exceder la velocidad segura de un motor, Bloque 16).

### 2. El mecanismo

El **perfil trapezoidal de velocidad** divide el movimiento en tres tramos: acelera a $a$ constante hasta alcanzar la velocidad pico $V$, viaja a $V$ constante, y frena a $-a$ constante — la gráfica de $\dot q(t)$ tiene forma de trapecio (de ahí el nombre). Si la distancia es tan corta que nunca se alcanza $V$, el perfil se vuelve **triangular** (acelera y frena sin tramo de velocidad constante) — `robotica.trayectorias.perfil_trapezoidal` maneja ambos casos automáticamente, calculando la velocidad pico real $V_p=\min(V,\sqrt{aD})$.

El costo del perfil trapezoidal: la **aceleración salta** instantáneamente al principio y al final de cada tramo (de 0 a $a$, de $a$ a $0$, etc.) — sigue habiendo una discontinuidad, ahora en la aceleración en vez de en la velocidad. El **perfil en S** (llamado así por la forma de $q(t)$, una S suave) elimina también esa discontinuidad, limitando el *jerk* (la derivada de la aceleración, Bloque 04 Tema 4.1) a un valor finito. La versión de este curso (`robotica.trayectorias.perfil_s`) es el caso particular del polinomio quíntico (Tema 19.2) con velocidad **y** aceleración cero en ambos extremos: un jerk continuo y acotado, más simple de deducir que el perfil trapezoidal-con-esquinas-suavizadas de siete tramos que usan algunos controladores industriales (mencionado en Barrientos y en Lynch & Park, fuera del alcance de este curso en su forma completa).

### 3. En la vida real

```python
from robotica.trayectorias import perfil_trapezoidal, perfil_s
t, q, qd, qdd = perfil_trapezoidal(q0=0, q1=90, V=60, a=120)
t, q, qd, qdd = perfil_s(q0=0, q1=90, T=2.0)
```

### 4. Limitaciones

El perfil en S de este curso (quíntico con fronteras nulas) no permite fijar la velocidad pico de antemano como sí lo hace el trapezoidal —la velocidad pico resulta de la duración $T$ elegida, no al revés—, a cambio de un jerk acotado en todo el recorrido.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un brazo con perfil trapezoidal vibra o "golpea" perceptiblemente al empezar o terminar cada tramo | Salto instantáneo de aceleración (jerk infinito en esos instantes) excita las frecuencias naturales de la estructura mecánica | Comparar la vibración con la misma trayectoria usando el perfil en S | Usar el perfil en S (o el trapezoidal con esquinas suavizadas) cuando la vibración sea un problema |

### 6. Dónde más aparece la idea

Ascensores y trenes de alta velocidad usan perfiles de aceleración tipo S para que los pasajeros no sientan un "tirón" al arrancar o frenar; el mismo principio de limitar el jerk aparece en el diseño de montañas rusas.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_19/comparar_perfiles.py`, que agrega el trapezoidal y el perfil en S a la comparación del Tema 19.2, graficando también la aceleración para mostrar los saltos (o su ausencia).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el jerk infinito del perfil trapezoidal no es un problema puramente matemático: qué le pasa físicamente a una estructura real sometida a eso.

**Serie B — Cálculo a mano**
- B1. Con $D=90°$, $V=30°/s$, $a=60°/s^2$, calcular si el perfil trapezoidal alcanza $V$ o queda triangular (fórmula $V_p=\min(V,\sqrt{aD})$).

**Serie C — Laboratorio**
- C1. Verificar B1 con `perfil_trapezoidal` y graficar la aceleración de los cuatro perfiles (lineal, cúbico, trapezoidal, S) juntos para comparar sus discontinuidades.

---

## Tema 19.4 — Trayectorias con puntos intermedios

### 1. El problema

Una tarea real rara vez es "de A a B": el brazo del Bloque 24 tiene que ir de la clasificadora a la cubeta pasando por una postura de aproximación segura, evitando golpear el borde de la cubeta.

### 2. El mecanismo

Con varios puntos intermedios, dos caminos:

- **Repetir el interpolador tramo por tramo**: `interpolador_lineal` y `interpolador_trapezoidal` (Temas 19.1-19.3) ya aceptan una lista `Q` de varios puntos, aplicando el mismo perfil a cada tramo consecutivo y garantizando que la posición pase exactamente por cada punto intermedio.
- **Splines**: en vez de tramos independientes, un spline ajusta una única curva suave (típicamente polinomios cúbicos empalmados, Tema 19.2) que pasa por todos los puntos con **continuidad de velocidad y aceleración en las uniones** — el movimiento no solo pasa por cada punto, sino que no tiene ningún salto brusco de velocidad al cruzar de un tramo al siguiente, algo que "repetir el interpolador tramo por tramo" con perfiles independientes no garantiza automáticamente (cada tramo empieza y termina en reposo, dando un movimiento "parado-arranca-parado" en cada punto intermedio en vez de uno continuo).

### 3. En la vida real

`robotica.trayectorias.polilinea` (cartesiano) y las versiones con lista `Q` de los interpoladores articulares (Temas 19.1-19.3) cubren el caso "pasar por varios puntos, deteniéndose en cada uno"; un spline completo (con continuidad entre tramos) queda fuera del alcance de este curso salvo mención, disponible en `scipy.interpolate` (`CubicSpline`) para quien quiera profundizar.

### 4. Limitaciones

Sin splines, cada punto intermedio implica una parada momentánea (velocidad cero) — aceptable para muchas tareas (Bloque 24: aproximar, tomar, levantar son fases naturalmente separadas), pero no ideal si se quiere un movimiento continuo sin pausas.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un movimiento con varios puntos intermedios se ve "entrecortado", deteniéndose en cada uno | Se usó un interpolador por tramos independientes (velocidad cero en cada punto intermedio) cuando se quería continuidad | Verificar si $\dot q=0$ en cada punto intermedio de la trayectoria generada | Usar un spline (`scipy.interpolate.CubicSpline`) si la continuidad de velocidad importa |

### 6. Dónde más aparece la idea

Cualquier trayectoria de dibujo o mecanizado con varios puntos de paso (la `polilinea` del Bloque 19 dibuja exactamente así); el trazado de una fuente tipográfica con curvas de Bézier sigue el mismo principio de empalmar curvas suaves.

### 7. Ejemplos resueltos

**Ejemplo:** una trayectoria del hombro pasando por $0°\to45°\to90°\to45°$ con `interpolador_trapezoidal` se detiene brevemente (velocidad cero) en cada uno de los cuatro puntos.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, en una tarea de recoger y depositar (Bloque 24), detenerse un instante en la postura de aproximación puede ser deseable en vez de un defecto.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Generar con `interpolador_trapezoidal` una trayectoria de cuatro puntos y verificar que la velocidad se anula en cada uno.

---

## Tema 19.5 — Línea recta cartesiana con cinemática inversa

### 1. El problema

Para que la pinza se mueva realmente en línea recta (no solo los ángulos por separado, Tema 19.1), hace falta resolver la cinemática inversa (Bloque 12) en cada instante de la línea — y algo puede salir mal en el camino, no solo en los extremos.

### 2. El mecanismo

`robotica.trayectorias.resolver_trayectoria` recorre una curva cartesiana (`linea`, `circulo`) punto por punto, llamando a una función de cinemática inversa (Bloque 12) en cada uno y devolviendo un `ResultadoTrayectoria` con tres estados posibles: `"ok"` (toda la curva resuelta), `"sin_solucion"` (algún punto quedó fuera del espacio de trabajo, Bloque 12 Tema 12.7) o `"fuera_de_limites"` (la solución existe pero algún ángulo excede los límites articulares del brazo, Bloque 07) — con el índice exacto del punto donde falló, para poder diagnosticar sin tener que revisar toda la trayectoria a mano.

Un peligro específico de la interpolación cartesiana que no aparece en la articular (Tema 19.1): la línea recta puede pasar **cerca de una singularidad** (Bloque 13, Tema 13.5) sin que ningún punto individual esté fuera de alcance — ahí, aunque la cinemática inversa sí encuentra una solución en cada punto, las velocidades articulares necesarias para mantener la velocidad cartesiana deseada (Bloque 13, Tema 13.4) pueden dispararse, aunque la *posición* en sí sea perfectamente alcanzable.

### 3. En la vida real

```python
from robotica.trayectorias import linea, resolver_trayectoria
from robotica.inversa import inv_2r_geometrica

puntos = linea([0.30, 0.10, 0], [0.20, 0.30, 0], 20)
inv = lambda px, py, pz: inv_2r_geometrica(px, py, L1, L2)
resultado = resolver_trayectoria(puntos, inv)
if not resultado.ok:
    print(f"Falló en el punto {resultado.indice_fallo}: {resultado.estado}")
```

### 4. Limitaciones

`resolver_trayectoria` verifica la posición alcanzable en cada punto, pero no verifica automáticamente la proximidad a una singularidad (Bloque 13) ni las velocidades articulares resultantes — eso se agrega aparte, combinando con `robotica.jacobiana.manipulabilidad` (Bloque 13, Tema 13.6).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una trayectoria cartesiana se resuelve sin error en cada punto, pero el brazo se mueve de forma errática o muy rápida en algún tramo | La línea pasa cerca de una singularidad (Bloque 13): posiciones alcanzables, pero con manipulabilidad muy baja | Calcular la manipulabilidad (Bloque 13, Tema 13.6) a lo largo de la trayectoria resuelta | Replanificar la línea para evitar la zona, o reducir la velocidad cerca de ahí |

### 6. Dónde más aparece la idea

Cualquier planificador de movimiento cartesiano de un robot industrial revisa, además de la alcanzabilidad punto por punto, la proximidad a singularidades a lo largo de todo el camino.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_19/romper_singularidad_trayectoria.py`, que traza una línea recta cartesiana del 2R que cruza la postura de brazo estirado (la singularidad del Bloque 13, Tema 13.5) y muestra cómo la manipulabilidad cae a casi cero a mitad de camino, aunque `resolver_trayectoria` no reporte ningún error de alcanzabilidad.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un punto puede ser perfectamente alcanzable (la inversa lo resuelve sin error) y aun así ser problemático para una trayectoria cartesiana que pasa cerca de él.

**Serie B — Cálculo a mano**
- B1. Para el 2R, describir qué línea recta cartesiana pasaría exactamente por la postura de brazo estirado (Bloque 13, Tema 13.5).

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_19/romper_singularidad_trayectoria.py` y confirmar dónde a lo largo del camino la manipulabilidad es mínima.

---

## Tema 19.6 — Muestreo de la trayectoria y el error histórico de no llegar al destino

### 1. El problema

Una trayectoria continua ($q(t)$ como fórmula) tiene que convertirse en una lista finita de puntos para enviarla, muestra a muestra, al controlador digital (Bloque 18, Tema 18.6) — y un error sutil al hacerlo puede dejar el movimiento sin llegar exactamente al destino, sin que nada lo avise.

### 2. El mecanismo

El número de puntos y el periodo de muestreo de la trayectoria deben ser consistentes con el periodo de muestreo del controlador (Bloque 18, Tema 18.6): generar una trayectoria con más resolución de la que el controlador puede consumir es trabajo desperdiciado; con menos, el controlador recibe referencias "a saltos" que degradan el seguimiento.

Un error real y documentado, útil como advertencia concreta: las primeras versiones de los interpoladores por tramos de `robotica-manipuladores` (antes de corregirse) concatenaban cada tramo **descartando su último punto**, sin agregar el punto final de la trayectoria completa al final — el resultado: un movimiento pedido de 0° a 90° terminaba, en los hechos, en 80° o algún valor cercano, sin ningún error ni aviso, porque cada tramo individual sí llegaba a su propio final, solo que ese final se descartaba antes de pegar el siguiente tramo. La corrección (ya incorporada en `robotica.trayectorias.interpolador_lineal` e `interpolador_trapezoidal`, Temas 19.1-19.3) es concatenar los tramos **sin** su último punto y agregar el punto final completo una sola vez, al final de todo.

### 3. En la vida real

```python
# el patrón correcto, ya usado en robotica.trayectorias:
tramos = [tramo[:-1] for tramo in lista_de_tramos]   # sin el último punto
Qn = np.concatenate(tramos + [Q[-1:]])               # + el destino final, una vez
```

### 4. Limitaciones

Este error específico ya está corregido en la librería de este curso; se documenta aquí porque es exactamente el tipo de error silencioso —sin ningún mensaje, sin ninguna excepción— que hace falta saber reconocer en código propio o ajeno.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un brazo se queda sistemáticamente un poco antes del punto pedido, en todos los movimientos, sin ningún error reportado | El generador de trayectorias descarta el último punto de cada tramo sin agregar el destino final por separado (el error histórico de esta sección) | Verificar explícitamente que el último valor de la trayectoria generada coincida exactamente con el destino pedido | Concatenar los tramos sin su último punto y agregar el destino una sola vez al final |

### 6. Dónde más aparece la idea

Cualquier código que concatena segmentos de una curva o de una lista corre el riesgo de duplicar o descartar el punto de unión; es un error clásico de "off-by-one" (Bloque 01 ya tuvo un ejemplo análogo con `atan` contra `atan2`, un error silencioso de otro tipo).

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_19/romper_descartar_punto_final.py`, que reproduce a propósito la versión con el error (sin agregar el punto final) y la compara contra la versión corregida.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué este error es particularmente peligroso: no lanza ninguna excepción ni da ningún valor obviamente absurdo, solo un destino ligeramente incorrecto.

**Serie B — Cálculo a mano**
- B1. Con `n_puntos=10` por tramo y una trayectoria de 3 puntos (2 tramos), contar cuántos puntos tiene la salida con el patrón correcto (Tema 19.6, sección 3) y compararlo con la versión que simplemente concatena todos los tramos completos sin descartar nada (que duplicaría los puntos de unión).

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_19/romper_descartar_punto_final.py` y medir el error final (en grados) que deja la versión con el bug para distintos números de tramos.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/trayectorias.py`: `interpolador_lineal`, `perfil_trapezoidal`, `interpolador_trapezoidal` (portadas), `interpolador_cubico`, `interpolador_quintico`, `perfil_s` (originales), `linea`, `circulo`, `polilinea`, `ResultadoTrayectoria`, `resolver_trayectoria` (portadas, adaptadas a radianes).

## Glosario del bloque

| Término | Definición |
|---|---|
| Espacio articular / cartesiano | Interpolar directamente los ángulos, o interpolar la posición de la pinza y resolver la inversa en cada instante. |
| Jerk | Derivada de la aceleración; un perfil con jerk acotado evita saltos instantáneos de aceleración. |
| Perfil trapezoidal | Velocidad que acelera a un valor constante, viaja a velocidad constante, y frena; se vuelve triangular si la distancia es corta. |
| Perfil en S | Perfil con aceleración también suave (sin saltos), a costa de un jerk acotado pero no nulo. |
| Spline | Curva suave que pasa por varios puntos con continuidad de velocidad y aceleración en las uniones. |
| `ResultadoTrayectoria` | Resultado de resolver una trayectoria cartesiana con cinemática inversa: éxito, sin solución, o fuera de límites, con el punto exacto del fallo. |
