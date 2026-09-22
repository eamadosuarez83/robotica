# Bloque 01 — Trigonometría y geometría del plano

> **Problema que abre el bloque:** un brazo plano con dos eslabones de 30 cm y 20 cm. Si el hombro gira 40° y el codo 30°, ¿dónde queda la punta?
>
> **Necesitas antes:** Bloque 00. · **Lectura:** cualquier texto de precálculo; Corke, apéndice de geometría.

## Tema 1.1 — El radián

### 1. El problema

Un grado es una convención arbitraria: dividir la vuelta completa en 360 partes porque los babilonios contaban en base 60. Sirve para hablar con una persona ("gira 40°"), pero en cuanto aparece una derivada, un grado deja de tener sentido físico: $\frac{d}{d\theta}\sin\theta = \cos\theta$ **solo es cierto si $\theta$ está en radianes**. En grados aparece una constante de conversión molesta ($\pi/180$) en cada derivada, velocidad angular y ecuación del curso.

### 2. El mecanismo

Un radián es el ángulo central que recorre, sobre una circunferencia de radio $r$, un arco de longitud exactamente $r$. Como la circunferencia completa mide $2\pi r$, una vuelta completa son $2\pi$ radianes:

$$\theta_{rad} = \frac{\text{longitud de arco}}{r}, \qquad 2\pi \text{ rad} = 360°$$

De ahí la conversión que se usa en todo el curso:

$$\theta_{rad} = \theta_{deg} \cdot \frac{\pi}{180}, \qquad \theta_{deg} = \theta_{rad} \cdot \frac{180}{\pi}$$

El radián no es una unidad arbitraria: es la que hace que la velocidad lineal de un punto sobre un círculo de radio $r$ sea, simplemente, $v = r\dot\theta$, sin ninguna constante extra. Por eso toda la mecánica y el cálculo del curso se escriben en radianes.

### 3. En la vida real

En Python, `numpy.sin`, `numpy.cos` y toda la librería estándar esperan radianes. `np.radians(40)` y `np.degrees(x)` convierten en ambos sentidos. La convención del curso (ver [FILOSOFIA.md](../FILOSOFIA.md)) es: **radianes en todo cálculo y todo código; grados solo para mostrarle un número a una persona**, por ejemplo en una etiqueta de gráfica.

### 4. Limitaciones

Ninguna: es una elección de unidad, no una aproximación física.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El brazo simulado da vueltas descontroladas o queda casi quieto cuando debería moverse mucho | Se pasó un ángulo en grados a una función que espera radianes (o viceversa) | Imprimir el valor del ángulo antes de usarlo: si es del orden de 40–360, probablemente son grados; si es del orden de 0–6.28, son radianes | Convertir explícitamente con `np.radians` / `np.degrees` en la frontera entre "lo que ve la persona" y "lo que calcula el programa" |

### 6. Dónde más aparece la idea

Velocidad angular de un motor (rad/s), frecuencia angular en circuitos ($\omega = 2\pi f$), la fórmula $v = r\omega$ de cualquier rueda.

### 7. Ejemplos resueltos

**Ejemplo:** convertir 40° y 30° a radianes.

$$40° \cdot \frac{\pi}{180} \approx 0.698\ \text{rad}, \qquad 30° \cdot \frac{\pi}{180} \approx 0.524\ \text{rad}$$

Verificación en código: `np.radians([40, 30])` → `[0.698, 0.524]`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar con una frase por qué $\frac{d}{d\theta}\sin\theta = \cos\theta$ deja de ser cierto si $\theta$ se mide en grados.

**Serie B — Cálculo a mano**
- B1. Convertir 15°, 200° y 315° a radianes, dejando el resultado en términos de $\pi$ cuando sea posible.

**Serie C — Laboratorio**
- C1. Escribir una función `grados_a_radianes(theta_deg)` sin usar NumPy (solo `math.pi`) y comparar su salida con `np.radians` para los tres ángulos de B1.

---

## Tema 1.2 — Seno y coseno como proyecciones

### 1. El problema

En el colegio, seno y coseno se definen como "cateto opuesto sobre hipotenusa": una razón entre lados de un triángulo rectángulo. Esa definición se rompe apenas el ángulo pasa de 90°, porque ya no hay triángulo. Para describir la punta de un brazo que gira una vuelta completa, hace falta una definición que funcione para *cualquier* ángulo.

### 2. El mecanismo

