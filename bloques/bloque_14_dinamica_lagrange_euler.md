# Bloque 14 — Dinámica por Lagrange-Euler

> **Problema que abre el bloque:** la simulación cinemática mueve el brazo perfecto. El brazo real no llega, oscila o el servo se quema. Falta saber qué par necesita cada motor.
>
> **Necesitas antes:** Bloque 13 (abre la Parte IV). · **Lectura:** Barrientos, cap. 5; Spong, Hutchinson & Vidyasagar, capítulo de dinámica.

`robotica-manipuladores` no tiene dinámica de manipuladores completa (solo el tensor de inercia de
un prisma, que ya se usó en el Bloque 06): este bloque es **original** — ver
[docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md).

## Tema 14.1 — Dinámica inversa y dinámica directa

### 1. El problema

Todo lo visto hasta el Bloque 13 es cinemática: relaciona ángulos, velocidades y posiciones, sin preguntarse nunca **por qué** el brazo se mueve así. Un motor real no puede ejecutar "muévete con esta aceleración": solo puede aplicar un par, y hace falta saber la relación entre ambos.

### 2. El mecanismo

Dos preguntas, inversas entre sí:

- **Dinámica inversa**: dado el movimiento deseado ($\vec q,\dot{\vec q},\ddot{\vec q}$), ¿qué par $\vec\tau$ hace falta en cada motor? Es la que responde el problema que abre el bloque, y la que usa un controlador en tiempo real (Bloque 20: par calculado).
- **Dinámica directa**: dado el par aplicado $\vec\tau$, ¿cómo se mueve el brazo ($\ddot{\vec q}$, y de ahí $\dot{\vec q},\vec q$ integrando, Bloque 05)? Es la que hace falta para **simular** el brazo de forma realista (Bloque 15), en vez de solo animarlo cinemáticamente como hasta ahora.

Ambas preguntas comparten el mismo modelo matemático (Tema 14.5): la dinámica inversa evalúa la fórmula directamente; la directa requiere despejar $\ddot{\vec q}$ de ella (una inversión de matriz, Bloque 03).

### 3. En la vida real

Hasta el Bloque 13, `codigo/bloque_NN/` animaba brazos especificando $\vec q(t)$ directamente (cinemática pura). Desde este bloque, una simulación *dinámicamente* realista parte de un par $\vec\tau(t)$ (o de una fuerza externa) y **calcula** $\vec q(t)$ resolviendo la dinámica directa — una diferencia cualitativa, no solo de detalle.

### 4. Limitaciones

Ninguna nueva: es una distinción de qué es el dato y qué es la incógnita, no una aproximación.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una simulación "dinámica" en realidad solo anima $\vec q(t)$ elegido a mano, sin ningún par de por medio | Se confundió cinemática con dinámica: mover el brazo con ángulos prescritos no verifica que esos ángulos sean físicamente alcanzables con un motor real | Preguntar: ¿de dónde sale $\vec q(t)$? Si se especificó directamente, es cinemática | Para una simulación dinámica real, integrar $\ddot{\vec q}=f(\vec q,\dot{\vec q},\vec\tau)$ (Bloque 15), no prescribir $\vec q(t)$ |

### 6. Dónde más aparece la idea

Cualquier sistema de control: "qué entrada hace falta para este resultado" (inversa) contra "qué resultado da esta entrada" (directa) — la misma dualidad de la cinemática (Bloques 11-12), ahora aplicada a fuerzas en vez de posiciones.

### 7. Ejemplos resueltos

**Ejemplo:** el péndulo del Bloque 05 resuelto con $\tau=0$ (sin motor, solo gravedad) es un caso de dinámica directa: se integra $\ddot\theta=-\frac gL\sin\theta$ para obtener $\theta(t)$. Preguntarse "¿qué $\tau(t)$ haría falta para que el péndulo siguiera una trayectoria $\theta_d(t)$ elegida de antemano?" es dinámica inversa.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Clasificar como dinámica directa o inversa: (a) calcular el par necesario para que un brazo siga una trayectoria dada; (b) simular cómo cae un brazo al que se le corta la energía a los motores.

