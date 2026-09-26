# Bloque 18 — Control PID de una articulación

> **Problema que abre el bloque:** un controlador proporcional deja al brazo colgando un poco por debajo, y si se sube la ganancia empieza a vibrar.
>
> **Necesitas antes:** Bloque 17 (función de transferencia, polos, respuesta al escalón, realimentación); Bloque 16 (motor DC y reductor); Bloque 05 (RK4, segundo orden). · **Lectura:** Barrientos, cap. 7 (control monoarticular); Åström & Murray, *Feedback Systems*, capítulo de control PID (libre).

Todo el bloque trabaja sobre **una sola articulación**, la misma del Bloque 17 (motor DC + reductor + eslabón), a la que ahora se le agrega la gravedad:

$$J\ddot\theta + b_{eff}\dot\theta = K\,u - \tau_g\cos\theta$$

| Símbolo | Significado | Valor | Unidades |
|---|---|---|---|
| $\theta$ | ángulo del eslabón, medido desde la horizontal | — | rad |
| $u$ | voltaje que el *driver* aplica al motor, limitado a $\pm12$ V | — | V |
| $J$ | inercia total (motor + reductor + eslabón, Bloque 16) | 0.02 | kg·m² |
| $b_{eff}$ | fricción viscosa más la fuerza contraelectromotriz, $b+K_tK_e/R$ (Bloque 17) | 0.01125 | N·m·s |
| $K$ | par por voltio a velocidad cero, $K_t/R$ | 0.025 | N·m/V |
| $\tau_g$ | par de gravedad con el eslabón horizontal, visto desde el motor | 0.1 | N·m |

Sostener el eslabón horizontal ($\theta=0$) exige $u=\tau_g/K=4$ V. Los scripts del bloque importan este modelo de `codigo/bloque_18/articulacion.py`, así que todos hablan de la misma articulación.

---

## Tema 18.1 — Acción proporcional, integral y derivativa

### 1. El problema

El Bloque 17 cerró el lazo con la idea más simple posible: aplicar un voltaje proporcional al error, $u=k_p e$. Con la articulación horizontal y una referencia de 0.5 rad, `codigo/bloque_18/p_pi_pd_pid.py` muestra dos cosas que ningún ajuste de $k_p$ arregla a la vez:

- con $k_p=20$ V/rad, el eslabón **se queda 0.19 rad (11°) por debajo** de la referencia, para siempre;
- con $k_p=80$ V/rad cuelga menos (0.045 rad), pero **se pasa 45 %** y oscila durante segundos.

Hace falta entender *por qué* cada cosa pasa, para saber qué agregarle al controlador.

### 2. El mecanismo

**Por qué cuelga el control P.** Cuando el eslabón queda quieto, $\dot\theta=\ddot\theta=0$ y la ecuación de la articulación se reduce a un equilibrio de pares:

$$0 = K\,u - \tau_g\cos\theta = K\,k_p\,e - \tau_g\cos\theta$$

Despejando el error:

$$e = \frac{\tau_g\cos\theta}{K\,k_p}$$

El control P **necesita** un error distinto de cero para producir voltaje: si $e=0$, entonces $u=0$ y nada sostiene el eslabón contra la gravedad. El eslabón baja justo lo necesario para que el error genere el voltaje que la gravedad pide. Con $k_p=20$: $e=0.1\cos\theta/(0.025\cdot20)=0.2\cos\theta$. Como $\theta=0.5-e$, se resuelve iterando: $e\approx0.19$ rad. Subir $k_p$ achica ese error, pero nunca lo anula.

**Por qué vibra el control P.** Sin gravedad (se estudia la forma de la respuesta, no dónde se queda), el lazo cerrado con P tiene la ecuación característica (Bloque 17, Tema 17.6):

$$J s^2 + b_{eff}s + K k_p = 0 \quad\Longrightarrow\quad s = -\frac{b_{eff}}{2J} \pm j\sqrt{\frac{K k_p}{J} - \left(\frac{b_{eff}}{2J}\right)^2}$$

La **parte real** de los polos, que dice qué tan rápido se apaga la oscilación (Bloque 17, Tema 17.5), es $-b_{eff}/(2J)=-0.281$ s⁻¹, y **no depende de $k_p$**. Subir $k_p$ solo sube la frecuencia de la oscilación, sin amortiguarla más. El factor de amortiguamiento $\zeta=b_{eff}/(2\sqrt{JKk_p})$ baja como $1/\sqrt{k_p}$: 0.11 con $k_p=5$, 0.056 con $k_p=20$, 0.028 con $k_p=80$. Esta articulación tiene muy poca fricción propia, y el P no le agrega ninguna.

De ahí salen las otras dos acciones, cada una para un problema:

- **Acción integral** $k_i\int_0^t e\,dt$: acumula el error pasado. Mientras quede error, la integral sigue creciendo y empuja cada vez más fuerte. Solo deja de crecer cuando $e=0$. Así el controlador puede entregar los 4 V que pide la gravedad **con error cero**: los guarda la integral, no el término proporcional. Analogía: quien sostiene una caja y la siente bajar aprieta un poco más, y sigue apretando mientras la caja no deje de bajar. Dónde falla: la integral no "sabe" que está compensando la gravedad; si el actuador no puede dar lo que ella pide, igual sigue acumulando (Tema 18.4).
- **Acción derivativa** $k_d\,\dot e$: reacciona a la *velocidad* con que cambia el error. Si el eslabón se acerca rápido a la referencia, $\dot e$ es grande y negativo y la acción derivativa frena antes de llegar. En la ecuación característica se suma a $b_{eff}$: es **fricción artificial**, amortiguamiento que el motor fabrica. Dónde falla: la derivada del ruido del sensor es enorme (Tema 18.5).

El controlador completo, **PID** (proporcional-integral-derivativo), en el tiempo y en Laplace:

$$u(t) = k_p e(t) + k_i\int_0^t e(\tau)\,d\tau + k_d\,\dot e(t) \qquad\Longleftrightarrow\qquad C(s) = k_p + \frac{k_i}{s} + k_d s = \frac{k_d s^2 + k_p s + k_i}{s}$$

A veces se escribe con el **tiempo integral** $T_i=k_p/k_i$ y el **tiempo derivativo** $T_d=k_d/k_p$: $C(s)=k_p\left(1+\frac{1}{T_i s}+T_d s\right)$. Es la forma que usa Ziegler-Nichols (Tema 18.3).

**Qué rompe cada una.** Cerrando el lazo con $C(s)$ sobre $G(s)=K/(s(Js+b_{eff}))$, el denominador de $C G/(1+C G)$ es

$$J s^3 + (b_{eff} + K k_d)s^2 + K k_p s + K k_i = 0$$

