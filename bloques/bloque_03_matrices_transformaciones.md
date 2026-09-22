# Bloque 03 — Matrices como transformaciones

> **Problema que abre el bloque:** se sabe multiplicar matrices, pero ¿qué *hace* una matriz a un vector? Sin esa respuesta, toda la Parte II (marcos de referencia, rotaciones, cinemática) es memorizar recetas.
>
> **Necesitas antes:** Bloque 02. · **Lectura:** 3Blue1Brown, *Essence of Linear Algebra*, episodios 3–7 y 13–14; Strang, *Introduction to Linear Algebra*, caps. 2–6.

## Tema 3.1 — La matriz como máquina que transforma vectores

### 1. El problema

$\begin{pmatrix}0&-1\\1&0\end{pmatrix}\begin{pmatrix}3\\0\end{pmatrix}=\begin{pmatrix}0\\3\end{pmatrix}$ se sabe calcular fila por columna. Pero esa cuenta, sola, no dice nada: no explica por qué esta operación —y no otra— es la que describe girar un brazo, cambiar de marco de referencia o deformar una pieza. Falta la pregunta que Barrientos y el resto del curso dan por sabida: ¿qué le *hace* una matriz a un vector?

### 2. El mecanismo

Una matriz de $2\times2$ transforma **todo el plano**: toma cada vector $\vec v$ y lo manda a otro vector $A\vec v$. La forma más rápida de saber qué hace una matriz, sin calcular nada, es mirar **dónde manda a los vectores de la base**:

$$A = \begin{pmatrix}a&b\\c&d\end{pmatrix} \quad\Longrightarrow\quad A\begin{pmatrix}1\\0\end{pmatrix}=\begin{pmatrix}a\\c\end{pmatrix},\qquad A\begin{pmatrix}0\\1\end{pmatrix}=\begin{pmatrix}b\\d\end{pmatrix}$$

Es decir: **la primera columna de $A$ es hacia dónde termina el eje x; la segunda columna es hacia dónde termina el eje y**. Cualquier otro vector es una combinación de los de la base ($\vec v = v_x\hat x+v_y\hat y$), así que su imagen es la misma combinación de las columnas transformadas: $A\vec v = v_x(\text{col}_1) + v_y(\text{col}_2)$. Por eso la multiplicación matriz-vector, fila por columna, da exactamente eso.

Esta lectura convierte cada matriz del curso en un dibujo: rotar 90° manda $\hat x\to(0,1)$ y $\hat y\to(-1,0)$, de donde sale directo $\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ sin memorizarla. Escalar el eje x por 2 es $\begin{pmatrix}2&0\\0&1\end{pmatrix}$. Un "corte" (*shear*) que inclina el eje y sin tocar el x es $\begin{pmatrix}1&k\\0&1\end{pmatrix}$.

En 3D es igual: una matriz de $3\times3$ tiene tres columnas, una por cada eje transformado.

### 3. En la vida real

```python
import numpy as np
A = np.array([[0, -1], [1, 0]])   # rotación de 90°
v = np.array([3, 0])
A @ v          # array([0, 3])  -- usar @, no * (que multiplica elemento a elemento)
```

### 4. Limitaciones

Esta lectura vale para **transformaciones lineales**: rectas por el origen se van a rectas por el origen, y una cuadrícula uniforme se va a otra cuadrícula uniforme (aunque deformada). No describe traslaciones (mover el origen), que necesitan coordenadas homogéneas (Bloque 10).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El resultado de `A * v` en NumPy no es el esperado | Se usó `*` (elemento a elemento) en vez de `@` o `np.dot` (multiplicación matricial) | Comparar `A * v` contra `A @ v` con una matriz no diagonal | Usar `@` para multiplicación matriz-vector o matriz-matriz |
| Se arma la matriz con las filas en vez de las columnas correctas | Se piensa "fila = a dónde va el eje", cuando es la columna | Evaluar `A @ [1,0]` y `A @ [0,1]` por separado y comparar con lo esperado | Escribir la matriz columna por columna: cada columna es la imagen de un eje |

### 6. Dónde más aparece la idea

Toda animación 2D/3D (una matriz de "modelo" ubica cada objeto en la escena), compresión de imágenes (transformaciones que aplastan direcciones poco importantes), redes neuronales (cada capa lineal es una matriz que transforma un vector de entrada).

