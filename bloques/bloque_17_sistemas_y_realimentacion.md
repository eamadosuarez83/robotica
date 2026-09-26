# Bloque 17 — Sistemas y realimentación

> **Problema que abre el bloque:** se manda el ángulo exacto y el brazo no llega, porque el modelo nunca es perfecto y siempre hay perturbaciones. Hay que medir y corregir.
>
> **Necesitas antes:** Bloque 16 (cierra la Parte IV, abre la Parte V). · **Lectura:** Ogata, *Ingeniería de control moderna*, caps. 1–5; Åström & Murray, *Feedback Systems* (libre).

## Tema 17.1 — Lazo abierto y lazo cerrado

### 1. El problema

Los Bloques 14-16 calculan el par exacto que hace falta, *asumiendo* que el modelo (masas, longitudes, fricción) es perfecto. En la práctica nunca lo es: la masa real de un huevo varía, la fricción cambia con el desgaste, y el viento o un golpe accidental perturban al brazo. Mandar el par calculado y esperar que el brazo llegue exactamente donde se predijo —sin verificar nada— falla tarde o temprano.

### 2. El mecanismo

Un sistema en **lazo abierto** aplica una entrada calculada de antemano (el par de los Bloques 14-16) sin nunca mirar el resultado real — funciona solo si el modelo es perfecto y no hay perturbaciones, una condición que casi nunca se cumple del todo. Un sistema en **lazo cerrado** (o con **realimentación**, *feedback*) mide la salida real (con un sensor, Bloque 07 Tema 7.7), la compara contra lo deseado, y usa esa diferencia —el **error**— para corregir la entrada continuamente:

$$e(t) = \theta_{deseado}(t) - \theta_{medido}(t)$$

La idea central, que el resto de la Parte V desarrolla en detalle: **no hace falta un modelo perfecto si se corrige el error constantemente**. Un termostato no necesita saber exactamente cuánto calor pierde una habitación: mide la temperatura, compara contra la deseada, y enciende o apaga la calefacción según el signo del error — sin ningún modelo térmico explícito.

### 3. En la vida real

```python
error = theta_deseado - theta_medido
# el controlador (Bloque 18) decide la acción a partir de error, no de un cálculo ciego
```

### 4. Limitaciones

La realimentación no elimina la necesidad de un buen modelo (los Bloques 14-16 siguen siendo la base del control por par calculado, Bloque 20): lo que hace es tolerar los errores que **cualquier** modelo inevitablemente tiene.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un brazo en lazo abierto llega sistemáticamente a un punto distinto del pedido, y el error no se corrige solo con el tiempo | No hay realimentación: el sistema nunca compara lo que hizo contra lo que debía hacer | Verificar si existe una medición de la posición real que se compare contra la deseada | Cerrar el lazo: medir, comparar, corregir (Bloque 18) |

### 6. Dónde más aparece la idea

El termostato de una casa, la ducha (ajustar la llave según la temperatura sentida), el control de crucero de un automóvil, mantener el equilibrio al caminar (el oído interno y la vista realimentan constantemente la postura).

### 7. Ejemplos resueltos

**Ejemplo:** hornear un pastel siguiendo una receta al pie de la letra, sin abrir el horno a verificar, es lazo abierto; ajustar el tiempo de horneado según cómo se ve el pastel es lazo cerrado.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Dar dos ejemplos cotidianos de control en lazo abierto y dos en lazo cerrado, y explicar qué perturbación podría hacer fallar a cada uno en lazo abierto.

**Serie B — Cálculo a mano**
- B1. Ninguno: este tema es conceptual.

**Serie C — Laboratorio**
- C1. Nada nuevo todavía; se practica desde el Tema 17.4 en adelante.

---

## Tema 17.2 — La transformada de Laplace sin miedo

### 1. El problema

La dinámica de una articulación (Bloques 14-16) es una ecuación diferencial. Diseñar un controlador resolviendo EDO directamente, una y otra vez para cada candidato de controlador, es tedioso. Hace falta una herramienta que convierta el problema en álgebra.

### 2. El mecanismo

La **transformada de Laplace** de una función del tiempo $f(t)$ es

$$F(s) = \mathcal{L}\{f(t)\} = \int_0^\infty f(t)e^{-st}\,dt$$

con $s$ una variable compleja. No hace falta calcular esta integral a mano más que un par de veces para entender de dónde sale (está en cualquier tabla, como una tabla de integrales): lo que importa es su propiedad central, que convierte cálculo en álgebra:

$$\mathcal{L}\{\dot f(t)\} = sF(s) - f(0)$$

