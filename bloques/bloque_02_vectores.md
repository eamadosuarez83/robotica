# Bloque 02 — Vectores

> **Problema que abre el bloque:** la punta del brazo está en un punto, pero además empuja con una fuerza en una dirección. ¿Cómo se describe algo que tiene tamaño y dirección, y cómo se calcula el giro que produce?
>
> **Necesitas antes:** Bloque 01. · **Lectura:** Strang, *Introduction to Linear Algebra*, cap. 1; 3Blue1Brown, *Essence of Linear Algebra*, episodios 1–2.

## Tema 2.1 — Vector: flecha y lista de números

### 1. El problema

"El motor gira 40°" es un número. "La pinza está en (0.30, 0.20, 0.15) m" ya no lo es: hace falta algo con varias componentes a la vez, y que además se pueda sumar, escalar y comparar en dirección. Eso es un vector.

### 2. El mecanismo

Un vector se puede ver de dos formas, y el curso usa las dos según convenga:

- **Como flecha**: tiene magnitud (qué tan largo) y dirección (hacia dónde apunta). No tiene una posición fija: la flecha de $(0,0)$ a $(3,4)$ es "el mismo" vector que la de $(1,1)$ a $(4,5)$.
- **Como lista de números**: `np.array([3, 4])` en un programa, o $\begin{pmatrix}3\\4\end{pmatrix}$ en una ecuación. Cada número es la componente del vector a lo largo de un eje.

Ambas vistas son la misma cosa. La vista de flecha ayuda a *entender* (sumar vectores es poner una flecha a continuación de la otra); la vista de lista de números es la que permite *calcular* con NumPy.

**Vector posición** contra **vector desplazamiento**: la posición de la pinza, $\vec p = (0.30,0.20,0.15)$, está anclada al origen del sistema de coordenadas. Un desplazamiento, $\Delta\vec p = \vec p_2 - \vec p_1$, no depende de dónde esté el origen: es "cuánto y hacia dónde se movió", y se puede dibujar empezando en cualquier lado.

**Suma, resta y escalamiento**: $\vec u + \vec v$ se hace componente a componente; geométricamente es poner la flecha de $\vec v$ en la punta de $\vec u$. $c\vec u$ (con $c$ un número) estira o encoge la flecha, y la invierte si $c<0$.

**Norma** (longitud): $\|\vec v\| = \sqrt{v_x^2+v_y^2+v_z^2}$, el teorema de Pitágoras en tres dimensiones.

**Vector unitario**: $\hat v = \vec v / \|\vec v\|$, la misma dirección con longitud 1. Sirve para separar "hacia dónde" de "qué tan largo".

### 3. En la vida real

```python
import numpy as np
u = np.array([3.0, 4.0, 0.0])
v = np.array([1.0, 0.0, 2.0])
u + v            # suma componente a componente
2.0 * u          # escalamiento
np.linalg.norm(u)  # norma: 5.0
u / np.linalg.norm(u)  # vector unitario
```

### 4. Limitaciones

Un vector describe una cantidad con magnitud y dirección (posición, fuerza, velocidad); no describe una orientación completa en 3D por sí solo (para eso hace falta un marco de referencia entero, Bloque 08) ni una rotación (Bloque 09).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una resta de posiciones da un vector con dirección invertida | Se restó en el orden equivocado ($\vec p_1-\vec p_2$ en vez de $\vec p_2-\vec p_1$) | Comparar el signo de cada componente con el sentido físico esperado del movimiento | El desplazamiento de 1 a 2 es siempre $\vec p_2-\vec p_1$ |

### 6. Dónde más aparece la idea

Velocidad y aceleración (Bloque 04) son vectores; fuerzas en estática y dinámica (Bloques 06, 14–16); cualquier magnitud con dirección en física.

### 7. Ejemplos resueltos

**Ejemplo:** $\vec u=(3,4,0)$, $\vec v=(1,0,2)$. $\vec u+\vec v=(4,4,2)$. $\|\vec u\|=5$. $\hat u=(0.6,0.8,0)$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar la diferencia entre vector posición y vector desplazamiento con un ejemplo del brazo.

**Serie B — Cálculo a mano**
- B1. Con $\vec u=(2,-1,2)$, calcular $\|\vec u\|$ y $\hat u$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `robotica.vectores.norma` y `robotica.vectores.vector_unitario`, comparando además con `np.linalg.norm`.

---

## Tema 2.2 — Producto punto

### 1. El problema

Se empuja una caja con una fuerza en diagonal, pero la caja solo se puede mover en línea recta sobre el piso. ¿Cuánta de esa fuerza diagonal realmente "sirve" para mover la caja en esa dirección? Hace falta una operación que mida cuánto de un vector va en la dirección de otro.