### 7. Ejemplos resueltos

**Ejemplo:** ¿a dónde manda $A=\begin{pmatrix}2&1\\0&1\end{pmatrix}$ al vector $(1,1)$? Columnas: $\hat x\to(2,0)$, $\hat y\to(1,1)$. Entonces $(1,1) = 1\hat x+1\hat y \to 1(2,0)+1(1,1) = (3,1)$. Verificación por la cuenta fila-columna: $\begin{pmatrix}2\cdot1+1\cdot1\\0\cdot1+1\cdot1\end{pmatrix}=\begin{pmatrix}3\\1\end{pmatrix}$. Coincide.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Sin calcular, describir en palabras qué le hace al plano la matriz $\begin{pmatrix}1&0\\0&-1\end{pmatrix}$, leyendo sus columnas.

**Serie B — Cálculo a mano**
- B1. Escribir la matriz de $2\times2$ que refleja el plano respecto al eje x, razonando dónde termina cada eje de la base.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_03/animador_transformaciones.py`, escribir la matriz de B1 en los deslizadores y verificar que la cuadrícula se refleja como se predijo.

---

## Tema 3.2 — Composición de transformaciones: por qué el orden importa

### 1. El problema

Rotar un brazo y después estirarlo no es lo mismo que estirarlo y después rotarlo (dibujar un rectángulo y probarlo convence enseguida). Sin embargo, en las fórmulas del curso las transformaciones se escriben una junto a otra, como $R_2R_1\vec v$. Hay que saber qué significa esa yuxtaposición y en qué orden se aplica.

### 2. El mecanismo

Aplicar primero $A$ y después $B$ a un vector $\vec v$ es $B(A\vec v)$. Como la multiplicación de matrices se construye exactamente para que esto sea asociativo, $B(A\vec v) = (BA)\vec v$: **la matriz combinada es $BA$, con la que se aplica primero a la derecha**. Esta es la razón por la que, en el curso (y en Barrientos), las transformaciones que se leen de izquierda a derecha en el papel se *aplican* de derecha a izquierda sobre el vector.

Multiplicar dos matrices, $C=BA$, es entonces "transformar las columnas de $A$ con $B$": la columna $i$ de $C$ es $B$ aplicada a la columna $i$ de $A$. Esto explica por qué, en general, $AB\neq BA$: son dos composiciones distintas, una transforma los ejes ya transformados por la otra, y el resultado depende de cuál se hizo primero.

Geométricamente: girar 90° y después reflejar respecto al eje x no da el mismo resultado que reflejar y después girar. Una forma sin simetría (como una "L" o una casita, no un cuadrado) hace evidente la diferencia; una figura simétrica puede ocultarla y hacer creer, por error, que el orden no importa.

### 3. En la vida real

```python
A = np.array([[0, -1], [1, 0]])   # rotación 90°
B = np.array([[1, 0], [0, -1]])   # reflexión en el eje x
(B @ A)   # primero rota, luego refleja
(A @ B)   # primero refleja, luego rota -- matriz distinta
```

### 4. Limitaciones

La asociatividad ($(BA)\vec v = B(A\vec v)$) siempre vale; lo que **no** vale en general es la conmutatividad ($AB=BA$). Hay excepciones (por ejemplo, dos rotaciones alrededor del mismo eje sí conmutan), pero no se pueden asumir sin verificar.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una cadena de transformaciones da un resultado "reflejado" o girado al revés de lo esperado | Se multiplicaron las matrices en el orden contrario al que se aplican | Probar la cadena sobre una figura asimétrica y comparar paso a paso, transformación por transformación, contra el resultado de la matriz combinada | Escribir explícitamente "primero $A$, luego $B$" y armar $BA$, no $AB$ |

### 6. Dónde más aparece la idea

Composición de rotaciones con ejes fijos y ejes móviles (Bloque 08), encadenar transformaciones homogéneas base→cámara→objeto (Bloque 10), el orden de las capas en una red neuronal.

### 7. Ejemplos resueltos

**Ejemplo:** con $A$ (rotación 90°) y $B$ (reflexión en x) de la sección 3, aplicar ambas a $(1,0)$ en los dos órdenes.

Primero $A$, luego $B$: $A(1,0)=(0,1)$; $B(0,1)=(0,-1)$.
Primero $B$, luego $A$: $B(1,0)=(1,0)$; $A(1,0)=(0,1)$.

Resultados distintos: $(0,-1)$ contra $(0,1)$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué una figura simétrica (como un cuadrado centrado en el origen) puede ocultar que el orden de dos transformaciones importa, y proponer una figura que sí lo revele.

**Serie B — Cálculo a mano**
- B1. Con $A=\begin{pmatrix}2&0\\0&1\end{pmatrix}$ (escala x por 2) y $B=\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ (rotación 90°), calcular $AB$ y $BA$ y mostrar que son distintas.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_03/romper_orden_matrices.py`, que aplica dos transformaciones a la imagen de una casita en los dos órdenes posibles y grafica ambos resultados lado a lado.

