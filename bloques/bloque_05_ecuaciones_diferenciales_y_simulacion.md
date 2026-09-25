# Bloque 05 — Ecuaciones diferenciales y simulación

> **Problema que abre el bloque:** Newton dice cuánto acelera algo, pero lo que se quiere saber es dónde estará dentro de dos segundos.
>
> **Necesitas antes:** Bloque 04. · **Lectura:** Zill, *Ecuaciones diferenciales con aplicaciones de modelado*, caps. 1–5.

## Tema 5.1 — Qué es una ecuación diferencial y qué significa "resolverla"

### 1. El problema

La segunda ley de Newton, $F=ma$, relaciona una fuerza con una *aceleración*: $\ddot x = F/m$. Eso dice cuánto cambia la velocidad en cada instante, no dónde está el objeto. Para responder "¿dónde estará en 2 segundos?" hace falta ir de la aceleración a la posición, y esa relación —una ecuación que involucra a una función *y a sus derivadas*, no solo a la función— es una ecuación diferencial.

### 2. El mecanismo

Una **ecuación diferencial ordinaria** (EDO) es una ecuación donde la incógnita es una función $x(t)$ y aparecen, además de $x$, alguna de sus derivadas ($\dot x$, $\ddot x$, ...). "Ordinaria" distingue estas ecuaciones de las que además involucran derivadas parciales respecto a varias variables (Bloque 04, Tema 4.3) — aquí solo hay una variable independiente, el tiempo.

**Resolver** una EDO es encontrar la función $x(t)$ que la cumple para todo $t$, no un número. A diferencia de una ecuación algebraica ($x^2=4$, cuya solución son números), la solución de una EDO es toda una función, y en general hay infinitas funciones que cumplen la ecuación (una familia con una o más constantes libres); la **condición inicial** ($x(0)=x_0$, o también $\dot x(0)=v_0$ si la ecuación es de segundo orden) es la que elige, de esa familia, la única solución que describe la situación física concreta.

$$\dot x = -x, \qquad x(0)=1 \quad\Longrightarrow\quad x(t) = e^{-t}$$

es el ejemplo más simple: la función cuya tasa de cambio es siempre el negativo de sí misma. La familia de soluciones de $\dot x=-x$ es $x(t)=Ce^{-t}$ para cualquier constante $C$; la condición inicial fija $C=1$.

### 3. En la vida real

```python
import sympy as sp
t = sp.symbols('t')
x = sp.Function('x')
edo = sp.Eq(x(t).diff(t), -x(t))
sp.dsolve(edo, x(t), ics={x(0): 1})   # Eq(x(t), exp(-t))
```

### 4. Limitaciones

No toda EDO tiene una solución expresable con funciones conocidas (exponenciales, senos, polinomios); muchas —incluida la del péndulo sin aproximar, Tema 5.3— no tienen solución analítica cerrada, y de ahí la necesidad de los métodos numéricos del Tema 5.5.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una solución propuesta "parece funcionar" pero no coincide con la simulación numérica | La función propuesta no cumple la condición inicial, o se le olvidó una constante de integración | Sustituir la solución propuesta en la EDO original y en $t=0$, a mano | Resolver de nuevo la constante con la condición inicial, o verificar la sustitución en la EDO |

### 6. Dónde más aparece la idea

Desintegración radiactiva ($\dot N=-\lambda N$), carga de un capacitor, crecimiento poblacional, enfriamiento de un cuerpo (ley de Newton del enfriamiento) — todas estas comparten la misma forma $\dot x=-kx$ del ejemplo.

### 7. Ejemplos resueltos

**Ejemplo:** verificar que $x(t)=3e^{-2t}$ resuelve $\dot x=-2x$ con $x(0)=3$. $\dot x(t)=-6e^{-2t}=-2(3e^{-2t})=-2x(t)$, cumple la ecuación. $x(0)=3e^0=3$, cumple la condición inicial.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la solución de una EDO es una función y no un número, con un ejemplo que no sea de física.

**Serie B — Cálculo a mano**
- B1. Verificar que $x(t)=5\cos(2t)$ resuelve $\ddot x=-4x$ con $x(0)=5,\dot x(0)=0$.

**Serie C — Laboratorio**
- C1. Resolver B1 con `sympy.dsolve` y graficar la solución con Matplotlib para $t\in[0,10]$.

---

## Tema 5.2 — Orden de una EDO y el espacio de estados

### 1. El problema

