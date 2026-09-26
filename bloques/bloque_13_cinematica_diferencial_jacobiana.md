# Bloque 13 — Cinemática diferencial: la matriz Jacobiana

> **Problema que abre el bloque:** se quiere mover la pinza en línea recta a 5 cm/s. ¿A qué velocidad debe girar cada motor en cada instante? Y en ciertas posturas, ¿por qué la respuesta es "infinito"?
>
> **Necesitas antes:** Bloque 12 (cierra la Parte III). · **Lectura:** Barrientos, cap. 4 (matriz Jacobiana); Lynch & Park, cap. 5.

`robotica-manipuladores` no tiene cinemática diferencial: este bloque es **original** del curso — ver
[docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md). Una nota para más
adelante: el Bloque 12 (Tema 12.5) estimó la Jacobiana por diferencias finitas porque todavía no
existía; la Jacobiana geométrica de este bloque es la versión analítica exacta, y podría usarse
para mejorar `inversa_numerica` (no se vuelve atrás a editar el Bloque 12: queda como una
extensión natural para quien quiera profundizar).

## Tema 13.1 — De los ángulos a las velocidades: $\dot{\vec x}=J(\vec q)\dot{\vec q}$

### 1. El problema

La cinemática directa (Bloque 11) relaciona posiciones: $\vec x=f(\vec q)$. Pero un controlador de velocidad (mover la pinza a 5 cm/s en línea recta, Bloque 19) necesita la relación entre **velocidades**: qué tan rápido debe girar cada motor para que la pinza se mueva a la velocidad deseada.

### 2. El mecanismo

Esto es la regla de la cadena con varias variables, ya vista en el Bloque 04 (Tema 4.4), aplicada a $\vec x=f(\vec q(t))$:

$$\dot{\vec x} = \frac{d}{dt}f(\vec q(t)) = \frac{\partial f}{\partial q_1}\dot q_1+\cdots+\frac{\partial f}{\partial q_n}\dot q_n = J(\vec q)\,\dot{\vec q}$$

donde $J(\vec q)$ es la **matriz Jacobiana**: la matriz de todas las derivadas parciales de la cinemática directa (Bloque 04, Tema 4.3), organizada en columnas, una por articulación. Para un brazo con posición $(x,y,z)$ y orientación (3 números más, Bloque 09), $J$ es de $6\times n$; para el 2R plano, basta con la parte de posición, $2\times2$.

Que $J$ dependa de $\vec q$ (no es una matriz constante, a diferencia de las del Bloque 03) es la razón física de que el mismo movimiento articular produzca velocidades de la pinza completamente distintas según la postura — y, en el caso extremo, de que ciertas posturas no puedan producir cierta velocidad de ninguna manera (Tema 13.5).

### 3. En la vida real

```python
from robotica.jacobiana import jacobiana_geometrica
J = jacobiana_geometrica(dh, q)   # (6, n): filas 0-2 lineal, 3-5 angular
x_punto = J @ q_punto
```

### 4. Limitaciones

$J(\vec q)$ solo vale, exactamente, en la postura $\vec q$ en la que se evalúa — para un movimiento finito hace falta recalcularla en cada instante (o usarla como aproximación de primer orden, Bloque 04 Tema 4.5, válida para pasos pequeños).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La velocidad de la pinza calculada con $J\dot{\vec q}$ no coincide con la que se mide derivando la posición numéricamente | Se evaluó $J$ en una postura distinta de la actual, o se mezclaron unidades (grados con radianes, Bloque 01) | Comparar $J(\vec q)\dot{\vec q}$ contra $(\vec x(t+h)-\vec x(t))/h$ (diferencias finitas, Bloque 04) | Evaluar $J$ en la postura correcta y verificar unidades |

### 6. Dónde más aparece la idea