---

## Tema 3.3 — Transpuesta e inversa

### 1. El problema

Si una matriz lleva un vector de un marco a otro, hace falta poder deshacer ese cambio: volver del segundo marco al primero. Y para resolver sistemas de ecuaciones o despejar incógnitas en las fórmulas de cinemática, hace falta saber cuándo esa operación inversa existe.

### 2. El mecanismo

**Transpuesta** ($A^T$): se intercambian filas por columnas, $\left(A^T\right)_{ij}=A_{ji}$. No es, en general, la inversa; es una operación distinta que aparece por su cuenta (en el producto punto escrito como $\vec u^T\vec v$, y en las matrices ortogonales del Tema 3.5).

**Inversa** ($A^{-1}$): la matriz tal que $A^{-1}A=AA^{-1}=I$ (la identidad, que no transforma nada). Si $A$ manda $\vec v \to A\vec v$, entonces $A^{-1}$ deshace exactamente ese paso: $A^{-1}(A\vec v)=\vec v$.

No toda matriz tiene inversa. Una matriz cuadrada tiene inversa **si y solo si su determinante no es cero** (Tema 3.4). Geométricamente: si la transformación aplasta el plano a una línea (o el espacio a un plano), la información sobre la dirección perpendicular al aplastamiento se pierde para siempre, y no hay forma de reconstruirla: no existe una transformación que "desaplaste".

Para $2\times2$, hay una fórmula directa:

$$A=\begin{pmatrix}a&b\\c&d\end{pmatrix} \quad\Longrightarrow\quad A^{-1}=\frac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$$

donde $ad-bc$ es precisamente el determinante: si es cero, la fórmula divide entre cero y la inversa no existe.

### 3. En la vida real

```python
np.linalg.inv(A)     # inversa
A.T                   # transpuesta
np.linalg.inv(A) @ A  # debe dar (aprox.) la identidad
```

### 4. Limitaciones

Calcular la inversa explícita es costoso e innecesario cuando solo se necesita resolver $A\vec x=\vec b$ para un $\vec b$ dado: para eso conviene `np.linalg.solve(A, b)`, que es más rápido y más estable numéricamente que calcular $A^{-1}$ y multiplicar.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| `np.linalg.inv` lanza `LinAlgError: Singular matrix` | El determinante de $A$ es cero (o casi cero) | Calcular `np.linalg.det(A)` | Revisar si la transformación realmente debería aplastar el espacio en ese caso; si no, hay un error antes en cómo se armó $A$ |
| Se confunde $A^{-1}$ con $A^T$ | Se asume sin verificar que son lo mismo (solo es cierto para matrices ortogonales, Tema 3.5) | Calcular ambas y compararlas para la $A$ en cuestión | Usar $A^{-1}$ salvo que se haya confirmado que $A$ es ortogonal |

### 6. Dónde más aparece la idea

Deshacer una transformación homogénea sin invertir la matriz de $4\times4$ completa (Bloque 10), resolver sistemas de ecuaciones en general.

### 7. Ejemplos resueltos

**Ejemplo:** $A=\begin{pmatrix}2&0\\0&1\end{pmatrix}$ (escala x por 2). $\det A = 2\cdot1-0\cdot0=2\neq0$, sí tiene inversa: $A^{-1}=\begin{pmatrix}0.5&0\\0&1\end{pmatrix}$, que "deshace" el escalamiento comprimiendo x por 0.5, como se espera.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, en términos de "aplastar el espacio", por qué una matriz con determinante cero no puede tener inversa.