Sea un punto que se mueve sobre un círculo de radio 1 (el **círculo unitario**), centrado en el origen, empezando en $(1,0)$ y girando un ángulo $\theta$ en sentido antihorario (positivo, por convención de mano derecha). Ese punto queda en:

$$(x, y) = (\cos\theta, \sin\theta)$$

Es decir: **coseno es la proyección sobre el eje x, seno es la proyección sobre el eje y**, del punto que gira. Esta definición vale para cualquier $\theta$, positivo o negativo, mayor que $2\pi$ o no; el triángulo rectángulo es apenas el caso $0 < \theta < 90°$.

Como el punto siempre está a distancia 1 del origen, el teorema de Pitágoras aplicado a sus dos proyecciones da la identidad fundamental:

$$\sin^2\theta + \cos^2\theta = 1$$

**Identidades que el curso usa de verdad** (se deducen proyectando la suma de dos giros, no se piden de memoria sin más):

$$\sin(\alpha+\beta) = \sin\alpha\cos\beta + \cos\alpha\sin\beta$$
$$\cos(\alpha+\beta) = \cos\alpha\cos\beta - \sin\alpha\sin\beta$$

Y, para un triángulo con lados $a,b,c$ y el ángulo $\gamma$ opuesto a $c$, la **ley de cosenos** (una generalización de Pitágoras cuando el ángulo no es de 90°):

$$c^2 = a^2 + b^2 - 2ab\cos\gamma$$

Esta es exactamente la herramienta que resuelve el problema que abre el bloque: con $a = L_1$, $b = L_2$ y $c$ la distancia del hombro a la punta, $\gamma$ es el ángulo del codo.

### 3. En la vida real

`np.sin`, `np.cos` reciben arreglos completos de ángulos y devuelven un arreglo de resultados, sin ciclos:

```python
import numpy as np
theta = np.radians([0, 40, 90, 180])
np.cos(theta)  # array([ 1.   ,  0.766,  0.   , -1.   ])
```

### 4. Limitaciones

Ninguna en sí misma; la limitación aparece al *invertir* seno y coseno (siguiente tema): recuperar $\theta$ a partir de $(x,y)$ no es tan directo.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| $\sin^2\theta+\cos^2\theta$ da un número distinto de 1 en el código | Se mezclaron grados y radianes al calcular $\theta$, o hay un error de tipeo en la fórmula | Evaluar la identidad numéricamente para el $\theta$ sospechoso | Revisar en qué unidad está $\theta$ antes de usarlo |

### 6. Dónde más aparece la idea

Coordenadas polares en general, ondas (una señal senoidal es la proyección de un punto girando), corriente alterna, el círculo unitario en trigonometría de cualquier ingeniería.

### 7. Ejemplos resueltos

**Ejemplo:** coordenadas del punto a 150° en el círculo unitario.

$150° = 180° - 30°$, así que por simetría: $\cos150° = -\cos30° = -\tfrac{\sqrt3}{2}$, $\sin150° = \sin30° = \tfrac12$.

Verificación: `np.cos(np.radians(150))` → `-0.866`; `np.sin(np.radians(150))` → `0.5`.

**Ejemplo (el problema del bloque):** eslabones $L_1=0.30$ m, $L_2=0.20$ m; ángulo del codo (entre eslabones) $\theta_{codo}=30°$. Distancia del hombro a la punta por ley de cosenos:

$$c = \sqrt{L_1^2+L_2^2-2L_1L_2\cos(30°)} = \sqrt{0.09+0.04-0.12\cdot0.866} \approx 0.152\ \text{m}$$

(La posición completa $(x,y)$ de la punta, no solo la distancia, se calcula en el Tema 1.4 con coordenadas polares encadenadas — es la cinemática directa del brazo 2R.)

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la definición "cateto sobre hipotenusa" no sirve para $\theta = 200°$, y qué la reemplaza.

**Serie B — Cálculo a mano**
- B1. Dar $\sin\theta$ y $\cos\theta$ para $\theta = 0°, 90°, 180°, 270°$ sin calculadora, pensando en el punto que gira.
- B2. Con $L_1=0.30$ m, $L_2=0.20$ m y ángulo del codo de 60°, calcular la distancia del hombro a la punta con la ley de cosenos.

**Serie C — Laboratorio**
- C1. Verificar B2 con `numpy` y graficar cómo cambia esa distancia al variar el ángulo del codo de 0° a 180°.

---

## Tema 1.3 — `atan2` contra `atan`

### 1. El problema