Sensibilidad de cualquier sistema de ingeniería (cuánto cambia una salida ante un cambio pequeño en una entrada), el jacobiano de un cambio de variables en cálculo multivariable, la matriz de derivadas que usa retropropagación en redes neuronales.

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R con $L_1=0.30,L_2=0.20$ m en $\theta_1=40°,\theta_2=30°$ (el mismo caso del Bloque 04, Tema 4.4), con $\dot\theta_1=1,\dot\theta_2=0.5$ rad/s: $\dot{\vec x}=J\dot{\vec q}\approx(-0.475,0.332)$ m/s — exactamente el resultado que el Bloque 04 obtuvo con la regla de la cadena aplicada a mano, ahora escrito como una sola multiplicación matricial.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $J$ no es una matriz constante, a diferencia de una matriz de rotación (Bloque 08).

**Serie B — Cálculo a mano**
- B1. Verificar que $J\dot{\vec q}$ con los datos del ejemplo reproduce el resultado del Bloque 04, Tema 4.4.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_13/jacobiana_2r.py`: calcula $J$ simbólica y numéricamente para el 2R, y verifica el ejemplo resuelto.

---

## Tema 13.2 — Jacobiana analítica: derivando la cinemática directa

### 1. El problema

La forma más directa de obtener $J$ es, literalmente, derivar la fórmula de la cinemática directa (Bloque 11) respecto a cada $q_i$ — el mismo procedimiento del Bloque 04, aplicado ahora de forma sistemática a los seis componentes de la pose (posición y orientación).

### 2. El mecanismo

Si $\vec x=(\vec p,\vec\phi)$ con $\vec p$ la posición y $\vec\phi$ alguna representación mínima de la orientación (por ejemplo, RPY, Bloque 09), la **Jacobiana analítica** es simplemente:

$$J_a(\vec q) = \frac{\partial(\vec p,\vec\phi)}{\partial\vec q}$$

calculada derivando la cinemática directa componente a componente (a mano para el 2R, con SymPy para casos generales, Bloque 04 Tema 4.1). Es "analítica" porque depende de qué representación de orientación se eligió — y por eso hereda las singularidades de esa representación (Bloque 09, Tema 9.2: el bloqueo del cardán de RPY aparece como una singularidad *extra* de $J_a$ que no tiene nada que ver con la geometría del brazo, solo con la elección de $\vec\phi$). Esta es la razón por la que, en la práctica, se prefiere la Jacobiana geométrica (Tema 13.3), que no tiene ese problema.

### 3. En la vida real

```python
import sympy as sp
# derivar simbólicamente la posición del 2R respecto a theta1, theta2
# (Bloque 04, Tema 4.3), organizado en columnas: eso YA es J_a de posición.
```

### 4. Limitaciones

Como se explicó, hereda las singularidades de representación de $\vec\phi$ (Bloque 09) además de las singularidades físicas reales del brazo (Tema 13.5) — mezclando dos fenómenos de origen distinto.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| $J_a$ se anula (o su determinante se dispara) en una postura donde el brazo no está, en realidad, en ninguna configuración física especial | Se está cerca de una singularidad de la *representación* de orientación (bloqueo del cardán, Bloque 09), no del brazo | Repetir el cálculo con otra representación de orientación (o con la Jacobiana geométrica, Tema 13.3) y comparar | Usar la Jacobiana geométrica para diagnosticar singularidades físicas, no la analítica con RPY |

### 6. Dónde más aparece la idea

Cualquier "matriz de sensibilidad" calculada derivando directamente una fórmula, en vez de razonar la física del mecanismo.

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R (sin orientación que considerar, solo posición en el plano), $J_a=J_g$ (analítica igual a geométrica) exactamente — la distinción solo importa cuando hay orientación de por medio.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, para un brazo que solo posiciona (sin controlar orientación), la Jacobiana analítica y la geométrica son siempre la misma matriz.

**Serie B — Cálculo a mano**
- B1. Derivar a mano $\partial x/\partial\theta_1$ y $\partial x/\partial\theta_2$ del 2R (ya hecho en el Bloque 04, Tema 4.3) y confirmar que son la primera fila de $J$.

**Serie C — Laboratorio**
- C1. Nada nuevo: se verifica junto con el Tema 13.3 en `codigo/bloque_13/jacobiana_2r.py`.

---

## Tema 13.3 — Jacobiana geométrica: con los ejes de cada articulación

### 1. El problema

Derivar la cinemática directa a mano (Tema 13.2) se vuelve pesado para más de 2-3 GDL, y además mezcla singularidades de representación con singularidades físicas. Hace falta una fórmula directa, en términos de la geometría del brazo (los ejes de cada articulación), sin pasar por ninguna derivada explícita.

### 2. El mecanismo

Cada columna de la **Jacobiana geométrica** se construye directamente con los datos que ya da la cinemática directa (Bloque 11, Tema 11.4: la lista de marcos `marcos(dh,q)`), sin derivar nada:

- **Articulación rotacional** $i$: gira alrededor de su propio eje $z_{i-1}$ (el eje z del marco $i-1$, expresado en el marco base) con velocidad $\dot\theta_i$. Esto aporta una velocidad angular $\dot\theta_i\,z_{i-1}$ al efector final, y una velocidad lineal $\dot\theta_i\,z_{i-1}\times(\vec p_e-\vec p_{i-1})$ — la fórmula de velocidad de un punto de un cuerpo rígido que gira (Bloque 06, Tema 6.2: $\vec v=\vec\omega\times\vec r$, aquí con $\vec r=\vec p_e-\vec p_{i-1}$, el brazo de palanca desde el eje de giro hasta la punta). Columna $i$:

$$J_i = \begin{pmatrix}z_{i-1}\times(\vec p_e-\vec p_{i-1})\\z_{i-1}\end{pmatrix}$$

- **Articulación prismática** $i$: se desliza a lo largo de $z_{i-1}$; aporta solo velocidad lineal en esa dirección, sin girar nada: $J_i=\begin{pmatrix}z_{i-1}\\\vec 0\end{pmatrix}$.

Cada columna se calcula con información que ya está disponible (los propios marcos de la cinemática directa), sin ninguna derivada simbólica — y no hereda ninguna singularidad de representación de orientación (Tema 13.2), porque nunca se eligió ninguna: las filas 3-5 son directamente la velocidad angular en $\mathbb R^3$.

### 3. En la vida real

`robotica/jacobiana.py` implementa `jacobiana_geometrica(dh, q)` con exactamente esta receta, reutilizando `robotica.dh.marcos` (Bloque 11). Verificado contra diferencias finitas de la posición (Bloque 04, Tema 4.6): error del orden de $10^{-6}$–$10^{-7}$, atribuible al método de diferencias finitas, no a la fórmula geométrica (que es exacta).

### 4. Limitaciones

Ninguna: a diferencia de la analítica, la geométrica no tiene singularidades espurias de representación.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una columna de $J$ calculada a mano no coincide con la versión numérica | Se usó $\vec p_i-\vec p_e$ en vez de $\vec p_e-\vec p_i$ (orden invertido en la resta del producto cruz) | Comparar signo de cada columna contra `jacobiana_geometrica` | El brazo de palanca es siempre "del eje de giro a la punta": $\vec p_e-\vec p_{i-1}$ |

### 6. Dónde más aparece la idea

Es el método estándar en robótica industrial y en librerías profesionales (Robotics Toolbox, MoveIt) para calcular la Jacobiana de cualquier cadena cinemática.

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R en $\theta_1=40°,\theta_2=30°$, $\det(J_v)=L_1L_2\sin\theta_2=0.30\times0.20\times\sin30°=0.03$ — un resultado limpio que se deduce con la fórmula geométrica en una línea, y que reaparece exacto en el Tema 13.5.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la fila de velocidad angular de una articulación prismática es siempre cero, pensando en qué le hace al efector final deslizar sin girar.

**Serie B — Cálculo a mano**
- B1. Para el 2R, calcular a mano $J_2$ (la segunda columna, correspondiente a $\theta_2$) usando la fórmula $z_1\times(\vec p_e-\vec p_1)$.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_13/jacobiana_2r.py`: compara `jacobiana_geometrica` contra diferencias finitas para el 2R y para `curso_3gdl` (Bloque 11), reportando el error máximo.