- Sin $k_i$ (PD) el término independiente desaparece y queda de segundo orden: $k_d$ suma amortiguamiento y $k_p$ fija la frecuencia. Estable para cualquier $k_p,k_d>0$, pero con error ante la gravedad.
- Sin $k_d$ (PI) es de tercer orden. Un polinomio $a_3s^3+a_2s^2+a_1s+a_0$ con todos sus coeficientes positivos tiene todas sus raíces en el semiplano izquierdo **solo si** $a_2a_1>a_3a_0$ (criterio de Routh-Hurwitz para tercer orden, Ogata cap. 5). Con las ganancias del ejemplo, $a_2a_1=0.01125\cdot0.832=0.0094$ contra $a_3a_0=0.02\cdot1.28=0.0256$: **el PI es inestable** en esta articulación. La integral agrega retardo al lazo, y sin la fricción artificial de la derivada no hay con qué absorberlo.

### 3. En la vida real

```python
from robotica.control import PID, simular_lazo
pid = PID(kp=33.28, ki=51.2, kd=7.87, ts=0.001, u_min=-12, u_max=12)
u = pid.paso(referencia=0.5, medicion=theta_medido)   # una vez por periodo de muestreo
```

`codigo/bloque_18/p_pi_pd_pid.py` corre los cinco casos (P bajo, P alto, PI, PD, PID) durante 20 s e imprime:

```
control          kp      ki     kd  error medio  oscilación  sobrepaso  |u| máx
                                  (últimos 2 s) pico a pico
P  (kp=20)    20.00    0.00   0.00       0.1908      0.0039      14.7%    10.00
P  (kp=80)    80.00    0.00   0.00       0.0448      0.0058      45.5%    12.00
PI            33.28   51.20   0.00       0.2355      0.9352      55.7%    12.00
PD            12.80    0.00   4.67       0.3067      0.0000       0.0%     6.40
PID           33.28   51.20   7.87      -0.0000      0.0000      14.1%    12.00
```

Cómo leerla: el error del P coincide con la fórmula a mano (0.1908 contra 0.1905; 0.0448 contra 0.0449). El PI oscila 0.94 rad pico a pico sin detenerse: la saturación a 12 V evita que crezca sin límite y lo deja en un **ciclo límite**. El PD no oscila pero cuelga más que el P de $k_p=20$, porque su $k_p$ es menor (12.8): la derivada no ayuda con el error estacionario. Solo el PID llega sin error.

### 4. Limitaciones

- El análisis de polos es **lineal**: se hizo sin la gravedad y sin la saturación. La gravedad desplaza el equilibrio pero, cerca de él, no cambia la forma de la respuesta. La saturación sí la cambia, y mucho (Tema 18.4).
- La "derivada" del mundo real nunca es la derivada ideal $k_d s$: siempre va filtrada (Tema 18.5), y ese filtro es un poco de retardo que el análisis de esta sección no incluye.
- Un PID corrige **después** de que aparece el error. Si se conoce la perturbación (la gravedad es calculable con el modelo del Bloque 14), es mejor compensarla antes: es la idea del Bloque 20.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El eslabón se queda quieto, pero siempre un poco por debajo, y más cuanto más horizontal está | Control P o PD: sin integral, el error es lo único que produce voltaje contra la gravedad | El error final cumple $e\approx\tau_g\cos\theta/(Kk_p)$: es máximo horizontal y casi cero vertical | Agregar acción integral (o compensar la gravedad, Bloque 20) |
| Al subir $k_p$ para reducir ese error, el eslabón vibra más y tarda más en quedarse quieto | La parte real de los polos del P es $-b/(2J)$, fija; subir $k_p$ solo sube la frecuencia | Medir el decaimiento entre picos: no mejora al subir $k_p$ | Agregar acción derivativa: es la única que agrega amortiguamiento |
| Al agregar integral a un P que "funcionaba", aparece una oscilación que no se apaga | PI sobre una planta con poco amortiguamiento: no cumple $a_2a_1>a_3a_0$ | Calcular Routh con $J$, $b$, $K$, $k_p$, $k_i$ | Agregar $k_d$, o bajar $k_i$ hasta cumplir la condición |

### 6. Dónde más aparece la idea

El control de crucero de un auto (la integral compensa la pendiente de la carretera, que para el lazo es lo mismo que la gravedad para el eslabón); el horno de reflujo de una fábrica de circuitos; el piloto automático de un dron que se mantiene quieto contra el viento; los controladores de temperatura de laboratorio, que se venden como "controlador PID" con tres perillas.

### 7. Ejemplos resueltos

**Ejemplo 1 — Error del P ante la gravedad, a mano.** Con $k_p=80$ y referencia 0.5 rad: $e=0.1\cos\theta/(0.025\cdot80)=0.05\cos\theta$. Primer intento con $\theta\approx0.5$: $e=0.05\cdot0.878=0.0439$. Segundo intento con $\theta=0.5-0.0439=0.456$: $e=0.05\cdot0.898=0.0449$. Tercer intento: sin cambio. Error: **0.045 rad (2.6°)**. La simulación da 0.0448.

**Ejemplo 2 — Qué guarda la integral.** Con el PID quieto en $\theta=0.5$ rad, el error es cero, así que el término P es cero, y la velocidad es cero, así que el término D es cero. Todo el voltaje lo pone la integral: $u=\tau_g\cos(0.5)/K=0.1\cdot0.878/0.025=3.51$ V. La integral terminó valiendo exactamente la **estimación de la gravedad** en esa postura, aunque nadie le dio el modelo.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar con palabras propias por qué un control P puro necesita error para sostener una carga, y por qué el PID no.
- A2. Con el eslabón **vertical** hacia arriba ($\theta=\pi/2$), ¿cuánto cuelga el P? ¿Por qué?
- A3. Predecir, antes de simular, qué pasa con el error del P si la articulación carga un huevo en la punta (sube $\tau_g$).

