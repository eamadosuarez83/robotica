# Bloque 04 — Cálculo para cosas que se mueven

> **Problema que abre el bloque:** si cada motor gira a cierta velocidad, ¿a qué velocidad se mueve la punta? La respuesta requiere derivar una función de varias variables que dependen del tiempo.
>
> **Necesitas antes:** Bloques 01 y 03. · **Lectura:** Stewart, *Cálculo*, capítulos de derivadas parciales y regla de la cadena.

## Tema 4.1 — Derivada como velocidad

### 1. El problema

La posición de la punta del brazo, $x(t)$, cambia con el tiempo mientras los motores giran. "¿Qué tan rápido cambia?" es una pregunta distinta de "¿dónde está?", y hace falta una herramienta para responderla en cualquier instante, no solo en promedio entre dos instantes.

### 2. El mecanismo

La velocidad promedio entre dos instantes $t$ y $t+h$ es $\dfrac{x(t+h)-x(t)}{h}$. La **derivada** es lo que queda cuando ese intervalo se hace arbitrariamente pequeño:

$$\dot x(t) = \frac{dx}{dt} = \lim_{h\to0}\frac{x(t+h)-x(t)}{h}$$

Es la velocidad **instantánea**: la pendiente de la recta tangente a $x(t)$ en ese instante. Derivar de nuevo da la **aceleración**, $\ddot x(t)=\dfrac{d^2x}{dt^2}$: qué tan rápido cambia la velocidad. El curso usa el punto sobre la variable ($\dot x$, $\ddot x$) como abreviatura de derivada respecto al tiempo, la notación estándar en mecánica (y en Barrientos).

Reglas básicas que el curso usa constantemente: derivada de una potencia ($\frac{d}{dt}t^n=nt^{n-1}$), de una suma (se deriva término a término), de un producto (regla del producto) y de seno/coseno ($\frac{d}{dt}\sin t=\cos t$, $\frac{d}{dt}\cos t=-\sin t$ — válido porque $t$ está en radianes, Bloque 01).

### 3. En la vida real

Derivada simbólica con SymPy (para *ver* la fórmula) y numérica con diferencias finitas (Tema 4.2 y Bloque 04, laboratorio):

```python
import sympy as sp
t = sp.symbols('t')
x = 3*t**2
sp.diff(x, t)        # 6*t
sp.diff(x, t, 2)      # 6  (segunda derivada)
```

### 4. Limitaciones

La derivada asume que $x(t)$ es una función suave (sin saltos ni esquinas) en el instante considerado; una colisión o un tope mecánico rompe esa suposición y la velocidad puede cambiar bruscamente (discontinuidad en $\dot x$).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una "velocidad" calculada no cambia de signo cuando debería (el objeto sigue acelerando cuando ya debería estar frenando) | Se confundió velocidad con aceleración, o se usó $x(t)$ donde se necesitaba $\dot x(t)$ | Graficar $x(t)$, $\dot x(t)$ y $\ddot x(t)$ juntas y comparar sus ceros y cambios de signo | Revisar cuál cantidad pide cada fórmula antes de sustituir |

### 6. Dónde más aparece la idea

Velocidad y aceleración de cualquier móvil, corriente eléctrica como derivada de la carga, tasa de cambio en cualquier ciencia (población, temperatura, precio).

### 7. Ejemplos resueltos

**Ejemplo:** $x(t)=3t^2$. $\dot x(t)=6t$ (velocidad, crece con el tiempo), $\ddot x(t)=6$ (aceleración constante).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar con una situación del brazo qué significaría que $\dot x(t)=0$ en un instante, pero $\ddot x(t)\neq0$.

**Serie B — Cálculo a mano**
- B1. Derivar $x(t) = 2\sin(t) + t^3$ dos veces.

**Serie C — Laboratorio**
- C1. Verificar B1 con `sympy.diff` y graficar $x(t)$, $\dot x(t)$, $\ddot x(t)$ con Matplotlib para $t\in[0,5]$.

---

## Tema 4.2 — Derivada de un vector y de una matriz

### 1. El problema

La posición de la punta del brazo no es un número, es un vector $\vec p(t)=(x(t),y(t))$. ¿Qué significa "derivar" algo con varias componentes a la vez?

### 2. El mecanismo

Se deriva **componente a componente**: si $\vec p(t) = (x(t), y(t), z(t))$, entonces

$$\dot{\vec p}(t) = (\dot x(t), \dot y(t), \dot z(t))$$

