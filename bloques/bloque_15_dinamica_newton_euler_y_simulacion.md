# Bloque 15 — Dinámica por Newton-Euler y simulación

> **Problema que abre el bloque:** Lagrange produce ecuaciones enormes para 4 GDL o más, y un controlador necesita el par en milisegundos.
>
> **Necesitas antes:** Bloque 14. · **Lectura:** Barrientos, cap. 5; Craig, *Introduction to Robotics*, capítulo de dinámica.

Original: `robotica-manipuladores` no tiene dinámica de manipuladores más allá del tensor de inercia
(Bloque 06) — ver [docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md).

## Tema 15.1 — El algoritmo recursivo: velocidades hacia afuera, fuerzas hacia adentro

### 1. El problema

El Bloque 14 dedujo $M,C,G$ del 2R con SymPy en unos segundos. Para un brazo de 6 GDL, la misma deducción simbólica genera expresiones de miles de términos, y evaluarlas numéricamente en cada instante de una simulación o de un lazo de control (Bloque 20, cientos de veces por segundo) es demasiado lento. Hace falta un método que dé el mismo resultado sin pasar por una fórmula simbólica gigante.

### 2. El mecanismo

El algoritmo de **Newton-Euler recursivo** calcula la dinámica inversa ($\vec\tau$ a partir de $\vec q,\dot{\vec q},\ddot{\vec q}$, Bloque 14 Tema 14.1) eslabón por eslabón, en dos pasadas:

- **Hacia afuera** (de la base a la punta, $i=1,\ldots,n$): usando que la velocidad y aceleración angular de cada eslabón es la del anterior más lo que aporta su propia articulación (Bloque 06, Tema 6.2: $\vec v=\vec\omega\times\vec r$, la misma fórmula de velocidad de un punto de un cuerpo rígido), se calculan $\vec\omega_i,\vec\alpha_i$ y la aceleración lineal de cada centro de masa, **sin necesitar la postura completa del brazo de antemano**: cada eslabón solo usa lo que ya calculó el anterior.
- **Hacia adentro** (de la punta a la base, $i=n,\ldots,1$): con las aceleraciones ya conocidas, se calcula la fuerza y el par que cada eslabón necesita (Bloque 06: $F=ma$, $\tau=I\alpha$), y se propaga hacia la base sumando las reacciones que cada eslabón recibe del siguiente (la tercera ley de Newton, acción y reacción, en cada articulación) — el par que hace falta en la articulación $i$ es, literalmente, "lo que necesita este eslabón más lo que ya necesitaban todos los que están más allá".

Un truco práctico: incluir la gravedad como si la base tuviera una aceleración $\vec a_0=(0,g,0)$ hacia arriba (en vez de sumar un término de peso aparte a cada eslabón) hace que el mismo algoritmo, sin ninguna rama especial, incluya automáticamente el par de gravedad $G(\vec q)$ del Bloque 14 — una simplificación algorítmica, no un truco físico.

### 3. En la vida real

`robotica.dinamica.newton_euler_plano(theta, thetadot, thetaddot, m, L, lc, I, g)` implementa exactamente este algoritmo para una cadena planar de $n$ eslabones rotacionales, verificado contra el modelo de Lagrange del Bloque 14 (con masas puntuales y con varillas uniformes de inercia distribuida) con error del orden de $10^{-15}$ (precisión de máquina) en decenas de posturas aleatorias.

### 4. Limitaciones

La versión de este curso está escrita para el caso **planar** (todas las articulaciones rotacionales alrededor de ejes paralelos, como el 2R o el 3R plano); el caso espacial general (Barrientos, Craig) sigue exactamente la misma estructura de dos pasadas, pero con velocidades y fuerzas como vectores 3D completos y matrices de rotación entre eslabones (Bloque 08) en vez de ángulos escalares — más álgebra, misma idea.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Los pares calculados con Newton-Euler no coinciden con los de Lagrange para el mismo brazo | Error de signo en la propagación de fuerzas/momentos hacia adentro (el error más fácil de cometer en este algoritmo) | Comparar contra Lagrange (Bloque 14) para casos aleatorios, no solo para $\vec q=\vec0$ | Revisar con cuidado el signo de cada término de la recursión hacia adentro; un solo signo mal puede dar resultados "casi correctos" en algunas posturas y muy mal en otras |

### 6. Dónde más aparece la idea