**Serie B — Cálculo a mano**
- B1. Para $\tau=I\ddot\theta$ (Bloque 06, Tema 6.2, caso escalar), escribir la fórmula de la dinámica inversa y la de la directa.

**Serie C — Laboratorio**
- C1. Nada nuevo todavía: se practica en los Temas 14.2–14.5.

---

## Tema 14.2 — El lagrangiano y la ecuación de Lagrange

### 1. El problema

Deducir la dinámica de un brazo con las leyes de Newton "a mano", eslabón por eslabón, sumando fuerzas de reacción entre piezas conectadas, es tedioso y propenso a errores incluso para 2 GDL. Hace falta un método que llegue a las mismas ecuaciones partiendo de una sola función escalar.

### 2. El mecanismo

El **lagrangiano** es la diferencia entre energía cinética y potencial (Bloque 06, Tema 6.5), en función de las coordenadas generalizadas $\vec q$ y sus velocidades $\dot{\vec q}$:

$$L(\vec q,\dot{\vec q}) = K(\vec q,\dot{\vec q}) - U(\vec q)$$

La **ecuación de Lagrange** dice que, para cada coordenada $q_i$, el par generalizado que actúa sobre ella cumple:

$$\tau_i = \frac{d}{dt}\left(\frac{\partial L}{\partial\dot q_i}\right) - \frac{\partial L}{\partial q_i}$$

De dónde sale esta fórmula (idea, no demostración formal): es una consecuencia del **principio de mínima acción** — de todas las trayectorias posibles entre dos configuraciones, la que el sistema realmente sigue es la que hace estacionaria (típicamente mínima) la integral de $L$ en el tiempo. No hace falta demostrar esto para usarlo: lo notable, y lo que se verifica en el laboratorio, es que aplicar esta receta a $K-U$ de un sistema conocido (el péndulo del Bloque 05) reproduce exactamente la ecuación que ya se dedujo con Newton directamente — dos caminos, mismo resultado.

La ventaja práctica: $K$ y $U$ son **escalares** (mucho más simples de escribir que fuerzas vectoriales con sus reacciones), y derivarlas —aunque tedioso a mano para más de 2 GDL— es mecánico y automatizable con SymPy (Bloque 04, Tema 4.1).

### 3. En la vida real

`robotica/dinamica.py` implementa `deducir_lagrange(K, U, coords, t)`: dadas $K,U$ simbólicas (SymPy) en función de coordenadas que son funciones del tiempo, aplica la receta de la sección 2 automáticamente y devuelve las ecuaciones ya en símbolos algebraicos limpios ($q_i$, $\dot q_i$, $\ddot q_i$), listas para trabajar.

### 4. Limitaciones

El método asume que las coordenadas $\vec q$ son **independientes** (sin restricciones adicionales entre ellas) — válido para cadenas cinemáticas abiertas (Bloque 07), no directamente para cadenas cerradas.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Las ecuaciones deducidas con Lagrange no coinciden con las de Newton para un caso conocido (el péndulo) | Error al escribir $K$ o $U$ en función de las coordenadas elegidas (por ejemplo, velocidad mal derivada) | Reconstruir $K,U$ para el caso más simple posible y comparar contra la ecuación ya conocida | Revisar la posición y velocidad de cada masa antes de sustituir en $K,U$ |

### 6. Dónde más aparece la idea

La mecánica lagrangiana es el lenguaje estándar de la física teórica (desde partículas hasta campos); en ingeniería, es la base de la dinámica de cualquier sistema multicuerpo (vehículos, robots, estructuras).

### 7. Ejemplos resueltos