**Serie B — Cálculo a mano**
- B1. Calcular $A^{-1}$ para $A=\begin{pmatrix}1&2\\3&4\end{pmatrix}$ y verificar que $A^{-1}A=I$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `np.linalg.inv` y con `np.linalg.solve(A, b)` para un `b` cualquiera, comparando contra `np.linalg.inv(A) @ b`.

---

## Tema 3.4 — El determinante: cuánto crece o encoge el espacio

### 1. El problema

Al aplicar una transformación, algunas encogen el espacio, otras lo estiran, y algunas lo "voltean" como un espejo. Hace falta un solo número que resuma ese efecto, porque en el curso reaparece una y otra vez: como condición de existencia de la inversa (Tema 3.3), y más adelante como la señal de que un brazo está en una postura imposible de mover en cierta dirección (singularidad, Bloque 13).

### 2. El mecanismo

Para $A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$, el **determinante** es $\det A = ad-bc$. Su significado: es el **factor por el que cambia el área** de cualquier figura al aplicarle la transformación. El cuadrado unitario (lado 1, área 1) formado por $\hat x$ y $\hat y$ se transforma en el paralelogramo formado por las columnas de $A$; el área de ese paralelogramo es $|\det A|$.

- $|\det A| > 1$: la transformación agranda áreas.
- $0<|\det A|<1$: las encoge.
- $\det A = 0$: aplasta el plano a una línea (o un punto): las dos columnas quedan alineadas (paralelas), y el "paralelogramo" que forman tiene área cero. Esta es la condición de no invertibilidad del Tema 3.3, y la razón física de una singularidad cinemática (Bloque 13): en esa postura, cierta dirección de movimiento de la pinza requeriría velocidad infinita en algún motor.
- **Signo negativo**: la transformación invierte la orientación del plano (lo que era "antihorario" en la figura original queda "horario" en la transformada) — es un espejo. El signo positivo conserva la orientación.

En 3D, el determinante de una matriz de $3\times3$ mide el cambio de **volumen** del mismo modo, con las tres columnas formando un paralelepípedo.

### 3. En la vida real

```python
np.linalg.det(A)
```

### 4. Limitaciones

El determinante resume el cambio de área/volumen *promedio*, no cómo se distribuye la deformación en cada dirección; para eso hacen falta los valores propios (Tema 3.7) o, más adelante, la descomposición en valores singulares.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una figura transformada aparece "en espejo" sin que se esperara | El determinante de la matriz usada es negativo | Calcular `np.linalg.det(A)` y ver su signo | Revisar si de verdad se quería una reflexión; si no, hay un signo mal puesto en alguna columna |
| Un cálculo posterior (inversa, cinemática inversa) falla cerca de cierta postura | El determinante se acerca a cero ahí: el sistema está cerca de una singularidad | Graficar `det(A)` (o, en el Bloque 13, el de la Jacobiana) en función de la postura | Evitar esa zona, o usar métodos numéricos robustos a determinante pequeño (mínimos cuadrados amortiguados, Bloque 12) |

### 6. Dónde más aparece la idea

Singularidades de la Jacobiana (Bloque 13), el jacobiano en el cambio de variables de una integral múltiple, compresión/expansión de volumen en mecánica de fluidos.

### 7. Ejemplos resueltos

**Ejemplo:** $A=\begin{pmatrix}2&1\\0&1\end{pmatrix}$: $\det A = 2\cdot1-1\cdot0=2$. El cuadrado unitario se transforma en un paralelogramo de área 2: la transformación duplica áreas y no refleja (signo positivo).

**Ejemplo (aplastamiento):** $A=\begin{pmatrix}2&4\\1&2\end{pmatrix}$: $\det A = 2\cdot2-4\cdot1=0$. Las columnas $(2,1)$ y $(4,2)$ son paralelas (una es el doble de la otra): todo el plano se aplasta sobre esa única dirección.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué dos columnas paralelas en una matriz implican determinante cero, pensando en el área del paralelogramo que forman.