---

## Tema 13.4 — Jacobiana inversa y pseudoinversa

### 1. El problema

$\dot{\vec x}=J\dot{\vec q}$ (Tema 13.1) resuelve "dados los $\dot q_i$, ¿qué velocidad tiene la pinza?". La pregunta que de verdad hace falta para controlar el brazo es la inversa: "para que la pinza tenga esta velocidad, ¿qué $\dot q_i$ hacen falta?" — el mismo tipo de inversión de problema que motivó el Bloque 12.

### 2. El mecanismo

Si $J$ es cuadrada ($6\times6$, o $2\times2$ para el 2R) e invertible (Bloque 03), la respuesta es directa:

$$\dot{\vec q} = J^{-1}\dot{\vec x}$$

Si $J$ no es cuadrada (brazo con GDL $\neq$ 6, Bloque 07 Tema 7.2), se usa la **pseudoinversa** (Bloque 03, Tema 3.6, mínimos cuadrados): con más articulaciones que componentes de velocidad deseadas (brazo redundante), $J^+=J^T(JJ^T)^{-1}$ da la solución de **norma mínima** entre las infinitas posibles; con menos articulaciones que componentes deseadas, $J^+=(J^TJ)^{-1}J^T$ da la que **minimiza el error** cuando no hay solución exacta.