**Serie B — Cálculo a mano**
- B1. Calcular el error final del P con $k_p=40$ y referencia 0 rad (horizontal).
- B2. Para el lazo P, calcular $\omega_n=\sqrt{Kk_p/J}$ y $\zeta$ con $k_p=20$ y $k_p=80$, y comprobar que $\zeta\omega_n$ es igual en los dos casos.
- B3. Aplicar la condición de Routh a un PI con $k_p=33.28$ y encontrar el $k_i$ máximo que lo deja estable.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_18/p_pi_pd_pid.py` y comparar la tabla con los ejemplos resueltos.
- C2. Con el resultado de B3, correr el PI con un $k_i$ un 20 % por debajo y un 20 % por encima del límite.

---

## Tema 18.2 — Control monoarticular: cada motor con su lazo

### 1. El problema

Un brazo de 4 GDL tiene cuatro motores, y la dinámica del Bloque 14 dice que están **acoplados**: el par que necesita el hombro depende de dónde está y de cuán rápido se mueve el codo ($\boldsymbol{M}(\vec q)$, términos de Coriolis y gravedad). Diseñar un controlador para las cuatro articulaciones a la vez, con esas ecuaciones no lineales, es difícil. ¿Se puede tratar cada motor por separado?

### 2. El mecanismo

El **control monoarticular** (o **descentralizado**) le da a cada articulación su propio PID, que solo mira su propio ángulo. Todo lo que no es "esta articulación sola" se trata como **perturbación**: un par externo desconocido que el lazo tiene que rechazar, igual que la gravedad del Tema 18.1.

Escribiendo la ecuación de la articulación $i$ desde el lado del motor, con un reductor de relación $N$ (Bloque 16, Tema 16.2), la inercia de la carga llega dividida entre $N^2$:

$$\left(J_m + \frac{M_{ii}(\vec q)}{N^2}\right)\ddot\theta_m + b_m\dot\theta_m = K u_i - \frac{1}{N}\,d_i(\vec q,\dot{\vec q},\ddot{\vec q})$$

donde $J_m$ es la inercia del rotor del motor [kg·m²], $M_{ii}(\vec q)$ el elemento diagonal de la matriz de masas del Bloque 14 (la inercia que "ve" la articulación $i$, que cambia con la postura), $\theta_m=N\theta_i$ el ángulo del motor, y $d_i$ todo lo demás: gravedad, Coriolis, y el efecto de las aceleraciones de las otras articulaciones. Dos consecuencias:

1. Con $N$ grande, $M_{ii}/N^2$ se vuelve pequeño frente a $J_m$: la inercia que ve el motor **casi no cambia con la postura**, y un PID sintonizado para una inercia fija sirve en todo el espacio de trabajo.
2. La perturbación $d_i$ llega dividida entre $N$: el reductor la atenúa, y lo que queda (sobre todo la gravedad, que es casi constante en movimientos lentos) lo absorbe la integral.

Por eso el control monoarticular funciona tan bien en brazos industriales con reductores de $N=100$ o más, y es el punto de partida del Barrientos (cap. 7). Por eso también empieza a fallar en brazos de transmisión directa, o cuando se mueven rápido (Bloque 20).

### 3. En la vida real

```python
pids = [PID(kp, ki, kd, ts=0.001, u_min=-12, u_max=12) for _ in range(4)]
u = [pid.paso(q_ref[i], q_medido[i]) for i, pid in enumerate(pids)]
```

Cuatro objetos independientes, uno por motor; ninguno lee el ángulo de los otros. En el brazo real, cada uno puede incluso correr en un microcontrolador distinto (Tema 18.6).

### 4. Limitaciones

La perturbación $d_i$ **no es realmente independiente**: depende de las velocidades y aceleraciones de las otras articulaciones. En movimientos lentos es casi constante (gravedad) y la integral la absorbe. En movimientos rápidos cambia más deprisa de lo que la integral alcanza a seguir, y aparecen errores de seguimiento que ningún ajuste de ganancias elimina. Es el problema que abre el Bloque 20.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un PID que funcionaba bien con el brazo recogido oscila con el brazo extendido | Reductor pequeño (o transmisión directa): $M_{ii}(\vec q)/N^2$ cambia mucho con la postura y el lazo queda sintonizado para otra inercia | Calcular $J_m+M_{ii}/N^2$ en ambas posturas con la matriz de masas (Bloque 14) | Sintonizar para la inercia máxima, o usar ganancias por postura (*gain scheduling*), o el Bloque 20 |
| El hombro se desvía cada vez que el codo acelera | El acoplamiento dinámico ($d_i$) llega como perturbación rápida | Registrar el error del hombro junto con la aceleración del codo | Movimientos más suaves (Bloque 19) o prealimentación del modelo (Bloque 20) |

### 6. Dónde más aparece la idea

Un edificio con un termostato por habitación: el calor que pasa por las paredes desde la habitación vecina es la perturbación de cada lazo. El tráfico de una ciudad con semáforos independientes por cruce. Cualquier sistema grande que se controla por partes, aceptando que las partes se molestan entre sí.

### 7. Ejemplos resueltos

**Ejemplo — Cuánto cambia la inercia que ve el motor.** El hombro de un brazo tiene $M_{11}$ entre 0.05 kg·m² (recogido) y 0.2 kg·m² (extendido), y un motor con $J_m=2\times10^{-5}$ kg·m².
- Sin reductor ($N=1$): la inercia cambia de 0.05 a 0.2, un factor 4.
- Con $N=100$: $M_{11}/N^2$ va de $5\times10^{-6}$ a $2\times10^{-5}$; sumado al rotor, de $2.5\times10^{-5}$ a $4\times10^{-5}$, un factor **1.6**.

El mismo PID sirve razonablemente en todo el rango.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el reductor, que el Bloque 16 presentó como "multiplicador de par", también es un aliado del control.
- A2. ¿Qué pierde un brazo de transmisión directa (sin reductor) en términos de control, y qué gana (juego mecánico, Bloque 16)?

**Serie B — Cálculo a mano**
- B1. Repetir el ejemplo con $N=30$ y $N=300$ y graficar a mano el factor de cambio de inercia contra $N$.

**Serie C — Laboratorio**
- C1. Con la matriz de masas del 2R (`robotica.dinamica`, Bloque 14), calcular $M_{11}$ del hombro con el codo en 0 y en $\pi/2$, y repetir el ejemplo con esos valores.

---

## Tema 18.3 — Sintonía: a mano, Ziegler-Nichols, ubicación de polos

### 1. El problema

El PID tiene tres perillas. Probar combinaciones al azar sobre el brazo real es lento y peligroso: una mala combinación lo hace oscilar contra sus topes. Hacen falta métodos para elegir $k_p$, $k_i$ y $k_d$.

### 2. El mecanismo

**A mano (sintonía empírica).** Con el brazo real, en este orden:

1. $k_i=k_d=0$. Subir $k_p$ hasta que la respuesta sea rápida y con poca oscilación.
2. Subir $k_d$ hasta que la oscilación desaparezca. Si el motor empieza a zumbar, $k_d$ amplifica ruido: bajarlo o filtrar (Tema 18.5).
3. Subir $k_i$ hasta que el error final desaparezca en un tiempo aceptable. Si vuelve la oscilación lenta, se pasó.

Funciona y es lo que se hace en campo. Lo malo es que no dice cuándo detenerse ni si existe algo mejor.

**Ziegler-Nichols en lazo cerrado.** Dos ingenieros de Taylor Instruments lo publicaron en 1942 para plantas sin modelo:

1. Con solo P, subir $k_p$ hasta que el lazo **oscile con amplitud constante**, sin crecer ni decaer. Esa es la **ganancia última** $k_u$, y el periodo de la oscilación es el **periodo último** $T_u$.
2. Aplicar la tabla: $k_p=0.6k_u$, $T_i=T_u/2$, $T_d=T_u/8$. En ganancias: $k_i=k_p/T_i$, $k_d=k_pT_d$.

La tabla apunta a una respuesta rápida con un sobrepaso considerable (un decaimiento de un cuarto entre picos sucesivos). Es un **punto de partida** que después se retoca a mano.

Hay un detalle que el modelo ideal esconde. El lazo P de esta articulación **nunca** oscila con amplitud constante (Tema 18.1: sus polos tienen parte real $-0.281$ para cualquier $k_p$). Ziegler-Nichols funciona en la articulación real porque la real tiene **retardo**: filtro del sensor, tiempo de cálculo, comunicación (Bloque 17, Tema 17.5). Aquí se modela un retardo $L=20$ ms, y `codigo/bloque_18/sintonia.py` encuentra con python-control $k_u=22.54$ V/rad y $T_u=1.187$ s. Simulando con $k_p=k_u$, la oscilación mide el mismo periodo y crece apenas 0.8 % por ciclo.

**Ubicación de polos.** Si se conocen $J$, $b_{eff}$ y $K$, se elige *dónde* se quieren los polos del lazo cerrado y se despejan las ganancias. El denominador del lazo cerrado (Tema 18.1), dividido entre $J$:

$$s^3 + \frac{b_{eff}+Kk_d}{J}s^2 + \frac{Kk_p}{J}s + \frac{Kk_i}{J}$$

Se elige un par de polos dominantes con frecuencia natural $\omega_n$ y amortiguamiento $\zeta$ (Bloque 05, Tema 5.4), más un tercer polo real en $-p$:

$$(s^2 + 2\zeta\omega_n s + \omega_n^2)(s+p) = s^3 + (2\zeta\omega_n+p)s^2 + (\omega_n^2+2\zeta\omega_n p)s + \omega_n^2 p$$

Igualando coeficiente por coeficiente y despejando cada ganancia:

$$k_d = \frac{J(2\zeta\omega_n+p) - b_{eff}}{K},\qquad k_p = \frac{J(\omega_n^2+2\zeta\omega_n p)}{K},\qquad k_i = \frac{J\omega_n^2p}{K}$$

Esto es lo que calcula `robotica.control.pid_por_polos` (y `pd_por_polos`, el caso de segundo orden sin integral).

**La trampa: los ceros.** La ubicación de polos fija el denominador, pero el PI también pone un **cero** en el numerador, en $s=-k_i/k_p$. Si ese cero es más lento que los polos, produce sobrepaso aunque los polos tengan $\zeta=0.8$. El remedio estándar es **filtrar la referencia** con $1/((k_p/k_i)s+1)$ antes de restarla: ese polo cancela el cero y no toca la respuesta a perturbaciones.

### 3. En la vida real

```python
from robotica.control import ziegler_nichols, pid_por_polos
kp, ki, kd = ziegler_nichols(ku=22.54, tu=1.187)
kp, ki, kd = pid_por_polos(J=0.02, b=0.01125, K=0.025, wn=4.0, zeta=0.8, p=4.0)
```

`codigo/bloque_18/sintonia.py`, escalón de 0.2 rad desde el eslabón sostenido horizontal, con gravedad y 20 ms de retardo:

```
sintonía                  kp      ki     kd  sobrepaso  t_est 2%  |u| máx
Ziegler-Nichols        13.53   22.79   2.01      87.0%     9.29s     6.81
polos ωn=4, ζ=0.8      33.28   51.20   7.87      30.7%     1.69s    10.88
polos + filtro de r    33.28   51.20   7.87       0.7%     1.39s     4.80
```

### 4. Limitaciones

- Ziegler-Nichols fue calibrado para plantas de procesos industriales (lentas, con retardo). En una articulación con tan poca fricción propia da un sobrepaso enorme. Es un punto de partida, no un resultado.
- Llevar el brazo real a oscilar con amplitud constante puede ser peligroso: se hace con poco rango de movimiento y la mano en la parada de emergencia (Bloque 22).
- La ubicación de polos es tan buena como el modelo. Si $J$ está mal (el huevo, una pieza más pesada), los polos reales no son los pedidos. El Bloque 20 estudia qué tan grave es.
- Polos más rápidos piden más voltaje. Pedir $\omega_n=10$ rad/s con esta articulación satura el driver en cualquier escalón razonable, y la respuesta ya no es la diseñada (Tema 18.4).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Se buscó $k_u$ en simulación y el lazo nunca oscila con amplitud constante, por mucho que se suba $k_p$ | El modelo no tiene retardo: un segundo orden con P no se desestabiliza nunca | Revisar si el modelo incluye el retardo del sensor y del cálculo | Agregar el retardo real al modelo, o sintonizar por polos |
| Polos ubicados con $\zeta=0.8$ y aun así 30 % de sobrepaso | El cero del PI en $-k_i/k_p$ es más lento que los polos | Calcular $-k_i/k_p$ y compararlo con $\zeta\omega_n$ | Filtrar la referencia, o elegir $p$ y $\omega_n$ que alejen el cero |
| Las ganancias por polos dan $k_d<0$ | Se pidió menos amortiguamiento del que la planta ya tiene: $J(2\zeta\omega_n+p)<b_{eff}$ | Revisar la fórmula de $k_d$ | Pedir polos más rápidos o más amortiguados |

### 6. Dónde más aparece la idea

Los controladores de temperatura industriales traen "autosintonía" (*autotune*): inducen una oscilación pequeña con un relé y aplican una variante de Ziegler-Nichols, el método del relé de Åström-Hägglund. La ubicación de polos es la base del control por espacio de estados, en satélites y en la suspensión activa de un auto.

### 7. Ejemplos resueltos

**Ejemplo 1 — Ubicación de polos a mano.** $\omega_n=4$ rad/s, $\zeta=0.8$, $p=4$ s⁻¹.
- Coeficientes deseados: $2\zeta\omega_n+p=6.4+4=10.4$; $\omega_n^2+2\zeta\omega_np=16+25.6=41.6$; $\omega_n^2p=64$.
- $k_d=(0.02\cdot10.4-0.01125)/0.025=(0.208-0.01125)/0.025=7.87$ V·s/rad.
- $k_p=0.02\cdot41.6/0.025=33.28$ V/rad.
- $k_i=0.02\cdot64/0.025=51.2$ V/(rad·s).

Verificado con `control.feedback`: los polos del lazo cerrado quedan en $-4$ y $-3.2\pm2.4j$, exactamente $-\zeta\omega_n\pm j\omega_n\sqrt{1-\zeta^2}$.

**Ejemplo 2 — Ziegler-Nichols a mano.** Con $k_u=22.54$ y $T_u=1.187$ s:
- $k_p=0.6\cdot22.54=13.52$.
- $T_i=0.594$ s, así que $k_i=13.52/0.594=22.8$.
- $T_d=0.148$ s, así que $k_d=13.52\cdot0.148=2.0$.

**Ejemplo 3 — El cero que causa el sobrepaso.** Con las ganancias del ejemplo 1, el cero está en $-k_i/k_p=-51.2/33.28=-1.54$, más cerca del origen que la parte real de los polos ($-3.2$ y $-4$). Un cero lento "adelanta" la respuesta y la hace pasarse. El modelo continuo predice 30.3 % de sobrepaso y la simulación con retardo mide 30.7 %.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué Ziegler-Nichols no necesita modelo, y qué precio se paga por eso?
- A2. ¿Por qué filtrar la referencia elimina el sobrepaso ante un cambio de referencia, pero no cambia en nada cómo se rechaza un empujón al eslabón?

**Serie B — Cálculo a mano**
- B1. Calcular un PD por ubicación de polos con $\omega_n=4$, $\zeta=0.8$ y comprobar que da $k_p=12.8$, $k_d=4.67$.
- B2. Calcular el PID por polos con $\omega_n=3$, $\zeta=1$, $p=3$ y la ubicación de su cero.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_18/sintonia.py`. Cambiar el retardo a 50 ms (como en el Bloque 17) y observar cómo cambian $k_u$, $T_u$ y el resultado de Ziegler-Nichols.
- C2. Sintonizar a mano, siguiendo los tres pasos de la sección 2, y tratar de ganarle a las tres sintonías de la tabla.