**Serie B — Cálculo a mano**
- B1. Calcular el determinante de $\begin{pmatrix}3&0\\0&-2\end{pmatrix}$ y describir en palabras el efecto geométrico completo de esta matriz (tamaño y orientación).

**Serie C — Laboratorio**
- C1. En `codigo/bloque_03/animador_transformaciones.py`, llevar los deslizadores hasta que las dos columnas queden paralelas y observar cómo la cuadrícula se aplasta a una línea.

---

## Tema 3.5 — Matrices ortogonales: las que no deforman

### 1. El problema

Rotar un brazo no debería estirarlo ni encogerlo: una rotación mueve las piezas sin cambiar su forma ni su tamaño. Hace falta identificar qué matrices tienen esa propiedad, porque son exactamente las que van a describir orientaciones en el Bloque 08.

### 2. El mecanismo

Una matriz $A$ es **ortogonal** cuando sus columnas son vectores unitarios y perpendiculares entre sí (una base ortonormal). Eso tiene tres consecuencias que se usan sin parar en el resto del curso:

1. **No deforma**: conserva longitudes ($\|A\vec v\|=\|\vec v\|$ para todo $\vec v$) y ángulos entre vectores. Un círculo se transforma en un círculo del mismo radio, nunca en una elipse.
2. **Su inversa es su transpuesta**: $A^{-1}=A^T$. Esto es enorme en la práctica: invertir una rotación (Bloque 08) no requiere el cálculo general de una inversa (Tema 3.3, costoso e inestable), solo transponer la matriz, una operación trivial y exacta.
3. **Su determinante es $+1$ o $-1$**: $+1$ si además conserva la orientación (es una rotación pura), $-1$ si incluye una reflexión.

Las matrices de rotación del Bloque 08 son, exactamente, las matrices ortogonales con determinante $+1$.

### 3. En la vida real

```python
# comprobar que A es ortogonal:
np.allclose(A.T @ A, np.eye(A.shape[0]))
```

### 4. Limitaciones

La propiedad es exacta solo en aritmética exacta; en código, tras muchas operaciones en cadena (por ejemplo, integrar una rotación paso a paso), los errores de redondeo pueden hacer que una matriz que "debería" ser ortogonal deje de serlo poco a poco (deriva numérica) y hay que reortonormalizarla.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Al invertir una rotación con $A^{-1}=A^T$ el resultado es incorrecto | La matriz usada no era realmente ortogonal (por ejemplo, incluía un escalamiento) | Comprobar `A.T @ A ≈ I` | Usar $A^{-1}=A^T$ solo tras confirmar la ortogonalidad; si no, usar `np.linalg.inv` |
| Una rotación acumulada en una simulación larga empieza a "estirar" el objeto | Deriva numérica: la matriz dejó de ser exactamente ortogonal tras muchas multiplicaciones | Medir `np.linalg.det(A)` y `A.T @ A - I` a lo largo del tiempo | Reortonormalizar periódicamente (tema que se retoma con cuaterniones en el Bloque 09) |

### 6. Dónde más aparece la idea

Matrices de rotación (Bloque 08), bases ortonormales en cualquier marco de referencia, matrices de cambio de base entre sistemas de coordenadas.

### 7. Ejemplos resueltos

**Ejemplo:** $A=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}$ (rotación por $\theta$). Sus columnas tienen norma $\sqrt{\cos^2\theta+\sin^2\theta}=1$ y producto punto $-\cos\theta\sin\theta+\sin\theta\cos\theta=0$: son unitarias y perpendiculares, así que $A$ es ortogonal para cualquier $\theta$, y $A^{-1}=A^T=\begin{pmatrix}\cos\theta&\sin\theta\\-\sin\theta&\cos\theta\end{pmatrix}$, que es la rotación por $-\theta$ — exactamente lo que se espera para deshacer un giro.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué una matriz de escalamiento (distinto de 1) no puede ser ortogonal.