Ese vector $\dot{\vec p}$ es la **velocidad** de la punta: su dirección es hacia dónde se mueve en ese instante, su magnitud es la rapidez ($\|\dot{\vec p}\|$). Lo mismo aplica a una matriz que depende del tiempo, $A(t)$: su derivada $\dot A(t)$ se obtiene derivando cada elemento por separado. Esto es exactamente lo que se necesita, más adelante, para derivar una matriz de rotación que cambia con el tiempo (velocidad angular, Bloque 13).

La regla del producto se extiende igual: $\dfrac{d}{dt}\big(A(t)\vec v(t)\big) = \dot A(t)\vec v(t) + A(t)\dot{\vec v}(t)$, cuidando **no cambiar el orden** de los factores (una matriz no conmuta con otra en general, Bloque 03).

### 3. En la vida real

```python
import sympy as sp
t = sp.symbols('t')
p = sp.Matrix([sp.cos(t), sp.sin(t)])
sp.diff(p, t)   # Matrix([[-sin(t)], [cos(t)]])
```

### 4. Limitaciones

Ninguna nueva: es la misma derivada del Tema 4.1, aplicada elemento a elemento.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La derivada de un producto de matrices que dependen de $t$ da un resultado que no coincide con SymPy | Se aplicó la regla del producto cambiando el orden de los factores ($\vec v\dot A$ en vez de $\dot A\vec v$) | Comparar con `sp.diff(A(t)*v(t), t)` calculado directamente | Mantener siempre el orden original: $\dot A\vec v + A\dot{\vec v}$ |

### 6. Dónde más aparece la idea

Velocidad y aceleración en 3D (cualquier trayectoria), derivada de una matriz de rotación (Bloque 13), ecuaciones de movimiento en forma matricial (Bloque 14).

### 7. Ejemplos resueltos

**Ejemplo:** $\vec p(t) = (\cos t, \sin t)$ (un punto que gira sobre el círculo unitario). $\dot{\vec p}(t) = (-\sin t, \cos t)$: su magnitud es $\sqrt{\sin^2t+\cos^2t}=1$ (rapidez constante) y es perpendicular a $\vec p(t)$ en todo instante (el producto punto $\vec p\cdot\dot{\vec p}=-\cos t\sin t+\sin t\cos t=0$, Bloque 02) — la velocidad de algo que gira siempre es tangente a su trayectoria.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, para un punto que se mueve en círculo a rapidez constante, la velocidad siempre es perpendicular a la posición.

**Serie B — Cálculo a mano**
- B1. Derivar $\vec p(t) = (t^2, 3t)$ y evaluar la velocidad en $t=2$.

**Serie C — Laboratorio**
- C1. Verificar B1 con SymPy y graficar la trayectoria junto con el vector velocidad en $t=2$ como una flecha (usar `robotica.graficar.dibujar_vector`).

---

## Tema 4.3 — Derivadas parciales

### 1. El problema

La posición de la punta del brazo 2R depende de **dos** ángulos, $x(\theta_1,\theta_2)$. Si solo se mueve el motor del hombro y el del codo se mantiene fijo, ¿cuánto se mueve la punta? Hace falta derivar respecto a una sola variable, tratando las demás como constantes.

### 2. El mecanismo

La **derivada parcial** de $f(\theta_1,\theta_2)$ respecto a $\theta_1$, escrita $\dfrac{\partial f}{\partial\theta_1}$, se calcula derivando como siempre respecto a $\theta_1$ mientras $\theta_2$ se trata como un número fijo. Es la respuesta exacta a "cuánto cambia $f$ si solo se mueve $\theta_1$, un poquito".

Para la cinemática directa del brazo 2R (Bloque 01, Tema 1.4):

$$x(\theta_1,\theta_2) = L_1\cos\theta_1 + L_2\cos(\theta_1+\theta_2)$$

$$\frac{\partial x}{\partial\theta_1} = -L_1\sin\theta_1 - L_2\sin(\theta_1+\theta_2), \qquad \frac{\partial x}{\partial\theta_2} = -L_2\sin(\theta_1+\theta_2)$$

(la segunda es más simple porque $\theta_1$, al ser constante en esta derivada, no aporta el primer término). Nótese que $\theta_2$ solo aparece en el segundo sumando de $x$, porque solo el segundo eslabón "siente" directamente el ángulo del codo.

### 3. En la vida real

```python
import sympy as sp
t1, t2, L1, L2 = sp.symbols('theta1 theta2 L1 L2')
x = L1*sp.cos(t1) + L2*sp.cos(t1+t2)
sp.diff(x, t1)   # derivada parcial respecto a theta1
sp.diff(x, t2)   # derivada parcial respecto a theta2
```

### 4. Limitaciones