Esta es exactamente la misma matemática que ya apareció en el Bloque 12 (Tema 12.5) para la cinemática inversa numérica de posición — no es casualidad: Newton-Raphson aplicado a $f(\vec q)=\vec p(\vec q)-\vec p_d$ usa, en cada paso, la Jacobiana de $f$, que es $J$. El Bloque 12 la estimaba por diferencias finitas porque este bloque todavía no existía; con la Jacobiana geométrica exacta de este bloque, esa misma inversa numérica sería más precisa y más barata de evaluar.

### 3. En la vida real

```python
q_punto = np.linalg.inv(J) @ x_punto          # J cuadrada
q_punto = np.linalg.pinv(J) @ x_punto         # J no cuadrada (pseudoinversa)
```

### 4. Limitaciones

Tanto $J^{-1}$ como $J^+$ se vuelven numéricamente inestables cerca de una singularidad (Tema 13.5): valores pequeños en el determinante (o en los valores singulares) producen velocidades articulares desproporcionadamente grandes.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| $\dot{\vec q}=J^{-1}\dot{\vec x}$ da velocidades articulares absurdamente grandes para una velocidad de pinza modesta | La postura está cerca de una singularidad: $J^{-1}$ amplifica el error | Revisar $\det J$ (o los valores singulares de $J$) en esa postura | Usar mínimos cuadrados amortiguados (Bloque 12, Tema 12.5) en vez de la inversa directa cerca de singularidades |

### 6. Dónde más aparece la idea

Control de velocidad de brazos robóticos en tiempo real, teleoperación (traducir el movimiento de un joystick a velocidades articulares).

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R en una postura normal ($\theta_2=30°$, lejos de singularidad), $J^{-1}\dot{\vec x}$ da velocidades articulares del mismo orden de magnitud que $\dot{\vec x}$; cerca de $\theta_2\to0$ (Tema 13.5), la misma $\dot{\vec x}$ pedida requeriría velocidades articulares que crecen sin límite.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, en términos de la pseudoinversa como problema de mínimos cuadrados (Bloque 03, Tema 3.6), qué significa "la solución de norma mínima" para un brazo redundante.

**Serie B — Cálculo a mano**
- B1. Invertir a mano la Jacobiana $2\times2$ del 2R (Bloque 03, fórmula de la inversa de una matriz $2\times2$) y evaluarla en $\theta_1=40°,\theta_2=30°$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `np.linalg.inv` y usar el resultado para calcular $\dot{\vec q}$ dado $\dot{\vec x}=(0.05,0)$ m/s (moverse en línea recta horizontal a 5 cm/s, el problema que abre el bloque).

---

## Tema 13.5 — Singularidades

### 1. El problema

En ciertas posturas, ninguna combinación de velocidades articulares —por rápido que giren los motores— puede producir cierta dirección de movimiento de la pinza. Hace falta saber identificar esas posturas antes de pedirle al robot algo imposible.