---

## Tema 18.4 — Saturación del actuador y efecto *windup*

### 1. El problema

Todos los análisis anteriores suponen que el motor entrega el voltaje que el PID pide. Pero el driver tiene un límite: aquí, 12 V. Con un escalón de 1.5 rad, el término proporcional solo ya pide $33.28\cdot1.5=50$ V. ¿Qué le pasa al PID cuando lo que pide no llega?

### 2. El mecanismo

Durante la **saturación**, el lazo está efectivamente **abierto**: el voltaje es 12 V pase lo que pase, y el controlador no tiene cómo acelerar más. El término P y el D no guardan memoria, así que se recuperan en cuanto el error baja. La integral, en cambio, **sigue acumulando** todo el error de la subida, que es grande y dura bastante. Cuando el eslabón por fin llega a la referencia, la integral vale mucho más que los pocos voltios que pide la gravedad, y ese exceso lo empuja **de largo**. Para descargar la integral hace falta error negativo, es decir, pasarse de la referencia. A este efecto se le llama ***windup*** (de "dar cuerda", como a un reloj).

El **anti-windup** más simple es la **integración condicional** (*clamping*), la que implementa `robotica.control.PID`:

> Si la salida está saturada **y** el error empuja hacia afuera del límite (en el mismo sentido de la saturación), no se acumula la integral en esta muestra.