Cualquier algoritmo recursivo que evita repetir cálculo global aprovechando estructura local (propagación de errores hacia adelante y hacia atrás en redes neuronales, algoritmos de programación dinámica), simuladores de física de videojuegos y de robots (PyBullet, MuJoCo) que usan variantes de este mismo algoritmo internamente.

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R con $m_1=1.3,m_2=0.7$ kg, $L_1=0.30,L_2=0.20$ m (masas puntuales en la punta de cada eslabón), en $\theta_1=30°,\theta_2=45°,\dot\theta_1=0.5,\dot\theta_2=0.3,\ddot\theta_1=0.1,\ddot\theta_2=-0.2$: `newton_euler_plano` da $\vec\tau\approx(5.457,0.363)$ N·m — el mismo resultado, verificado en el laboratorio, que evaluar las ecuaciones de Lagrange del Bloque 14 en ese mismo punto.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, en una frase, por qué el algoritmo necesita dos pasadas (afuera y adentro) y no le alcanza con una sola.

**Serie B — Cálculo a mano**
- B1. Para un solo eslabón ($n=1$, un péndulo con motor), escribir a mano las ecuaciones de la pasada hacia afuera y hacia adentro, y verificar que se reducen a $\tau=I\ddot\theta+mgL_c\cos\theta$ (con $L_c$ la distancia al centro de masa).

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_15/newton_euler_vs_lagrange.py`: compara `newton_euler_plano` contra las ecuaciones de Lagrange del Bloque 14 en decenas de posturas aleatorias, con masas puntuales y con varillas uniformes.

---

## Tema 15.2 — Costo computacional: Newton-Euler contra Lagrange

### 1. El problema

Ambos métodos dan el mismo resultado (Tema 15.1). ¿Por qué entonces se enseñan los dos, en vez de quedarse con uno solo?

### 2. El mecanismo

- **Lagrange simbólico** (Bloque 14): produce una **fórmula cerrada** para $M,C,G$ — valiosa para *entender* la estructura del problema (qué términos existen, cómo dependen de la postura, Bloque 14 Tema 14.5), para verificar propiedades (simetría, definitud positiva, Tema 14.6), y para diseñar controladores que cancelan términos específicos (Bloque 20). Pero evaluarla numéricamente, para $n$ grande, es costosa: el número de términos de $C(\vec q,\dot{\vec q})$ crece rápidamente con $n$.
- **Newton-Euler recursivo** (Tema 15.1): no da una fórmula cerrada — da un **procedimiento numérico** que, para una postura y velocidad concretas, calcula $\vec\tau$ con un costo que crece **linealmente** con el número de eslabones $n$ (cada eslabón hace un trabajo fijo en cada pasada), muy por debajo del crecimiento de Lagrange simbólico.

La consecuencia práctica: Lagrange (o su resultado ya simplificado una vez) se usa para *diseñar* y *entender*; Newton-Euler se usa para *calcular en tiempo real*, dentro de un lazo de control que corre cientos o miles de veces por segundo (Bloque 18, Bloque 20) — ahí no hay margen para evaluar una expresión simbólica gigante en cada paso.

### 3. En la vida real

Las librerías profesionales de robótica (Robotics Toolbox, `rne()`, y los motores de simulación física como PyBullet) usan Newton-Euler recursivo (o variantes más sofisticadas del mismo principio, como el algoritmo de Featherstone) para la dinámica inversa y directa en tiempo real, reservando la formulación de Lagrange para el análisis y diseño.

### 4. Limitaciones

Para brazos con muy pocos GDL (2-3, como los de este curso), la diferencia de costo es poco relevante en la práctica; la elección importa de verdad a partir de 6 GDL o más, o cuando el par debe recalcularse a alta frecuencia (Bloque 18).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un controlador en tiempo real (Bloque 20) se retrasa o no alcanza a calcular el par a tiempo | Se está evaluando la expresión simbólica completa de Lagrange en cada paso del lazo de control, en vez de Newton-Euler | Medir el tiempo de cómputo de cada método para el mismo brazo | Usar Newton-Euler (o una versión ya optimizada de Lagrange) dentro del lazo de control |

### 6. Dónde más aparece la idea

La misma disyuntiva "fórmula cerrada para entender, algoritmo eficiente para calcular" aparece en optimización (forma cerrada de un mínimo contra descenso de gradiente iterativo), en cálculo simbólico contra numérico en general (Bloque 04).

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R, ambos métodos son rápidos (la diferencia es imperceptible); para el catálogo de 6 GDL del Bloque 11 (`curso_6gdl`, `abb_6gdl`), la expresión simbólica de $C(\vec q,\dot{\vec q})$ con Lagrange ya tiene cientos de términos, mientras que Newton-Euler recursivo mantiene el mismo costo por eslabón sin importar $n$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el número de términos de $C(\vec q,\dot{\vec q})\dot{\vec q}$ (Bloque 14) crece más rápido que linealmente con $n$, pensando en cuántos pares de velocidades $\dot q_i\dot q_j$ distintos existen para $n$ articulaciones.

**Serie B — Cálculo a mano**
- B1. Contar cuántos términos cuadráticos distintos ($\dot q_i\dot q_j$, incluyendo $i=j$) hay para $n=2,3,6$ articulaciones.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_15/costo_computacional.py`: mide, para brazos de 2 y 3 eslabones, tanto el tiempo de **construir** el modelo simbólico de Lagrange (el que realmente explota con $n$) como el de evaluarlo ya construido, y compara ambos contra Newton-Euler recursivo (que no necesita ninguna construcción previa).

