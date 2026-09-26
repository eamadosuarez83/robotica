# Bloque 06 — Mecánica del sólido rígido

> **Problema que abre el bloque:** un eslabón de aluminio no es un punto. ¿Qué tan difícil es hacerlo girar y cuánto pesa "dónde"?
>
> **Necesitas antes:** Bloques 02 y 05. · **Lectura:** Beer & Johnston o Hibbeler, *Dinámica*, capítulos de cuerpo rígido.

## Tema 6.1 — De la partícula al cuerpo rígido: centro de masa

### 1. El problema

$F=ma$ (Bloque 05) describe una partícula: un punto sin tamaño. Un eslabón real tiene forma, volumen y masa repartida de manera desigual (más metal cerca de las articulaciones). Para seguir usando $F=ma$ sin repetir la cuenta átomo por átomo, hace falta un solo punto que resuma "dónde está" toda esa masa repartida.

### 2. El mecanismo

Un cuerpo rígido es una colección de partículas cuyas distancias mutuas no cambian (Bloque 03, Tema 3.5: se mueve por transformaciones que no deforman). Para un cuerpo con densidad $\rho(\vec r)$ ocupando un volumen $V$, el **centro de masa** es el promedio de la posición, pesado por la masa de cada punto:

$$\vec r_{cm} = \frac{1}{m}\int_V \vec r\,\rho(\vec r)\,dV, \qquad m = \int_V \rho(\vec r)\,dV$$

Para un cuerpo formado por $n$ piezas discretas de masa $m_i$ en $\vec r_i$ (por ejemplo, un eslabón con un motor en un extremo), la versión discreta es más simple:

$$\vec r_{cm} = \frac{\sum_i m_i\vec r_i}{\sum_i m_i}$$

Lo notable: **las leyes de Newton para un cuerpo rígido completo son las mismas que para una partícula, aplicadas al centro de masa** — $\sum\vec F = m\ddot{\vec r}_{cm}$ — sin importar cómo esté repartida la masa. Esta es la razón por la que, para describir *cómo se traslada* un eslabón, basta con un punto (su centro de masa); para describir cómo *gira*, hacen falta las herramientas de los siguientes temas.

### 3. En la vida real

```python
import sympy as sp
x, y, z, w, h, d = sp.symbols('x y z w h d', positive=True)
# eslabón: prisma homogéneo de ancho w, alto h, largo d, densidad rho
rho = sp.symbols('rho', positive=True)
m = sp.integrate(rho, (x, 0, w), (y, 0, h), (z, 0, d))
x_cm = sp.integrate(rho*x, (x, 0, w), (y, 0, h), (z, 0, d)) / m
```

Para un prisma homogéneo el resultado es obvio sin integrar (el centro geométrico), pero la misma integral es la que hace falta para una pieza con densidad no uniforme o forma irregular.

### 4. Limitaciones

Todo este bloque asume **sólido rígido**: el eslabón no se deforma al moverse. Un brazo real flexiona un poco bajo carga (Bloque 22 lo retoma como una fuente de error que el modelo no ve).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El centro de masa calculado no coincide con el punto de equilibrio real de la pieza | Se ignoró la masa de piezas añadidas (motor, tornillos, cableado) que desplazan el centro de masa del prisma "limpio" | Sumar esas masas como puntos discretos con la fórmula de $n$ piezas | Incluir todas las masas relevantes, no solo la geometría base |

### 6. Dónde más aparece la idea

El centro de masa de un vehículo (estabilidad), el "centroide" en resistencia de materiales, el punto de equilibrio de cualquier objeto que se balancea.

### 7. Ejemplos resueltos

**Ejemplo:** un eslabón de 20 cm modelado como una varilla de masa $m_1=0.3$ kg con un motor de $m_2=0.2$ kg en su extremo ($x=20$ cm). Centro de masa de la varilla sola: $x=10$ cm (su centro geométrico). Centro de masa del conjunto: $x_{cm}=\dfrac{0.3\cdot10+0.2\cdot20}{0.5}=14$ cm — desplazado hacia el motor, como es de esperar.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el centro de masa de una herramienta con el mango hueco y la cabeza de metal está mucho más cerca de la cabeza que su centro geométrico.

**Serie B — Cálculo a mano**
- B1. Calcular el centro de masa de un eslabón de 30 cm (masa 0.4 kg, centrada) con una pinza de 0.15 kg en la punta ($x=30$ cm).