En código, para el límite superior: si $u>u_{max}$ y $e>0$, la integral queda congelada. Si $e<0$ (el error ya empuja hacia adentro), la integral sí se actualiza, porque eso ayuda a salir de la saturación.

Otra técnica, el **cálculo hacia atrás** (*back-calculation*), descarga la integral en proporción a cuánto se pasó la salida del límite. Es más suave pero tiene un parámetro más. Åström & Murray la desarrollan.

### 3. En la vida real

```python
pid = PID(kp, ki, kd, ts=0.001, u_min=-12, u_max=12, anti_windup=True)   # por defecto
```

`codigo/bloque_18/romper_windup.py` (escalón de 0 a 1.5 rad, eslabón sostenido al inicio):

```
anti-windup   sobrepaso  t_est 2%  tiempo saturado  integral máx
no                60.3%     2.69s            0.48s         33.0V
sí                21.8%     1.83s            0.34s         11.5V
```

Al final, la gravedad en 1.5 rad solo pide $0.1\cos(1.5)/0.025=0.28$ V. Sin anti-windup, la integral llegó a guardar 33 V. El 22 % que queda con anti-windup no viene del windup: es el cero del PI (Tema 18.3), y el filtro de la referencia lo quita.

### 4. Limitaciones

- La integración condicional congela la integral, pero no la corrige: si entró a la saturación con un valor malo, sale con ese valor.
- La saturación no es solo de voltaje. También hay límite de corriente del driver, de velocidad del motor (Bloque 16, curva par-velocidad) y de posición (topes). Un PID que ignora esos límites produce windup en cualquiera de ellos.
- La mejor forma de evitar la saturación es **no pedir escalones**: una trayectoria suave (Bloque 19) mantiene el error siempre pequeño.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Movimientos cortos salen bien; los largos se pasan mucho y tardan en asentarse | Windup: en los largos el actuador satura y la integral se infla | Registrar $u$ y la integral: la integral sigue creciendo mientras $u$ está pegado al límite | Anti-windup; trayectorias suaves en vez de escalones |
| Tras chocar con un obstáculo o un tope, al liberarlo el brazo "salta" | La integral acumuló durante todo el bloqueo | Mismo registro durante el bloqueo | Anti-windup y un límite absoluto para la integral; reiniciar el PID al detectar el bloqueo |
| El brazo se descuelga lentamente al encenderlo | El PID arranca con la integral en cero y tiene que construir el voltaje de la gravedad | Mirar cuánto tarda la integral en llegar a $\tau_g\cos\theta/K$ | Precargar la integral con la gravedad calculada (así arrancan los scripts de este bloque), o compensarla (Bloque 20) |

### 6. Dónde más aparece la idea

Un calentador que no alcanza la temperatura pedida en invierno y, cuando por fin llega, la sobrepasa por horas. Un regulador de velocidad de un auto que viene de subir una pendiente larga a fondo y se pasa al coronarla. Cualquier "memoria del error" que no se entera de que no la estaban escuchando.

### 7. Ejemplos resueltos

**Ejemplo — Cuánto se infla la integral, a mano.** Durante la subida saturada, suponiendo un error medio de unos 0.75 rad (la mitad de 1.5) durante los 0.48 s saturados: $\Delta I\approx k_i\cdot\bar e\cdot t=51.2\cdot0.75\cdot0.48\approx18$ V. Sumados a los 4 V iniciales dan unos 22 V. El registro dice 33 V porque el error sigue siendo grande un rato después de salir de la saturación. El orden de magnitud cuadra: decenas de voltios guardados cuando al final hacen falta 0.28.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el término P no sufre windup y el I sí.
- A2. ¿Por qué el anti-windup no debe congelar la integral cuando el error ya empuja hacia adentro del límite?