$F=ma$ da una EDO de **segundo orden** ($\ddot x$ aparece), pero los métodos numéricos del Tema 5.5 y la teoría de control de la Parte V trabajan con sistemas de **primer orden**. Hace falta una forma estándar de convertir cualquier EDO de orden superior en una de primer orden, sin perder información.

### 2. El mecanismo

El **orden** de una EDO es el de su derivada más alta. Toda EDO de orden $n$ se puede reescribir como un **sistema de $n$ ecuaciones de primer orden**, introduciendo una variable nueva por cada derivada, hasta la de orden $n-1$. Para $\ddot x + b\dot x + kx = 0$ (segundo orden), se define el **estado** $\vec z = (z_1,z_2) = (x,\dot x)$:

$$\dot z_1 = z_2, \qquad \dot z_2 = \ddot x = -bz_2-kz_1$$

El estado $\vec z$ es la información mínima que hace falta conocer *en un instante* para poder predecir el futuro del sistema sin necesitar su historia pasada: con $(x(0),\dot x(0))$ alcanza, no hace falta saber cómo llegó ahí. Esta es la razón por la que $F=ma$ necesita *dos* condiciones iniciales (posición y velocidad) y no una sola.

Escrito en forma vectorial, $\dot{\vec z}=f(t,\vec z)$, esta es la forma que esperan **todos** los métodos numéricos del resto del curso (Tema 5.5, y más adelante el Bloque 15 con la dinámica completa del brazo).

### 3. En la vida real

```python
def f(t, z):
    x, xdot = z
    return [xdot, -b*xdot - k*x]   # dz/dt
```

### 4. Limitaciones

Ninguna: es siempre posible para una EDO ordinaria de orden finito; no aplica tal cual a ecuaciones en derivadas parciales.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El sistema de primer orden simulado no coincide con la EDO original | Se definió $\dot z_1$ mal (por ejemplo, $\dot z_1=\ddot x$ en vez de $\dot z_1=\dot x=z_2$) | Revisar que cada componente del estado se derive exactamente a la siguiente | $\dot z_1=z_2$ siempre, y $\dot z_2$ es la que viene de despejar la EDO original |

### 6. Dónde más aparece la idea

El espacio de estados de un sistema de control (Bloque 17 en adelante), el estado de cualquier simulación física, redes neuronales recurrentes (el estado oculto).

### 7. Ejemplos resueltos

**Ejemplo:** convertir $\dddot x + 2\ddot x + \dot x + x=0$ (tercer orden) a sistema de primer orden. Estado $\vec z=(x,\dot x,\ddot x)$: $\dot z_1=z_2$, $\dot z_2=z_3$, $\dot z_3=-2z_3-z_2-z_1$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $F=ma$ necesita conocer posición *y* velocidad iniciales, y no solo la posición.

**Serie B — Cálculo a mano**
- B1. Convertir $\ddot\theta + \sin\theta = 0$ (péndulo, Tema 5.3) a un sistema de primer orden.

**Serie C — Laboratorio**
- C1. Escribir la función `f(t, z)` de B1 en Python y evaluarla en `z=[0.5, 0]`.

---

## Tema 5.3 — Ejemplos fundacionales: masa-resorte-amortiguador y péndulo simple

### 1. El problema

Antes de simular un brazo completo hace falta dominar dos sistemas mucho más simples que reaparecen una y otra vez en el curso: uno que oscila con fricción (una articulación con un resorte de retorno, o cualquier vibración mecánica) y uno que oscila por gravedad (la aproximación más simple de un eslabón colgando).

### 2. El mecanismo

**Masa-resorte-amortiguador**: una masa $m$ sujeta a un resorte (fuerza restauradora $-kx$, con $k$ la rigidez) y un amortiguador viscoso (fuerza opuesta a la velocidad, $-b\dot x$, con $b$ el coeficiente de amortiguamiento). Por Newton:

$$m\ddot x + b\dot x + kx = 0$$

**Péndulo simple**: una masa puntual $m$ al extremo de una varilla rígida sin masa de longitud $L$, que gira libremente alrededor de un pivote. El torque de la gravedad respecto al pivote (Bloque 02, Tema 2.3) es $\tau=-mgL\sin\theta$ (el signo negativo porque empuja de vuelta hacia $\theta=0$), y por la versión rotacional de $F=ma$ ($\tau=I\ddot\theta$, con $I=mL^2$ el momento de inercia de una masa puntual, Bloque 06):