**Ejemplo:** para el péndulo simple ($K=\tfrac12mL^2\dot\theta^2$, $U=-mgL\cos\theta$, con $\theta=0$ hacia abajo): $\dfrac{\partial L}{\partial\dot\theta}=mL^2\dot\theta$, $\dfrac{d}{dt}(\cdot)=mL^2\ddot\theta$; $\dfrac{\partial L}{\partial\theta}=-mgL\sin\theta$. La ecuación de Lagrange da $mL^2\ddot\theta+mgL\sin\theta=0$ — exactamente la del Bloque 05, Tema 5.3, deducida ahí con Newton directamente.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $K,U$ escalares son más fáciles de escribir que las fuerzas de reacción entre eslabones vectoriales.

**Serie B — Cálculo a mano**
- B1. Repetir la deducción del ejemplo resuelto paso a paso, sin saltar ninguna derivada.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_14/lagrange_pendulo.py`: verifica con `robotica.dinamica.deducir_lagrange` que el péndulo simple reproduce la ecuación del Bloque 05.

---

## Tema 14.3 — Péndulo simple y doble como primeros casos

### 1. El problema

Antes de encarar un brazo completo, conviene practicar el método con dos casos progresivamente más complejos: el péndulo simple (ya resuelto con Newton, Bloque 05, y ahora con Lagrange, Tema 14.2) y el péndulo doble, el primer caso con **dos** coordenadas generalizadas acopladas — el primer sistema verdaderamente representativo de lo que hace falta para un brazo de varios eslabones.

### 2. El mecanismo

El **péndulo doble** (dos varillas de masas puntuales $m_1,m_2$ y longitudes $L_1,L_2$, la segunda colgando de la primera) tiene coordenadas $\theta_1,\theta_2$ (cada ángulo medido desde la vertical, o el segundo relativo al primero, según convención). Las posiciones de las masas:

$$x_1=L_1\sin\theta_1,\ y_1=-L_1\cos\theta_1;\qquad x_2=x_1+L_2\sin\theta_2,\ y_2=y_1-L_2\cos\theta_2$$

(nótese el parecido estructural con la cinemática del 2R, Bloque 01 — un péndulo doble es, cinemáticamente, casi el mismo problema que un brazo 2R, solo que sin motores: se mueve libremente por gravedad). $K=\tfrac12m_1(\dot x_1^2+\dot y_1^2)+\tfrac12m_2(\dot x_2^2+\dot y_2^2)$, $U=m_1gy_1+m_2gy_2$; aplicando la receta del Tema 14.2 salen dos ecuaciones acopladas —$\ddot\theta_1$ depende de $\theta_2,\dot\theta_2$ y viceversa— con la misma estructura de términos de masa, Coriolis/centrífugos y gravedad que va a aparecer, ya con motores, en el brazo 2R del Tema 14.4.

El péndulo doble es famoso además por ser un ejemplo clásico de **caos**: para amplitudes grandes, dos condiciones iniciales casi idénticas divergen exponencialmente — un recordatorio de que "determinista" (las ecuaciones no tienen ningún término aleatorio) no es lo mismo que "predecible a largo plazo" en la práctica, por la sensibilidad extrema del error numérico (Bloque 05, Tema 5.6).

### 3. En la vida real

`codigo/bloque_14/lagrange_pendulo_doble.py` deduce las ecuaciones con SymPy y simula el péndulo doble con `robotica.simular.rk4` (Bloque 05), mostrando el comportamiento caótico para amplitudes grandes.

### 4. Limitaciones

El modelo usa masas puntuales (sin tensor de inercia propio, Bloque 06); para varillas con masa distribuida hace falta incluir también la energía cinética de rotación de cada varilla.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Dos simulaciones del péndulo doble con condiciones iniciales casi idénticas divergen rápidamente, y se sospecha un error de código | Es el comportamiento **esperado** de un sistema caótico para amplitudes grandes, no necesariamente un bug | Repetir con amplitudes pequeñas: ahí el comportamiento debería ser mucho más parecido entre las dos simulaciones | Verificar primero con amplitudes pequeñas (régimen no caótico) antes de sospechar del código |

### 6. Dónde más aparece la idea

El péndulo doble es el ejemplo introductorio estándar de sistemas caóticos y dinámica no lineal; la misma sensibilidad a condiciones iniciales aparece en meteorología (el "efecto mariposa").

### 7. Ejemplos resueltos

**Ejemplo:** con $m_1=m_2=1$ kg, $L_1=L_2=1$ m, y ambos péndulos partiendo casi en reposo con una diferencia de $10^{-3}$ rad en $\theta_1(0)$, las dos trayectorias son casi indistinguibles durante 1-2 segundos y luego divergen completamente — el horizonte de predictibilidad típico de un sistema caótico.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar la diferencia entre "el sistema es impredecible porque las ecuaciones tienen algo aleatorio" (falso aquí) y "el sistema es impredecible en la práctica porque amplifica cualquier error inicial" (lo que realmente ocurre).

**Serie B — Cálculo a mano**
- B1. Escribir $K$ y $U$ del péndulo doble a partir de las posiciones de la sección 2 (sin derivar las ecuaciones completas, solo plantear $K,U$).

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_14/lagrange_pendulo_doble.py` y comparar dos simulaciones con condiciones iniciales que difieren en $10^{-3}$ rad, graficando cómo diverge la diferencia con el tiempo.