**Serie B — Cálculo a mano**
- B1. Con $k_p=33.28$ y $u_{max}=12$ V, ¿desde qué tamaño de escalón satura el PID en el primer instante?

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_18/romper_windup.py` y leer las tres gráficas: ángulo, voltaje, integral.
- C2. Bajar $u_{max}$ a 8 V y repetir. ¿Crece la diferencia entre con y sin anti-windup? ¿Por qué?

---

## Tema 18.5 — Derivada del error contra derivada de la medición; ruido

### 1. El problema

La acción derivativa es la que amortigua (Tema 18.1), pero tiene dos problemas prácticos. Ante un cambio brusco de referencia produce un pico de voltaje enorme. Y cualquier ruido del sensor, por pequeño que sea, sale multiplicado.

### 2. El mecanismo

**La patada derivativa** (*derivative kick*). Si la referencia salta de 0 a 0.2 rad, el error $e=r-y$ salta igual, y su derivada es, en teoría, infinita. En un PID discreto, esa derivada es $\Delta e/t_s=0.2/0.001=200$ rad/s durante una muestra. Multiplicada por $k_d=7.87$ da 1574 V.

La solución es notar que, entre cambios de referencia, $\dot e=\dot r-\dot y=-\dot y$. Derivar **menos la medición** en lugar del error da exactamente la misma acción amortiguadora, sin la patada: la medición es la posición de un objeto con masa y **no puede saltar**. Es la opción por defecto de `robotica.control.PID` (`derivada_de="medicion"`).

**El ruido.** Un potenciómetro bueno tiene ruido de unos 0.002 rad (0.1°). La derivada discreta de ese ruido es del orden de $\sigma\sqrt2/t_s$ (dos muestras con ruido independiente, restadas, divididas entre $t_s$): con $t_s=1$ ms, unos 2.8 rad/s de "velocidad" que no existe. Por $k_d=7.87$ da unos 22 V de desviación: el driver pasa más de la mitad del tiempo saturado, el motor zumba y se calienta.

El remedio es **filtrar la derivada** con un filtro de primer orden de constante de tiempo $t_f$:

$$D(s) = \frac{k_d\,s}{t_f s + 1}$$

A frecuencias bajas ($\omega\ll1/t_f$) es la derivada normal. A frecuencias altas, donde vive el ruido, la ganancia deja de crecer y se queda en $k_d/t_f$. Precio: el filtro es un pequeño retardo más en el lazo (Bloque 17, Tema 17.5), así que $t_f$ debe ser bastante menor que $1/\omega_n$ del lazo.

### 3. En la vida real

```python
pid = PID(kp, ki, kd, ts=0.001, derivada_de="medicion", tf=0.01)
```

`codigo/bloque_18/derivada_y_ruido.py`:

```
Parte 1 — escalón de 0 a 0.2 rad en t = 0.5 s  (tf = 10 ms)
  derivada de   |u| máx  ms saturado  sobrepaso
  error           12.00           39      23.7%
  medicion        10.67            0      29.6%

Parte 2 — quieta en 0.5 rad, ruido de medición σ = 0.002 rad
   tf [ms]  desv. de u [V]  % del tiempo saturado
         0            9.73                  61.8%
        10            1.53                   0.0%
        30            0.58                   0.0%
```

Con derivada del error, el driver queda 39 ms pegado a 12 V justo después del escalón. Para el ángulo eso no es "malo" (aquí hasta baja el sobrepaso), pero es un golpe de corriente y de par en el reductor en cada cambio de referencia. Con la derivada sin filtrar y el ruido de un potenciómetro bueno, el voltaje satura el 62 % del tiempo.

### 4. Limitaciones

- La derivada de la medición no produce patada, pero tampoco "anticipa" los cambios de referencia. Si la referencia es una trayectoria suave (Bloque 19), esa anticipación se recupera con prealimentación (Bloque 20).
- El filtro de primer orden es el mínimo. Encoders de baja resolución producen un ruido de **cuantización** (escalones de un pulso) que a veces pide filtros mejores, o estimar la velocidad a partir del tiempo entre pulsos.
- $k_d$ y $t_s$ tiran en sentidos contrarios: muestrear más rápido mejora el lazo (Tema 18.6) pero amplifica el ruido de la derivada ($k_d/t_s$). El filtro es lo que permite tener las dos cosas.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El motor zumba o se calienta estando quieto | Ruido del sensor amplificado por $k_d/t_s$ | Registrar $u$ con el brazo quieto: si su desviación es de voltios, es la derivada | Filtrar la derivada ($t_f$), bajar $k_d$, mejorar el sensor |
| Golpe seco en cada cambio de referencia; el driver se protege por sobrecorriente | Patada derivativa: se deriva el error | Mirar $u$ justo después del cambio | Derivar la medición en lugar del error |
| Se filtró la derivada y el brazo empezó a oscilar | $t_f$ demasiado grande: un retardo más en el lazo | Comparar $t_f$ con $1/\omega_n$ | Bajar $t_f$; aceptar algo de ruido |

### 6. Dónde más aparece la idea

Cualquier derivada numérica de datos medidos: la aceleración calculada a partir de un GPS, la velocidad de un auto a partir del odómetro, la "tendencia" de una serie de precios. Siempre hay que suavizar antes de derivar, y siempre se paga con retardo.

### 7. Ejemplos resueltos

**Ejemplo — Ruido en el voltaje, a mano.** $\sigma_y=0.002$ rad, $t_s=0.001$ s, $k_d=7.87$.
- Sin filtro: $\sigma_D\approx k_d\sqrt2\sigma_y/t_s=7.87\cdot1.414\cdot0.002/0.001=22$ V. Con eso, el voltaje se sale de $\pm12$ V buena parte del tiempo.
- Con filtro, la ganancia de alta frecuencia baja a $k_d/(t_f+t_s)$. Con $t_f=10$ ms, $7.87/0.011=715$ V/rad en lugar de 7870: once veces menos.

La simulación da 9.7 V de desviación sin filtro, que es menos que 22 V porque la saturación recorta, y 1.5 V con filtro.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué derivar la medición en lugar del error no cambia el amortiguamiento del lazo?
- A2. Explicar el compromiso entre muestrear rápido y derivar sin ruido.

**Serie B — Cálculo a mano**
- B1. Calcular la ganancia de alta frecuencia de la derivada filtrada con $t_f=30$ ms.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_18/derivada_y_ruido.py`. Subir el ruido a 0.01 rad (un potenciómetro barato) y buscar el $t_f$ mínimo que evita la saturación.