**Derivar en el tiempo se convierte en multiplicar por $s$** (con condiciones iniciales cero, el caso más común al analizar el comportamiento del sistema en sí). Una ecuación diferencial lineal, como $J\ddot\theta+b\dot\theta=\tau$ (Bloque 06), se convierte en una ecuación **algebraica**: $Js^2\Theta(s)+bs\Theta(s)=T(s)$, que se resuelve despejando $\Theta(s)$ como en cualquier ecuación de álgebra — sin integrar ni derivar nada más.

### 3. En la vida real

```python
import control
# python-control trabaja directamente con funciones de transferencia en s,
# sin pedir nunca la transformada explícita: el Tema 17.3 la usa así.
```

### 4. Limitaciones

La transformada de Laplace, tal como se usa aquí, solo aplica directamente a sistemas **lineales** (Bloque 03); la dinámica completa de un brazo (Bloque 14) es no lineal, y el control clásico de este bloque se aplica a una articulación **linealizada** cerca de un punto de operación (Bloque 04, Tema 4.5) — el Bloque 20 retoma el caso no lineal completo.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Se intenta aplicar directamente las herramientas de este bloque (función de transferencia) a la dinámica completa y no lineal del brazo (Bloque 14) | Confundir el alcance del control clásico (lineal) con el del control no lineal (Bloque 20) | Verificar si el sistema en cuestión es lineal o si se linealizó cerca de un punto de operación | Usar las herramientas de este bloque solo sobre modelos lineales o linealizados |

### 6. Dónde más aparece la idea

Cualquier análisis de circuitos eléctricos en corriente alterna, procesamiento de señales, la transformada de Fourier (un caso particular de Laplace con $s=j\omega$, en el eje imaginario).

### 7. Ejemplos resueltos

**Ejemplo:** $J\ddot\theta+b\dot\theta=\tau$, con condiciones iniciales cero: $\mathcal{L}\{\ddot\theta\}=s^2\Theta(s)$, $\mathcal{L}\{\dot\theta\}=s\Theta(s)$, así que $Js^2\Theta(s)+bs\Theta(s)=T(s)$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, en una frase, qué gana un ingeniero al poder tratar una ecuación diferencial como álgebra.

**Serie B — Cálculo a mano**
- B1. Aplicar la transformada de Laplace a $m\ddot x+kx=F$ (resorte sin amortiguar, Bloque 05) con condiciones iniciales cero.

**Serie C — Laboratorio**
- C1. Nada nuevo: se aplica directamente en el Tema 17.3.

---

## Tema 17.3 — Función de transferencia, polos y ceros

### 1. El problema

Con la ecuación ya en forma algebraica (Tema 17.2), hace falta una manera estándar de escribir "cómo responde este sistema a cualquier entrada" — sin tener que rehacer el álgebra cada vez.

### 2. El mecanismo

La **función de transferencia** es el cociente entre la salida y la entrada, en el dominio de Laplace, con condiciones iniciales cero:

$$G(s) = \frac{\Theta(s)}{T(s)}$$

Para la articulación del ejemplo del Tema 17.2: $G(s)=\dfrac{1}{Js^2+bs}=\dfrac{1/J}{s(s+b/J)}$. El **denominador** igualado a cero da los **polos** del sistema (aquí, $s=0$ y $s=-b/J$): determinan la forma cualitativa de la respuesta (Tema 17.5) y son, hasta una constante, las mismas raíces de la ecuación característica del Bloque 05 (Tema 5.4) — la transformada de Laplace no inventa un concepto nuevo, empaqueta el mismo análisis de otra forma. El **numerador** igualado a cero da los **ceros**, menos frecuentes en los modelos simples de este curso pero relevantes en sistemas más complejos.

Incluir el motor DC del Bloque 16 (constantes $K_t,K_e,R$) en vez de solo $J,b$: retomando la ecuación del Tema 16.1, la función de transferencia de voltaje a ángulo de una articulación es

$$G(s) = \frac{\Theta(s)}{V(s)} = \frac{K_t/R}{s\big(Js+b+K_tK_e/R\big)}$$

— el mismo tipo de expresión, con los parámetros del motor y del reductor (Bloque 16, Tema 16.2: $J$ y $b$ ya incluyen lo reflejado por el reductor) empaquetados dentro.

### 3. En la vida real

```python
import control
J, b, Kt, Ke, R = 0.02, 0.01, 0.05, 0.05, 2.0
num = [Kt / R]
den = [J, b + Kt * Ke / R, 0]   # s(Js + b_eff) = J s^2 + b_eff s
G = control.tf(num, den)
print(G.poles())
```