---

## Tema 14.4 — El brazo 2R completo

### 1. El problema

El péndulo doble (Tema 14.3) es cinemáticamente igual al brazo 2R, pero sin motores ni control: solo gravedad. El brazo 2R real del curso (Bloque 01, Bloque 11) tiene, además, pares $\tau_1,\tau_2$ aplicados por los motores en cada articulación — hace falta incorporarlos y llegar al modelo dinámico completo que el resto de la Parte IV usa constantemente.

### 2. El mecanismo

Con las mismas posiciones del 2R (Bloque 01, ahora con masas $m_1,m_2$ en cada eslabón, simplificadas como puntuales en el extremo de cada uno, igual que el péndulo doble del Tema 14.3) y aplicando la receta de Lagrange (Tema 14.2), el lado izquierdo de cada ecuación es $\dfrac{d}{dt}\dfrac{\partial L}{\partial\dot\theta_i}-\dfrac{\partial L}{\partial\theta_i}$; el lado derecho, ahora, **no es cero**: es el par $\tau_i$ que aplica el motor $i$. El resultado (verificado en el laboratorio, coincide con la deducción clásica de Spong et al.):

$$M(\vec\theta)\ddot{\vec\theta} + \vec c(\vec\theta,\dot{\vec\theta}) + \vec g(\vec\theta) = \vec\tau$$

con $M$ la matriz de masas del Tema 14.5, y $\vec c,\vec g$ los términos de Coriolis/centrífugos y de gravedad. La diferencia con el péndulo doble es puramente de interpretación: el mismo lado izquierdo, pero ahora igualado a $\vec\tau$ (lo que aplican los motores) en vez de a $\vec 0$ (movimiento libre).

### 3. En la vida real

```python
from robotica.dinamica import deducir_lagrange, matriz_masas, separar_gravedad_y_coriolis
ecuaciones, q, qdot, qddot = deducir_lagrange(K, U, [theta1, theta2], t)
M = matriz_masas(ecuaciones, qddot)
G, C_qdot = separar_gravedad_y_coriolis(ecuaciones, qdot, qddot)
```

### 4. Limitaciones

Como el péndulo doble, este modelo usa masas puntuales; el Bloque 15 (Newton-Euler) trabaja con el tensor de inercia completo de cada eslabón (Bloque 06), más realista para eslabones con masa distribuida.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El modelo del 2R con motores da las mismas ecuaciones que el péndulo doble libre | Se olvidó que el lado derecho ya no es cero: falta interpretar el resultado de Lagrange como $=\vec\tau$, no $=\vec 0$ | Verificar que, en las ecuaciones de movimiento planteadas para simular, el par aparezca explícitamente del lado derecho | Escribir $M\ddot{\vec\theta}+\vec c+\vec g=\vec\tau$ y despejar $\ddot{\vec\theta}$ para la dinámica directa (Tema 14.1), no asumir $\vec\tau=\vec0$ |