### 2. El mecanismo

El **producto punto** (o producto escalar) de dos vectores se define, en componentes, como:

$$\vec u \cdot \vec v = u_xv_x+u_yv_y+u_zv_z$$

y es equivalente a:

$$\vec u \cdot \vec v = \|\vec u\|\,\|\vec v\|\cos\theta$$

donde $\theta$ es el ángulo entre ambos vectores. La segunda forma es la que da el significado geométrico: $\vec u\cdot\hat v$ (con $\hat v$ unitario) es exactamente **la proyección de $\vec u$ sobre la dirección de $\vec v$** — "cuánto de $\vec u$ va en la dirección de $\vec v$".

De esa fórmula se despeja el ángulo entre dos vectores, útil en todo el curso para medir qué tan alineados están dos ejes o dos direcciones:

$$\theta = \arccos\left(\frac{\vec u\cdot\vec v}{\|\vec u\|\,\|\vec v\|}\right)$$

**Ortogonalidad**: si $\vec u\cdot\vec v=0$ y ninguno de los dos es el vector cero, entonces $\cos\theta=0$, es decir $\theta=90°$: los vectores son perpendiculares. Esta es la prueba que se usa en el Bloque 08 para confirmar que los ejes de un marco de referencia son perpendiculares entre sí.

### 3. En la vida real

```python
np.dot(u, v)   # o: u @ v
```

`robotica/vectores.py` implementa `producto_punto` a mano (sumando `u*v` elemento a elemento) para ver el mecanismo antes de usar `np.dot`.

### 4. Limitaciones

El producto punto no distingue si $\vec v$ está "a la izquierda" o "a la derecha" de $\vec u$: solo mide alineación, no un sentido de giro (para eso hace falta el producto cruz).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| $\arccos$ lanza un error de dominio (`nan`) | El argumento de `arccos` quedó ligeramente fuera de $[-1,1]$ por redondeo numérico | Imprimir el valor exacto antes de aplicar `arccos` | Recortar (`np.clip`) el argumento al rango $[-1,1]$ antes de usar `arccos` |

### 6. Dónde más aparece la idea

Trabajo mecánico ($W=\vec F\cdot\vec d$), potencia eléctrica en corriente alterna, similitud entre vectores en aprendizaje automático, iluminación en gráficos 3D (cuánto "de frente" está una superficie a la luz).

### 7. Ejemplos resueltos

**Ejemplo:** $\vec u=(1,2,3)$, $\vec v=(0,1,-1)$. $\vec u\cdot\vec v = 0+2-3=-1$. Como $\|\vec u\|=\sqrt{14}$, $\|\vec v\|=\sqrt2$: $\theta=\arccos(-1/\sqrt{28})\approx 100.9°$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $\vec u\cdot\vec v=0$ implica perpendicularidad, usando la fórmula $\|\vec u\|\|\vec v\|\cos\theta$.

**Serie B — Cálculo a mano**
- B1. Calcular el ángulo entre $\vec u=(1,0,0)$ y $\vec v=(1,1,0)$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `robotica.vectores.angulo_entre` y `robotica.vectores.son_ortogonales`.

---

## Tema 2.3 — Producto cruz y torque

### 1. El problema

Una llave gira una tuerca porque se le aplica una fuerza a cierta distancia del eje. El efecto de giro (el torque) no es un número: tiene un eje de giro y un sentido (horario o antihorario visto desde cierto lado). Hace falta una operación que combine dos vectores —la posición donde se aplica la fuerza y la fuerza misma— y devuelva ese eje de giro.

### 2. El mecanismo

El **producto cruz** de dos vectores de 3 componentes es otro vector, perpendicular a los dos originales:

$$\vec u \times \vec v = \begin{pmatrix} u_yv_z-u_zv_y \\ u_zv_x-u_xv_z \\ u_xv_y-u_yv_x \end{pmatrix}$$

Su **dirección** se obtiene con la regla de la mano derecha: se apuntan los dedos en la dirección de $\vec u$ y se cierran hacia $\vec v$; el pulgar da la dirección de $\vec u\times\vec v$. Su **magnitud** es:

$$\|\vec u\times\vec v\| = \|\vec u\|\,\|\vec v\|\sin\theta$$

que es exactamente el área del paralelogramo que forman $\vec u$ y $\vec v$ — por eso el producto cruz de dos vectores paralelos es el vector cero (no encierran área).

**El torque**: una fuerza $\vec F$ aplicada en un punto ubicado en $\vec r$ respecto al eje de giro produce un torque