**Serie B — Cálculo a mano**
- B1. Verificar a mano que $A=\begin{pmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{pmatrix}$ tiene determinante 1 para cualquier $\theta$.

**Serie C — Laboratorio**
- C1. Generar una matriz de rotación con `theta=37°`, comprobar en código que `A.T @ A` da la identidad y que `np.linalg.inv(A)` coincide con `A.T`.

---

## Tema 3.6 — Sistemas de ecuaciones lineales, rango y mínimos cuadrados

### 1. El problema

Varias veces el curso necesita resolver un sistema $A\vec x=\vec b$: por ejemplo, plantear ecuaciones a partir de mediciones y despejar una incógnita. Pero no siempre hay una solución única: a veces hay muchas soluciones, a veces ninguna exacta (cuando las mediciones tienen ruido), y hace falta saber distinguir estos casos.

### 2. El mecanismo

Un sistema $A\vec x=\vec b$ se puede leer con la misma idea del Tema 3.1: se busca un vector $\vec x$ que, transformado por $A$, dé $\vec b$.

- Si $A$ es cuadrada e invertible ($\det A\neq0$), hay **una única solución**: $\vec x=A^{-1}\vec b$ (en la práctica, `np.linalg.solve`).
- El **rango** de $A$ es la dimensión del espacio que realmente alcanzan las columnas de $A$ (cuántas direcciones distintas genera la transformación). Si el rango es menor que el número de columnas, hay direcciones que $A$ no puede alcanzar de ninguna forma, o varias combinaciones de $\vec x$ que dan el mismo resultado.
- Cuando hay **más ecuaciones que incógnitas** (sistema sobredeterminado, típico cuando se combinan varias mediciones con ruido), en general no existe un $\vec x$ que cumpla todas las ecuaciones exactamente. La **solución por mínimos cuadrados** es el $\vec x$ que minimiza el error total $\|A\vec x-\vec b\|^2$: no resuelve el sistema, lo acerca lo más posible.

### 3. En la vida real

```python
x = np.linalg.solve(A, b)          # A cuadrada e invertible
np.linalg.matrix_rank(A)           # rango
x, *_ = np.linalg.lstsq(A, b, rcond=None)  # mínimos cuadrados
```

### 4. Limitaciones

`np.linalg.solve` falla (o da un resultado numéricamente inestable) si $A$ está cerca de ser singular; en ese caso conviene revisar el rango o usar `lstsq`, que es más robusto.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| `np.linalg.solve` da un resultado con números enormes o inestables | $A$ tiene rango incompleto o está cerca de serlo (columnas casi paralelas) | `np.linalg.matrix_rank(A)` y `np.linalg.cond(A)` (número de condición, alto = mal condicionado) | Revisar si las ecuaciones son realmente independientes; considerar `lstsq` |

### 6. Dónde más aparece la idea

Calibración de sensores a partir de varias mediciones (Bloque 22), ajuste de una recta o curva a datos experimentales, la pseudoinversa de la Jacobiana en cinemática inversa (Bloque 12).

### 7. Ejemplos resueltos

**Ejemplo:** el sistema $\begin{cases}x+y=3\\2x+2y=6\end{cases}$ tiene infinitas soluciones (la segunda ecuación es la primera multiplicada por 2): la matriz $A=\begin{pmatrix}1&1\\2&2\end{pmatrix}$ tiene rango 1, no 2.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, en palabras, qué significa que una matriz tenga "rango incompleto" en términos de las direcciones que sus columnas pueden alcanzar.

**Serie B — Cálculo a mano**
- B1. Resolver a mano $\begin{pmatrix}2&0\\0&3\end{pmatrix}\vec x=\begin{pmatrix}4\\9\end{pmatrix}$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `np.linalg.solve`, y comparar con `np.linalg.lstsq` sobre el mismo sistema con un `b` extra (tercera fila inventada, inconsistente) para ver la solución de mínimos cuadrados.

---

## Tema 3.7 — Valores y vectores propios

### 1. El problema

Algunas direcciones son especiales para una transformación: la matriz las estira o encoge, pero no las gira ni las saca de su línea original. Encontrar esas direcciones va a ser la clave, más adelante, para entender los ejes principales de inercia de un eslabón (Bloque 06) y la estabilidad de un sistema controlado.

### 2. El mecanismo

Un **vector propio** de $A$ es un vector $\vec v\neq\vec 0$ tal que $A\vec v$ es un múltiplo del propio $\vec v$:

$$A\vec v = \lambda\vec v$$

El número $\lambda$ es el **valor propio** asociado: cuánto se estira (o encoge, si $|\lambda|<1$, o invierte, si $\lambda<0$) esa dirección particular. La mayoría de los vectores cambian de dirección al aplicarles $A$; los vectores propios son las excepciones: su dirección queda fija.

Para encontrarlos, se reescribe la ecuación como $(A-\lambda I)\vec v=\vec 0$. Esto tiene una solución $\vec v\neq\vec 0$ solo si $A-\lambda I$ no es invertible, es decir, si $\det(A-\lambda I)=0$ (Temas 3.3 y 3.4). Esta ecuación en $\lambda$ (el **polinomio característico**) da los valores propios; sustituyendo cada uno de vuelta se obtiene su vector propio.

### 3. En la vida real

```python
valores, vectores = np.linalg.eig(A)
# vectores[:, i] es el vector propio asociado a valores[i]
```

### 4. Limitaciones

En este bloque solo se usan matrices simétricas reales (como el tensor de inercia del Bloque 06), donde los valores propios son siempre reales y los vectores propios siempre perpendiculares entre sí. En general, una matriz puede tener valores propios complejos, que aparecerán al estudiar estabilidad de sistemas dinámicos (Parte V).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| `np.linalg.eig` devuelve valores propios complejos para una matriz que se esperaba real y simétrica | La matriz no es realmente simétrica (posible error de tipeo al construirla) | Comprobar `np.allclose(A, A.T)` | Corregir cómo se arma la matriz; para matrices simétricas, `np.linalg.eigh` es además más preciso |

### 6. Dónde más aparece la idea

Ejes principales de inercia (Bloque 06), análisis de estabilidad por la ubicación de los polos (Bloque 17), compresión de datos (análisis de componentes principales), vibraciones de un sistema mecánico (modos propios).

### 7. Ejemplos resueltos

**Ejemplo:** $A=\begin{pmatrix}2&0\\0&3\end{pmatrix}$ (ya diagonal). Sus columnas son múltiplos de $\hat x$ y $\hat y$, así que $\hat x$ y $\hat y$ son directamente los vectores propios, con valores propios 2 y 3: la matriz estira el eje x por 2 y el eje y por 3, sin mezclarlos ni rotarlos.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, para una matriz diagonal, los vectores de la base canónica son siempre vectores propios.

**Serie B — Cálculo a mano**
- B1. Encontrar los valores propios de $\begin{pmatrix}2&1\\1&2\end{pmatrix}$ resolviendo $\det(A-\lambda I)=0$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `np.linalg.eig` y graficar, sobre la cuadrícula deformada por `animador_transformaciones.py`, los dos vectores propios encontrados: deben quedar sobre la misma línea antes y después de la transformación.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/graficar.py`: `dibujar_cuadricula`, `dibujar_vector`, `dibujar_marco2d` — funciones para dibujar una cuadrícula (deformada opcionalmente por una matriz), vectores y marcos de referencia 2D, reutilizadas en los laboratorios de este bloque y en los siguientes.

## Glosario del bloque

| Término | Definición |
|---|---|
| Transformación lineal | Función que manda vectores a vectores conservando sumas y escalamientos; toda matriz cuadrada representa una. |
| Composición de transformaciones | Aplicar una transformación tras otra; se representa multiplicando sus matrices, en el orden inverso al que se aplican sobre el vector. |
| Transpuesta ($A^T$) | Matriz con filas y columnas intercambiadas. |
| Inversa ($A^{-1}$) | Matriz que deshace la transformación de $A$: $A^{-1}A=I$. Existe solo si $\det A\neq0$. |
| Determinante | Factor por el que una transformación cambia áreas (2D) o volúmenes (3D); su signo indica si invierte la orientación. |
| Matriz ortogonal | Matriz cuyas columnas son unitarias y perpendiculares entre sí; no deforma longitudes ni ángulos, y su inversa es su transpuesta. |
| Rango | Dimensión del espacio que alcanzan las columnas de una matriz. |
| Mínimos cuadrados | Método para encontrar la solución que minimiza el error total en un sistema sin solución exacta. |
| Valor y vector propio | Dirección ($\vec v$) que una matriz solo estira, y el factor ($\lambda$) por el que la estira: $A\vec v=\lambda\vec v$. |