$$mL^2\ddot\theta = -mgL\sin\theta \quad\Longrightarrow\quad \ddot\theta + \frac{g}{L}\sin\theta = 0$$

El $\sin\theta$ hace que esta ecuación **no sea lineal**: a diferencia del resorte, no tiene solución analítica cerrada en general. Solo para oscilaciones pequeñas vale la linealización del Bloque 04 (Tema 4.5), $\sin\theta\approx\theta$, que la reduce a

$$\ddot\theta + \frac{g}{L}\theta = 0$$

— la misma forma que el resorte sin amortiguar, con $k/m\to g/L$. Esta es la razón física de por qué el período del péndulo "no depende de la masa ni de la amplitud" que se enseña en el colegio: **solo es cierto para oscilaciones pequeñas**; el Tema 5.6 muestra qué tan rápido deja de serlo.

### 3. En la vida real

```python
def f_resorte(t, z, m=1.0, b=0.2, k=4.0):
    x, xdot = z
    return [xdot, -(b*xdot + k*x)/m]

def f_pendulo(t, z, g=9.81, L=1.0):
    theta, omega = z
    return [omega, -(g/L)*np.sin(theta)]
```

### 4. Limitaciones

El péndulo simple asume una masa puntual sin fricción en el pivote y una varilla rígida sin masa — el Bloque 06 (tensor de inercia) y el Bloque 14 (Lagrange) generalizan a cuerpos con masa distribuida. El resorte asume que la fuerza es exactamente proporcional a $x$ (ley de Hooke), válida solo para deformaciones pequeñas.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El péndulo simulado con la versión linealizada se ve razonable a baja amplitud pero muy distinto de la realidad a 90° | La linealización $\sin\theta\approx\theta$ (Bloque 04, Tema 4.5) solo vale cerca de $\theta=0$ | Comparar la solución linealizada contra la no lineal (Tema 5.5, numérica) para distintas amplitudes iniciales | Usar la ecuación no lineal completa para amplitudes grandes |

### 6. Dónde más aparece la idea

El resorte-amortiguador es el modelo de cualquier suspensión, de una articulación con retorno elástico, de un circuito RLC (analogía eléctrica exacta); el péndulo es la base de relojes de péndulo, de sensores inerciales, y su versión "doble péndulo" es un ejemplo clásico de caos.

### 7. Ejemplos resueltos

**Ejemplo:** péndulo linealizado con $L=1$ m: $\ddot\theta+9.81\theta=0$, misma forma que un resorte con $k/m=9.81$. Frecuencia angular $\omega_n=\sqrt{g/L}\approx3.13$ rad/s, período $T=2\pi/\omega_n\approx2.01$ s — el valor clásico $T=2\pi\sqrt{L/g}$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el signo de $-mgL\sin\theta$ es negativo, pensando en qué le hace la gravedad al péndulo cuando $\theta>0$ y cuando $\theta<0$.