$$\vec\tau = \vec r \times \vec F$$

Su dirección es el eje sobre el que la fuerza tiende a girar el cuerpo; su magnitud, $\|\vec r\|\|\vec F\|\sin\theta$, dice que solo la componente de $\vec F$ *perpendicular* a $\vec r$ produce giro (empujar una llave hacia el eje de la tuerca, en vez de perpendicular a ella, no la gira).

**Orden**: el producto cruz **no es conmutativo**: $\vec u\times\vec v = -(\vec v\times\vec u)$. Invertir el orden invierte el sentido del giro resultante.

### 3. En la vida real

```python
np.cross(u, v)
```

`robotica/vectores.py` implementa `producto_cruz` y `torque` a mano, comparables con `np.cross`.

### 4. Limitaciones

El producto cruz, tal como se define aquí, solo existe en 3D (y de forma degenerada en 2D, como un escalar). No aplica directamente a espacios de más dimensiones.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El torque calculado gira al lado contrario del esperado | Se invirtió el orden del producto cruz ($\vec F\times\vec r$ en vez de $\vec r\times\vec F$) | Recalcular con el orden correcto y comparar el signo de cada componente | Usar siempre $\vec r\times\vec F$, en ese orden |
| El torque da cero cuando debería haber giro | $\vec r$ y $\vec F$ son paralelos (la fuerza apunta directo al eje, o el punto de aplicación coincide con el eje) | Revisar el ángulo entre $\vec r$ y $\vec F$ | Verificar que el punto de aplicación y la dirección de la fuerza sean los correctos |

### 6. Dónde más aparece la idea

El torque de cada articulación de un brazo robótico (Bloques 13 a 16), el momento angular, la fuerza de Lorentz en electromagnetismo, la normal a una superficie en gráficos 3D, la velocidad lineal de un punto en un cuerpo rígido en rotación ($\vec v=\vec\omega\times\vec r$).

### 7. Ejemplos resueltos

**Ejemplo:** $\vec u=(1,2,3)$, $\vec v=(0,1,-1)$. $\vec u\times\vec v=(2\cdot(-1)-3\cdot1,\ 3\cdot0-1\cdot(-1),\ 1\cdot1-2\cdot0)=(-5,1,1)$.

**Ejemplo (torque):** una llave de $\vec r=(0.20,0,0)$ m (20 cm desde la tuerca) recibe una fuerza $\vec F=(0,50,0)$ N perpendicular al mango. $\vec\tau=\vec r\times\vec F=(0,0,10)$ N·m: gira alrededor del eje z, con magnitud 10 N·m.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué empujar una llave *hacia* la tuerca (en la dirección de $\vec r$) no la afloja, usando la fórmula de la magnitud del producto cruz.

**Serie B — Cálculo a mano**
- B1. Calcular $\vec r\times\vec F$ para $\vec r=(0.15,0,0)$ m y $\vec F=(0,0,-30)$ N. ¿Alrededor de qué eje gira?

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_02/demo_vectores.py`, que dibuja en 3D el torque de una llave sobre una tuerca.
- C2. Correr `codigo/bloque_02/romper_orden_cruz.py`, que invierte el orden del producto cruz del ejercicio anterior y grafica cómo el torque cambia de sentido.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/vectores.py`: `norma`, `vector_unitario`, `producto_punto`, `angulo_entre`, `son_ortogonales`, `producto_cruz`, `torque`.

## Glosario del bloque

| Término | Definición |
|---|---|
| Vector | Cantidad con magnitud y dirección; se representa como una flecha o como una lista de números (sus componentes). |
| Norma | Longitud de un vector, $\|\vec v\|=\sqrt{v_x^2+v_y^2+v_z^2}$. |
| Vector unitario | Vector de longitud 1 en la dirección de otro vector. |
| Producto punto (escalar) | $\vec u\cdot\vec v=\|\vec u\|\|\vec v\|\cos\theta$; mide cuánto de un vector va en la dirección del otro. |
| Ortogonal | Perpendicular; dos vectores son ortogonales si su producto punto es cero. |
| Producto cruz (vectorial) | $\vec u\times\vec v$, un vector perpendicular a ambos, cuya magnitud es el área del paralelogramo que forman. |
| Torque (momento de una fuerza) | $\vec\tau=\vec r\times\vec F$, el efecto de giro que produce una fuerza aplicada a cierta distancia de un eje. |
| Regla de la mano derecha | Convención para la dirección del producto cruz: dedos de $\vec u$ a $\vec v$, pulgar da $\vec u\times\vec v$. |