**Serie C — Laboratorio**
- C1. Verificar B1 con SymPy, generalizando la fórmula discreta a una función que reciba una lista de $(m_i,\vec r_i)$.

---

## Tema 6.2 — Torque, momento angular y la versión rotacional de $F=ma$

### 1. El problema

Empujar un eslabón por su centro de masa lo traslada sin girarlo; empujarlo por un extremo lo hace girar también. $F=ma$ no distingue estos dos casos porque solo mira la fuerza neta. Hace falta la versión de la segunda ley de Newton para el giro.

### 2. El mecanismo

El **torque** de una fuerza respecto a un punto, ya definido en el Bloque 02 (Tema 2.3) como $\vec\tau=\vec r\times\vec F$, es lo que produce el giro. El **momento angular** de una partícula respecto a un punto es $\vec L=\vec r\times m\vec v$ — el análogo rotacional de la cantidad de movimiento lineal $m\vec v$. Para un cuerpo rígido girando con velocidad angular $\vec\omega$ alrededor de un eje fijo, se puede mostrar que $\vec L=I\vec\omega$, con $I$ el momento de inercia (Tema 6.3) — la misma relación que $\vec p=m\vec v$, cambiando masa por inercia y velocidad lineal por velocidad angular.

La versión rotacional de $F=ma$ es entonces:

$$\vec\tau = \dot{\vec L}$$

que, cuando $I$ es constante (el cuerpo no cambia de forma), se reduce a la fórmula que se usa una y otra vez en el resto del curso:

$$\tau = I\ddot\theta$$

Esta es exactamente la ecuación que dedujo, sin nombrarla así, el péndulo del Bloque 05 (Tema 5.3): $\tau=-mgL\sin\theta$ y $I=mL^2$ dan $mL^2\ddot\theta=-mgL\sin\theta$.

### 3. En la vida real

```python
tau = np.cross(r, F)          # Bloque 02
alfa = tau / I                # aceleración angular, con I momento de inercia escalar
```

### 4. Limitaciones

$\vec\tau=I\vec\omega$ como escalar solo vale para rotación alrededor de un **eje fijo conocido**; en 3D general, sin un eje fijo, $I$ deja de ser un número y se convierte en el tensor de inercia (Tema 6.4), porque el cuerpo puede resistir el giro de forma distinta según el eje.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Dos fuerzas de igual magnitud producen aceleraciones angulares distintas y no se entiende por qué | Se aplicaron a distancias distintas del eje de giro (el torque depende de $\vec r$, no solo de $\vec F$) | Calcular el torque de cada fuerza por separado, no solo comparar sus magnitudes | Comparar torques, no fuerzas, al razonar sobre el giro |

### 6. Dónde más aparece la idea

El par (torque) que debe entregar cada motor de un brazo (Bloques 14–16), el momento angular conservado de un patinador que cierra los brazos, giroscopios.

### 7. Ejemplos resueltos

**Ejemplo:** una puerta ($I=5$ kg·m²) recibe un torque de 10 N·m. $\ddot\theta=\tau/I=2$ rad/s².

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué empujar una puerta cerca de las bisagras cuesta más esfuerzo que empujarla cerca del borde libre, en términos de torque.

**Serie B — Cálculo a mano**
- B1. Con $I=2$ kg·m² y $\tau=6$ N·m constante, calcular $\ddot\theta$, y con $\theta(0)=0,\dot\theta(0)=0$, la posición $\theta(t)$ (integrando dos veces, Bloque 05).

**Serie C — Laboratorio**
- C1. Verificar B1 con `robotica.simular.rk4` (Bloque 05), planteando el sistema de primer orden $\dot\theta=\omega$, $\dot\omega=\tau/I$.

---

## Tema 6.3 — Momento de inercia y el teorema de Steiner

### 1. El problema

$\tau=I\ddot\theta$ necesita $I$: un número que resuma qué tan "difícil" es hacer girar un cuerpo alrededor de un eje dado. Y ese número no es el mismo si el eje pasa por el centro de masa del eslabón o por su extremo (donde suele estar el motor que lo mueve) — hace falta saber relacionar ambos casos sin repetir la integral completa.

### 2. El mecanismo

El **momento de inercia** respecto a un eje es la suma de cada elemento de masa multiplicado por el cuadrado de su distancia $d$ al eje:

$$I = \int_V d(\vec r)^2\,\rho(\vec r)\,dV$$

El cuadrado de la distancia (no la distancia misma) aparece porque la energía cinética de un punto girando a velocidad angular $\omega$ es $\tfrac12mv^2=\tfrac12m(d\omega)^2$: la masa lejana al eje "cuesta" desproporcionadamente más hacerla girar.

Calcular esta integral respecto al centro de masa es, para las formas típicas de un eslabón (varilla, prisma, cilindro), un resultado conocido y tabulado. El problema es que casi nunca interesa el eje por el centro de masa: interesa el eje de la articulación, en un extremo. El **teorema de ejes paralelos** (Steiner) evita repetir la integral:

$$I_{eje} = I_{cm} + md^2$$

donde $I_{cm}$ es el momento de inercia respecto a un eje paralelo que pasa por el centro de masa, y $d$ es la distancia entre ambos ejes. La lectura física: alejar el eje de giro del centro de masa siempre **aumenta** la inercia (el término $md^2\geq0$), nunca la disminuye — girar un eslabón desde su extremo es siempre más difícil que girarlo desde su centro.

### 3. En la vida real

```python
I_cm = m * L**2 / 12          # varilla uniforme de largo L, eje perpendicular por el centro
I_extremo = I_cm + m * (L/2)**2   # Steiner, eje en un extremo
```

### 4. Limitaciones

Steiner solo relaciona ejes **paralelos**; para comparar momentos de inercia respecto a ejes con distinta orientación hace falta el tensor de inercia completo (Tema 6.4).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El momento de inercia respecto al extremo calculado es menor que respecto al centro de masa | Error de signo o de fórmula: Steiner siempre suma $md^2$, nunca resta | Verificar que $I_{eje}\geq I_{cm}$ siempre | Revisar la fórmula: $I_{eje}=I_{cm}+md^2$ |

### 6. Dónde más aparece la idea

El "efecto pluma" de extender los brazos al patinar sobre hielo (aumenta $I$), el diseño de volantes de inercia, por qué un péndulo físico (con masa distribuida) no oscila con el mismo período que uno simple de la misma longitud.

### 7. Ejemplos resueltos

**Ejemplo:** varilla uniforme, $m=0.3$ kg, $L=0.4$ m. $I_{cm}=\tfrac{1}{12}(0.3)(0.4)^2=0.004$ kg·m². Respecto a un extremo ($d=L/2=0.2$ m): $I_{extremo}=0.004+0.3(0.2)^2=0.016$ kg·m² — cuatro veces más grande.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué $I_{extremo}$ resultó ser *exactamente* 4 veces $I_{cm}$ en el ejemplo (pista: para una varilla, $I_{cm}=mL^2/12$ e $I_{extremo}=mL^2/3$).