Ninguna nueva conceptualmente; la dificultad práctica crece con el número de variables (en un brazo de 6 GDL hay 6 derivadas parciales por cada coordenada de la punta), razón por la que el Bloque 13 organiza todas estas derivadas en una sola matriz: la Jacobiana.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| $\partial x/\partial\theta_2$ da un resultado con términos de más | Se derivó como si $\theta_1$ también dependiera de $\theta_2$, sin tratarlo como constante | Recalcular fijando $\theta_1$ en un valor numérico y derivando solo en $\theta_2$ | Al derivar parcialmente, congelar explícitamente las demás variables |

### 6. Dónde más aparece la idea

La Jacobiana (Bloque 13) es, literalmente, la matriz de todas las derivadas parciales de la cinemática directa; en economía, "cuánto cambia el ingreso si solo sube el precio, con la cantidad fija"; en termodinámica, calor a volumen constante contra a presión constante.

### 7. Ejemplos resueltos

**Ejemplo:** para $f(\theta_1,\theta_2) = L_1\sin\theta_1 + L_2\sin(\theta_1+\theta_2)$ (la coordenada $y$ del brazo 2R), $\dfrac{\partial f}{\partial\theta_2} = L_2\cos(\theta_1+\theta_2)$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $\partial x/\partial\theta_2$ del brazo 2R nunca depende de $L_1$.

**Serie B — Cálculo a mano**
- B1. Calcular $\partial y/\partial\theta_1$ para $y(\theta_1,\theta_2) = L_1\sin\theta_1 + L_2\sin(\theta_1+\theta_2)$.

**Serie C — Laboratorio**
- C1. Verificar B1 con SymPy y evaluarla numéricamente en $\theta_1=40°,\theta_2=30°,L_1=0.30,L_2=0.20$ (mismo caso del Bloque 01).

---

## Tema 4.4 — Regla de la cadena con varias variables y el gradiente

### 1. El problema

Los ángulos del brazo no son constantes: son funciones del tiempo, $\theta_1(t)$, $\theta_2(t)$, porque los motores giran. Para obtener la velocidad de la punta hace falta derivar $x(\theta_1(t),\theta_2(t))$ respecto a $t$ — una función compuesta de dos variables que a su vez dependen de una tercera.

### 2. El mecanismo

La **regla de la cadena con varias variables** dice que el cambio total es la suma de cómo cambia por cada camino posible:

$$\frac{d}{dt}f(\theta_1(t),\theta_2(t)) = \frac{\partial f}{\partial\theta_1}\dot\theta_1 + \frac{\partial f}{\partial\theta_2}\dot\theta_2$$

Cada término es "cuánto cambia $f$ por ese ángulo" multiplicado por "qué tan rápido cambia ese ángulo". Esta es, literalmente, la fórmula que en el Bloque 13 se escribe como $\dot{\vec p}=J(\vec q)\dot{\vec q}$: la Jacobiana $J$ es la matriz que junta todas las derivadas parciales, y esta ecuación es la regla de la cadena escrita en forma matricial.

El vector que reúne todas las derivadas parciales de una función escalar, $\nabla f = \left(\dfrac{\partial f}{\partial\theta_1}, \dfrac{\partial f}{\partial\theta_2}\right)$, es el **gradiente**. Apunta en la dirección donde $f$ crece más rápido, y su magnitud es la rapidez de ese crecimiento — una idea que el Bloque 14 reutiliza para deducir las ecuaciones de Lagrange a partir de la energía.

### 3. En la vida real

```python
import sympy as sp
t = sp.symbols('t')
t1 = sp.Function('theta1')(t)
t2 = sp.Function('theta2')(t)
L1, L2 = sp.symbols('L1 L2')
x = L1*sp.cos(t1) + L2*sp.cos(t1+t2)
sp.diff(x, t)   # aplica la regla de la cadena automáticamente
```

### 4. Limitaciones

Ninguna nueva; es una consecuencia directa de las derivadas parciales del Tema 4.3.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La velocidad de la punta calculada a mano no coincide con la de SymPy | Se olvidó uno de los dos términos de la suma (solo se consideró el efecto de un ángulo) | Comparar término a término con la salida simbólica de `sp.diff` sobre las funciones del tiempo | Verificar que la suma incluya un término por cada variable de la que depende $f$ |

### 6. Dónde más aparece la idea

La Jacobiana completa (Bloque 13), las ecuaciones de Lagrange (Bloque 14), retropropagación en redes neuronales (la regla de la cadena aplicada capa por capa), el método de Newton en varias variables.

### 7. Ejemplos resueltos