### 2. El mecanismo

Una **singularidad** es una postura donde $J$ pierde rango (Bloque 03, Tema 3.6): para un brazo con $J$ cuadrada, esto es exactamente $\det J=0$ (Bloque 03, Tema 3.4) — la transformación que $J$ representa "aplasta" el espacio de velocidades articulares a un subespacio de menor dimensión, y hay direcciones de velocidad de la pinza que quedan **fuera de ese subespacio**, inalcanzables sin importar $\dot{\vec q}$.

Dos tipos, según dónde ocurren dentro del espacio de trabajo (Bloque 07, Tema 7.3):

- **Singularidades de frontera**: en el borde del espacio de trabajo (brazo completamente estirado o completamente plegado) — intuitivas: ahí el brazo ya no puede "alargarse" más en esa dirección.
- **Singularidades de interior**: dentro del espacio de trabajo alcanzable, en posturas donde dos o más ejes de articulación quedan alineados (por ejemplo, la singularidad de muñeca del Bloque 12, Tema 12.4, cuando los ejes 4 y 6 de un brazo con muñeca esférica se alinean) — menos intuitivas, porque el punto sí es alcanzable, solo que ciertas *direcciones* de movimiento ahí no lo son.

Cerca de una singularidad (sin estar exactamente en ella), $J^{-1}$ o $J^+$ (Tema 13.4) siguen siendo calculables pero producen velocidades articulares que crecen sin control — la manifestación práctica de que el determinante se acerca a cero.

### 3. En la vida real

```python
np.linalg.det(J)          # J cuadrada: cero exacto en singularidad
np.linalg.svd(J)[1]       # valores singulares: el menor se acerca a cero
```

### 4. Limitaciones

Detectar una singularidad exacta ($\det J=0$ exactamente) rara vez ocurre en la práctica por errores de redondeo; lo relevante es monitorear qué tan **cerca** se está (Tema 13.6, manipulabilidad), no solo verificar la igualdad exacta.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El robot, cerca de cierta postura, empieza a moverse erráticamente o a vibrar al pedirle una trayectoria en línea recta | Se está cruzando o pasando cerca de una singularidad (Bloque 19 retoma esto para el diseño de trayectorias) | Graficar $\det J$ (o la manipulabilidad, Tema 13.6) a lo largo de la trayectoria planeada | Replanificar la trayectoria para evitar la zona, o reducir la velocidad al pasar cerca |

### 6. Dónde más aparece la idea

Determinante cero como aplastamiento del espacio (Bloque 03, Tema 3.4) — esta es, literalmente, esa misma idea aplicada a la Jacobiana; puntos de "bloqueo" mecánico en cualquier mecanismo articulado (por ejemplo, la rodilla humana completamente estirada).

### 7. Ejemplos resueltos

**Ejemplo (el problema del Bloque 01 y de este bloque):** para el 2R, $\det J_v=L_1L_2\sin\theta_2$ (Tema 13.3): singularidad exacta en $\theta_2=0°$ (brazo estirado, frontera) y $\theta_2=180°$ (plegado, también frontera para este brazo sin obstáculos). En $\theta_2=30°$, lejos de ambas, el brazo está en una postura "cómoda".

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, en la singularidad de brazo estirado, el 2R no puede moverse instantáneamente "hacia afuera" (alejándose del hombro) por rápido que giren los motores.