### 6. Dónde más aparece la idea

Es, literalmente, el modelo que reutilizan los Bloques 15 a 20 para simular, controlar y dimensionar motores del brazo del curso.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_14/lagrange_2r.py`, que deduce $M,\vec c,\vec g$ del 2R con `robotica.dinamica` y los compara contra la forma cerrada clásica de Spong et al. (mismo resultado que el péndulo doble del Tema 14.3, con $\tau$ del lado derecho).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el brazo 2R "colgado sin motores" ($\tau=\vec0$) es exactamente el péndulo doble del Tema 14.3.

**Serie B — Cálculo a mano**
- B1. Con las ecuaciones deducidas para el 2R, escribir qué par $\tau_1,\tau_2$ hace falta para mantenerlo perfectamente quieto ($\dot{\vec\theta}=\ddot{\vec\theta}=\vec0$) en una postura dada — comparar con el Bloque 13, Tema 13.7.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_14/lagrange_2r.py` y verificar B1 numéricamente: el par estático de Lagrange en $\dot{\vec\theta}=\ddot{\vec\theta}=0$ debe coincidir con $J^T\vec F$ del Bloque 13 para el peso de cada masa.

---

## Tema 14.5 — La forma general $M(\vec q)\ddot{\vec q}+C(\vec q,\dot{\vec q})\dot{\vec q}+G(\vec q)=\vec\tau$

### 1. El problema

El resultado del Tema 14.4, escrito a mano para un caso particular, hay que entenderlo también en su forma general, la que aparece en todos los libros de robótica y con la que se piensa la dinámica de cualquier brazo, no solo del 2R.

### 2. El mecanismo

Para cualquier manipulador de $n$ GDL, la dinámica siempre tiene esta forma, sin importar cuántos eslabones tenga:

$$M(\vec q)\ddot{\vec q} + C(\vec q,\dot{\vec q})\dot{\vec q} + G(\vec q) = \vec\tau$$

con significado físico preciso para cada término:

- $M(\vec q)\ddot{\vec q}$: **fuerzas de inercia** — la resistencia a acelerar, generalización de $F=ma$ (Bloque 06) a un sistema de varios GDL acoplados. $M$ depende de $\vec q$ (a diferencia de una masa constante) porque la distribución efectiva de masa "sentida" por cada articulación cambia con la postura (Bloque 06, Tema 6.3: el mismo fenómeno de Steiner, ahora dependiente de la configuración).
- $C(\vec q,\dot{\vec q})\dot{\vec q}$: **fuerzas de Coriolis y centrífugas** — aparecen solo cuando hay más de una articulación moviéndose a la vez (son cuadráticas en $\dot{\vec q}$, Tema 14.4: términos como $\dot\theta_1\dot\theta_2$ o $\dot\theta_2^2$), consecuencia de que el marco de cada eslabón se mueve respecto a los demás.
- $G(\vec q)$: **par de gravedad** — el que hace falta solo para sostener el brazo contra la gravedad en la postura $\vec q$, sin moverlo ($\dot{\vec q}=\ddot{\vec q}=\vec 0$): exactamente el $J^T\vec F$ del Bloque 13 (Tema 13.7), con $\vec F$ el peso de cada eslabón.

Esta descomposición no es solo notación: separar los tres efectos permite, por ejemplo, la **compensación de gravedad** del Bloque 20 (cancelar $G(\vec q)$ explícitamente con el control) sin tocar los otros dos términos.

### 3. En la vida real