**Ejemplo:** brazo 2R con $\dot\theta_1=1$ rad/s, $\dot\theta_2=0.5$ rad/s en $\theta_1=40°,\theta_2=30°$, $L_1=0.30,L_2=0.20$. Usando $\partial x/\partial\theta_1$ y $\partial x/\partial\theta_2$ del Tema 4.3:

$$\dot x = \left(-L_1\sin\theta_1-L_2\sin(\theta_1+\theta_2)\right)\dot\theta_1 + \left(-L_2\sin(\theta_1+\theta_2)\right)\dot\theta_2$$

Numéricamente: $\dot x \approx (-0.193-0.188)(1) + (-0.188)(0.5) \approx -0.475$ m/s.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la fórmula de $\dot x$ tiene dos términos y no uno solo, pensando en que ambos motores giran a la vez.

**Serie B — Cálculo a mano**
- B1. Con los mismos datos del ejemplo, calcular $\dot y$ usando $\partial y/\partial\theta_1$ y $\partial y/\partial\theta_2$ del Tema 4.3.

**Serie C — Laboratorio**
- C1. Verificar B1 con SymPy (derivando $\theta_1(t),\theta_2(t)$ simbólicamente) y con diferencias finitas: calcular $x(\theta_1+\dot\theta_1 h,\theta_2+\dot\theta_2 h)$ para un $h$ pequeño y comparar $(x(t+h)-x(t))/h$ contra el resultado analítico.

---

## Tema 4.5 — Series de Taylor y linealización

### 1. El problema

Las ecuaciones del brazo (cinemática, dinámica) son curvas: senos, cosenos, productos de ángulos. Para varios métodos del curso —Newton-Raphson (Tema 4.6), control cerca de un punto de operación (Parte V)— hace falta poder reemplazar, cerca de un punto, esa curva complicada por una recta (o un plano) mucho más fácil de manejar.

### 2. El mecanismo

La **serie de Taylor** de primer orden aproxima una función suave cerca de un punto $a$ por la recta tangente en ese punto:

$$f(x) \approx f(a) + f'(a)(x-a)$$

Es exacta en $x=a$ y cada vez menos precisa a medida que $x$ se aleja de $a$; el error que se comete es proporcional a $(x-a)^2$ (siguiente término de la serie completa), así que para desplazamientos pequeños el error es muy pequeño. A esto se le llama **linealizar**: cambiar algo curvo por algo recto cerca de un punto de trabajo.

Para funciones de varias variables, la misma idea usa el gradiente (Tema 4.4):

$$f(\vec\theta) \approx f(\vec\theta_0) + \nabla f(\vec\theta_0)\cdot(\vec\theta-\vec\theta_0)$$

### 3. En la vida real

```python
import sympy as sp
theta = sp.symbols('theta')
f = sp.sin(theta)
a = sp.pi/6
aprox = f.subs(theta, a) + sp.diff(f, theta).subs(theta, a) * (theta - a)
```

### 4. Limitaciones

La aproximación solo es buena **cerca** de $a$; usarla lejos del punto de linealización da resultados incorrectos sin ningún aviso — el error crece silenciosamente. En el Bloque 20 esta es exactamente la razón por la que un control PD con compensación de gravedad, linealizado alrededor de una postura, deja de funcionar bien si el brazo se mueve lejos de esa postura.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una aproximación lineal da buenos resultados cerca de un punto pero falla notoriamente más lejos | Es el comportamiento esperado de una linealización: el error crece con la distancia al punto de referencia | Comparar la aproximación contra la función real en un rango de valores, no solo en un punto | Relinealizar en un nuevo punto, o usar el modelo completo si el rango de operación es amplio |

### 6. Dónde más aparece la idea

Control linealizado alrededor de un punto de operación (Parte V), el método de Newton-Raphson (Tema 4.6), cualquier "aproximación de primer orden" en física o ingeniería.

### 7. Ejemplos resueltos

**Ejemplo:** linealizar $\sin\theta$ alrededor de $\theta=0$: $f(0)=0$, $f'(0)=\cos0=1$, así que $\sin\theta\approx\theta$ para $\theta$ pequeño (la aproximación de ángulo pequeño, muy usada en física básica). En $\theta=0.1$ rad: real $\sin(0.1)=0.0998$, aproximación $0.1$ — error menor al 0.2 %.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la aproximación $\sin\theta\approx\theta$ deja de ser útil cerca de $\theta=\pi/2$.

**Serie B — Cálculo a mano**
- B1. Linealizar $f(\theta)=\cos\theta$ alrededor de $\theta=0$.

**Serie C — Laboratorio**
- C1. Graficar $\cos\theta$ y su linealización de B1 juntas para $\theta\in[-1,1]$ rad, y graficar el error entre ambas.