**Serie B — Cálculo a mano**
- B1. Deducir el sistema de primer orden (Tema 5.2) para el resorte-amortiguador con $m=2,b=1,k=8$.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_05/masa_resorte_amortiguador.py` y verificar B1 comparando la simulación con los valores dados.

---

## Tema 5.4 — Solución analítica del sistema lineal de segundo orden

### 1. El problema

El resorte-amortiguador (y el péndulo linealizado) tienen solución exacta, expresable con funciones conocidas. Antes de simular numéricamente cualquier cosa, conviene saber resolver este caso a mano, porque su comportamiento —oscila, no oscila, vuelve al equilibrio rápido o lento— reaparece constantemente en control (Parte V) para describir la respuesta de un sistema realimentado.

### 2. El mecanismo

Para $m\ddot x+b\dot x+kx=0$, se propone una solución de la forma $x(t)=e^{\lambda t}$ (una función que se reproduce a sí misma al derivar, la candidata natural para una ecuación lineal de coeficientes constantes). Sustituyendo:

$$m\lambda^2+b\lambda+k=0 \quad\Longrightarrow\quad \lambda = \frac{-b\pm\sqrt{b^2-4mk}}{2m}$$

la **ecuación característica**. El signo del discriminante $b^2-4mk$ define tres comportamientos cualitativamente distintos:

- **Subamortiguado** ($b^2<4mk$): $\lambda$ es complejo, $\lambda=-\alpha\pm i\omega_d$. La solución es $x(t)=e^{-\alpha t}\big(C_1\cos\omega_dt+C_2\sin\omega_dt\big)$: oscila con frecuencia $\omega_d$ dentro de una envolvente que decae como $e^{-\alpha t}$. Es el caso de poco amortiguamiento: un columpio que sigue vaivén varias veces antes de detenerse.
- **Críticamente amortiguado** ($b^2=4mk$): raíz doble $\lambda=-b/2m$. $x(t)=(C_1+C_2t)e^{-b t/2m}$: vuelve al equilibrio **sin oscilar**, en el menor tiempo posible sin pasarse. Es el punto de diseño ideal para muchos amortiguadores (puertas de cierre automático, suspensiones).
- **Sobreamortiguado** ($b^2>4mk$): dos raíces reales distintas, $x(t)=C_1e^{\lambda_1t}+C_2e^{\lambda_2t}$: vuelve al equilibrio sin oscilar, pero más lento que el caso crítico.

Las constantes $C_1,C_2$ se fijan con las condiciones iniciales $x(0),\dot x(0)$ (Tema 5.1).

### 3. En la vida real

```python
import sympy as sp
t, m, b, k = sp.symbols('t m b k', positive=True)
x = sp.Function('x')
edo = sp.Eq(m*x(t).diff(t,2) + b*x(t).diff(t) + k*x(t), 0)
sp.dsolve(edo, x(t))
```

### 4. Limitaciones

Esta solución exacta solo existe para EDO **lineales** de coeficientes **constantes**; el péndulo no linealizado (Tema 5.3) no la tiene, y de ahí la necesidad de los métodos numéricos del Tema 5.5.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La solución calculada tiene una frecuencia $\omega_d$ que no es un número real | Se está en el caso sobreamortiguado ($b^2>4mk$) pero se siguió usando la fórmula del caso subamortiguado | Calcular primero el discriminante $b^2-4mk$ y elegir la fórmula según su signo | Usar la forma con exponenciales reales para el caso sobreamortiguado |

### 6. Dónde más aparece la idea

La respuesta al escalón de cualquier sistema de control de segundo orden (Bloque 17), circuitos RLC, la respuesta de una suspensión de automóvil.

### 7. Ejemplos resueltos

**Ejemplo:** $m=1,b=2,k=5$. Discriminante $=4-20=-16<0$: subamortiguado. $\lambda=-1\pm2i$, así que $\alpha=1,\omega_d=2$: $x(t)=e^{-t}(C_1\cos2t+C_2\sin2t)$, oscila amortiguándose con envolvente $e^{-t}$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, sin resolver ninguna ecuación, por qué el caso crítico es el "límite" entre oscilar y no oscilar.

**Serie B — Cálculo a mano**
- B1. Clasificar (sub/crítico/sobreamortiguado) y resolver $\ddot x+5\dot x+6x=0$ con $x(0)=1,\dot x(0)=0$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `sympy.dsolve` y graficar junto con los otros dos casos (mismo $m,k$, variando $b$) para comparar visualmente los tres comportamientos.

---

## Tema 5.5 — Solución numérica: Euler y Runge-Kutta 4

### 1. El problema

El péndulo sin linealizar, la dinámica completa de un brazo (Bloque 14) y casi todo lo que el curso simula de aquí en adelante no tiene solución analítica. Hace falta un método que, partiendo del estado inicial, avance paso a paso en el tiempo y calcule una aproximación de la solución.

### 2. El mecanismo

Dado el sistema de primer orden $\dot{\vec z}=f(t,\vec z)$ (Tema 5.2) y un estado inicial $\vec z_0$, ambos métodos avanzan con un paso de tiempo $h$ fijo, calculando $\vec z_{i+1}$ a partir de $\vec z_i$.

**Método de Euler**: usa la definición misma de derivada (Bloque 04, Tema 4.1) para aproximar el siguiente estado con la pendiente actual:

$$\vec z_{i+1} = \vec z_i + h\,f(t_i,\vec z_i)$$

Es la serie de Taylor de primer orden (Bloque 04, Tema 4.5) aplicada paso a paso: **cada paso comete un error proporcional a $h^2$**, y esos errores se acumulan.

**Runge-Kutta de cuarto orden (RK4)**: en vez de usar solo la pendiente al inicio del paso, promedia cuatro estimaciones de la pendiente (al inicio, dos a la mitad del paso con distintas correcciones, y una al final), con un peso mayor para las dos del medio:

$$k_1=f(t_i,\vec z_i),\quad k_2=f\!\left(t_i+\tfrac h2,\vec z_i+\tfrac h2k_1\right),\quad k_3=f\!\left(t_i+\tfrac h2,\vec z_i+\tfrac h2k_2\right),\quad k_4=f(t_i+h,\vec z_i+hk_3)$$

$$\vec z_{i+1}=\vec z_i+\frac h6\big(k_1+2k_2+2k_3+k_4\big)$$

El error por paso de RK4 es proporcional a $h^5$ (mucho más pequeño que el de Euler para el mismo $h$), a costa de evaluar $f$ cuatro veces por paso en vez de una.

### 3. En la vida real

`codigo/robotica/simular.py` implementa `euler(f, x0, t)` y `rk4(f, x0, t)` a mano, comparables con la librería profesional:

```python
from scipy.integrate import solve_ivp
sol = solve_ivp(f, [0, 10], x0, t_eval=t, method="RK45")  # adaptativo, más robusto aún
```

`solve_ivp` con `method="RK45"` va más allá de RK4: además ajusta $h$ automáticamente según el error estimado en cada paso — la herramienta profesional que se usa en el resto del curso una vez entendido el mecanismo con Euler y RK4 propios.

### 4. Limitaciones

Todos son métodos aproximados: incluso RK4 acumula error si el paso $h$ es demasiado grande (Tema 5.6) o si la simulación corre por mucho tiempo. Ninguno "sabe" si el sistema tiene una solución analítica más simple.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La simulación con Euler se aleja visiblemente de la de RK4 o `solve_ivp` para el mismo sistema | El paso $h$ de Euler es demasiado grande para la rapidez con que cambia el sistema | Repetir con un $h$ más pequeño y ver si Euler se acerca a RK4 | Usar un $h$ menor, o directamente RK4/`solve_ivp` |

### 6. Dónde más aparece la idea

Simulación de cualquier sistema dinámico (circuitos, clima, órbitas), la dinámica directa del brazo completo (Bloque 15), videojuegos (motores de física).

### 7. Ejemplos resueltos

**Ejemplo:** un paso de Euler para $\dot x=-x$, $x_0=1$, $h=0.1$: $x_1=1+0.1\cdot(-1)=0.9$. Valor exacto $e^{-0.1}\approx0.905$: el error de un solo paso es pequeño (0.005) pero se acumula en cada paso siguiente.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, sin fórmulas, por qué promediar cuatro pendientes (RK4) da una mejor aproximación que usar solo la pendiente inicial (Euler).

**Serie B — Cálculo a mano**
- B1. Hacer dos pasos de Euler con $h=0.5$ para $\dot x=-x$, $x_0=1$, y comparar con el valor exacto $e^{-1}$.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_05/simular_pendulo.py`: compara Euler, RK4 y `solve_ivp` para el péndulo no lineal, mismo $h$, y grafica $\theta(t)$ de los tres métodos juntos.

