# Bloque 09 — Localización espacial II: otras formas de decir la orientación

> **Problema que abre el bloque:** un operador no puede escribir una matriz de 3×3 en una pantalla, y un giroscopio integrando matrices termina con algo que ya no es una rotación.
>
> **Necesitas antes:** Bloque 08. · **Lectura:** Barrientos, cap. 3; Corke, *Robotics, Vision and Control* (ed. Python), cap. 2.
>
> **Dónde más aparece:** IMU de drones y celulares, animación 3D, videojuegos, naves espaciales.

Este bloque porta parcialmente `transformaciones.py` de
[`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores)
(`rpy2mat`/`mat2rpy`, `zxz2mat`/`mat2zxz`) — ver
[docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md). Con una diferencia
deliberada de convención: allá esas cuatro funciones trabajan en **grados** (así lo documenta su
`docs/convenciones.md`); aquí trabajan en **radianes**, como el resto del código de este curso
(FILOSOFIA.md: "radianes en todo cálculo y todo código"). El mecanismo se porta; la unidad se
adapta a la del curso. Eje-ángulo y cuaterniones no están en `robotica-manipuladores` y se
desarrollan aquí por primera vez.

## Tema 9.1 — Ángulos de Euler: RPY y ZXZ

### 1. El problema

Una matriz de rotación (Bloque 08) tiene 9 números para describir algo que solo tiene 3 grados de libertad. Un operador necesita escribir esos 3 números en una pantalla o en un formulario, no una matriz.

### 2. El mecanismo

Los **ángulos de Euler** describen una orientación como **tres rotaciones sucesivas** alrededor de ejes elegidos por convención. Hay 12 convenciones posibles (cualquier secuencia de 3 ejes sin repetir dos consecutivos); dos dominan la práctica:

- **Roll-Pitch-Yaw (RPY)**, alabeo-cabeceo-guiñada: rota primero $\alpha$ (roll) en x, luego $\beta$ (pitch) en y, luego $\gamma$ (yaw) en z, **respecto a ejes fijos** (Bloque 08, Tema 8.5) — por eso se premultiplica en el orden inverso al que se nombran:

$$R_{RPY}(\alpha,\beta,\gamma) = R_z(\gamma)\,R_y(\beta)\,R_x(\alpha)$$

- **Euler ZXZ**: rota $\phi$ en z, luego $\beta$ en el **nuevo** x (ejes móviles), luego $\alpha$ en el **nuevo** z:

$$R_{ZXZ}(\phi,\beta,\alpha) = R_z(\phi)\,R_x(\beta)\,R_z(\alpha)$$

Cada fabricante y cada libro elige su propia convención (de ahí las 12 posibles), y **mezclarlas sin darse cuenta es el error más común** al leer documentación de robots distintos: los mismos tres números significan orientaciones distintas según la convención.

### 3. En la vida real

`robotica/orientacion.py` implementa `rpy2mat`/`mat2rpy` y `zxz2mat`/`mat2zxz`, en radianes, portadas del mecanismo de `robotica-manipuladores`:

```python
from robotica.orientacion import rpy2mat, mat2rpy
R = rpy2mat(np.radians(10), np.radians(20), np.radians(30))
mat2rpy(R)   # recupera (0.1745, 0.3491, 0.5236) rad
```

### 4. Limitaciones

`mat2rpy` (la función inversa) no es única en general: la misma matriz puede corresponder a más de una terna de ángulos (Tema 9.2 explica el caso extremo). Distintas librerías, incluso con la misma convención nominal, pueden diferir en el rango de salida ($(-\pi,\pi]$ contra $[0,2\pi)$, por ejemplo).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una orientación "correcta" en un sistema se ve girada de forma extraña al importarla a otro | Los dos sistemas usan convenciones de Euler distintas (por ejemplo, RPY contra ZXZ, o el orden de los ángulos invertido) | Reconstruir la matriz de rotación con cada convención y comparar | Confirmar explícitamente la convención de cada sistema antes de intercambiar ángulos; comparar siempre a nivel de matriz, no de ángulos sueltos |

### 6. Dónde más aparece la idea

La actitud de un avión se describe clásicamente en RPY (de ahí el nombre); brazos robóticos industriales suelen reportar orientación en alguna convención de Euler en su panel de control.

### 7. Ejemplos resueltos

**Ejemplo:** $\alpha=\beta=\gamma=0$ da $R_{RPY}=I$ (sin giro), como se espera de cualquier convención en el origen.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el orden de multiplicación de $R_{RPY}$ es $R_zR_yR_x$ y no $R_xR_yR_z$, repasando el Bloque 08 (Tema 8.5): son ejes fijos, se premultiplica.

**Serie B — Cálculo a mano**
- B1. Calcular $R_{RPY}(0,0,90°)$ y confirmar que coincide con $R_z(90°)$ solo (Bloque 08).

**Serie C — Laboratorio**
- C1. Verificar B1 con `robotica.orientacion.rpy2mat` y comparar con `scipy.spatial.transform.Rotation.from_euler('xyz', [...])` (cuidado: hay que revisar contra qué convención exacta compara scipy).

---

## Tema 9.2 — Bloqueo del cardán (*gimbal lock*)

### 1. El problema

En cierta orientación, dos de los tres ángulos de Euler parecen "fundirse" en uno solo: mover uno de ellos produce el mismo efecto que mover el otro, y de pronto ya no se puede alcanzar cualquier orientación cercana con un cambio pequeño de ángulos. Un giroscopio mecánico real (un *gimbal*, un anillo montado sobre otro anillo) se queda literalmente trabado en esa configuración — de ahí el nombre.

### 2. El mecanismo

Cuando el ángulo intermedio de una convención de Euler llega a $\pm90°$ (por ejemplo, $\beta=90°$ en RPY), el primer eje de giro y el tercero quedan **alineados**. Es fácil verlo sustituyendo en $R_{RPY}$: con $\beta=90°$, $R_y(90°)$ manda al eje z hacia donde estaba el eje x, así que el giro posterior en z (yaw) termina rotando alrededor del **mismo eje físico** que el giro en x (roll) — los dos ángulos ya no controlan direcciones independientes, sino la misma, y su suma es lo único que importa: se perdió un grado de libertad *de la representación* (no del objeto físico, que sigue teniendo 3 GDL de orientación; es la parametrización la que colapsa).

Esto **no es un defecto de un fabricante en particular**: es una consecuencia matemática de describir una esfera (todas las orientaciones posibles) con dos números tipo latitud-longitud (Tema 8.2) — exactamente igual que los polos de un globo terráqueo, donde la longitud deja de tener sentido. Toda convención de Euler tiene su propio "polo" de bloqueo.

### 3. En la vida real

```python
R = rpy2mat(np.radians(30), np.radians(90), np.radians(45))
# roll y yaw ya no son recuperables por separado desde R: mat2rpy
# puede devolver, por ejemplo, (0°, 90°, 75°) -- la SUMA se preserva,
# no cada ángulo individual.
```

### 4. Limitaciones

El bloqueo del cardán es un problema de la *representación*, no del objeto: la orientación en sí sigue siendo perfectamente válida y alcanzable. El problema aparece al **interpolar** o **controlar** usando esos ángulos cerca de la singularidad (Tema 9.6).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Cerca de cierta orientación, un pequeño cambio deseado en un ángulo de Euler produce un salto grande o inesperado en los otros dos | El sistema está cerca del bloqueo del cardán de esa convención (ángulo intermedio cerca de $\pm90°$) | Verificar si el ángulo intermedio (pitch en RPY, o el segundo ángulo en ZXZ) está cerca de $\pm90°$ | Usar cuaterniones (Tema 9.4) para control o interpolación cerca de esas orientaciones |

### 6. Dónde más aparece la idea

El motivo histórico real (el Apolo 11 estuvo cerca de un bloqueo de cardán durante la misión, por eso las naves posteriores añadieron un cuarto anillo o usaron otras representaciones), por qué los motores gráficos de videojuegos usan cuaterniones para las cámaras.

### 7. Ejemplos resueltos

**Ejemplo:** con $\beta=90°$ exacto en RPY, $R_{RPY}(\alpha,90°,\gamma)$ resulta ser función únicamente de $\alpha+\gamma$ (o $\gamma-\alpha$, según la convención de signos) — infinitas parejas $(\alpha,\gamma)$ dan la misma matriz.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar la analogía con los polos de un globo terráqueo: ¿qué papel juega la latitud (equivalente al ángulo intermedio) en que la longitud pierda sentido en el polo?

**Serie B — Cálculo a mano**
- B1. Mostrar, sustituyendo $\beta=90°$ en la matriz $R_{RPY}$ del Tema 9.1, que el resultado depende solo de $\alpha+\gamma$ (o de su diferencia, según el signo).

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_09/romper_gimbal_lock.py`: lleva el cabeceo (pitch) a 90° y trata de girar la guiñada (yaw) por separado del alabeo (roll); graficar cómo el marco resultante no cambia al variar uno de los dos por separado, solo al variar su suma.

---

## Tema 9.3 — Eje y ángulo: toda rotación es un solo giro

### 1. El problema

Los ángulos de Euler describen una rotación como *tres* giros sucesivos alrededor de ejes que cambian en el camino — una forma indirecta. Físicamente, sin embargo, cualquier orientación final se puede alcanzar con un solo giro, de una sola vez, alrededor de algún eje fijo. Hace falta la fórmula que encuentra ese eje y ese ángulo.

### 2. El mecanismo

**Teorema de Euler de la rotación**: toda rotación en 3D equivale a un giro de un único ángulo $\theta$ alrededor de un único eje $\hat k$ (un vector unitario). La **fórmula de Rodrigues** construye la matriz de rotación directamente a partir de $\hat k$ y $\theta$, sin pasar por ángulos de Euler:

$$R = I + \sin\theta\,[\hat k]_\times + (1-\cos\theta)\,[\hat k]_\times^2$$

donde $[\hat k]_\times$ es la matriz antisimétrica tal que $[\hat k]_\times\vec v=\hat k\times\vec v$ para cualquier $\vec v$ (una forma de escribir el producto cruz, Bloque 02, como multiplicación matricial):

$$[\hat k]_\times = \begin{pmatrix}0&-k_z&k_y\\k_z&0&-k_x\\-k_y&k_x&0\end{pmatrix}$$

El eje $\hat k$ tiene una interpretación directa: es la dirección que **no cambia** al aplicar $R$ — es decir, el único vector propio real de $R$ con valor propio $+1$ (Bloque 03, Tema 3.7), consistente con que $R\hat k=\hat k$: girar alrededor de un eje deja ese eje quieto.

La representación eje-ángulo usa solo 4 números (3 del eje, 1 del ángulo) para 3 GDL —sigue siendo redundante, porque $\hat k$ tiene norma 1— pero, a diferencia de los ángulos de Euler, no tiene una convención ambigua que recordar: es la misma fórmula siempre.

### 3. En la vida real

```python
from robotica.orientacion import eje_angulo2mat, mat2eje_angulo
R = eje_angulo2mat(np.array([0, 0, 1]), np.pi/2)   # 90° alrededor de z
eje, angulo = mat2eje_angulo(R)                     # recupera (≈[0,0,1], π/2)
```

### 4. Limitaciones

$(\hat k,\theta)$ y $(-\hat k,-\theta)$ describen la **misma** rotación — no es una representación única, y $\theta=0$ deja $\hat k$ indefinido (cualquier eje sirve para "no girar").

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Al extraer el eje de una matriz casi identidad (ángulo muy pequeño), el eje calculado es ruidoso o inconsistente | Con $\theta\approx0$, el eje está casi indefinido numéricamente (división por un $\sin\theta$ cercano a cero) | Revisar si $\theta$ está cerca de 0 antes de confiar en el eje extraído | Para $\theta$ pequeño, tratar la rotación como aproximadamente nula en vez de confiar en su eje |

### 6. Dónde más aparece la idea

El "eje de rotación" que se reporta en la física de un giroscopio, la base matemática de la interpolación SLERP (Tema 9.6), la fórmula de Rodrigues reaparece en visión artificial (`cv2.Rodrigues`).

### 7. Ejemplos resueltos

**Ejemplo:** $\hat k=(0,0,1)$, $\theta=90°$: $[\hat k]_\times=\begin{pmatrix}0&-1&0\\1&0&0\\0&0&0\end{pmatrix}$. Sustituyendo en Rodrigues se recupera exactamente $R_z(90°)$ del Bloque 08 — el caso particular en que el eje coincide con uno de los ejes coordenados.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $\hat k$ es, necesariamente, un vector propio de $R$ con valor propio 1, pensando en qué significa físicamente "el eje de giro no se mueve".

**Serie B — Cálculo a mano**
- B1. Usando Rodrigues, verificar que $\hat k=(1,0,0)$, $\theta=90°$ reproduce $R_x(90°)$ del Bloque 08.

**Serie C — Laboratorio**
- C1. Verificar B1 con `robotica.orientacion.eje_angulo2mat` y extraer de vuelta $(\hat k,\theta)$ con `mat2eje_angulo` para confirmar la ida y vuelta.

---

## Tema 9.4 — Cuaterniones

### 1. El problema

Los ángulos de Euler se traban (Tema 9.2); integrar velocidades angulares paso a paso con matrices de rotación (Bloque 13) acumula error hasta que la matriz deja de ser ortogonal (Bloque 08, Tema 8.6); interpolar entre dos orientaciones con ángulos de Euler da giros que no son el camino más corto (Tema 9.6). Hace falta una representación que evite los tres problemas a la vez.

### 2. El mecanismo

Un **cuaternión** es un número con cuatro componentes, $q=(w,\vec v)=(w,x,y,z)$, que generaliza los números complejos. Sin ninguna necesidad de misticismo: para representar una rotación, basta con esta receta directa a partir de eje-ángulo (Tema 9.3):

$$q = \left(\cos\frac\theta2,\ \hat k\sin\frac\theta2\right)$$

es decir, **medio ángulo** en la parte escalar y **el eje escalado por el seno del medio ángulo** en la parte vectorial. Un cuaternión de rotación válido tiene norma 1 ($w^2+x^2+y^2+z^2=1$) — el análogo, con solo 4 números en vez de 9, de que una matriz de rotación sea ortogonal.

**Componer** dos rotaciones es multiplicar sus cuaterniones con el producto de Hamilton (una fórmula fija, sin ambigüedad de convención como los ángulos de Euler):

$$q_1q_2 = \big(w_1w_2-\vec v_1\cdot\vec v_2,\ \ w_1\vec v_2+w_2\vec v_1+\vec v_1\times\vec v_2\big)$$

(nótese que aparecen el producto punto y el producto cruz del Bloque 02, no una fórmula nueva de la nada). **Invertir** una rotación es conjugar: $q^{-1}=(w,-\vec v)$ (para $q$ unitario). Y, crucialmente para el Bloque 13, **no hay bloqueo del cardán**: los cuaterniones no tienen "ángulo intermedio" que se acerque a una singularidad — el precio es que 4 números para 3 GDL siguen siendo redundantes (norma 1, igual que eje-ángulo), y que no son tan directamente "legibles" por una persona como un ángulo en grados.

### 3. En la vida real

```python
from robotica.orientacion import cuaternion_desde_eje_angulo, cuaternion2mat, mat2cuaternion
q = cuaternion_desde_eje_angulo(np.array([0, 0, 1]), np.pi/2)
R = cuaternion2mat(q)
```

`scipy.spatial.transform.Rotation` trabaja internamente con cuaterniones (en su propia convención $(x,y,z,w)$, escalar al final, distinta de la $(w,x,y,z)$ escalar-primero usada aquí) — otra convención más que hay que verificar al comparar bibliotecas, como en el Tema 9.1.

### 4. Limitaciones

Un cuaternión y su negativo, $q$ y $-q$, representan la **misma** rotación (doble cobertura) — otra forma de no-unicidad, distinta de la de eje-ángulo pero de la misma naturaleza.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Al comparar un cuaternión propio con el de otra librería, los signos no coinciden aunque la rotación parece correcta | $q$ y $-q$ son la misma rotación; o las convenciones de orden $(w,x,y,z)$ contra $(x,y,z,w)$ están intercambiadas | Convertir ambos a matriz de rotación (Tema 9.1 y 9.4) y comparar ahí, no los cuaterniones directamente | Comparar siempre a nivel de matriz, o normalizar el signo (forzando $w\geq0$) antes de comparar cuaterniones |
| Un cuaternión "deja de ser válido" tras muchas composiciones seguidas | Deriva numérica: la norma ya no es exactamente 1 | Calcular $\sqrt{w^2+x^2+y^2+z^2}$ | Renormalizar dividiendo por la norma, periódicamente |

### 6. Dónde más aparece la idea

La orientación de un dron o un teléfono reportada por su IMU (*Inertial Measurement Unit*), la interpolación de cámaras y personajes en cualquier motor de videojuegos, la actitud de naves espaciales.

### 7. Ejemplos resueltos

**Ejemplo:** $\hat k=(0,0,1)$, $\theta=90°$: $q=(\cos45°,\ 0,0,\sin45°)=(0.707,0,0,0.707)$. Verificación de norma: $0.707^2+0.707^2=1.0$, cumple.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un cuaternión de rotación válido siempre tiene norma 1, relacionándolo con que $\sin^2(\theta/2)+\cos^2(\theta/2)=1$ (Bloque 01) y que $\hat k$ es unitario.

**Serie B — Cálculo a mano**
- B1. Calcular el cuaternión correspondiente a $\hat k=(1,0,0)$, $\theta=180°$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `robotica.orientacion.cuaternion_desde_eje_angulo`, convertirlo a matriz con `cuaternion2mat` y comparar con `rotx(np.pi)` del Bloque 08.

---

## Tema 9.5 — Conversiones entre representaciones y cuándo usar cada una

### 1. El problema

El curso ya tiene cuatro formas de decir "esta es la orientación": matriz, Euler (dos convenciones), eje-ángulo, cuaternión. Hace falta poder pasar de una a otra sin perder información, y saber cuál conviene en cada situación.

### 2. El mecanismo

Todas las conversiones pasan, en la práctica, por la matriz de rotación como "moneda común" (aunque existen atajos directos, como eje-ángulo↔cuaternión del Tema 9.4):

$$\text{Euler} \longrightarrow R \longrightarrow \text{eje-ángulo} \longrightarrow \text{cuaternión}$$

y cada flecha se puede recorrer en ambos sentidos con las funciones ya vistas. La elección de representación depende de para qué se va a usar:

| Uso | Representación recomendada | Por qué |
|---|---|---|
| Mostrarle un número a una persona | Euler (RPY) | Intuitivo, pocos números, cada uno con significado físico directo |
| Calcular, componer, transformar puntos | Matriz de rotación | Se multiplica directo con vectores y otras matrices (Bloque 08) |
| Guardar/transmitir con el mínimo de números sin ambigüedad de convención | Eje-ángulo | 4 números, sin las 12 convenciones posibles de Euler |
| Integrar velocidad angular, interpolar, control (Bloque 13, 18) | Cuaternión | Sin bloqueo del cardán, interpolación con SLERP (Tema 9.6), renormalizar es barato |

### 3. En la vida real

`robotica/orientacion.py` reúne las cuatro conversiones en un solo módulo, verificado con pruebas de "ida y vuelta" (convertir y volver a convertir debe reproducir el original).

### 4. Limitaciones

Ninguna nueva: cada limitación ya se vio en el tema de la representación correspondiente.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Convertir ida y vuelta (por ejemplo, matriz → Euler → matriz) no reproduce la matriz original | Se cayó cerca de una singularidad de la representación intermedia (bloqueo del cardán, Tema 9.2) | Repetir la prueba lejos de $\beta=\pm90°$ | Elegir una representación intermedia sin singularidad (eje-ángulo o cuaternión) para la conversión |

### 6. Dónde más aparece la idea

Cualquier sistema que combine una interfaz humana (grados, Euler) con un motor de cálculo interno (cuaterniones o matrices): software de CAD, motores de videojuegos, sistemas de navegación.

### 7. Ejemplos resueltos

**Ejemplo:** convertir $R_{RPY}(10°,20°,30°)$ a eje-ángulo y de vuelta a matriz debe reproducir la matriz original con error numérico despreciable (se verifica en el laboratorio).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Justificar, con la tabla de la sección 2, por qué un sistema de control de actitud de un satélite reporta la orientación al operador en Euler pero la calcula internamente con cuaterniones.

**Serie B — Cálculo a mano**
- B1. Dado un cuaternión $q=(0.9239,0,0,0.3827)$ (rotación de 45° en z), calcular a mano el eje y el ángulo equivalentes.

**Serie C — Laboratorio**
- C1. Escribir una prueba en Python que tome una matriz de rotación aleatoria (usando `scipy` para generarla), la convierta por las cuatro representaciones en cadena y de vuelta a matriz, y verifique que el resultado final coincide con el original.

---

## Tema 9.6 — Interpolar orientaciones: por qué Euler da giros raros y SLERP no

### 1. El problema

Una trayectoria (Bloque 19) necesita, a veces, girar suavemente de una orientación inicial a una final. Interpolar cada ángulo de Euler por separado (una recta entre el valor inicial y el final de cada uno) parece la solución obvia, pero produce movimientos que no son el giro más corto y que cambian de velocidad de forma extraña.

### 2. El mecanismo

Interpolar linealmente cada ángulo de Euler por separado **no** interpola uniformemente la orientación en el espacio de rotaciones: cerca de un bloqueo del cardán (Tema 9.2) la velocidad angular efectiva puede dispararse o casi anularse, y en general el camino recorrido no es el giro de menor ángulo entre las dos orientaciones.

**SLERP** (*Spherical Linear intERPolation*, interpolación esférica lineal) resuelve esto interpolando directamente entre dos cuaterniones $q_0,q_1$ a lo largo del camino más corto sobre la "esfera" de cuaterniones unitarios:

$$\text{slerp}(q_0,q_1,t) = \frac{\sin\big((1-t)\Omega\big)}{\sin\Omega}q_0 + \frac{\sin(t\Omega)}{\sin\Omega}q_1, \qquad \cos\Omega = q_0\cdot q_1$$

con $t\in[0,1]$. El resultado es una rotación que avanza a **velocidad angular constante** desde $q_0$ hasta $q_1$, por el camino más corto — geométricamente, es la versión sobre la esfera de cuaterniones de "interpolar en línea recta" entre dos puntos, adaptada a que el camino más corto entre dos puntos de una esfera es un arco, no una recta.

### 3. En la vida real

```python
from robotica.orientacion import slerp
q_t = slerp(q0, q1, t=0.5)   # orientación intermedia, a mitad de camino
```

### 4. Limitaciones

Si $q_0\cdot q_1<0$, SLERP toma el camino "largo" (más de 180°) porque $q$ y $-q$ son la misma rotación (Tema 9.4) pero corresponden a puntos distintos en la fórmula; hay que negar uno de los dos cuaterniones si $q_0\cdot q_1<0$ para garantizar el camino corto.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Interpolar ángulos de Euler cerca de un bloqueo del cardán produce un giro visiblemente "raro" (acelera o cambia de eje bruscamente) | Interpolación lineal de Euler cerca de una singularidad de la representación (Tema 9.2) | Repetir la interpolación con SLERP sobre cuaterniones y comparar la trayectoria | Usar SLERP para cualquier interpolación de orientación, no interpolación de ángulos de Euler |
| SLERP toma el camino largo entre dos orientaciones que deberían estar cerca | $q_0\cdot q_1<0$: los cuaterniones "apuntan en direcciones opuestas" de la doble cobertura aunque representan orientaciones cercanas | Calcular el signo de $q_0\cdot q_1$ antes de interpolar | Negar $q_1$ (o $q_0$) si el producto punto es negativo |

### 6. Dónde más aparece la idea

Animación de cámaras y personajes en videojuegos y cine (SLERP es el estándar de la industria), planificación de movimiento de brazos robóticos y drones donde la orientación debe cambiar suavemente.

### 7. Ejemplos resueltos

**Ejemplo:** interpolar de $q_0=(1,0,0,0)$ (sin giro) a $q_1=(0,0,0,1)$ (180° en z) con SLERP en $t=0.5$ da exactamente el cuaternión de 90° en z, $(0.707,0,0,0.707)$ — la mitad exacta del camino angular, algo que la interpolación lineal de ángulos de Euler no garantiza en general cerca de singularidades.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, con la analogía de "el camino más corto entre dos puntos de una esfera es un arco, no una recta", por qué SLERP tiene esa fórmula con senos en vez de una interpolación lineal simple.

**Serie B — Cálculo a mano**
- B1. Verificar que $\cos\Omega=q_0\cdot q_1$ da $\Omega=90°$ para el ejemplo de la sección 7 ($q_0\cdot q_1=1\times0+0+0+0\times1=0$).

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_09/comparar_interpolacion.py`: interpola entre dos orientaciones cercanas a un bloqueo del cardán con ángulos de Euler (interpolación lineal ingenua) y con SLERP, animando ambas para comparar.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/orientacion.py`: `rpy2mat`/`mat2rpy`, `zxz2mat`/`mat2zxz` (Tema 9.1, portadas y adaptadas a radianes), `eje_angulo2mat`/`mat2eje_angulo` (Tema 9.3), `cuaternion_desde_eje_angulo`/`cuaternion2mat`/`mat2cuaternion` (Tema 9.4), `slerp` (Tema 9.6).

## Glosario del bloque

| Término | Definición |
|---|---|
| Ángulos de Euler | Tres rotaciones sucesivas alrededor de ejes elegidos por convención (12 convenciones posibles); RPY y ZXZ son las que usa este curso. |
| Roll-Pitch-Yaw (RPY) | Alabeo-cabeceo-guiñada: convención de Euler con rotaciones en x, y, z respecto a ejes fijos. |
| Bloqueo del cardán (*gimbal lock*) | Pérdida de un grado de libertad de la representación (no del objeto) cuando el ángulo intermedio de una convención de Euler llega a $\pm90°$. |
| Eje-ángulo | Representación de una rotación como un único giro $\theta$ alrededor de un eje unitario $\hat k$; fórmula de Rodrigues. |
| Cuaternión | Número de cuatro componentes $(w,x,y,z)$ que representa una rotación sin bloqueo del cardán; norma 1 si es válido. |
| SLERP | Interpolación esférica lineal entre cuaterniones, a velocidad angular constante por el camino más corto. |