### 4. Limitaciones

Una función de transferencia describe la relación entre **una** entrada y **una** salida de un sistema lineal; sistemas con varias entradas/salidas (un brazo completo) necesitan una generalización matricial, fuera del alcance de este curso (se controla, en la Parte V, articulación por articulación o con las técnicas del Bloque 20).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Los polos calculados de $G(s)$ no coinciden con lo esperado físicamente | Error al pasar de la ecuación diferencial a los coeficientes del denominador (orden invertido, signo) | Verificar que el denominador, igualado a cero, reproduzca la ecuación diferencial original | Revisar el orden de los coeficientes de `den` (potencias de $s$ de mayor a menor) |

### 6. Dónde más aparece la idea

La función de transferencia es el lenguaje universal del control clásico: filtros electrónicos, sistemas de audio, cualquier análisis de "cómo responde esto a aquello".

### 7. Ejemplos resueltos

**Ejemplo:** con $J=0.02$ kg·m², $b=0.01$ N·m·s, $K_t=K_e=0.05$, $R=2\,\Omega$: $b_{eff}=0.01+0.05^2/2=0.01125$, polos en $s=0$ y $s=-0.01125/0.02=-0.5625$ (verificado en el laboratorio con `python-control`).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el polo en $s=0$ de $G(s)$ (un **integrador puro**) significa que, ante un voltaje constante, el ángulo crece sin límite en vez de estabilizarse (relevante para el Tema 17.4).

**Serie B — Cálculo a mano**
- B1. Calcular los polos de $G(s)=\dfrac{1}{s^2+5s+6}$ factorizando el denominador.

**Serie C — Laboratorio**
- C1. Verificar el ejemplo resuelto con `control.tf` y `.poles()`.

---

## Tema 17.4 — Respuesta al escalón

### 1. El problema

Los polos (Tema 17.3) determinan cualitativamente la respuesta, pero para especificar qué tan rápido y qué tan preciso debe ser un controlador hacen falta números concretos, medidos sobre una entrada de prueba estándar: un **escalón** (pedir, de golpe, un ángulo nuevo y constante).

### 2. El mecanismo

Cuatro métricas resumen la respuesta al escalón de cualquier sistema:

- **Tiempo de subida** ($t_r$): cuánto tarda en pasar del 10% al 90% (o de 0% a 100%, según convención) del valor final.
- **Sobrepaso** (*overshoot*, $M_p$): cuánto se pasa del valor final antes de asentarse, como porcentaje — directamente relacionado con qué tan poco amortiguado está el sistema (Bloque 05, Tema 5.4: el caso subamortiguado).
- **Tiempo de establecimiento** ($t_s$): cuánto tarda en quedarse dentro de una banda (típicamente ±2% o ±5%) alrededor del valor final, sin volver a salir.
- **Error en estado estacionario** ($e_{ss}$): la diferencia entre el valor final alcanzado y el deseado, después de que todo transitorio se apagó — para el sistema con un integrador puro del Tema 17.3 en **lazo cerrado**, este error tiende a cero ante un escalón (una de las razones por las que un integrador en el lazo, natural aquí porque el motor integra velocidad a posición, es tan valioso para el control, adelanto del PID del Bloque 18).

Estas cuatro métricas son, en la práctica, las especificaciones que un ingeniero de control recibe como requisito ("que llegue en menos de 0.5 s, con menos de 10% de sobrepaso") y que debe traducir en una elección de controlador (Bloque 18).

### 3. En la vida real

```python
import control
t, theta = control.step_response(G_lazo_cerrado)
info = control.step_info(G_lazo_cerrado)
print(info['RiseTime'], info['Overshoot'], info['SettlingTime'])
```

### 4. Limitaciones

Estas métricas se definen de forma más directa para sistemas de segundo orden (Bloque 05, Tema 5.4); para sistemas de orden superior siguen siendo útiles pero su relación con los parámetros del sistema (frecuencia natural, amortiguamiento) ya no es tan directa.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un sistema en lazo abierto (Tema 17.1) tiene un error en estado estacionario grande ante un escalón | Sin realimentación, cualquier error de modelo (fricción no modelada, por ejemplo) se traduce directamente en un offset permanente | Comparar la respuesta en lazo abierto contra la de lazo cerrado para el mismo escalón | Cerrar el lazo (Bloque 18): el error en estado estacionario se reduce o elimina según el tipo de controlador |

### 6. Dónde más aparece la idea