**Serie B — Cálculo a mano**
- B1. Calcular $I$ de un disco uniforme de masa 0.5 kg y radio 0.1 m ($I_{cm}=\tfrac12mr^2$ para el eje perpendicular por el centro) respecto a un eje paralelo tangente al borde del disco.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_06/romper_sin_steiner.py`: calcula la inercia de un eslabón respecto a su extremo **sin** Steiner (usando por error la fórmula de $I_{cm}$ directamente) y compara contra el valor correcto.

---

## Tema 6.4 — El tensor de inercia: por qué en 3D la inercia es una matriz

### 1. El problema

Un eslabón real no gira solo alrededor de un eje conveniente: en 3D, la articulación puede orientarlo en cualquier dirección, y la inercia que "se siente" depende de alrededor de qué eje se gire. Un número ya no alcanza para describir eso.

### 2. El mecanismo

Para un cuerpo rígido girando con velocidad angular $\vec\omega$ (un vector, no un escalar, si el eje de giro no está fijo), el momento angular resulta:

$$\vec L = I\vec\omega$$

donde ahora $I$ es una **matriz de $3\times3$, el tensor de inercia**:

$$I = \begin{pmatrix} I_{xx} & -I_{xy} & -I_{xz} \\ -I_{xy} & I_{yy} & -I_{yz} \\ -I_{xz} & -I_{yz} & I_{zz} \end{pmatrix}$$

con los términos diagonales ($I_{xx}=\int(y^2+z^2)\rho\,dV$, y análogos) los momentos de inercia respecto a cada eje, y los términos fuera de la diagonal (los **productos de inercia**, $I_{xy}=\int xy\,\rho\,dV$) midiendo qué tan asimétrica es la distribución de masa respecto a los planos coordenados.

Que $I$ sea una matriz explica algo que un número no podría: $\vec L$ e $\vec\omega$ **no tienen por qué ser paralelos** — un cuerpo puede girar alrededor de un eje y "tambalear" ligeramente porque su momento angular apunta en otra dirección (la causa de que una llave inglesa lanzada al aire, girando sobre un eje que no es principal, se tambalee en vuelo).

$I$ es simétrica (Bloque 03, Tema 3.7) y siempre tiene valores propios reales y vectores propios perpendiculares entre sí: esas direcciones son los **ejes principales de inercia**, las únicas alrededor de las cuales el cuerpo puede girar con $\vec L\parallel\vec\omega$ sin tambalear. Para un eslabón con simetría (la mayoría de las piezas mecanizadas), los ejes principales coinciden con los ejes de simetría, y $I$ es diagonal en esa base — otra instancia del Tema 3.7: encontrar las direcciones que una matriz "solo estira".

### 3. En la vida real

```python
import numpy as np
valores, ejes_principales = np.linalg.eigh(I)   # I simétrica: eigh es más preciso que eig
```

`robotica-manipuladores/python/notebooks/09_tensor_de_inercia.ipynb` deduce con SymPy, paso a paso, el tensor de inercia de un prisma homogéneo — el mismo cálculo del laboratorio de este bloque, ya verificado; ver [docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md).

### 4. Limitaciones

Como en el resto del bloque, se asume sólido rígido y densidad conocida (uniforme, en los ejemplos del curso); un cuerpo real con huecos, tornillos o cableado interno tiene un tensor de inercia que hay que medir o corregir por superposición (sumando/restando los tensores de las piezas, cada uno trasladado con la versión matricial de Steiner).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un eslabón simulado gira sobre un eje y "tambalea" sin razón física aparente | El eje de giro elegido no es un eje principal de inercia (los productos de inercia no son cero para ese eje) | Diagonalizar $I$ (`np.linalg.eigh`) y comparar el eje de giro con los ejes principales resultantes | Girar sobre un eje principal, o incluir el tambaleo como parte esperada del modelo |
| El tensor de inercia calculado no es simétrico | Error de signo o de fórmula al calcular los productos de inercia | Comprobar `np.allclose(I, I.T)` | Revisar las integrales de $I_{xy},I_{xz},I_{yz}$ |

### 6. Dónde más aparece la idea

Por qué una moneda lanzada girando sobre un eje que no es principal se tambalea, el diseño de satélites y de ruedas de vehículos (balanceo), la estabilidad rotacional en general (retomada en el Bloque 06 del curso de control, análoga a la estabilidad de sistemas dinámicos).

### 7. Ejemplos resueltos

**Ejemplo:** un prisma homogéneo con simetría respecto a sus tres ejes tiene productos de inercia nulos ($I_{xy}=I_{xz}=I_{yz}=0$ por simetría del integrando: por cada punto $(x,y,z)$ con $x>0$ hay un punto simétrico $(-x,y,z)$ que cancela la contribución a $I_{xy}$). Su tensor de inercia ya es diagonal en los ejes del prisma: esos son directamente sus ejes principales.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué los productos de inercia de un cuerpo simétrico respecto a un plano coordenado son cero, usando el argumento de cancelación por simetría del ejemplo.

**Serie B — Cálculo a mano**
- B1. Para un prisma homogéneo de masa $m$, ancho $w$, alto $h$ y largo $d$ (ejes alineados con el prisma), el momento de inercia respecto al eje que pasa por su centro y es paralelo a $d$ es $I=\tfrac{1}{12}m(w^2+h^2)$. Calcularlo para $m=0.3$ kg, $w=0.03$ m, $h=0.02$ m.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_06/tensor_inercia_eslabon.py`: deduce con SymPy el tensor de inercia completo de un eslabón (prisma homogéneo), verifica B1 y confirma que ya es diagonal en los ejes del prisma.

---

## Tema 6.5 — Energía cinética y energía potencial de un cuerpo rígido

### 1. El problema

El Bloque 14 va a deducir la dinámica completa del brazo a partir de su energía (las ecuaciones de Lagrange, Bloque 04 Tema 4.4). Antes hace falta saber escribir la energía de un solo eslabón que se traslada y gira a la vez.