---

## Tema 15.3 — Dinámica directa para simular

### 1. El problema

Todo lo anterior calcula $\vec\tau$ a partir del movimiento (dinámica inversa). Para **simular** el brazo (Bloque 05: dado un par aplicado, ver cómo se mueve, sin prescribir el movimiento de antemano) hace falta la dirección opuesta.

### 2. El mecanismo

De la forma general (Bloque 14, Tema 14.5):

$$M(\vec q)\ddot{\vec q}+C(\vec q,\dot{\vec q})\dot{\vec q}+G(\vec q)=\vec\tau \quad\Longrightarrow\quad \ddot{\vec q}=M(\vec q)^{-1}\big(\vec\tau-C(\vec q,\dot{\vec q})\dot{\vec q}-G(\vec q)\big)$$

Esta es la **dinámica directa**: dado $\vec\tau(t)$ (constante, o calculado por un controlador, Bloque 18), se obtiene $\ddot{\vec q}$, y de ahí $\dot{\vec q},\vec q$ integrando en el tiempo (Bloque 05, Euler o RK4) — exactamente el mismo patrón del péndulo del Bloque 05, ahora con $M^{-1}$ en vez de $1/(mL^2)$, y con $C\dot{\vec q}+G$ en vez de solo el término de gravedad.

Que $M$ sea siempre invertible (Bloque 14, Tema 14.6: simétrica y definida positiva) es lo que garantiza que esta división (multiplicación por $M^{-1}$) siempre tiene sentido, para cualquier postura física del brazo.

### 3. En la vida real

```python
def f(t, z, tau):
    q, qdot = z[:n], z[n:]
    Mn = M_f(*q)
    resto = (C_qdot_f(*q, *qdot) + G_f(*q)).flatten()
    qddot = np.linalg.solve(Mn, tau - resto)
    return np.concatenate([qdot, qddot])

from robotica.simular import rk4
Z = rk4(lambda t, z: f(t, z, tau_aplicado), z0, t)
```

(el mismo `robotica.simular.rk4` del Bloque 05, ahora integrando el estado $(\vec q,\dot{\vec q})$ completo de un brazo con motores, no solo un péndulo libre).

### 4. Limitaciones

Igual que en el Bloque 05: el resultado depende de la precisión del integrador numérico (Tema 5.5) y puede ser inestable con pasos grandes (Tema 5.6) — la dinámica de un brazo con varios eslabones acoplados suele ser más sensible a esto que un péndulo simple.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una simulación de dinámica directa "explota" (valores que crecen sin control) para un brazo sin fricción y par constante razonable | Paso de integración demasiado grande para la rigidez del sistema (Bloque 05, Tema 5.6), agravado por el acoplamiento entre eslabones | Reducir el paso, o usar RK4 en vez de Euler | Verificar conservación de energía (sin fricción, debería mantenerse aproximadamente constante si $\tau=0$) como diagnóstico, igual que en el Bloque 05 |

### 6. Dónde más aparece la idea

Cualquier simulador físico de un robot o mecanismo articulado (PyBullet, MuJoCo, Gazebo) resuelve, en el fondo, esta misma ecuación en cada paso de tiempo.

### 7. Ejemplos resueltos

**Ejemplo:** el 2R con $\tau=\vec0$ (sin motores) es exactamente el péndulo doble del Bloque 14 (Tema 14.3): la dinámica directa con par cero reproduce ese mismo comportamiento, incluida la sensibilidad caótica para amplitudes grandes.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, sin fricción y sin par aplicado, la energía mecánica total del brazo debería mantenerse aproximadamente constante en la simulación (Bloque 05, Tema 5.6) — y qué significaría que no fuera así.

