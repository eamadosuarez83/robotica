# Bloque 00 — Cómo usar el curso y preparar el entorno

> **Problema que abre el bloque:** empezar un curso sin saber qué se sabe y qué no, ni con qué herramientas se va a trabajar.
>
> **Necesitas antes:** nada. · **Lectura:** Barrientos, cap. 1 (introducción y un poco de historia).

## 1. Cómo está organizado el curso

El curso tiene 25 bloques (00 a 24), agrupados en seis partes:

| Parte | Pregunta que responde | Bloques |
|---|---|---|
| I. Fundamentos | ¿Con qué herramientas matemáticas y físicas se piensa un robot? | 00 – 06 |
| II. Describir el robot | ¿Qué es un brazo y cómo se dice dónde está cada pieza? | 07 – 10 |
| III. Cinemática | ¿Qué relación hay entre los motores y la pinza? | 11 – 13 |
| IV. Dinámica | ¿Qué fuerzas hacen falta para moverlo? | 14 – 16 |
| V. Control | ¿Cómo se logra que haga lo que se le pide? | 17 – 20 |
| VI. Del modelo al brazo real | ¿Cómo se construye, se programa y se mantiene? | 21 – 24 |

Cada bloque sigue la misma columna vertebral descrita en [FILOSOFIA.md](../FILOSOFIA.md): el problema, el mecanismo, la aplicación real, las limitaciones, las fallas típicas, dónde más aparece la idea, ejemplos resueltos y ejercicios en tres series (A conceptual, B a mano, C laboratorio).

**Cómo leerlo junto a Barrientos:** cada bloque indica al inicio qué capítulo del libro leer. El curso no repite el libro; llena los pasos que Barrientos da por sabidos —sobre todo el álgebra y el cálculo de la Parte I— y lleva cada fórmula hasta código que corre y, más adelante, hasta un brazo real. Léase primero el bloque, después el capítulo correspondiente del libro, y al final las lecturas complementarias si algo no quedó claro.

**Símbolo `⚠ romperlo a propósito`:** en cada bloque, un ejercicio guiado rompe algo a propósito (invertir un orden, cambiar un signo, usar grados en vez de radianes) para que el síntoma se reconozca la próxima vez que aparezca solo.

## 2. Prueba diagnóstica

Esta prueba tiene 25 preguntas cortas. No se califica: cada pregunta indica el bloque de la Parte I que la cubre. Si se responde mal o con duda, ese es el bloque por el que conviene empezar con más cuidado; si se responde bien, ese bloque se puede leer en diagonal.

No hace falta desarrollar las respuestas por escrito: basta con saber resolverlas en un par de minutos cada una. Las soluciones están al final de esta sección.

### Trigonometría y geometría del plano (→ Bloque 01)

1. Convertir 40° a radianes y 30° a radianes, y sumarlos.
2. Un punto está en el círculo unitario a un ángulo de 150°. Dar sus coordenadas (x, y) sin calculadora, usando los valores conocidos de seno y coseno.
3. Explicar con palabras qué representa $\sin^2\theta + \cos^2\theta = 1$ (no solo escribir la identidad).
4. Un punto tiene coordenadas $(x,y) = (-3, 4)$. ¿Qué falla si su ángulo se calcula como $\arctan(y/x)$ en vez de $\text{atan2}(y,x)$?
5. Dos eslabones de longitudes $L_1$ y $L_2$ forman un triángulo con el segmento que une la base con la punta. Escribir la ley de cosenos para el lado opuesto al ángulo del codo.

### Vectores (→ Bloque 02)

6. Dados $\vec u = (1,2,3)$ y $\vec v = (0,1,-1)$, calcular $\vec u \cdot \vec v$.
7. ¿Qué significa, geométricamente, que $\vec u \cdot \vec v = 0$?
8. Calcular $\vec u \times \vec v$ para los mismos vectores de la pregunta 6.
9. ¿Qué cambia en $\vec u \times \vec v$ si se invierte el orden a $\vec v \times \vec u$?
10. Dar el vector unitario en la dirección de $(3,4,0)$.

### Matrices como transformaciones (→ Bloque 03)

11. Multiplicar $\begin{pmatrix}1&2\\0&1\end{pmatrix}\begin{pmatrix}2\\1\end{pmatrix}$.
12. ¿Es cierto en general que $AB = BA$ para matrices cuadradas? Dar un ejemplo donde no lo sea.
13. ¿Qué le dice el signo del determinante de una matriz de 2×2 sobre la transformación que representa?
14. ¿Cuándo una matriz cuadrada no tiene inversa? Relacionarlo con su determinante.
15. ¿Qué condición cumple una matriz ortogonal respecto a su transpuesta y su inversa?

### Cálculo para cosas que se mueven (→ Bloque 04)