Se tiene un vector $(x,y)$ y se quiere el ángulo que forma con el eje x. La tentación es $\theta = \arctan(y/x)$. Con $(x,y)=(-3,4)$ eso da el mismo resultado que con $(3,-4)$, porque el cociente $y/x$ es el mismo con los dos signos invertidos: $\arctan$ no puede distinguir en qué cuadrante está el punto. Un brazo que use esa fórmula manda la punta al lado opuesto del que se le pidió.

### 2. El mecanismo

`atan2(y, x)` es una función de **dos argumentos** (no un cociente) que mira el signo de $x$ y de $y$ por separado para devolver el ángulo correcto en los cuatro cuadrantes, en el rango $(-\pi, \pi]$:

| Cuadrante | Signo de x | Signo de y | `atan2(y,x)` |
|---|---|---|---|
| I | + | + | entre 0 y $\pi/2$ |
| II | − | + | entre $\pi/2$ y $\pi$ |
| III | − | − | entre $-\pi$ y $-\pi/2$ |
| IV | + | − | entre $-\pi/2$ y 0 |

Internamente, `atan2` sigue usando la tangente, pero decide el cuadrante final revisando los signos de $x$ e $y$ antes de devolver el resultado — exactamente lo que $\arctan(y/x)$ no puede hacer porque solo recibe el cociente.

### 3. En la vida real

`np.arctan2(y, x)` — **el orden de los argumentos es y, x**, no x, y; es el error de tipeo más común con esta función.

### 4. Limitaciones

`atan2(0, 0)` no está definido matemáticamente (el vector cero no apunta a ningún lado); NumPy devuelve 0.0 por convención, sin avisar. Conviene comprobar que el vector no sea (casi) cero antes de pedir su ángulo.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El brazo "salta" al lado contrario del punto pedido | Se usó `arctan(y/x)` en vez de `arctan2(y,x)` | Probar la fórmula con un punto de cuadrante II o III conocido y comparar contra el ángulo esperado | Reemplazar por `np.arctan2(y, x)`, revisando el orden de los argumentos |

### 6. Dónde más aparece la idea

Calcular el rumbo (*heading*) de un GPS o una brújula, el ángulo de la palanca de un joystick, cualquier conversión de coordenadas cartesianas a polares en robótica, gráficos o navegación.

### 7. Ejemplos resueltos

**Ejemplo:** $(x,y) = (-3, 4)$.

$\arctan(4/-3) = \arctan(-1.333) \approx -53.1°$ — en el cuadrante IV, que es **incorrecto**: el punto está en el cuadrante II.

$\text{atan2}(4,-3) \approx 126.9°$ — correcto: cuadrante II. La diferencia con el resultado de `arctan` es de $180°$, exactamente el error de "apuntar al lado contrario".

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué `arctan(y/x)` sí funciona sin problema para puntos del cuadrante I?