`robotica.dinamica.separar_gravedad_y_coriolis` extrae $G$ y $C\dot{\vec q}$ automáticamente de las ecuaciones deducidas (Tema 14.2), evaluando el residuo en $\dot{\vec q}=\vec0$ para $G$ (exactamente la definición de la sección 2) y lo que queda para $C\dot{\vec q}$.

### 4. Limitaciones

Esta función devuelve el **vector** $C(\vec q,\dot{\vec q})\dot{\vec q}$ ya combinado, no la matriz $C(\vec q,\dot{\vec q})$ descompuesta por separado (que requeriría los símbolos de Christoffel, fuera del alcance de este curso) — suficiente para dinámica directa e inversa (Tema 14.1), no para ciertas técnicas de control avanzado que sí necesitan $C$ como matriz.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| $G(\vec q)$ calculado no es cero en ninguna postura, incluso para un brazo que debería estar equilibrado en algún punto | Puede ser correcto (la mayoría de los brazos no están equilibrados en ninguna postura sin motores) o puede haber un error de signo en $U$ | Verificar el signo de $U$ (energía potencial creciente hacia arriba) para cada masa | Revisar que $U=\sum m_igy_i$ con $y_i$ medido hacia arriba, signo positivo |

### 6. Dónde más aparece la idea

Esta forma exacta (matriz de masas + Coriolis + gravedad) aparece en la dinámica de cualquier sistema mecánico articulado: vehículos, exoesqueletos, satélites con partes móviles.

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R (Tema 14.4), $G(\vec\theta)=\begin{pmatrix}(m_1+m_2)gL_1\cos\theta_1+m_2gL_2\cos(\theta_1+\theta_2)\\m_2gL_2\cos(\theta_1+\theta_2)\end{pmatrix}$ — comparado con el Bloque 13 (Tema 13.7, ejemplo resuelto), $G$ es exactamente $-J^T\vec F_{peso}$ sumado sobre ambas masas (el signo depende de la convención de si $\vec F$ es el peso o la fuerza que hay que ejercer para sostenerlo).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $C(\vec q,\dot{\vec q})\dot{\vec q}$ se anula si solo una articulación se mueve a la vez y las demás están quietas (pista: mirar los términos del Tema 14.4, todos tienen producto de dos velocidades distintas o una al cuadrado).

**Serie B — Cálculo a mano**
- B1. Evaluar $G(\vec\theta)$ del ejemplo resuelto en $\theta_1=0°,\theta_2=0°$ (brazo horizontal) y en $\theta_1=90°,\theta_2=0°$ (brazo vertical) y explicar la diferencia física.

**Serie C — Laboratorio**
- C1. Verificar B1 con `codigo/bloque_14/lagrange_2r.py` y graficar $G_1(\theta_1)$ para $\theta_2=0$ fijo, confirmando que se anula en $\theta_1=\pm90°$ (brazo vertical, sin brazo de palanca horizontal contra la gravedad).

---

## Tema 14.6 — Propiedades de $M$: simétrica y definida positiva

### 1. El problema

$M(\vec q)$ no es una matriz arbitraria: tiene propiedades matemáticas garantizadas por la física del problema, y esas propiedades son las que el laboratorio usa para verificar que una deducción de Lagrange (propia o de una fuente externa) es correcta, sin necesitar la solución exacta de antemano.

### 2. El mecanismo

Dos propiedades, ambas consecuencia de que $M$ viene de la energía cinética $K=\tfrac12\dot{\vec q}^TM(\vec q)\dot{\vec q}$ (una forma cuadrática, Bloque 03):

- **Simétrica**: $M=M^T$ — consecuencia de que las derivadas parciales cruzadas de una función suave no dependen del orden ($\partial^2K/\partial\dot q_i\partial\dot q_j=\partial^2K/\partial\dot q_j\partial\dot q_i$).
- **Definida positiva**: $\dot{\vec q}^TM\dot{\vec q}>0$ para cualquier $\dot{\vec q}\neq\vec0$ — consecuencia de que la energía cinética de un sistema físico real siempre es positiva mientras se mueva (Bloque 06, Tema 6.5): $K=\tfrac12\dot{\vec q}^TM\dot{\vec q}$, y $K>0$ si algo se mueve.