**Serie B — Cálculo a mano**
- B1. Para un solo eslabón (péndulo con motor), escribir la dinámica directa $\ddot\theta=(\tau-mgL_c\cos\theta)/I$ a partir de la inversa del Tema 15.1 (Ejercicio B1).

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_15/simular_2r_par_constante.py`: simula el 2R con un par constante en cada motor usando dinámica directa y `robotica.simular.rk4`, y grafica $\theta_1(t),\theta_2(t)$.

---

## Tema 15.4 — Modelo en espacio de estados del brazo

### 1. El problema

Para conectar la dinámica del brazo con las herramientas de control de la Parte V (Bloques 17-20), hace falta escribirla en la forma estándar de "espacio de estados" que esa teoría espera — la misma idea del Bloque 05 (Tema 5.2), ahora aplicada a un sistema con $2n$ variables de estado en vez de 2.

### 2. El mecanismo

El **estado** del brazo (Bloque 05, Tema 5.2: la información mínima para predecir el futuro) es $\vec z=(\vec q,\dot{\vec q})\in\mathbb R^{2n}$: posición y velocidad de cada articulación. La dinámica directa (Tema 15.3) escrita como sistema de primer orden:

$$\dot{\vec z} = \begin{pmatrix}\dot{\vec q}\\ M(\vec q)^{-1}\big(\vec\tau-C(\vec q,\dot{\vec q})\dot{\vec q}-G(\vec q)\big)\end{pmatrix} = f(\vec z,\vec\tau)$$

es exactamente la forma $\dot{\vec z}=f(\vec z,\vec u)$ que la Parte V va a usar para diseñar controladores: $\vec z$ es el estado, $\vec\tau$ es la **entrada de control** (lo que el controlador decide en cada instante), y $f$ es no lineal en general (por $M^{-1}$, $C$, $G$) — la razón de ser del control no lineal del Bloque 20 (par calculado), frente al control lineal más simple del Bloque 18 (PID), que funciona bien solo cerca de un punto de operación (Bloque 04, Tema 4.5: linealización).

### 3. En la vida real

Esta es exactamente la función `f(t, z, tau)` ya escrita en el Tema 15.3 — el mismo patrón que el Bloque 05 usó para el péndulo, generalizado a $2n$ variables de estado y con $\vec\tau$ como entrada explícita en vez de estar fijo de antemano.

### 4. Limitaciones

Ninguna nueva: es una forma de organizar la misma información, no una aproximación.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Al conectar el modelo dinámico con un controlador (Parte V), el código no sabe cómo actualizar $\vec q$ y $\dot{\vec q}$ por separado | No se organizó el estado como $\vec z=(\vec q,\dot{\vec q})$ concatenado, con las primeras $n$ componentes de $\dot{\vec z}$ iguales a las últimas $n$ de $\vec z$ | Verificar que `f(t,z,tau)[:n] == z[n:]` siempre (por construcción) | Seguir la forma estándar $\dot{\vec z}=(\dot{\vec q},\ddot{\vec q})$, nunca mezclar el orden |

### 6. Dónde más aparece la idea

El espacio de estados es el lenguaje universal de la teoría de control moderna (desde un termostato hasta un cohete); cualquier sistema dinámico se piensa así antes de diseñar un controlador.

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R, el estado es $\vec z=(\theta_1,\theta_2,\dot\theta_1,\dot\theta_2)\in\mathbb R^4$; el péndulo simple del Bloque 05 era el caso particular $n=1$, $\vec z=(\theta,\dot\theta)\in\mathbb R^2$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $f(\vec z,\vec\tau)$ es no lineal en $\vec z$ aunque $\vec\tau$ entre de forma lineal en la ecuación (pista: mirar dónde aparecen $M^{-1}$, $C$, $\text{sen}/\cos$ en $G$).

**Serie B — Cálculo a mano**
- B1. Escribir el vector de estado y la función $f$ completa (en símbolos, sin evaluar) para un brazo de 3 GDL.

**Serie C — Laboratorio**
- C1. Extender `codigo/bloque_15/simular_2r_par_constante.py` para recibir $\vec\tau(t)$ como una función del tiempo (por ejemplo, un escalón) en vez de una constante, y simular la respuesta.

---

## Tema 15.5 — Parámetros dinámicos: de dónde salen $m$, $L_c$, $I$

### 1. El problema

Todas las fórmulas de este bloque y del Bloque 14 necesitan, como datos de entrada, la masa, el centro de masa y el tensor de inercia de cada eslabón real. Ninguno de esos números aparece solo: hay que obtenerlos.

### 2. El mecanismo

Tres caminos, de más a menos preciso en general (y de más a menos disponible según la etapa del proyecto):

- **Del modelo CAD** (Bloque 21): un modelo paramétrico en build123d, con la densidad del material asignada, calcula masa, centro de masa y tensor de inercia automáticamente por integración (exactamente el cálculo del Bloque 06, Tema 6.4, aplicado a la geometría real en vez de un prisma idealizado). Es el camino más preciso si el diseño ya existe en CAD.
- **Midiendo directamente**: pesar cada eslabón (masa), encontrar su punto de equilibrio (centro de masa, Bloque 06 Tema 6.1), y estimar el momento de inercia con un péndulo físico (medir el período de oscilación de la pieza colgada de un punto conocido, y despejar $I$ de la fórmula del período — un método clásico de laboratorio de física). Es el camino más directo cuando la pieza física ya existe pero no hay CAD confiable.
- **Identificación**: si ninguno de los dos anteriores es práctico (por ejemplo, los parámetros cambian con una carga desconocida en la pinza), se puede *ajustar* los parámetros dinámicos a partir de datos de movimiento real: mover el brazo con pares conocidos, medir cómo se mueve, y resolver un problema de mínimos cuadrados (Bloque 03, Tema 3.6) que encuentre los parámetros que mejor expliquen las mediciones — el mismo tipo de ajuste que calibra cualquier modelo a partir de datos, fuera del alcance de deducirlo en detalle aquí pero importante saber que existe.

### 3. En la vida real

Para el proyecto integrador (Bloque 24), la combinación típica es: masa y centro de masa medidos directamente (una balanza y un punto de equilibrio son fáciles de conseguir), momento de inercia estimado del CAD si existe, o con el método del péndulo físico si no.

### 4. Limitaciones

Los tres métodos tienen su propio error: el CAD asume una densidad uniforme del material (rara vez exacta, por tornillos, cables y huecos internos); medir a mano tiene el error humano típico de cualquier medición; la identificación depende de la calidad y variedad de los datos de movimiento usados.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El par calculado (Newton-Euler o Lagrange) no coincide con el que realmente hace falta en el brazo real | Los parámetros dinámicos usados en el modelo (masa, $L_c$, $I$) no corresponden a los del brazo físico | Comparar la masa y el centro de masa medidos contra los usados en el modelo | Remedir o recalcular los parámetros; considerar piezas añadidas (cableado, conectores) que el CAD idealizado no incluye (Bloque 06, Tema 6.1) |

### 6. Dónde más aparece la idea

Calibración de cualquier modelo físico contra la realidad: parámetros de un circuito eléctrico, coeficientes de fricción, constantes de un motor (Bloque 16) — casi siempre alguna combinación de "calculado", "medido" e "identificado".

### 7. Ejemplos resueltos

**Ejemplo:** para un eslabón de aluminio de forma simple, el CAD puede dar $I$ con más de 3 cifras significativas de precisión (si la densidad del material es bien conocida); para el mismo eslabón con un motor y cableado añadidos, medir con un péndulo físico suele ser más confiable que confiar en un CAD que no modela esas piezas extra en detalle.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar en qué situación conviene identificar los parámetros dinámicos a partir de datos de movimiento en vez de medirlos directamente (pista: pensar en una carga que cambia de una tarea a otra).

**Serie B — Cálculo a mano**
- B1. La fórmula del período de un péndulo físico es $T=2\pi\sqrt{I_p/(mgL_c)}$, con $I_p$ el momento de inercia respecto al punto de suspensión (Bloque 06, Tema 6.3: Steiner). Despejar $I_p$ en función de $T,m,g,L_c$.

**Serie C — Laboratorio**
- C1. Con la fórmula de B1, escribir una función en Python que, dado el período medido de un péndulo físico (masa y $L_c$ conocidos), devuelva $I_p$ y, restando $mL_c^2$ (Steiner), el momento de inercia respecto al centro de masa.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/dinamica.py` (extendido): `newton_euler_plano` — dinámica inversa recursiva para una cadena planar de eslabones rotacionales.

## Glosario del bloque

| Término | Definición |
|---|---|
| Newton-Euler recursivo | Algoritmo de dinámica inversa en dos pasadas: velocidades/aceleraciones hacia afuera, fuerzas/pares hacia adentro. |
| Espacio de estados | Representación $\dot{\vec z}=f(\vec z,\vec u)$ de un sistema dinámico, con $\vec z$ el estado y $\vec u$ la entrada de control. |
| Parámetros dinámicos | Masa, centro de masa y tensor de inercia de cada eslabón; se obtienen del CAD, midiendo, o por identificación. |
| Péndulo físico | Cuerpo rígido que oscila alrededor de un punto de suspensión; su período de oscilación permite medir su momento de inercia. |