16. Si $x(t) = 3t^2$, dar $\dot x(t)$ y $\ddot x(t)$, y decir qué representa cada una físicamente.
17. Calcular la derivada parcial de $f(x,y) = x^2 y + \sin(y)$ respecto a $x$ y respecto a $y$.
18. Enunciar la regla de la cadena para $\frac{d}{dt} f(x(t), y(t))$.
19. ¿Qué es una serie de Taylor de primer orden y para qué sirve linealizar una función cerca de un punto?
20. Explicar en una frase la idea del método de Newton-Raphson para resolver $f(x) = 0$.

### Ecuaciones diferenciales y mecánica (→ Bloques 05 y 06)

21. ¿Qué significa "resolver" una ecuación diferencial ordinaria? Dar la solución de $\dot x = -x$ con $x(0) = 1$.
22. Convertir la ecuación de segundo orden $\ddot x + 3\dot x + 2x = 0$ en un sistema de dos ecuaciones de primer orden.
23. ¿Qué torque produce una fuerza $\vec F$ aplicada en un punto a una distancia $\vec r$ del eje de giro? Escribir la fórmula.
24. Enunciar el teorema de ejes paralelos (Steiner) en una frase.
25. Dar la fórmula de la energía cinética de rotación de un cuerpo rígido en función de su momento de inercia $I$ y su velocidad angular $\omega$.

<details>
<summary>Respuestas (desplegar solo después de intentar las 25)</summary>

1. $40° = \tfrac{2\pi}{9}$ rad $\approx 0.698$ rad; $30° = \tfrac{\pi}{6}$ rad $\approx 0.524$ rad; suma $\approx 1.222$ rad.
2. $(\cos 150°, \sin 150°) = (-\tfrac{\sqrt3}{2}, \tfrac12)$.
3. Es el teorema de Pitágoras aplicado al triángulo que forma un punto del círculo unitario con los ejes: la suma de los catetos al cuadrado (proyecciones en x y en y) da siempre 1, la hipotenusa.
4. $\arctan(y/x)$ no sabe en qué cuadrante está el punto porque pierde el signo de cada componente por separado; con $x=-3,y=4$ da un ángulo en el cuadrante equivocado. `atan2(y,x)` sí usa el signo de ambas componentes.
5. $L_{codo\;opuesto}^2 = L_1^2 + L_2^2 - 2L_1L_2\cos(\theta_{codo})$, donde $\theta_{codo}$ es el ángulo entre los dos eslabones.
6. $\vec u \cdot \vec v = 1\cdot0 + 2\cdot1 + 3\cdot(-1) = -1$.
7. Que los vectores son perpendiculares (ortogonales): ninguno tiene componente en la dirección del otro.
8. $\vec u \times \vec v = (2\cdot(-1)-3\cdot1,\; 3\cdot0-1\cdot(-1),\; 1\cdot1-2\cdot0) = (-5, 1, 1)$.
9. Cambia de signo: $\vec v \times \vec u = -(\vec u \times \vec v)$.
10. $\|(3,4,0)\| = 5$, así que el vector unitario es $(0.6, 0.8, 0)$.
11. $\begin{pmatrix}1\cdot2+2\cdot1\\0\cdot2+1\cdot1\end{pmatrix} = \begin{pmatrix}4\\1\end{pmatrix}$.
12. No, en general $AB \neq BA$. Ejemplo: $A=\begin{pmatrix}0&1\\0&0\end{pmatrix}$, $B=\begin{pmatrix}0&0\\1&0\end{pmatrix}$; $AB=\begin{pmatrix}1&0\\0&0\end{pmatrix}$, $BA=\begin{pmatrix}0&0\\0&1\end{pmatrix}$.
13. Positivo: la transformación conserva la orientación (no hay espejo). Negativo: invierte la orientación (refleja el plano).
14. Cuando su determinante es cero: la transformación aplasta el espacio a una dimensión menor y no hay forma de "deshacerla".
15. Su inversa es igual a su transpuesta ($A^{-1} = A^T$); no deforma longitudes ni ángulos, solo rota o refleja.
16. $\dot x(t) = 6t$ es la velocidad; $\ddot x(t) = 6$ es la aceleración (constante).
17. $\partial f/\partial x = 2xy$; $\partial f/\partial y = x^2 + \cos(y)$.
18. $\frac{d}{dt}f(x(t),y(t)) = \frac{\partial f}{\partial x}\dot x + \frac{\partial f}{\partial y}\dot y$.
19. Es la aproximación $f(x) \approx f(a) + f'(a)(x-a)$ cerca de $x=a$: cambia una curva por la recta tangente, útil para resolver ecuaciones difíciles o simplificar un modelo cerca de un punto de trabajo.
20. Parte de una aproximación $x_0$ y la mejora repetidamente siguiendo la tangente de $f$ hasta acercarse a la raíz.
21. Encontrar la función $x(t)$ que cumple la ecuación para todo $t$ y la condición inicial dada. Solución: $x(t) = e^{-t}$.
22. Con $x_1 = x$, $x_2 = \dot x$: $\dot x_1 = x_2$, $\dot x_2 = -3x_2 - 2x_1$.
23. $\vec\tau = \vec r \times \vec F$.
24. El momento de inercia respecto a un eje paralelo al que pasa por el centro de masa es $I = I_{cm} + md^2$, con $d$ la distancia entre los dos ejes.
25. $K_{rot} = \tfrac12 I \omega^2$.