**Serie B — Cálculo a mano**
- B1. Confirmar, con la fórmula $\det J_v=L_1L_2\sin\theta_2$, que $\theta_2=90°$ es la postura de **máxima** manipulabilidad del 2R (más lejos posible de cualquier singularidad).

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_13/romper_singularidad.py`: lleva el 2R a brazo estirado ($\theta_2\to0$) y pide una velocidad hacia afuera; grafica cómo las velocidades articulares calculadas con $J^{-1}$ se disparan a medida que la postura se acerca a la singularidad.

---

## Tema 13.6 — Manipulabilidad

### 1. El problema

"Cerca de una singularidad" (Tema 13.5) es cualitativo. Hace falta un número que resuma, para cualquier postura, qué tan lejos está de perder movilidad en alguna dirección — útil para comparar posturas y para elegir, entre varias soluciones de cinemática inversa (Bloque 12, Tema 12.6), la más "cómoda".

### 2. El mecanismo

La **manipulabilidad** de Yoshikawa es

$$w(\vec q) = \sqrt{\det\big(J(\vec q)J(\vec q)^T\big)}$$

(para $J$ cuadrada, esto se reduce a $w=|\det J|$, Bloque 03). $w=0$ exactamente en una singularidad (Tema 13.5); valores mayores indican posturas donde el brazo puede producir velocidades de la pinza en cualquier dirección con esfuerzos articulares comparables entre sí — geométricamente, $w$ es proporcional al volumen del **elipsoide de manipulabilidad**: el conjunto de velocidades de la pinza alcanzables con $\|\dot{\vec q}\|\leq1$ (un círculo/esfera de velocidades articulares unitarias, transformado por $J$ en una elipse/elipsoide de velocidades de la pinza, Bloque 03 Tema 3.4: el mismo "factor de cambio de área" del determinante, aplicado aquí a velocidades en vez de posiciones).

### 3. En la vida real

`robotica.jacobiana.manipulabilidad(J)` implementa esta fórmula directamente; un **mapa de manipulabilidad** (evaluarla en cada punto del espacio de trabajo, Bloque 07) muestra de un vistazo qué zonas son cómodas para trabajar y cuáles están cerca de singularidades.

### 4. Limitaciones

$w$ resume la manipulabilidad en un solo número "promedio"; no dice en qué **dirección específica** el brazo está más o menos capaz (para eso hacen falta los ejes del elipsoide, los valores singulares de $J$).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Se elige, entre varias soluciones de cinemática inversa (Bloque 12), la que resulta ser la más cercana a una singularidad | No se calculó ni comparó la manipulabilidad de cada solución antes de elegir | Calcular `manipulabilidad(J)` para cada solución candidata | Preferir, entre soluciones con distancia articular similar (Bloque 12, Tema 12.6), la de mayor manipulabilidad |

### 6. Dónde más aparece la idea

El número de condición de una matriz (una medida relacionada, usada en análisis numérico), el diseño de mecanismos (elegir dimensiones que maximicen la manipulabilidad promedio en el espacio de trabajo de interés).

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R con $L_1=L_2=0.25$ m, $w(\theta_2)=0.0625\sin\theta_2$ tiene su máximo en $\theta_2=90°$ (codo en ángulo recto) — la postura más "cómoda" de este brazo en particular.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, para el 2R, la manipulabilidad no depende de $\theta_1$ (el ángulo del hombro), solo de $\theta_2$ (el del codo).

**Serie B — Cálculo a mano**
- B1. Para $L_1=0.30,L_2=0.20$ m, dar el valor de $\theta_2$ que maximiza $w$ y el valor máximo correspondiente.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_13/mapa_manipulabilidad.py`: evalúa `manipulabilidad` en una malla de posturas $(\theta_1,\theta_2)$ del 2R y grafica un mapa de calor sobre el espacio de trabajo (Bloque 01, Tema 1.4).

---

## Tema 13.7 — Estática: $\vec\tau=J^T\vec F$

### 1. El problema

El brazo sostiene un huevo (o cualquier carga) en la pinza, quieto, sin moverse. ¿Qué par debe ejercer cada motor para sostenerlo contra la gravedad, sin que el brazo se mueva ni un milímetro?

### 2. El mecanismo

Este es un caso donde la Jacobiana se usa sin ninguna velocidad de por medio: por el **principio de trabajo virtual** (el trabajo que hace una fuerza en un desplazamiento pequeño debe ser consistente calculado desde cualquiera de los dos lados de la cadena cinemática), el par articular necesario para equilibrar una fuerza $\vec F$ aplicada en el efector final es

$$\vec\tau = J(\vec q)^T\vec F$$