Evaluar cualquier sistema de control (climatización, suspensión de un vehículo, respuesta de un altavoz) con estas mismas cuatro métricas sobre una entrada escalón.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_17/modelo_articulacion.py`, que calcula estas cuatro métricas para la articulación del Tema 17.3 en lazo abierto y en lazo cerrado con realimentación proporcional simple (adelanto del Bloque 18).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el sobrepaso y el tiempo de subida suelen ser un compromiso: hacer el sistema más rápido (menor $t_r$) tiende a aumentar $M_p$.

**Serie B — Cálculo a mano**
- B1. Para un sistema de segundo orden subamortiguado (Bloque 05, Tema 5.4) con $\alpha=1,\omega_d=3$ rad/s, estimar cualitativamente si el sobrepaso será grande o pequeño (pista: comparar $\alpha$ con $\omega_d$).

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_17/modelo_articulacion.py` y leer las cuatro métricas de `control.step_info` para el caso en lazo cerrado.

---

## Tema 17.5 — Estabilidad: la ubicación de los polos

### 1. El problema

Antes de medir tiempos de subida o sobrepaso, hay una pregunta más básica: ¿el sistema siquiera se asienta en algún valor, o crece sin límite? Hace falta un criterio rápido, sin simular nada, para saberlo con solo mirar la función de transferencia.

### 2. El mecanismo

Cada polo $s=\sigma+j\omega_d$ de $G(s)$ contribuye a la respuesta en el tiempo con un término proporcional a $e^{\sigma t}$ (multiplicado por un seno/coseno si $\omega_d\neq0$, exactamente la forma subamortiguada del Bloque 05, Tema 5.4, ahora vista como "la parte real del polo es la tasa de decaimiento"). La regla de estabilidad es directa:

- **Todos los polos con parte real negativa** ($\sigma<0$, en el semiplano izquierdo del plano complejo $s$): cada término decae con el tiempo, el sistema es **estable**.
- **Algún polo con parte real positiva** ($\sigma>0$): ese término crece sin límite, el sistema es **inestable**.
- **Algún polo en el eje imaginario** ($\sigma=0$, sin amortiguamiento): el sistema oscila sin decaer ni crecer (el caso límite, marginalmente estable) — el polo en $s=0$ del Tema 17.3 es exactamente este caso: por eso un motor en lazo abierto, ante un voltaje constante, no se "estabiliza" en ningún ángulo, sino que gira indefinidamente.

Esta es la misma lectura de los valores propios de una matriz (Bloque 03, Tema 3.7) aplicada a los polos de $G(s)$ — no es casualidad: los polos de la función de transferencia de un sistema en espacio de estados (Bloque 15, Tema 15.4) son exactamente los valores propios de su matriz de dinámica.

### 3. En la vida real

```python
import numpy as np
polos = G.poles()
estable = np.all(polos.real < 0)
```

### 4. Limitaciones

Este criterio aplica a sistemas **lineales**; para sistemas no lineales (el brazo completo, Bloque 14) la noción de estabilidad es más sutil (estabilidad de Lyapunov, fuera del alcance de este curso salvo mención).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un sistema que "debería" ser estable según la intuición física resulta con un polo de parte real positiva | Error en la deducción de $G(s)$ (signo de algún término, Tema 17.2-17.3), o el sistema realimentado (Bloque 18) realmente es inestable con esa ganancia | Recalcular $G(s)$ desde la ecuación diferencial original y verificar cada signo | Revisar la deducción; si es realimentación, reducir la ganancia del controlador (Bloque 18) |

### 6. Dónde más aparece la idea

Análisis de estabilidad de cualquier sistema dinámico: circuitos con realimentación (osciladores, si se diseñan polos en el eje imaginario a propósito), estabilidad de un avión, un edificio ante un sismo.

### 7. Ejemplos resueltos

**Ejemplo:** el motor en lazo abierto del Tema 17.3 tiene polos en $s=0$ y $s=-0.5625$: marginalmente estable (no crece sin límite, pero tampoco se asienta en un ángulo fijo ante un voltaje constante — gira indefinidamente a velocidad constante, consistente con que integra voltaje a posición a través de un polo en el origen).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un polo en el semiplano derecho ($\sigma>0$) es catastrófico para un sistema real, aunque $\sigma$ sea un número pequeño.