---

## Tema 5.6 — Paso de integración, estabilidad numérica y energía que aparece de la nada

### 1. El problema

Un péndulo sin fricción, por física, nunca gana energía: oscila para siempre a la misma amplitud. Simulado con Euler y un paso $h$ grande, sin embargo, la amplitud **crece** con el tiempo, como si algo lo empujara — un efecto puramente numérico, no físico, y hay que saber reconocerlo.

### 2. El mecanismo

La energía mecánica de un péndulo sin fricción, $E=\tfrac12mL^2\omega^2+mgL(1-\cos\theta)$ (cinética más potencial, Bloque 06), es constante en la solución real: es un sistema **conservativo**. El método de Euler, al usar solo la pendiente al inicio del paso, sistemáticamente "se pasa" hacia afuera de la trayectoria verdadera en cada paso de un sistema oscilatorio — el error no es aleatorio, tiene un sesgo que **inyecta energía** en cada ciclo. Con un paso $h$ pequeño ese sesgo es pequeño y tarda mucho en notarse; con un paso grande, la energía crece visiblemente en pocos ciclos y el péndulo termina dando vueltas completas en vez de oscilar.

Esto es un problema de **estabilidad numérica**, distinto del error de un solo paso (Tema 5.5): un método puede ser "consistente" (el error por paso tiende a cero si $h\to0$) y aun así ser **inestable** para un $h$ demasiado grande, con un error que crece sin control en vez de mantenerse acotado. RK4 tiene una región de estabilidad más amplia que Euler (tolera pasos más grandes antes de volverse inestable), pero **ningún método de paso fijo es incondicionalmente estable**: siempre existe un $h$ suficientemente grande que lo rompe.