### 2. El mecanismo

La energía cinética de un cuerpo rígido se separa, de forma exacta, en una parte de **traslación** del centro de masa y una de **rotación** alrededor de él:

$$K = \underbrace{\tfrac12 m\|\vec v_{cm}\|^2}_{\text{traslación}} + \underbrace{\tfrac12\vec\omega^T I_{cm}\vec\omega}_{\text{rotación}}$$

(la forma cuadrática $\vec\omega^TI_{cm}\vec\omega$, Bloque 03, es la generalización de $\tfrac12I\omega^2$ del Tema 6.2 cuando $I$ es una matriz). Esta separación —posible gracias a que $\vec r_{cm}$ es, por definición, el promedio de posición pesado por masa— es la razón por la que el centro de masa es tan conveniente: sin él, la energía de traslación y de rotación se mezclarían de forma mucho más incómoda de escribir.

La energía potencial gravitatoria, con $g$ apuntando en $-z$, depende solo de la altura del centro de masa:

$$U = mgz_{cm}$$

Ambas expresiones, sumadas eslabón por eslabón, son exactamente los términos $K$ y $U$ que el Bloque 14 deriva para obtener el lagrangiano $L=K-U$ del brazo completo.

### 3. En la vida real

```python
K = 0.5*m*np.dot(v_cm, v_cm) + 0.5*omega @ I_cm @ omega
U = m*g*z_cm
```

### 4. Limitaciones

Aquí $I_{cm}$ está expresado en el marco fijo; en la práctica conviene expresarlo en el marco del eslabón (donde es constante) y rotarlo, lo que el Bloque 14 retoma con las matrices de rotación del Bloque 08.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La energía cinética calculada es menor de lo esperado para un eslabón que gira rápido | Se calculó solo el término de traslación, olvidando el de rotación (o viceversa) | Calcular ambos términos por separado y verificar que ninguno sea cero sin razón física | Incluir siempre los dos términos para un cuerpo que se traslada y gira a la vez |

### 6. Dónde más aparece la idea

La energía total de cualquier sistema mecánico (base de las ecuaciones de Lagrange, Bloque 14), el diseño de volantes de inercia para almacenar energía, la energía de un satélite en rotación.

### 7. Ejemplos resueltos

**Ejemplo:** eslabón de $m=0.3$ kg con $\vec v_{cm}=(0.5,0,0)$ m/s, girando a $\omega=2$ rad/s alrededor de un eje principal con $I=0.004$ kg·m². $K=\tfrac12(0.3)(0.5)^2+\tfrac12(0.004)(2)^2=0.0375+0.008=0.0455$ J.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la energía potencial gravitatoria no depende de $x_{cm}$ ni de $y_{cm}$, solo de $z_{cm}$.

**Serie B — Cálculo a mano**
- B1. Calcular $K$ del eslabón del ejemplo si además $\omega$ se duplica a 4 rad/s (manteniendo $\vec v_{cm}$).

**Serie C — Laboratorio**
- C1. Verificar B1 en Python y graficar cómo crece $K$ con $\omega$ (debería ser una parábola: $K$ depende de $\omega^2$).

---

## Tema 6.6 — Fricción viscosa y fricción seca (Coulomb)

### 1. El problema

Hasta ahora el brazo se mueve sin resistencia. En la realidad, cada articulación tiene fricción en sus rodamientos y engranajes, que consume energía y que el Bloque 14 en adelante necesita incluir para que el modelo prediga los pares reales que hacen falta.

### 2. El mecanismo

Dos modelos de fricción cubren la mayoría de los casos del curso:

- **Fricción viscosa**: proporcional a la velocidad, $\tau_{fric}=-b\dot\theta$ (con $b\geq0$ el coeficiente de amortiguamiento viscoso) — la misma forma que el amortiguador del Bloque 05. Modela la resistencia de un fluido (aceite lubricante, aire) y **se anula en reposo**.
- **Fricción seca (Coulomb)**: de magnitud aproximadamente constante, en la dirección que se opone al movimiento, $\tau_{fric}=-\mu N\,\text{signo}(\dot\theta)$ (con $\mu$ el coeficiente de fricción y $N$ la fuerza normal). A diferencia de la viscosa, **no se anula en reposo**: hace falta superar un torque mínimo (fricción estática) para que la articulación empiece a moverse.