**Serie B — Cálculo a mano**
- B1. Calcular con `atan2` (a mano, razonando el cuadrante) el ángulo de los puntos $(1,1)$, $(-1,1)$, $(-1,-1)$, $(1,-1)$.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_01/romper_atan.py`, que calcula la orientación de un eslabón con `arctan(y/x)` y con `arctan2(y,x)` para los mismos puntos, y grafica ambos resultados para ver dónde se separan.

---

## Tema 1.4 — Coordenadas polares y la cinemática directa del brazo 2R

### 1. El problema

Ya se puede convertir un ángulo en un punto del círculo unitario (Tema 1.2) y un punto en un ángulo (Tema 1.3). Falta encadenar dos eslabones: el hombro gira $\theta_1$, y sobre la punta del primer eslabón se apoya el segundo, que gira $\theta_2$ **respecto al primero**. ¿Dónde queda la punta final?

### 2. El mecanismo

Un punto en coordenadas polares $(r,\theta)$ (distancia $r$ al origen, ángulo $\theta$) se convierte a cartesianas con la misma proyección del Tema 1.2:

$$x = r\cos\theta, \qquad y = r\sin\theta$$

Para el brazo plano de dos eslabones (2R — dos articulaciones de rotación) con longitudes $L_1, L_2$:

- La punta del primer eslabón (el codo) está a distancia $L_1$ del hombro, en el ángulo $\theta_1$:

$$x_{codo} = L_1\cos\theta_1, \qquad y_{codo} = L_1\sin\theta_1$$

- El segundo eslabón sale del codo con un ángulo **acumulado** $\theta_1+\theta_2$ respecto al eje x fijo (porque $\theta_2$ se mide respecto al primer eslabón, que ya está girado $\theta_1$):

$$x = L_1\cos\theta_1 + L_2\cos(\theta_1+\theta_2)$$
$$y = L_1\sin\theta_1 + L_2\sin(\theta_1+\theta_2)$$

Esto **ya es cinemática directa**: da la posición de la punta a partir de los ángulos de las articulaciones. El Bloque 11 generaliza esta misma idea a brazos de cualquier número de eslabones en 3D con la convención de Denavit-Hartenberg; aquí se ve el caso más simple, a mano, para poder predecir el resultado antes de que una librería lo calcule.

El **espacio de trabajo** (todos los puntos que la punta puede alcanzar) se obtiene barriendo $\theta_1$ y $\theta_2$ en todo su rango y graficando cada punto resultante.

### 3. En la vida real

Ver `codigo/bloque_01/cinematica_2r.py`: implementa `cinematica_directa_2r(theta1, theta2, L1, L2)` y genera la nube de puntos del espacio de trabajo.

### 4. Limitaciones

Se asume que el brazo es plano (2D) y que los eslabones son rígidos y no chocan entre sí ni con nada más. En 3D hace falta el Bloque 08 en adelante.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La punta calculada no coincide con lo que se ve al mover el brazo a mano | Se usó $\theta_2$ como ángulo absoluto en vez de relativo al primer eslabón | Probar con $\theta_1=0$: si ahí el resultado sí es correcto pero falla con $\theta_1\neq0$, es este error | Usar $\theta_1+\theta_2$ (no solo $\theta_2$) en el segundo término |
| El espacio de trabajo graficado es un disco lleno cuando debería tener un agujero en el centro | No se respetaron los límites reales de $\theta_1,\theta_2$, o $L_1 = L_2$ hace que sí llegue al centro | Revisar si $L_1 \neq L_2$: si son iguales, el brazo si alcanza el origen | Ajustar $L_1,L_2$ o los límites articulares según el brazo real |

### 6. Dónde más aparece la idea

Es el mismo patrón de "encadenar ángulos y longitudes" que usan los brazos robóticos reales (Bloque 11), los mecanismos de cuatro barras, y cualquier cadena de eslabones en 2D.

### 7. Ejemplos resueltos

**Ejemplo (el problema del bloque):** $L_1=0.30$ m, $L_2=0.20$ m, $\theta_1=40°$, $\theta_2=30°$.

$$x = 0.30\cos40° + 0.20\cos70° \approx 0.230 + 0.068 = 0.298\ \text{m}$$
$$y = 0.30\sin40° + 0.20\sin70° \approx 0.193 + 0.188 = 0.381\ \text{m}$$

Verificación en código: `cinematica_directa_2r(np.radians(40), np.radians(30), 0.30, 0.20)` → `(0.298, 0.381)`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el ángulo del segundo eslabón respecto al eje x fijo es $\theta_1+\theta_2$ y no $\theta_2$ solo.

**Serie B — Cálculo a mano**
- B1. Con $L_1=0.30$ m, $L_2=0.20$ m, calcular la posición de la punta para $\theta_1=90°,\theta_2=-90°$ y para $\theta_1=0°,\theta_2=0°$.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_01/cinematica_2r.py`, verificar a mano dos o tres de los puntos que grafica, y describir la forma del espacio de trabajo (¿es un disco completo?, ¿tiene un agujero?).

## Lo que este bloque agrega a `codigo/robotica/`

Nada todavía: la cinemática del 2R de este bloque vive en `codigo/bloque_01/` como ejercicio a mano. La librería propia empieza a crecer en el Bloque 02 con `robotica/vectores.py`.

## Glosario del bloque

| Término | Definición |
|---|---|
| Radián | Unidad de ángulo: el que subtiende, sobre un círculo de radio $r$, un arco de longitud $r$. Una vuelta completa son $2\pi$ radianes. |
| `atan2(y, x)` | Función de dos argumentos que da el ángulo de un vector $(x,y)$ respetando el cuadrante, a diferencia de `atan(y/x)`. |
| Ley de cosenos | Generalización del teorema de Pitágoras a triángulos sin ángulo recto: $c^2=a^2+b^2-2ab\cos\gamma$. |
| Espacio de trabajo (*workspace*) | Conjunto de todos los puntos que la punta de un brazo puede alcanzar, dados los límites de sus articulaciones. |
| Brazo 2R | Brazo plano de dos eslabones unidos por dos articulaciones de rotación (*Revolute*). |