Nótese que aparece $J^T$, no $J^{-1}$ ni $J^+$: no hace falta invertir nada, porque esta vez la incógnita ($\vec\tau$, de dimensión $n$) y el dato ($\vec F$, de dimensión 6 o 3) ya están en el orden correcto para que $J^T$ (de $n\times6$ o $n\times3$) los relacione directamente — la misma matriz $J$ del Tema 13.1, pero transportando fuerzas "hacia atrás" (de la pinza hacia los motores) en vez de velocidades "hacia adelante".

### 3. En la vida real

```python
from robotica.jacobiana import par_estatico
tau = par_estatico(J, F)   # F: fuerza en el efector final (N), tau: pares (N·m)
```

### 4. Limitaciones

Esta fórmula da el par para el equilibrio **estático** (brazo quieto); si el brazo además se mueve, hacen falta los términos dinámicos completos del Bloque 14 (inercia, Coriolis, gravedad) sumados a este.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El par calculado para sostener una carga da cero cuando claramente hace falta esfuerzo para sostenerla | La fuerza $\vec F$ no está en la dirección correcta respecto al plano de movimiento del brazo (por ejemplo, gravedad perpendicular al plano de un brazo que solo se mueve en ese plano, Bloque 07) | Revisar si el brazo puede, geométricamente, oponerse a esa fuerza con sus articulaciones disponibles | Verificar que $\vec F$ tenga componente en las direcciones que el brazo realmente controla |

### 6. Dónde más aparece la idea

Dimensionar los motores de un brazo para la carga máxima que debe sostener (Bloque 16), el principio de trabajo virtual en mecánica estructural, la relación fuerza-par en cualquier mecanismo de palanca.

### 7. Ejemplos resueltos

**Ejemplo (el problema del bloque):** 2R en el plano vertical ($L_1=0.30,L_2=0.20$ m, $\theta_1=40°,\theta_2=30°$) sosteniendo un huevo de 60 g ($F=(0,-0.589,0)$ N, con $g=9.81$ m/s²): $\vec\tau=J^T\vec F\approx(-0.176,-0.040)$ N·m — el hombro necesita más par que el codo, razonable porque sostiene todo el peso a mayor distancia del eje (Bloque 06, Tema 6.3: el mismo efecto de Steiner).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el par que hace falta en el hombro es mayor que en el codo para sostener la misma carga en la punta, retomando la idea de brazo de palanca del Bloque 02 (Tema 2.3, torque) y del Bloque 06 (Tema 6.3, Steiner).

**Serie B — Cálculo a mano**
- B1. Verificar el ejemplo resuelto calculando $J^T\vec F$ a mano con la $J$ del Tema 13.4 (Ejercicio B1).

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_13/estatica_carga.py`: calcula el par de sostenimiento para un huevo (60 g) y para la pinza vacía en varias posturas, y grafica cómo cambia el par del hombro con la postura.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/jacobiana.py`: `jacobiana_geometrica`, `jacobiana_posicion`, `manipulabilidad`, `par_estatico`.

## Glosario del bloque

| Término | Definición |
|---|---|
| Matriz Jacobiana | Matriz que relaciona velocidades articulares con velocidad de la pinza: $\dot{\vec x}=J(\vec q)\dot{\vec q}$. |
| Jacobiana analítica | Derivada directa de la cinemática directa respecto a $\vec q$; hereda singularidades de la representación de orientación elegida. |
| Jacobiana geométrica | Construida con los ejes de cada articulación, sin derivar ni elegir representación de orientación. |
| Singularidad | Postura donde $J$ pierde rango ($\det J=0$ si es cuadrada): ciertas velocidades de la pinza dejan de ser alcanzables. |
| Singularidad de frontera / de interior | Según ocurra en el borde del espacio de trabajo (brazo estirado) o dentro de él (ejes alineados). |
| Manipulabilidad | $w=\sqrt{\det(JJ^T)}$; mide qué tan lejos está una postura de una singularidad. |
| Estática ($\vec\tau=J^T\vec F$) | Relación entre una fuerza aplicada en el efector final y el par articular necesario para equilibrarla. |