La función $\text{signo}(\dot\theta)$ introduce una discontinuidad en $\dot\theta=0$ que complica tanto la simulación numérica (Bloque 05: un paso de integración puede "saltar" sobre la discontinuidad) como el control (Bloque 18: es la causa de un fenómeno llamado *stick-slip*, donde la articulación se traba y suelta a saltos en vez de moverse suavemente).

### 3. En la vida real

```python
def friccion_viscosa(omega, b):
    return -b * omega

def friccion_coulomb(omega, mu_N, eps=1e-6):
    return -mu_N * np.sign(omega) if abs(omega) > eps else 0.0
```

### 4. Limitaciones

Estos son modelos simplificados; la fricción real depende también de la temperatura, el desgaste y la lubricación, y modelos más finos (Stribeck) combinan viscosa y seca con una zona de transición suave — fuera del alcance de este curso, pero mencionado en el Bloque 16 al dimensionar actuadores.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una simulación con fricción de Coulomb oscila rápidamente alrededor de $\dot\theta=0$ sin asentarse | La discontinuidad de $\text{signo}(\dot\theta)$ combinada con un paso de integración grande (Bloque 05, Tema 5.6) | Reducir el paso de integración cerca de $\dot\theta\approx0$, o suavizar $\text{signo}$ con una tangente hiperbólica de pendiente alta | Usar un paso más fino o un modelo suavizado de la fricción seca |

### 6. Dónde más aparece la idea

*Stick-slip* en cualquier mecanismo con fricción seca (por qué una puerta chirría a intervalos y no de forma continua), la resistencia del aire (viscosa a baja velocidad, cuadrática a alta velocidad), frenos de fricción.

### 7. Ejemplos resueltos

**Ejemplo:** articulación con $b=0.05$ N·m·s girando a $\dot\theta=3$ rad/s: $\tau_{fric}=-0.05\times3=-0.15$ N·m, oponiéndose al movimiento.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la fricción viscosa no puede, por sí sola, explicar que haga falta "un empujón" para empezar a mover un objeto en reposo, y qué modelo sí lo explica.

**Serie B — Cálculo a mano**
- B1. Para el péndulo del Bloque 05 (Tema 5.3) con fricción viscosa añadida, escribir la EDO completa $\ddot\theta+\dfrac{b}{mL^2}\dot\theta+\dfrac gL\sin\theta=0$ y su sistema de primer orden.

**Serie C — Laboratorio**
- C1. Simular B1 con `robotica.simular.rk4` para $b=0$ y $b>0$, y graficar $\theta(t)$ de ambos junto con la energía (Bloque 05, Tema 5.6): con fricción, la energía debe decrecer monótonamente en vez de mantenerse constante.

## Lo que este bloque agrega a `codigo/robotica/`

Nada todavía: los cálculos de este bloque se resuelven directamente con SymPy y NumPy en `codigo/bloque_06/`. La librería propia retoma su crecimiento en la Parte II, con `robotica/rotaciones.py` (Bloque 08).

## Glosario del bloque

| Término | Definición |
|---|---|
| Cuerpo rígido | Colección de partículas cuyas distancias mutuas no cambian al moverse. |
| Centro de masa | Punto que resume la posición de un cuerpo pesada por su masa; permite aplicar $F=ma$ al cuerpo completo. |
| Torque | $\vec\tau=\vec r\times\vec F$; produce cambios en el momento angular. |
| Momento angular | $\vec L=\vec r\times m\vec v$ (partícula) o $\vec L=I\vec\omega$ (cuerpo rígido). |
| Momento de inercia | Resistencia de un cuerpo a girar alrededor de un eje dado; $I=\int d^2\rho\,dV$. |
| Teorema de ejes paralelos (Steiner) | $I_{eje}=I_{cm}+md^2$: relaciona el momento de inercia respecto a un eje con el respecto a un eje paralelo por el centro de masa. |
| Tensor de inercia | Matriz $3\times3$ que generaliza el momento de inercia a rotaciones alrededor de cualquier eje en 3D. |
| Ejes principales de inercia | Direcciones (vectores propios del tensor de inercia) donde $\vec L\parallel\vec\omega$, sin tambaleo. |
| Fricción viscosa | Resistencia proporcional a la velocidad; se anula en reposo. |
| Fricción seca (Coulomb) | Resistencia de magnitud aproximadamente constante, opuesta al movimiento; no se anula en reposo (fricción estática). |