---

## Tema 4.6 — Método de Newton-Raphson

### 1. El problema

Algunas ecuaciones no tienen una fórmula que despeje la incógnita directamente (por ejemplo, buena parte de la cinemática inversa, Bloque 12). Hace falta un método que se acerque a la solución paso a paso, sin necesitar esa fórmula.

### 2. El mecanismo

Para resolver $f(x)=0$, Newton-Raphson parte de una aproximación inicial $x_0$ y la mejora repetidamente siguiendo la recta tangente (la linealización del Tema 4.5) hasta que esa recta cruza el cero:

$$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}$$

Geométricamente: en $x_n$ se traza la tangente a $f$; $x_{n+1}$ es donde esa tangente cruza el eje horizontal, que suele estar más cerca de la raíz real que $x_n$. Se repite hasta que $f(x_n)$ sea suficientemente cercano a cero.

Para varias variables (varias ecuaciones y varias incógnitas a la vez, como en la cinemática inversa numérica del Bloque 12), $f'(x)$ se reemplaza por la matriz de derivadas parciales (la Jacobiana, Tema 4.4 y Bloque 13), y la división se convierte en resolver un sistema lineal (Bloque 03, Tema 3.6):

$$\vec x_{n+1} = \vec x_n - J(\vec x_n)^{-1}f(\vec x_n)$$

### 3. En la vida real

```python
def newton_raphson(f, fprime, x0, tol=1e-10, max_iter=50):
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        x = x - fx / fprime(x)
    raise RuntimeError("Newton-Raphson no convergió")
```

### 4. Limitaciones

No siempre converge: si $f'(x_n)$ es cero o muy pequeño (tangente casi horizontal), el paso se dispara y el método puede alejarse de la solución o oscilar sin converger. También puede converger a una raíz distinta de la esperada si $x_0$ está lejos de la raíz deseada — la semilla inicial importa.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El método diverge (los valores crecen sin control) o oscila sin converger | La semilla inicial está lejos de la raíz, o $f'(x_n)$ pasa cerca de cero en alguna iteración | Graficar $f(x)$ y observar dónde está realmente la raíz y qué tan plana es $f$ cerca de $x_0$ | Elegir una semilla más cercana a la raíz esperada; limitar el número de iteraciones y el tamaño del paso |

### 6. Dónde más aparece la idea

Cinemática inversa numérica (Bloque 12), entrenamiento de modelos (métodos de optimización basados en gradiente), cualquier ecuación de ingeniería sin solución cerrada.

### 7. Ejemplos resueltos

**Ejemplo:** resolver $f(x)=x^2-2=0$ (hallar $\sqrt2$) desde $x_0=1$. $f'(x)=2x$. $x_1 = 1-\dfrac{1^2-2}{2\cdot1}=1.5$. $x_2 = 1.5-\dfrac{1.5^2-2}{2\cdot1.5}\approx1.41\overline{6}$. Tras pocas iteraciones converge a $\sqrt2\approx1.41421356$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, con un dibujo mental de la tangente, por qué una semilla donde $f'(x_0)\approx0$ es peligrosa para el método.

**Serie B — Cálculo a mano**
- B1. Hacer dos iteraciones de Newton-Raphson para $f(x)=x^3-5=0$ desde $x_0=2$.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_04/romper_diferencias_finitas.py`, que compara la derivada analítica de una función contra su derivada numérica con pasos $h$ muy grandes y muy pequeños, y muestra cómo aparece el error de redondeo cuando $h$ es demasiado pequeño.

## Lo que este bloque agrega a `codigo/robotica/`

Nada todavía: las derivadas de este bloque se trabajan directamente con SymPy y NumPy en `codigo/bloque_04/`. La librería propia sigue creciendo desde el Bloque 05 (`robotica/simular.py`).

## Glosario del bloque

| Término | Definición |
|---|---|
| Derivada | Tasa de cambio instantánea de una función; geométricamente, la pendiente de su recta tangente. |
| Derivada parcial | Derivada respecto a una variable, tratando las demás como constantes. |
| Regla de la cadena (varias variables) | Suma de los efectos de cada variable intermedia sobre la variable final, cada uno multiplicado por su propia tasa de cambio. |
| Gradiente ($\nabla f$) | Vector de todas las derivadas parciales de una función escalar; apunta en la dirección de mayor crecimiento. |
| Serie de Taylor (primer orden) / linealización | Aproximación de una función curva por su recta (o plano) tangente cerca de un punto. |
| Newton-Raphson | Método iterativo que resuelve $f(x)=0$ siguiendo la tangente de $f$ en cada paso. |