---

## Tema 18.6 — Control digital: muestreo, discretización, microcontrolador

### 1. El problema

El PID de los temas anteriores es una fórmula continua, con integrales y derivadas. El brazo lo va a controlar un **microcontrolador**, que solo sabe leer el sensor cada cierto tiempo, hacer sumas y multiplicaciones, y escribir un voltaje. ¿Cómo se convierte la fórmula en código? ¿Cada cuánto hay que correrlo?

### 2. El mecanismo

**Muestreo.** El microcontrolador corre el PID cada $t_s$ segundos (el **periodo de muestreo**). Entre muestras, el voltaje queda congelado: es un **retenedor de orden cero** (ZOH, *zero-order hold*). Visto desde la planta, un voltaje que se actualiza solo cada $t_s$ equivale, aproximadamente, a un retardo de $t_s/2$, y ya se sabe lo que un retardo le hace a un lazo (Bloque 17, Tema 17.5).

**Discretización.** En la muestra $k$, con $e_k=r_k-y_k$, se reemplaza cada operación continua por una aproximación con muestras (**Euler hacia atrás**, Bloque 05):

- Integral: el área bajo $e$ crece en un rectángulo de base $t_s$ y altura $e_k$:
$$I_k = I_{k-1} + k_i\,t_s\,e_k$$
- Derivada filtrada $D(s)=k_d s/(t_f s+1)$, aplicada a $x=-y$. En el tiempo: $t_f\dot D + D = k_d\dot x$. Con $\dot D\approx(D_k-D_{k-1})/t_s$ y $\dot x\approx(x_k-x_{k-1})/t_s$:
$$t_f\frac{D_k - D_{k-1}}{t_s} + D_k = k_d\frac{x_k - x_{k-1}}{t_s}$$
Se multiplica por $t_s$ y se despeja $D_k$:
$$D_k = \frac{t_f}{t_f+t_s}D_{k-1} + \frac{k_d}{t_f+t_s}\left(x_k - x_{k-1}\right)$$
Con $t_f=0$ queda la derivada simple $k_d(x_k-x_{k-1})/t_s$.
- Salida: $u_k=k_pe_k+I_k+D_k$, luego saturación y anti-windup (Tema 18.4).

Estas tres líneas son, sin cambios, el método `PID.paso` de `codigo/robotica/control.py`.

**Cada cuánto muestrear.** Regla práctica: **20 o más muestras por periodo natural del lazo cerrado**, $t_s\le\frac{1}{20}\cdot\frac{2\pi}{\omega_n}$. Con $\omega_n=4$ rad/s (periodo de 1.57 s) basta con $t_s\le0.08$ s. En la práctica, los lazos de posición de un robot corren a 1-10 ms: no por esta regla, que sería muy holgada, sino por el ruido, la fricción y los modos de vibración que el modelo simple no tiene.

**Implementación en un microcontrolador.** La misma función, portada a C (`codigo/bloque_18/pid.h` y `pid.c`), sin memoria dinámica y sin `math.h`. Se llama desde una interrupción de temporizador que dispara cada $t_s$. El esqueleto es el siguiente; las funciones de hardware (`leer_angulo`, `escribir_voltaje`) dependen del microcontrolador y se escriben en el Bloque 22, así que este fragmento **no está probado en hardware**:

```c
#include "pid.h"

static PidControlador pid_hombro;
static volatile float referencia_hombro = 0.0f;   /* la escribe el enlace serie */

void configurar(void) {
    pid_iniciar(&pid_hombro, 33.28f, 51.2f, 7.87f, 0.001f,
                -12.0f, 12.0f, 0.01f, 1, 0);
    iniciar_temporizador_1ms(interrupcion_control);
}

void interrupcion_control(void) {                 /* cada 1 ms, siempre */
    float theta = leer_angulo();                  /* sensor -> rad (Bloque 22) */
    float u = pid_paso(&pid_hombro, referencia_hombro, theta);
    escribir_voltaje(u);                          /* PWM del driver (Bloque 22) */
}
```

Tres reglas de este código: la interrupción tiene que terminar **mucho antes** de $t_s$; no se imprime ni se espera nada dentro de ella; y las ganancias se calculan en el computador (Python) y se envían, no se deducen en el microcontrolador.

### 3. En la vida real

`codigo/bloque_18/comparar_c_python.py` compila `pid.c` con gcc, le pasa exactamente la misma secuencia de (referencia, medición) que recibió el PID de Python en una simulación con ruido, gravedad y saturación, y compara salida por salida:

```
caso                                               muestras saturadas  máx|dif| double  máx|dif| float
derivada de la medición, filtrada, anti-windup         6000       745         0.00e+00        6.47e-05
derivada del error, sin filtro, anti-windup            6000      3868         0.00e+00        1.22e-03
derivada de la medición, sin anti-windup               6000      1384         0.00e+00        1.23e-04
```

Compilado con `double`, el C da **exactamente** los mismos números que Python: las mismas operaciones en el mismo orden producen los mismos bits (IEEE 754). Compilado con `float`, que es lo que usa un microcontrolador con FPU simple, la diferencia es de milésimas de voltio o menos: mucho menor que el efecto del ruido del sensor.

`codigo/bloque_18/romper_muestreo_lento.py` corre el mismo PID con periodos cada vez más largos:

```
 ts [s]  muestras por periodo   máx θ  error en los últimos 2 s
  0.001                  1571   0.570                    0.0000
  0.010                   157   0.568                    0.0000
  0.050                    31   0.557                    0.0000
  0.100                    16   0.569                    0.0000
  0.150                    10   0.662                    0.2566
  0.200                     8   1.041                    0.6356
```

### 4. Limitaciones

- Euler hacia atrás es la discretización más simple. Con $t_s$ muy pequeño frente a la dinámica, cualquier método da lo mismo. Con $t_s$ grande conviene Tustin (trapecios) o diseñar directamente en tiempo discreto (transformada $z$, Ogata, *Sistemas de control en tiempo discreto*), fuera del alcance del curso.
- El análisis supone que $t_s$ es exacto. Si la interrupción se retrasa a veces (*jitter*), la integral y la derivada se calculan con un $t_s$ equivocado.
- En `float`, sumar un número muy pequeño ($k_i t_s e_k$) a una integral grande puede perder dígitos. Con los valores de este bloque no importa. Con $t_s$ de microsegundos, sí.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El PID que funcionaba en simulación oscila en el microcontrolador | $t_s$ real mayor que el supuesto (interrupción lenta, lectura del sensor lenta) | Medir con un osciloscopio o un pin que conmute en cada interrupción | Bajar el trabajo dentro de la interrupción; recalcular las ganancias con el $t_s$ real |
| Al cambiar $t_s$, el lazo cambia de comportamiento aunque las "ganancias" sean las mismas | Se usó $k_i$ y $k_d$ "por muestra", sin $t_s$ dentro de las fórmulas | Revisar que la integral multiplique por $t_s$ y la derivada divida | Usar siempre las fórmulas de la sección 2, con $t_s$ explícito |
| El brazo en reposo tiembla con una frecuencia fija | Muestreo lento frente a la dinámica, o retardo de cálculo | Contar muestras por periodo natural | $t_s$ más corto (regla de 20 muestras o más) |

