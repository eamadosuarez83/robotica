# Bloque 08 — Localización espacial I: posición y rotación

> **Problema que abre el bloque:** la pinza está en (0,30; 0,10; 0,20) m. Eso no dice si el huevo cae o no: falta saber hacia dónde apunta.
>
> **Necesitas antes:** Bloque 07. · **Lectura:** Barrientos, cap. 3 (primera parte); Lynch & Park, *Modern Robotics*, cap. 3.

Este bloque porta código de [`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores)
(`transformaciones.py`: `rotx`, `roty`, `rotz`) — ver
[docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md). Con una diferencia
deliberada: allá esas funciones devuelven matrices **homogéneas 4×4** (rotación y traslación ya
combinadas, porque ese repositorio no separa los dos temas); aquí devuelven matrices de rotación
**3×3 puras**, porque el curso reserva la combinación con traslación para el Bloque 10. La
convención de unidades (radianes) es idéntica en ambos.

## Tema 8.1 — Marco de referencia: por qué un robot tiene muchos

### 1. El problema

"La pinza está en (0,30; 0,10; 0,20)" no dice nada por sí solo: ¿medido desde dónde? ¿con qué eje hacia arriba? Sin fijar un origen y una dirección para cada eje, cualquier número de posición es ambiguo.

### 2. El mecanismo

Un **marco de referencia** (o sistema de coordenadas) es un origen más tres ejes perpendiculares entre sí, siempre **dextrógiros** (regla de la mano derecha, Bloque 02: $\hat x\times\hat y=\hat z$) por convención del curso. Un robot necesita, en realidad, varios marcos a la vez: uno fijo a la base (el marco "mundo", donde vive todo lo demás), uno por cada eslabón (que se mueve con él), uno en la pinza, y a veces uno más en la cámara o en el objeto que se manipula. Un mismo punto físico tiene coordenadas **distintas** según en qué marco se exprese — esta es exactamente la razón por la que el Bloque 10 necesita una forma sistemática de convertir coordenadas de un marco a otro.

### 3. En la vida real

En código, un marco no es más que una matriz (Bloque 10) o, por ahora, una matriz de rotación (Tema 8.3) más un vector de posición, ambos expresados respecto a algún otro marco de referencia (típicamente el fijo).

### 4. Limitaciones

Ninguna: es una elección de convención, no una aproximación física — pero **hay que ser consistente** con esa elección en todo el modelo.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Dos partes del código (por ejemplo, la cámara y el brazo) dan coordenadas incompatibles para el mismo punto físico | Se están usando marcos de referencia distintos sin convertir entre ellos | Preguntar explícitamente, para cada número, "¿respecto a qué marco?" | Definir un único marco de referencia global y convertir todo lo demás a él (Bloque 10) |

### 6. Dónde más aparece la idea

Coordenadas GPS (marco fijo a la Tierra) contra coordenadas de un mapa local, el marco de una cámara contra el marco del mundo en visión artificial, "arriba" en un videojuego (marco de la cámara) contra "arriba" en el mundo del juego.

### 7. Ejemplos resueltos

**Ejemplo:** la altura de un dron puede expresarse respecto al suelo (marco mundo) o respecto a su punto de despegue (marco local): mismo dron, mismo instante, dos números de altura distintos si despegó de una terraza.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Dar un ejemplo cotidiano (no de robótica) donde la misma posición se describa de forma distinta según el marco de referencia elegido.

**Serie B — Cálculo a mano**
- B1. Si el marco de un eslabón está desplazado $(0.1,0,0)$ m respecto al marco fijo, y un punto está en $(0.05,0.02,0)$ m en el marco del eslabón, dar sus coordenadas en el marco fijo (solo traslación, sin rotación).

**Serie C — Laboratorio**
- C1. Escribir en Python una función que sume el desplazamiento de B1 a un arreglo de puntos, y verificar el resultado.

---

## Tema 8.2 — Coordenadas cartesianas, cilíndricas y esféricas

### 1. El problema

Describir la posición de la pinza con $(x,y,z)$ es natural para un brazo cartesiano (Bloque 07), pero incómodo para uno que gira sobre una base (donde "qué tan lejos y en qué ángulo" es más directo que "cuánto en x y cuánto en y").

### 2. El mecanismo

Tres sistemas cubren los casos del curso, todos relacionados por trigonometría (Bloque 01):

- **Cartesianas** $(x,y,z)$: la base, sin conversión.
- **Cilíndricas** $(\rho,\phi,z)$: $\rho$ la distancia al eje $z$, $\phi$ el ángulo en el plano $xy$, $z$ igual que en cartesianas. $x=\rho\cos\phi,\ y=\rho\sin\phi$ — la misma relación seno/coseno-como-proyección del Bloque 01.
- **Esféricas** $(r,\theta,\phi)$: $r$ la distancia al origen, $\theta$ el ángulo desde el eje $z$ (colatitud), $\phi$ igual que en cilíndricas. $x=r\sin\theta\cos\phi,\ y=r\sin\theta\sin\phi,\ z=r\cos\theta$.

La elección no es solo estética: la configuración cilíndrica y la polar/esférica del Bloque 07 llevan ese nombre precisamente porque sus primeras articulaciones producen, de forma natural, coordenadas cilíndricas o esféricas de la punta — describir su espacio de trabajo en ese sistema es mucho más simple que en cartesianas.

### 3. En la vida real

```python
rho, phi, z = np.hypot(x, y), np.arctan2(y, x), z          # cartesianas -> cilíndricas
r = np.sqrt(x**2 + y**2 + z**2)
theta = np.arccos(z / r)                                   # cartesianas -> esféricas
```

### 4. Limitaciones

Cilíndricas y esféricas son singulares en su propio eje ($\rho=0$ deja $\phi$ indefinido; $r=0$ deja $\theta,\phi$ indefinidos) — el mismo tipo de problema que reaparece con las orientaciones en el Bloque 09.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| $\phi$ calculado con `arctan(y/x)` da el cuadrante equivocado | El mismo error del Bloque 01, Tema 1.3 | Usar un punto de prueba en el cuadrante II o III | Usar `arctan2(y,x)`, no `arctan(y/x)` |

### 6. Dónde más aparece la idea

Coordenadas geográficas (esféricas: latitud/longitud), radares (polares/esféricas), el espacio de trabajo de brazos cilíndricos y esféricos (Bloque 07).

### 7. Ejemplos resueltos

**Ejemplo:** el punto cartesiano $(1,1,1)$ en esféricas: $r=\sqrt3\approx1.73$, $\theta=\arccos(1/\sqrt3)\approx54.7°$, $\phi=\arctan2(1,1)=45°$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $\phi$ queda indefinido cuando $\rho=0$ (o $r=0$), pensando en qué significa geométricamente.

**Serie B — Cálculo a mano**
- B1. Convertir el punto cartesiano $(0,3,4)$ a cilíndricas y a esféricas.

**Serie C — Laboratorio**
- C1. Verificar B1 en Python y graficar los tres sistemas de coordenadas de ese mismo punto en una sola figura 3D.

---

## Tema 8.3 — La matriz de rotación

### 1. El problema

La orientación de la pinza —hacia dónde apuntan sus propios ejes x, y, z respecto al marco fijo— necesita una descripción tan precisa como su posición. El Bloque 03 ya enseñó que una matriz transforma vectores; una matriz de rotación es el caso particular que transforma *marcos completos* sin deformarlos.

### 2. El mecanismo

Retomando el Bloque 03 (Tema 3.1): las columnas de una matriz dicen a dónde va cada eje de la base. Una **matriz de rotación** $R$ de $3\times3$ es, exactamente, eso: sus tres columnas son los ejes $\hat x',\hat y',\hat z'$ del marco *girado*, expresados como vectores en el marco fijo:

$$R = \begin{pmatrix} | & | & | \\ \hat x' & \hat y' & \hat z' \\ | & | & | \end{pmatrix}$$

Por eso, para "leer" una matriz de rotación no hace falta ninguna fórmula: la primera columna dice literalmente hacia dónde apunta el eje x del marco girado, vista desde el marco fijo. Un vector $\vec v'$ expresado en el marco girado se convierte a coordenadas del marco fijo con $\vec v=R\vec v'$ — la misma multiplicación matriz-vector del Bloque 03.

### 3. En la vida real

```python
R = np.column_stack([x_prima, y_prima, z_prima])   # construir R a partir de los ejes girados
v_fijo = R @ v_movil
```

### 4. Limitaciones

$R$ por sí sola describe solo **orientación**, no posición — el Bloque 10 las combina.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una matriz de rotación se arma con los ejes girados como **filas** en vez de columnas | Confusión con la convención del Bloque 03 | Verificar que `R @ [1,0,0]` dé exactamente el eje x girado esperado | Ejes girados como columnas, siempre |

### 6. Dónde más aparece la idea

La orientación de una cámara en gráficos 3D, la actitud de una nave o un dron, cualquier "marco local" en animación.

### 7. Ejemplos resueltos

**Ejemplo:** si al girar, el eje x del marco móvil queda apuntando hacia $(0,1,0)$ del marco fijo, el eje y hacia $(-1,0,0)$ y el eje z se mantiene en $(0,0,1)$: $R=\begin{pmatrix}0&-1&0\\1&0&0\\0&0&1\end{pmatrix}$ — un giro de 90° alrededor de z (se confirma en el Tema 8.4).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la matriz identidad $I$ es la matriz de rotación de "ningún giro".

**Serie B — Cálculo a mano**
- B1. Si el eje z del marco móvil apunta hacia $(1,0,0)$ del fijo, el eje x hacia $(0,0,-1)$ y el eje y hacia $(0,1,0)$, escribir $R$.

**Serie C — Laboratorio**
- C1. Verificar B1 confirmando que `R.T @ R` da la identidad (Tema 8.6) y que `np.linalg.det(R)` da 1.

---

## Tema 8.4 — Rotaciones básicas alrededor de x, y, z

### 1. El problema

Antes de componer rotaciones arbitrarias, hace falta la forma explícita de las tres más simples: girar puro alrededor de cada eje del marco fijo.

### 2. El mecanismo

Girar un ángulo $\theta$ alrededor del eje z dice, por la lectura del Tema 8.3, que el eje z no se mueve, y que x e y giran entre sí como en el círculo unitario del Bloque 01 (Tema 1.2):

$$R_z(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{pmatrix}$$

y de forma análoga, permutando los ejes cíclicamente ($x\to y\to z\to x$):

$$R_x(\theta) = \begin{pmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{pmatrix}, \qquad R_y(\theta) = \begin{pmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{pmatrix}$$

Nótese el signo de $R_y$: está "al revés" respecto al patrón de $R_x$ y $R_z$ porque, para mantener la regla de la mano derecha, el ciclo correcto es $y\to z\to x$ visto desde el eje y positivo — un detalle que se verifica fácilmente evaluando $R_y(90°)\hat x$ y comprobando que da $-\hat z$, no $\hat z$.

### 3. En la vida real

`robotica/rotaciones.py` implementa `rotx`, `roty`, `rotz`, portadas de `transformaciones.py` de `robotica-manipuladores` pero devolviendo matrices **3×3** (ver nota al inicio del bloque). Ese módulo, además, redondea a cero los senos y cosenos que deberían ser exactamente cero en múltiplos de $\pi/2$ (por ejemplo, `cos(pi/2)` da `6e-17` en punto flotante, no `0.0`) — un detalle que evita arrastrar "casi ceros" en cálculos posteriores.

```python
from robotica.rotaciones import rotx, roty, rotz
rotz(np.pi/2)   # array 3x3
```

### 4. Limitaciones

Ninguna nueva.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un giro alrededor de y da un resultado "reflejado" respecto al esperado | Se copió el patrón de signos de $R_x$/$R_z$ sin ajustar el de $R_y$ | Evaluar `roty(np.pi/2) @ [1,0,0]`: debe dar $(0,0,-1)$ | Usar la fórmula de $R_y$ con el signo correcto (el opuesto al patrón de $R_x,R_z$) |

### 6. Dónde más aparece la idea

Cualquier giro puro alrededor de un eje principal: la rueda de un vehículo (alrededor de su propio eje), una puerta (alrededor de sus bisagras).

### 7. Ejemplos resueltos

**Ejemplo:** $R_x(90°)\hat y=(0,\cos90°,\sin90°)=(0,0,1)=\hat z$: girar el eje y 90° alrededor de x lo manda a z, consistente con la regla de la mano derecha.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Verificar, sin calculadora, que $R_z(360°)=I$.

**Serie B — Cálculo a mano**
- B1. Calcular $R_y(180°)$ y describir en palabras qué le hace al marco.

**Serie C — Laboratorio**
- C1. Verificar B1 con `robotica.rotaciones.roty` y comparar contra `scipy.spatial.transform.Rotation.from_euler('y', 180, degrees=True).as_matrix()`.

---

## Tema 8.5 — Composición de rotaciones: ejes fijos contra ejes móviles

### 1. El problema

Un procedimiento de ensamblaje dice "gira 90° en z, luego 90° en el nuevo eje x". Otro dice "gira 90° en z, luego 90° en el eje x *original*". Son instrucciones distintas que llevan a orientaciones finales distintas, y hay que saber traducir cada una a una multiplicación de matrices sin ambigüedad.

### 2. El mecanismo

Esto es una aplicación directa del Bloque 03 (Tema 3.2: el orden de composición) a rotaciones:

- **Posmultiplicar** ($R=R_1R_2$): la segunda rotación, $R_2$, se aplica respecto a los **ejes móviles** (el marco ya girado por $R_1$) — es como decir "ahora, desde donde quedaste, gira esto otro".
- **Premultiplicar** ($R=R_2R_1$): la segunda rotación se aplica respecto a los **ejes fijos** (los originales, sin importar cómo quedó el marco después de $R_1$) — "gira esto otro, medido siempre desde el marco original".

Ambos procedimientos son legítimos y aparecen en la práctica (los ángulos roll-pitch-yaw del Bloque 09 se definen, por convención, respecto a ejes fijos), pero dan resultados **distintos** salvo en casos especiales (rotaciones sobre el mismo eje). Confundir uno por otro es el error más común al describir una secuencia de giros.

### 3. En la vida real

```python
R_fijos = R2 @ R1     # R2 respecto a ejes fijos: se premultiplica
R_moviles = R1 @ R2   # R2 respecto a ejes móviles (los ya girados por R1): se posmultiplica
```

### 4. Limitaciones

Ninguna nueva: es la asociatividad y no conmutatividad del producto de matrices (Bloque 03), aplicada aquí con una interpretación física concreta.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Seguir un procedimiento de giros da una orientación distinta a la esperada por otra persona que lo interpretó igual "en palabras" | No se acordó explícitamente si cada paso es respecto a ejes fijos o móviles | Comparar el resultado premultiplicando y posmultiplicando; si difieren, la ambigüedad era real | Especificar siempre, sin ambigüedad, "respecto a ejes fijos" o "respecto a ejes móviles" en cada paso |

### 6. Dónde más aparece la idea

Instrucciones de vuelo de un avión (¿guiñada respecto a la Tierra o respecto al avión?), animación de personajes (rotaciones locales de huesos contra globales), la diferencia entre D-H estándar y D-H modificado (Bloque 11, adelanto).

### 7. Ejemplos resueltos

**Ejemplo:** $R_1=R_z(90°)$, $R_2=R_x(90°)$. Aplicado a $\hat x$: posmultiplicando ($R_1R_2$, $R_2$ respecto a ejes móviles) da un resultado distinto que premultiplicando ($R_2R_1$, $R_2$ respecto a ejes fijos) — se verifica en el laboratorio, C1.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar con un ejemplo cotidiano (por ejemplo, indicaciones para girar un mapa) la diferencia entre "gira respecto a como quedaste" y "gira respecto a como empezaste".

**Serie B — Cálculo a mano**
- B1. Calcular $R_z(90°)R_x(90°)$ y $R_x(90°)R_z(90°)$ y confirmar que son distintas.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_08/romper_orden_rotaciones.py`: compone las mismas dos rotaciones premultiplicando y posmultiplicando, dibuja los dos marcos resultantes y muestra que la pinza termina apuntando en direcciones distintas.

---

## Tema 8.6 — Propiedades de una matriz de rotación: por qué 9 números describen solo 3 GDL

### 1. El problema

Una matriz de rotación tiene 9 números, pero orientar un objeto rígido en 3D es un problema de **3 grados de libertad** (Bloque 07, Tema 7.2). Hacen falta 6 restricciones "escondidas" entre esos 9 números, y conviene saber cuáles son.

### 2. El mecanismo

Toda matriz de rotación es **ortogonal** (Bloque 03, Tema 3.5): sus columnas son los ejes girados, que por definición de "girar sin deformar" siguen siendo unitarios y perpendiculares entre sí. Eso impone exactamente las restricciones que faltan:

- Cada columna unitaria: $\|\hat x'\|=\|\hat y'\|=\|\hat z'\|=1$ → 3 restricciones.
- Columnas perpendiculares entre sí: $\hat x'\cdot\hat y'=\hat x'\cdot\hat z'=\hat y'\cdot\hat z'=0$ → 3 restricciones más.

$9-6=3$: exactamente los grados de libertad de una orientación. Como consecuencia directa de ser ortogonal (Bloque 03, Tema 3.5), toda matriz de rotación cumple $R^{-1}=R^T$ — invertir un giro es tan simple como transponer la matriz, sin el costo ni el riesgo numérico de una inversión general — y su determinante es $+1$ (no $-1$: eso sería una reflexión, un "espejo", no una rotación física alcanzable girando un objeto rígido).

Esta es la razón profunda por la que el Bloque 09 necesita representaciones alternativas: si de verdad solo hacen falta 3 números independientes, ¿por qué cargar con 9 y sus 6 restricciones? Los ángulos de Euler, el par eje-ángulo y los cuaterniones son distintas formas de aprovechar esa economía.

### 3. En la vida real

```python
np.allclose(R.T @ R, np.eye(3))   # ortogonal
np.isclose(np.linalg.det(R), 1.0) # rotación, no reflexión
Rinv = R.T                        # inversa = transpuesta
```

### 4. Limitaciones

Errores de redondeo acumulados (por ejemplo, integrar una rotación paso a paso, Bloque 13) pueden hacer que una matriz "deje de ser" exactamente ortogonal — el mismo problema de deriva numérica mencionado en el Bloque 03.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una matriz que debería ser de rotación tiene determinante $-1$ | Se construyó con un eje invertido por error (por ejemplo, $\hat z'=-\hat x'\times\hat y'$ en vez de $\hat x'\times\hat y'$) | Calcular `np.linalg.det(R)` | Revisar el signo del tercer eje: debe ser $\hat z'=\hat x'\times\hat y'$, respetando la mano derecha |
| Una matriz "de rotación" no es exactamente ortogonal tras muchas operaciones | Deriva numérica acumulada | `np.linalg.norm(R.T @ R - np.eye(3))` | Reortonormalizar (recalcular el tercer eje como producto cruz de los otros dos, o usar cuaterniones, Bloque 09) |

### 6. Dónde más aparece la idea

Por qué una imagen reflejada en un espejo no se puede obtener rotando la imagen original (determinante $-1$ contra $+1$); cualquier verificación de "esto sigue siendo una rotación válida" en gráficos 3D o robótica.

### 7. Ejemplos resueltos

**Ejemplo:** $R=\begin{pmatrix}1&0&0\\0&1&0\\0&0&-1\end{pmatrix}$ (invierte z, deja x,y igual): $\det R=-1$. Es ortogonal (columnas unitarias y perpendiculares) pero **no** es una rotación: es una reflexión, un marco "en espejo" (Bloque 03, Tema 3.4) — no hay ninguna forma de girar un objeto rígido para llegar a esa orientación.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué una reflexión no puede lograrse rotando un objeto rígido en el espacio, pensando en la "quiralidad" (una mano izquierda no se puede rotar para que coincida con una derecha).

**Serie B — Cálculo a mano**
- B1. Verificar a mano que $R_z(\theta)$ del Tema 8.4 cumple $R_z(\theta)^{-1}=R_z(\theta)^T=R_z(-\theta)$.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Construir en Python una matriz con determinante $-1$ (invertir un eje de una rotación válida) y dibujar el marco resultante junto al original: debe verse "en espejo", no como un giro alcanzable.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/rotaciones.py`: `rotx`, `roty`, `rotz` (matrices 3×3, radianes) — portadas de `robotica-manipuladores` con la adaptación de tamaño explicada al inicio del bloque.

## Glosario del bloque

| Término | Definición |
|---|---|
| Marco de referencia | Origen más tres ejes perpendiculares dextrógiros, respecto al cual se miden posiciones y orientaciones. |
| Coordenadas cilíndricas / esféricas | Sistemas alternativos a las cartesianas, naturales para brazos con configuración cilíndrica o esférica (Bloque 07). |
| Matriz de rotación | Matriz $3\times3$ cuyas columnas son los ejes de un marco girado, vistos desde el marco fijo. |
| Ejes fijos / ejes móviles | Al componer rotaciones: medir el siguiente giro respecto al marco original (fijo, se premultiplica) o respecto al marco ya girado (móvil, se posmultiplica). |
| Ortogonal | Matriz cuyas columnas son unitarias y perpendiculares entre sí (Bloque 03); toda matriz de rotación lo es. |
| Reflexión | Transformación ortogonal con determinante $-1$; invierte la orientación ("espejo"), no es alcanzable rotando un cuerpo rígido. |