</details>

## 3. Entorno de trabajo

El curso se trabaja en **Linux, con Python 3.10 o superior**, dentro de un entorno virtual para no mezclar las dependencias del curso con las del sistema.

```bash
# Crear el entorno virtual (una sola vez)
python3 -m venv .venv

# Activarlo (cada vez que se trabaje en el curso)
source .venv/bin/activate

# Instalar las dependencias
pip install -r requirements.txt
```

`requirements.txt` está organizado por la parte del curso que necesita cada paquete (ver el archivo en la raíz del repositorio): NumPy, SciPy, SymPy y Matplotlib alcanzan para toda la Parte I. Los paquetes de robótica, control, simulación física y hardware se instalan cuando el bloque correspondiente los pide; no hace falta tenerlos todos desde el día uno, salvo `graphviz` (el programa del sistema, no solo el paquete de Python) si se quieren regenerar los esquemas de `recursos/`.

**Editor:** cualquiera sirve. Se recomienda uno con autocompletado de Python (VS Code, PyCharm, o Neovim con un servidor de lenguaje) porque ayuda a explorar las funciones de NumPy y SymPy sin memorizar la documentación.

## 4. Python mínimo para el curso

No se enseña Python desde cero: se asume que ya se sabe programar. Esta sección repasa solo lo que el curso usa de verdad.

- **Listas y control de flujo**: `for`, `if`, listas y comprensión de listas (`[x**2 for x in range(5)]`).
- **Funciones**: definirlas con valores por defecto, devolver varios valores con tuplas (`return x, y`).
- **Arreglos de NumPy**: un arreglo no es una lista. `np.array([1,2,3])` permite operar elemento a elemento (`a + b`, `2*a`) sin escribir un ciclo. La mayoría de los errores de principiante en el curso vienen de mezclar listas con arreglos, o de confundir la forma (`shape`) de un arreglo: un vector de 3 componentes puede ser `(3,)` o `(3,1)`, y NumPy los trata distinto al multiplicar matrices.
- **Una gráfica en Matplotlib**: lo mínimo para todo el curso.

```python
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 2*np.pi, 200)
plt.plot(t, np.sin(t))
plt.xlabel("t [rad]")
plt.ylabel("sin(t)")
plt.title("Primera gráfica del curso")
plt.grid(True)
plt.show()
```

Si esto no corre, hay que resolverlo antes de seguir: el resto del curso depende de poder ver lo que se calcula.

## 5. La primera figura: un brazo que se mueve

Antes de deducir nada, conviene ver la forma final de lo que se va a construir. `codigo/bloque_00/primera_figura.py` dibuja un brazo plano de dos eslabones ("dos palitos") con dos deslizadores que controlan el ángulo del hombro y del codo. Mover los deslizadores mueve la punta del brazo.

Todavía no se explica la fórmula que ubica la punta (eso es el Bloque 01); por ahora basta con jugar con los deslizadores y notar dos cosas que el curso va a explicar con precisión más adelante:

- Hay ángulos que el brazo no puede alcanzar sin "doblarse al revés" (codo arriba / codo abajo): eso es cinemática inversa (Bloque 12).
- Cerca de ciertas posturas, mover un poco un deslizador mueve mucho la punta, y en otras casi no la mueve: eso son singularidades y manipulabilidad (Bloque 13).

## 6. Laboratorio

1. Crear el entorno virtual e instalar `requirements.txt` (sección 3).
2. Correr `python codigo/bloque_00/verificar_entorno.py` y resolver cualquier `✗` que aparezca antes de seguir.
3. Hacer la prueba diagnóstica de la sección 2 sin ver las respuestas primero.
4. Anotar, en un archivo propio (por ejemplo `mi_ruta_de_repaso.md`, fuera del repositorio o en una rama personal), los bloques de la Parte I donde hubo dudas. Esa es la ruta personal de repaso: no hace falta leer con el mismo detalle un bloque que ya se domina.
5. Correr `python codigo/bloque_00/primera_figura.py` y mover los dos deslizadores.

## Lectura

Barrientos, cap. 1 (introducción y un poco de historia de la robótica).

## Glosario del bloque

| Término | Definición |
|---|---|
| GDL | Grados de libertad: número de movimientos independientes que puede hacer un mecanismo. |
| Entorno virtual (*virtual environment*) | Copia aislada del intérprete de Python y sus paquetes, para que las dependencias de un proyecto no choquen con las de otro. |
| `atan2` | Función que calcula el ángulo de un vector $(x,y)$ usando el signo de ambas componentes, a diferencia de `atan(y/x)`, que solo ve el cociente. |