### 3. En la vida real

```python
from robotica.simular import euler
Z = euler(f_pendulo, [np.radians(30), 0.0], t)
energia = 0.5*m*L**2*Z[:,1]**2 + m*g*L*(1-np.cos(Z[:,0]))
```

Graficar `energia` contra `t`: debería ser una línea plana; con Euler y `h` grande, crece.

### 4. Limitaciones

Reducir $h$ siempre ayuda a la estabilidad, pero cuesta más cómputo (más pasos para el mismo tiempo total) y, en el límite de $h$ extremadamente pequeño, introduce el error de redondeo visto en el Bloque 04 (Tema 4.6) — el mismo balance en forma de V, ahora aplicado a la estabilidad de una simulación completa en vez de a una sola derivada.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un péndulo o resorte sin fricción simulado gana amplitud con el tiempo, o "explota" (valores que crecen sin control) | Paso $h$ demasiado grande para el método usado (típicamente Euler) | Graficar la energía del sistema a lo largo del tiempo: debería mantenerse constante (sin fricción) | Reducir $h$, o cambiar a un método con mejor estabilidad (RK4, o un integrador que conserve energía) |

### 6. Dónde más aparece la idea

Cualquier simulación física de largo plazo (clima, órbitas planetarias) donde la conservación de energía es la prueba estándar de que el integrador numérico es confiable; el mismo concepto de estabilidad reaparece en el Bloque 18 con el control digital y el período de muestreo.

### 7. Ejemplos resueltos

**Ejemplo:** péndulo con $L=1$ m, $\theta_0=30°$, simulado 15 s. Con Euler y $h=0.2$ s la energía crece más de 60 veces (6300 %); con Euler y $h=0.01$ s el crecimiento es mucho más lento (algo más del 280 %) pero sigue siendo grande en una simulación larga; con RK4 y $h=0.2$ s —un paso 20 veces mayor que el Euler más fino— la energía se mantiene prácticamente constante (deriva de apenas un 5 %, y de signo contrario: RK4 tiende a perder un poco de energía, no a ganarla).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué "el error por paso es pequeño" (Tema 5.5) no es garantía de que una simulación larga sea confiable.

**Serie B — Cálculo a mano**
- B1. Sin calcular nada numéricamente: ¿qué se espera que le pase a la energía de un resorte-amortiguador (con $b>0$, es decir, con fricción real) simulado con Euler y paso grande? ¿Se puede distinguir la pérdida de energía real (por el amortiguador) del posible sesgo numérico?

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_05/romper_euler_paso_grande.py`: simula el péndulo sin fricción con Euler para varios pasos $h$, grafica la energía contra el tiempo en cada caso, y compara contra RK4 con el mismo $h$ más grande.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/simular.py`: `euler(f, x0, t)`, `rk4(f, x0, t)` — integradores propios de sistemas de primer orden, usados en los laboratorios de este bloque y comparados con `scipy.integrate.solve_ivp`.

## Glosario del bloque

| Término | Definición |
|---|---|
| Ecuación diferencial ordinaria (EDO) | Ecuación donde la incógnita es una función de una variable y aparecen sus derivadas. |
| Orden (de una EDO) | El de su derivada más alta. |
| Estado | Conjunto mínimo de variables (por ejemplo, posición y velocidad) que describe la condición de un sistema en un instante y basta para predecir su futuro. |
| Sistema conservativo | Sistema cuya energía mecánica total se mantiene constante en el tiempo (sin fricción ni otras pérdidas). |
| Ecuación característica | Ecuación algebraica que resulta de proponer $x(t)=e^{\lambda t}$ en una EDO lineal de coeficientes constantes. |
| Subamortiguado / crítico / sobreamortiguado | Los tres comportamientos posibles de un sistema lineal de segundo orden, según el signo del discriminante de su ecuación característica. |
| Método de Euler | Integrador numérico que avanza con la pendiente al inicio de cada paso; error por paso $O(h^2)$. |
| Runge-Kutta 4 (RK4) | Integrador numérico que promedia cuatro estimaciones de la pendiente por paso; error por paso $O(h^5)$. |
| Estabilidad numérica | Propiedad de un método de no amplificar el error sin control a medida que avanza la simulación, para un paso $h$ dado. |