### 6. Dónde más aparece la idea

Todo control moderno es digital: el termostato programable, el control de inyección de un motor, el estabilizador de una cámara, un marcapasos. La música digital es la misma idea al revés: el teorema de muestreo dice cuántas muestras por segundo hacen falta para no perder información, y de ahí sale 44.1 kHz.

### 7. Ejemplos resueltos

**Ejemplo 1 — Un paso del PID a mano.** $k_p=33.28$, $k_i=51.2$, $k_d=7.87$, $t_s=0.001$, $t_f=0$. Estado anterior: $I=4.0$ V, $y_{anterior}=0.100$ rad. Nueva muestra: $r=0.2$, $y=0.101$.
- $e=0.2-0.101=0.099$ rad.
- $D=k_d\cdot(-0.101-(-0.100))/0.001=7.87\cdot(-1)=-7.87$ V. El eslabón subió 1 mrad en 1 ms, así que la derivada frena.
- $I=4.0+51.2\cdot0.001\cdot0.099=4.00507$ V.
- $u=33.28\cdot0.099+4.00507-7.87=3.2947+4.00507-7.87=-0.570$ V. Dentro de $\pm12$: no satura.

Verificable con `PID.paso` después de fijar `pid.integral = 4.0` y `pid.anterior = -0.100`.

**Ejemplo 2 — Periodo de muestreo máximo.** Con $\omega_n=4$ rad/s, el periodo natural es $2\pi/4=1.57$ s, y con 20 muestras por periodo, $t_s\le0.079$ s. La simulación funciona bien hasta 0.1 s (16 muestras) y se degrada a 0.15 s (10 muestras). La regla deja margen, que es para lo que existe.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué el ZOH se comporta como un retardo de $t_s/2$?
- A2. ¿Qué pasa con el término integral si el código se olvida de multiplicar por $t_s$ y luego se cambia $t_s$ de 1 ms a 10 ms?

**Serie B — Cálculo a mano**
- B1. Repetir el ejemplo 1 con $t_f=0.01$ s y $D_{anterior}=-5$ V.
- B2. Discretizar la integral con trapecios (Tustin): $I_k=I_{k-1}+k_it_s(e_k+e_{k-1})/2$, y explicar qué variable nueva tiene que guardar el PID.

**Serie C — Laboratorio**
- C1. Verificar el ejemplo 1 con `robotica.control.PID`.
- C2. Correr `codigo/bloque_18/comparar_c_python.py`. Cambiar un signo en `pid.c` (por ejemplo, en la derivada) y ver cómo la comparación lo detecta de inmediato.
- C3. (`⚠ romperlo a propósito`) Correr `codigo/bloque_18/romper_muestreo_lento.py` y encontrar, por bisección, el $t_s$ exacto a partir del cual el lazo deja de asentarse.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/control.py`, original de este curso (robotica-manipuladores no tiene control):

| Función / clase | Qué hace |
|---|---|
| `PID` | PID discreto: Euler hacia atrás, derivada de la medición o del error con filtro de primer orden, saturación, anti-windup por integración condicional. Métodos `paso(r, y)` y `reiniciar()`. |
| `pd_por_polos`, `pid_por_polos` | Ganancias por ubicación de polos para la planta $K/(s(Js+b))$. |
| `ziegler_nichols` | Ganancias por la tabla de Ziegler-Nichols en lazo cerrado. |
| `simular_lazo` | Planta continua (RK4, Bloque 05) controlada por un controlador discreto con retenedor de orden cero. |

Verificación hecha antes de publicar: los polos que pide `pid_por_polos` coinciden con los que calcula `control.feedback`. El PID discreto con $t_s=0.1$ ms reproduce la respuesta continua de python-control (diferencia máxima de $6\times10^{-5}$ rad con derivada de la medición y $1\times10^{-4}$ rad con derivada del error). El port a C coincide bit a bit con `double`.

Además, en `codigo/bloque_18/`: `pid.h`, `pid.c` (el PID para el microcontrolador) y `prueba_pid.c` (su banco de prueba).

## Glosario del bloque

| Término | Definición |
|---|---|
| Acción proporcional, integral, derivativa | Voltaje proporcional al error presente, a la suma del error pasado y a la velocidad de cambio del error. |
| PID | Controlador que suma las tres acciones: $C(s)=k_p+k_i/s+k_ds$. |
| Tiempo integral / derivativo | $T_i=k_p/k_i$ y $T_d=k_d/k_p$: la forma del PID que usa Ziegler-Nichols. |
| Control monoarticular (descentralizado) | Un lazo independiente por articulación; el acoplamiento con las demás se trata como perturbación. |
| Ganancia y periodo últimos | $k_u$: la ganancia P con la que el lazo oscila con amplitud constante; $T_u$: el periodo de esa oscilación. |
| Ziegler-Nichols | Tabla de sintonía a partir de $k_u$ y $T_u$, sin modelo. |
| Ubicación de polos | Elegir los polos del lazo cerrado y despejar las ganancias con el modelo. |
| Filtro de referencia | Filtro sobre la referencia que cancela el cero del PI y quita el sobrepaso ante cambios de referencia. |
| Saturación | Límite físico del actuador: por mucho que el controlador pida, no entrega más. |
| *Windup* / anti-*windup* | Acumulación de la integral mientras el actuador está saturado / técnicas que la evitan (integración condicional, cálculo hacia atrás). |
| Patada derivativa | Pico de la acción derivativa ante un cambio brusco de referencia, cuando se deriva el error. |
| Filtro de la derivada | Filtro de primer orden $k_ds/(t_fs+1)$ que limita la amplificación del ruido. |
| Periodo de muestreo $t_s$ | Tiempo entre dos ejecuciones del controlador digital. |
| Retenedor de orden cero (ZOH) | Mantener la salida constante entre muestras; equivale a un retardo de alrededor de $t_s/2$. |
| Euler hacia atrás | Discretización que aproxima $\dot x$ por $(x_k-x_{k-1})/t_s$. |
| Ciclo límite | Oscilación sostenida de amplitud fija, típica de un lazo inestable cuya amplitud recorta la saturación. |