Estas dos propiedades (Bloque 03, Tema 3.7: los valores propios de una matriz simétrica definida positiva son todos reales y positivos) son las que **garantizan que $M$ siempre tiene inversa** (Bloque 03, Tema 3.3: determinante distinto de cero) — indispensable para la dinámica directa (Tema 14.1, despejar $\ddot{\vec q}=M^{-1}(\vec\tau-C\dot{\vec q}-G)$).

### 3. En la vida real

```python
np.allclose(M, M.T)                      # simétrica
np.all(np.linalg.eigvalsh(M) > 0)        # definida positiva (autovalores > 0)
```

### 4. Limitaciones

Estas propiedades garantizan que $M$ es invertible en principio; numéricamente, $M$ puede estar **mal condicionada** (autovalores muy dispares) en ciertas posturas, lo que amplifica el error numérico al invertirla — un problema práctico distinto de la invertibilidad teórica.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una matriz $M$ deducida con SymPy no resulta simétrica al evaluarla numéricamente | Error algebraico en la deducción de Lagrange, o en cómo se extrajeron los coeficientes de $\ddot{\vec q}$ | Comparar `M` contra `M.T` para varios valores numéricos de $\vec q$ | Revisar la deducción; una $M$ correctamente obtenida de $K$ siempre es simétrica |

### 6. Dónde más aparece la idea

Matrices de masa en elementos finitos (estructuras), matrices de covarianza en estadística (también simétricas y semidefinidas positivas), cualquier forma cuadrática de energía en física.

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R del Tema 14.4 evaluado en $\theta_1=30°,\theta_2=45°$ con $m_1=1,m_2=0.5$ kg, $L_1=0.30,L_2=0.20$ m, los autovalores de $M$ son ambos positivos (se verifica en el laboratorio) — confirma que la deducción es físicamente consistente antes de usarla para simular.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué una matriz $M$ con algún autovalor negativo o cero **no puede** ser la matriz de masas de un sistema físico real, en términos de la energía cinética.

**Serie B — Cálculo a mano**
- B1. Verificar a mano que $M_{11}M_{22}-M_{12}^2>0$ (determinante positivo, condición de definida positiva para $2\times2$ junto con $M_{11}>0$) para el $M$ del 2R evaluado en una postura concreta.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_14/lagrange_2r.py` y verificar B1 numéricamente para varias posturas aleatorias, confirmando simetría y definitud positiva en todas.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/dinamica.py`: `deducir_lagrange` (ecuaciones de movimiento con SymPy), `matriz_masas`, `separar_gravedad_y_coriolis`.

## Glosario del bloque

| Término | Definición |
|---|---|
| Dinámica inversa | De movimiento deseado a par necesario: $\vec\tau=f(\vec q,\dot{\vec q},\ddot{\vec q})$. |
| Dinámica directa | De par aplicado a movimiento resultante: $\ddot{\vec q}=f(\vec q,\dot{\vec q},\vec\tau)$. |
| Lagrangiano | $L=K-U$, diferencia entre energía cinética y potencial. |
| Ecuación de Lagrange | $\tau_i=\frac{d}{dt}(\partial L/\partial\dot q_i)-\partial L/\partial q_i$; produce las ecuaciones de movimiento. |
| Matriz de masas $M(\vec q)$ | Coeficientes de $\ddot{\vec q}$ en la dinámica; simétrica y definida positiva. |
| Términos de Coriolis y centrífugos $C(\vec q,\dot{\vec q})\dot{\vec q}$ | Efectos que aparecen solo cuando más de una articulación se mueve a la vez; cuadráticos en $\dot{\vec q}$. |
| Par de gravedad $G(\vec q)$ | Par necesario para sostener el brazo, quieto, contra la gravedad en la postura $\vec q$. |