**Serie B — Cálculo a mano**
- B1. Clasificar como estable, inestable o marginalmente estable un sistema con polos en (a) $-2,-3$; (b) $1,-5$; (c) $\pm3j$.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_17/romper_retardo.py`: agrega un retardo de transporte al lazo cerrado del Tema 17.4 (aproximado con un polo adicional, la aproximación de Padé) y aumenta el retardo hasta que un sistema antes estable empiece a oscilar sin decaer.

---

## Tema 17.6 — Diagramas de bloques

### 1. El problema

Un sistema de control real combina varios elementos (planta, sensor, controlador, referencia) conectados de formas específicas (realimentación negativa, suma de señales). Hace falta una notación gráfica estándar para representarlos sin ambigüedad, y reglas para simplificarlos a una sola función de transferencia.

### 2. El mecanismo

Un **diagrama de bloques** representa cada elemento como una caja con su función de transferencia, conectada por flechas que llevan una señal (en el dominio de Laplace) de un bloque a otro, con **sumadores** (círculos con $+/-$) donde se combinan señales — típicamente, el error $E(s)=R(s)-Y(s)$ (referencia menos salida medida, Tema 17.1). La configuración estándar de **realimentación negativa unitaria** con controlador $C(s)$ y planta $G(s)$ se reduce, por álgebra de bloques, a una única función de transferencia de lazo cerrado:

$$\frac{Y(s)}{R(s)} = \frac{C(s)G(s)}{1+C(s)G(s)}$$

— la fórmula que el Bloque 18 usa constantemente para analizar el efecto de cada controlador candidato, sin tener que resolver el diagrama completo cada vez.

### 3. En la vida real

```python
import control
G = control.tf([Kt/R], [J, b_eff, 0])
C = control.tf([Kp], [1])              # controlador proporcional (adelanto del Bloque 18)
lazo_cerrado = control.feedback(C * G, 1)   # realimentación negativa unitaria
```

### 4. Limitaciones

La fórmula de realimentación negativa unitaria de la sección 2 es el caso más común de este curso; lazos con sensores no ideales (realimentación no unitaria) o con perturbaciones externas explícitas tienen una fórmula ligeramente distinta, disponible en cualquier texto de control (Ogata).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El lazo cerrado calculado con `control.feedback` no coincide con lo esperado | Se usó realimentación positiva por error (signo), o se olvidó que `feedback` espera la ganancia de lazo directo $C(s)G(s)$, no cada uno por separado sin combinar | Verificar el signo del argumento de `feedback` (por defecto, negativa) | Revisar la documentación de `control.feedback` y el signo de la realimentación |

### 6. Dónde más aparece la idea

Cualquier diagrama de flujo de señal en ingeniería (circuitos, procesamiento de señales); los diagramas de bloques de Simulink son, esencialmente, esta misma notación hecha interactiva.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_17/modelo_articulacion.py`, que arma el diagrama de bloques planta+controlador proporcional con `control.feedback` y compara la respuesta al escalón resultante contra la planta sola (lazo abierto).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, cuando $C(s)G(s)$ es muy grande (ganancia de lazo alta), $Y(s)/R(s)\to1$: la salida sigue casi exactamente a la referencia.

**Serie B — Cálculo a mano**
- B1. Con $G(s)=1/(s+2)$ y $C(s)=10$ (controlador proporcional puro), calcular $Y(s)/R(s)$ y sus polos.

**Serie C — Laboratorio**
- C1. Verificar B1 con `control.feedback` y graficar la respuesta al escalón.

## Lo que este bloque agrega a `codigo/robotica/`

Nada nuevo: este bloque introduce `python-control` como herramienta externa (FILOSOFIA.md: la librería profesional del área), sin agregar funciones propias — la Parte V trabaja principalmente con esa librería en vez de código propio.

## Glosario del bloque

| Término | Definición |
|---|---|
| Lazo abierto / lazo cerrado | Sin medir el resultado real (abierto) o midiéndolo y corrigiendo según el error (cerrado, con realimentación). |
| Transformada de Laplace | Herramienta que convierte una ecuación diferencial lineal en una ecuación algebraica en la variable compleja $s$. |
| Función de transferencia $G(s)$ | Cociente salida/entrada en el dominio de Laplace, con condiciones iniciales cero. |
| Polos / ceros | Raíces del denominador / numerador de $G(s)$; los polos determinan la forma cualitativa de la respuesta y la estabilidad. |
| Tiempo de subida, sobrepaso, tiempo de establecimiento, error en estado estacionario | Las cuatro métricas estándar de la respuesta al escalón. |
| Estabilidad (polos) | Un sistema lineal es estable si todos sus polos tienen parte real negativa. |
| Diagrama de bloques | Representación gráfica de un sistema de control como bloques (funciones de transferencia) y sumadores conectados. |
