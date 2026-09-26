# Bloque 19 — Generación de trayectorias

> **Problema que abre el bloque:** si se le manda al brazo "ve a este punto" de golpe, arranca con aceleración infinita, sacude la estructura y el huevo sale volando.
>
> **Necesitas antes:** Bloque 18 (PID de una articulación); Bloque 15 (Newton-Euler, para el par); Bloque 13 (Jacobiana y singularidades); Bloque 12 (cinemática inversa). · **Lectura:** Barrientos, cap. 6; Lynch & Park, *Modern Robotics*, cap. 9 (libre).

El Bloque 18 dejó una articulación que llega a donde se le pide. Lo que no dijo es **qué pedirle en cada instante**. Una **trayectoria** es la respuesta: una función del tiempo, $q(t)$, que dice dónde debe estar cada articulación (o la pinza) en cada momento, con su velocidad $\dot q(t)$ y su aceleración $\ddot q(t)$. Un **camino** es solo la curva, sin tiempo. La trayectoria es el camino más el horario.

Los ejemplos usan dos modelos ya conocidos:
- el **brazo 2R plano** de los Bloques 15 y 16 ($m_1=1.3$ kg y $m_2=0.7$ kg concentradas en la punta de cada eslabón, $L_1=0.30$ m, $L_2=0.20$ m), en `codigo/bloque_19/brazo_2r.py`;
- la **articulación con PID** del Bloque 18, en `codigo/bloque_18/articulacion.py`.

---

## Tema 19.1 — Espacio articular contra espacio cartesiano

### 1. El problema

La pinza tiene que ir de encima de la clasificadora a encima de la cubeta. ¿Se interpola cada ángulo del motor por separado, o se le dice a la pinza por qué curva ir y se calculan los ángulos después?

### 2. El mecanismo

- **Trayectoria en el espacio articular.** Se calculan los ángulos del inicio y del destino con la inversa (Bloque 12), **una sola vez**, y se interpola cada ángulo en el tiempo. Es barato, nunca pasa por una singularidad a mitad de camino (los ángulos solo van de un valor a otro) y respeta directamente los límites de cada motor. A cambio, **no se controla la curva de la pinza**: la cinemática directa de ángulos que varían suave no es una recta, sino una curva que depende del brazo.
- **Trayectoria en el espacio cartesiano.** Se define la curva de la pinza (una recta, un arco) con su horario, y **en cada instante** se resuelve la inversa. La pinza sigue exactamente la curva pedida. A cambio, se resuelve la inversa cientos de veces por segundo; la curva puede salirse del espacio de trabajo a mitad de camino; y cerca de una singularidad los ángulos tienen que girar muy rápido (Tema 19.5).

Regla práctica: **espacio articular para moverse libremente** (ir de un lado a otro sin obstáculos) y **espacio cartesiano cuando la curva importa** (bajar en vertical hacia el huevo, soldar un cordón, trazar una letra).

### 3. En la vida real

Los robots industriales distinguen las dos órdenes con nombres propios: en el lenguaje de ABB, `MoveJ` (*joint*, articular) y `MoveL` (*linear*, cartesiano). En la librería del curso:

```python
from robotica.trayectorias import quintica, linea, resolver_trayectoria
q, qd, qdd = quintica(q_inicio, q_destino, T, t)        # articular, una articulación
res = resolver_trayectoria(puntos, inversa, solucion=0)  # cartesiano, punto por punto
```

### 4. Limitaciones

Las dos formas necesitan una **ley temporal**: cómo avanzar a lo largo del camino en el tiempo. Los Temas 19.2 y 19.3 son sobre eso, y valen para las dos. En el espacio cartesiano, la "variable" que se interpola es el avance $s(t)$ de 0 a 1 a lo largo de la curva.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Se pidió ir "derecho" y la pinza hizo un arco que chocó con el borde de la cubeta | Movimiento articular: la pinza no sigue rectas | Dibujar la cinemática directa de la trayectoria articular antes de ejecutarla | Movimiento cartesiano en ese tramo, o puntos de paso que esquiven el obstáculo (Tema 19.4) |
| Un movimiento cartesiano se detiene a mitad de camino con "sin solución" | La recta sale del espacio de trabajo aunque sus extremos estén dentro | Revisar `resultado.indice_fallo` y el punto correspondiente | Mover el camino, o usar movimiento articular |

### 6. Dónde más aparece la idea

Una cámara de cine en una grúa (se programan las articulaciones de la grúa o la curva de la cámara); un avión que vuela por puntos de navegación (ruta) con un horario (plan de vuelo); las animaciones por fotogramas clave, que interpolan en "ángulos de las articulaciones" del personaje.

### 7. Ejemplos resueltos

**Ejemplo:** el 2R con codo arriba va de $(-0.3,\,0.105)$ m a $(0.3,\,0.105)$ m. Interpolando en el espacio articular, el hombro necesita como máximo 2.31 rad/s y la punta se aparta de la recta horizontal hasta **21 cm**. Siguiendo la recta, la punta no se aparta nada, pero el hombro necesita **7.4 rad/s** (`romper_singularidad.py`, Tema 19.5).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Para cada tarea, decidir si conviene movimiento articular o cartesiano y por qué: llevar el brazo a su posición de reposo; bajar la pinza en vertical sobre el huevo; volver de la cubeta a la clasificadora.

**Serie B — Cálculo a mano**
- B1. Con el 2R en $\theta_1=0,\theta_2=0$ y en $\theta_1=\pi/2,\theta_2=0$, calcular la posición de la punta a mitad de camino si se interpolan los ángulos linealmente. ¿Está sobre la recta que une los extremos?

**Serie C — Laboratorio**
- C1. Dibujar con `brazo_2r.directa` la curva de la punta del ejercicio B1.

---

## Tema 19.2 — Interpoladores: lineal, cúbico, quíntico

### 1. El problema

La articulación tiene que ir de $q_0$ a $q_f$ en $T$ segundos, arrancando y terminando quieta. La forma más obvia, avanzar a velocidad constante, tiene un problema escondido en los extremos.

### 2. El mecanismo

**Lineal.** $q(t)=q_0+D\,t/T$, con $D=q_f-q_0$. La velocidad es $D/T$ todo el tiempo. Pero antes de $t=0$ la articulación estaba quieta: la velocidad **salta** de 0 a $D/T$ en un instante, y la aceleración, que es la derivada de ese salto, es **infinita**. Por la dinámica (Bloque 14), par infinito. En la simulación, la aceleración que se mide es $\frac{D/T}{\Delta t}$: crece sin límite al achicar el paso de tiempo $\Delta t$.

**Cúbico.** Se exige, además de las posiciones, que la velocidad en los extremos sea la pedida. Son **cuatro condiciones**, así que hace falta un polinomio de cuatro coeficientes:

$$q(t) = a_0 + a_1t + a_2t^2 + a_3t^3, \qquad \dot q(t) = a_1 + 2a_2t + 3a_3t^2$$

Condiciones: $q(0)=q_0$, $\dot q(0)=v_0$, $q(T)=q_f$, $\dot q(T)=v_f$. Las dos primeras dan directamente $a_0=q_0$ y $a_1=v_0$. Las otras dos:

$$q_0 + v_0T + a_2T^2 + a_3T^3 = q_f \qquad\qquad v_0 + 2a_2T + 3a_3T^2 = v_f$$

De la primera, $a_2T^2+a_3T^3=D-v_0T$. Multiplicando la segunda por $T$: $2a_2T^2+3a_3T^3=(v_f-v_0)T$. Restando dos veces la primera a la segunda:

$$a_3T^3 = (v_f-v_0)T - 2(D - v_0T) = -2D + (v_0+v_f)T \quad\Longrightarrow\quad a_3 = \frac{-2D + (v_0+v_f)T}{T^3}$$

y sustituyendo, $a_2=\dfrac{3D-(2v_0+v_f)T}{T^2}$. Con $v_0=v_f=0$ (reposo a reposo): $a_2=3D/T^2$, $a_3=-2D/T^3$, y

$$\ddot q(t) = \frac{6D}{T^2} - \frac{12D}{T^3}t$$

La aceleración máxima está en los extremos: $6D/T^2$ en $t=0$. La velocidad ya no salta, pero la **aceleración sí**: pasa de 0 (quieto) a $6D/T^2$ en un instante. Eso es un *jerk* (la derivada de la aceleración, en rad/s³) infinito: el brazo no se rompe, pero recibe un golpe seco que excita vibraciones.

**Quíntico.** Se exige también la aceleración en los extremos: **seis condiciones**, polinomio de grado 5. El mismo procedimiento (tres coeficientes salen directos, los otros tres de un sistema de 3×3) da, de reposo a reposo:

$$q(t) = q_0 + D\left(10\tau^3 - 15\tau^4 + 6\tau^5\right), \qquad \tau = t/T$$

Se comprueba derivando: $\dot q=\frac{D}{T}(30\tau^2-60\tau^3+30\tau^4)$ y $\ddot q=\frac{D}{T^2}(60\tau-180\tau^2+120\tau^3)$, que valen cero en $\tau=0$ y en $\tau=1$. La aceleración arranca desde cero, así que el jerk es finito. Su máximo sale de $d\ddot q/d\tau=0$: $60-360\tau+360\tau^2=0$, es decir $\tau=\frac12-\frac{1}{2\sqrt3}\approx0.211$, donde $\ddot q_{max}=\frac{10\sqrt3}{3}\frac{D}{T^2}\approx5.77\,D/T^2$.

**Precio del quíntico:** la velocidad pico es $\frac{15}{8}\frac{D}{T}=1.875\,D/T$, contra $1.5\,D/T$ del cúbico. Para suavizar los extremos, tiene que ir más rápido por el medio.

### 3. En la vida real

`codigo/bloque_19/comparar_perfiles.py` mueve el hombro del 2R de 0 a $\pi/2$ en 1.5 s, con el codo fijo, y calcula el par con Newton-Euler (Bloque 15):

```
perfil         v máx    a máx  salto de a   τ pico   τ RMS  τ pico sin g
             [rad/s] [rad/s²]      en t=0    [N·m]   [N·m]         [N·m]
lineal         1.047  1047.20     1047.20   313.04   13.66        305.78
cúbico         1.571     4.19        4.19     8.48    5.52          1.22
quíntico       1.963     4.03        0.00     8.40    5.61          1.18
trapezoidal    1.571     3.14        3.14     8.18    5.54          0.92
en S           1.571     4.49        0.00     8.57    5.57          1.31
```

Cómo leerla: con el brazo horizontal, la gravedad sola pide 7.26 N·m, así que domina el par pico. La última columna separa lo que depende del perfil (inercia y Coriolis). El lineal pide 306 N·m con pasos de 1 ms, 3065 con pasos de 0.1 ms: ese número no significa nada, es "infinito" medido con una regla.

### 4. Limitaciones

- Subir el grado del polinomio no es gratis: más grado, más velocidad pico para la misma duración.
- Un polinomio **no respeta límites**: si $T$ es corto, la velocidad o la aceleración pueden pasarse de lo que el motor da. Hay que verificarlas después (o usar los perfiles del Tema 19.3, que se construyen desde los límites).
- Estos interpoladores son para **un tramo**. Para pasar por varios puntos sin detenerse, ver el Tema 19.4.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El brazo termina siempre un poco antes del destino, más cuanto más largo el último tramo | Bug real de robotica-manipuladores (`Interpolador_lineal.m`, `correcciones.md` caso 5): cada tramo descartaba su último punto y el final nunca se agregaba. De 0° a 90° terminaba en 80° | Comparar el último valor de la trayectoria con el destino pedido | Agregar el punto final después del último tramo (`romper_ultimo_punto.py`) |
| La trayectoria llega, pero el motor se pasa de su velocidad límite en algunos tramos | Los puntos de todos los tramos se repartieron en un eje de tiempo uniforme, aunque los tramos duran distinto | Derivar numéricamente $q$ respecto al tiempo asignado y comparar con el límite | Encadenar los tiempos reales de cada tramo (`robotica.trayectorias.interpolador_trapezoidal`) |
| Golpe o zumbido al arrancar y al frenar, aunque la posición se ve suave | Salto de aceleración (perfil lineal, cúbico o trapezoidal) | Graficar $\ddot q(t)$: si no arranca en cero, hay salto | Quíntico o perfil en S |

### 6. Dónde más aparece la idea

Las curvas de animación "ease in, ease out" de cualquier programa de gráficos son polinomios cúbicos o quínticos. El quíntico reposo a reposo, $10\tau^3-15\tau^4+6\tau^5$, es también la función *smootherstep* de los *shaders*. Los ascensores usan perfiles con jerk limitado para que los pasajeros no sientan el arranque.

### 7. Ejemplos resueltos

**Ejemplo 1 — Coeficientes del cúbico.** $q_0=0$, $q_f=\pi/2$, $T=1.5$ s, reposo a reposo: $a_2=3(1.5708)/2.25=2.094$ rad/s², $a_3=-2(1.5708)/3.375=-0.931$ rad/s³. Aceleración inicial: $2a_2=4.19$ rad/s², y $6D/T^2=4.19$. Velocidad en $T/2$: $2(2.094)(0.75)+3(-0.931)(0.5625)=3.142-1.571=1.571$ rad/s, igual a $1.5\,D/T$.

**Ejemplo 2 — Par inercial.** Con el codo estirado, la inercia que ve el hombro es $m_1L_1^2+m_2(L_1+L_2)^2=1.3(0.09)+0.7(0.25)=0.292$ kg·m². Con la aceleración máxima del cúbico: $0.292\times4.19=1.22$ N·m. La tabla dice 1.22.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué el perfil lineal tiene aceleración infinita, si la posición no salta?
- A2. ¿Qué gana y qué pierde el quíntico frente al cúbico?

**Serie B — Cálculo a mano**
- B1. Coeficientes del cúbico para ir de 0.5 a 1.0 rad en 2 s, con velocidad final 0.2 rad/s.
- B2. Comprobar que $q=D(10\tau^3-15\tau^4+6\tau^5)$ cumple las seis condiciones de reposo a reposo.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_19/comparar_perfiles.py` y verificar la tabla contra los ejemplos.
- C2. (`⚠ romperlo a propósito`) Correr `codigo/bloque_19/romper_ultimo_punto.py`, cambiar $N$ a 5 y predecir, antes de correrlo, dónde termina el interpolador original.

---

## Tema 19.3 — Perfil trapezoidal de velocidad y perfil en S

### 1. El problema

Los polinomios se definen por la duración $T$, y después se revisa si respetan los límites del motor. En la práctica se conoce al revés: el motor da como máximo cierta velocidad y cierta aceleración (Bloque 16), y se quiere **el movimiento más rápido** que las respete.

### 2. El mecanismo

**Perfil trapezoidal.** Tres fases: acelerar con la aceleración máxima $a$ hasta la velocidad máxima $V$; avanzar a $V$; frenar con $-a$. La gráfica de la velocidad es un trapecio. La fase de aceleración dura $\tau=V/a$ y recorre $\frac12a\tau^2=\frac{V^2}{2a}$; el frenado, lo mismo. El crucero recorre el resto, $D-\frac{V^2}{a}$, en $\frac{D}{V}-\frac{V}{a}$. Duración total:

$$T = \frac{D}{V} + \frac{V}{a}$$

Si el tramo es tan corto que $D<V^2/a$, no hay tiempo de llegar a $V$: el perfil queda **triangular**, con velocidad pico $V_p=\sqrt{aD}$. Olvidar este caso fue otro de los bugs de manipuladores (el perfil quedaba mal y no llegaba). La versión portada lo resuelve con `Vp = min(V, sqrt(a*D))`.

Con los límites que el motor permite, el trapezoidal es el movimiento **más rápido** posible: usa la aceleración máxima todo lo que puede. Pero la aceleración salta de 0 a $a$, de $a$ a 0 y de 0 a $-a$: tres golpes de jerk infinito.

**Perfil en S (jerk limitado).** Se agrega un tercer límite, el jerk máximo $J$ [rad/s³], y la aceleración sube **en rampa** en vez de saltar. La velocidad, en lugar de un trapecio con esquinas, queda con forma de "S" en cada rampa. Son **siete fases** de jerk constante:

$$+J,\; 0,\; -J,\; 0\;(\text{crucero}),\; -J,\; 0,\; +J$$

La fase con $+J$ sube la aceleración de 0 a $A$ en $T_j=A/J$; la fase con 0 la mantiene; la fase con $-J$ la baja a 0 justo al llegar a $V$. Luego crucero y lo mismo en espejo para frenar. Si el tramo es corto, primero desaparece el crucero, y luego tampoco se alcanza $A$.

**Cómo se calcula (original de este curso).** Como el jerk es constante en cada fase, cada fase se integra **exacta**: partiendo del estado al final de la fase anterior $(q_i,v_i,a_i)$, con $\tau$ el tiempo dentro de la fase,

$$q = q_i + v_i\tau + \tfrac12a_i\tau^2 + \tfrac16J\tau^3$$

Las duraciones de las fases salen de las fórmulas de Biagiotti y Melchiorri (*Trajectory Planning for Automatic Machines and Robots*, cap. 3), que distinguen si se alcanzan $V$ y $A$ o no. `robotica.trayectorias.perfil_s` las implementa. Se verificó en seis casos (tramos largos, cortos, negativos, sin llegar a $V$, sin llegar a $A$): siempre llega exacto al destino, con velocidad final cero, sin pasarse de $V$, $A$ ni $J$.

### 3. En la vida real

```python
from robotica.trayectorias import perfil_trapezoidal, perfil_s
t, q, qd, qdd = perfil_trapezoidal(0, 1.5, V=1.0, a=2.0, n_puntos=200)
t, q, qd, qdd = perfil_s(0, 1.5, V=1.0, A=2.0, J=10.0, n_puntos=200)
```

En la tabla del Tema 19.2, el trapezoidal (con 1/3 del tiempo para acelerar) tiene el menor par inercial pico (0.92 N·m), pero salta 3.14 rad/s² en $t=0$. El en S, con 0.15 s de jerk en cada rampa, no salta, a cambio de un pico algo mayor (1.31 N·m).

**Romperlo a propósito: un escalón en lugar de una trayectoria.** `codigo/bloque_19/romper_escalon.py` pide a la articulación del Bloque 18 que vaya de 0 a 1.5 rad:

```
Cálculo previo con el modelo: voltaje ideal para seguir cada quíntica
  T = 1.5 s: u ideal máx =  7.45 V  -> posible
  T = 0.6 s: u ideal máx = 24.19 V  -> IMPOSIBLE: pasa de 12 V

referencia                  |u| máx  par pico  ms saturado  error máx  sobrepaso  llega (2%)
escalón                      12.00V   0.300Nm          339      1.500      20.7%       1.87s
quíntica 1.5 s                8.09V   0.202Nm            0      0.194      12.8%       1.93s
quíntica 0.6 s               12.00V   0.300Nm          384      0.650      14.0%       1.78s
quíntica 1.5 s + prealim.     7.46V   0.186Nm            0      0.000       0.0%       1.30s
```

Tres lecciones:

1. **El escalón lleva el motor a su par máximo** (0.3 N·m) durante un tercio de segundo. Con un escalón, quien decide cómo se mueve el brazo es el límite del motor, no el ingeniero.
2. **La trayectoria dice de antemano si un movimiento es posible.** Con el modelo, el voltaje que pide una quíntica se calcula antes de moverse: la de 0.6 s pide 24 V y el driver da 12. No hace falta probarla en el brazo real.
3. **Una trayectoria con PID solo no basta para seguirla bien.** El PID necesita error para empujar, así que va 0.19 rad detrás y se pasa 13 %. Sumándole el voltaje que el modelo dice que hace falta (**prealimentación**, *feedforward*), el error baja a cero. El cálculo previo decía 7.45 V y la simulación usa 7.46. Es un adelanto del Bloque 20.

Un detalle del código: con escalones se deriva la medición (Bloque 18, Tema 18.5). Con una trayectoria suave no hay patada, y derivar la medición **frena** la velocidad planeada (el término $-k_d\dot\theta$ llega a restar 15 V). Con trayectorias se deriva el error, $\dot q_{ref}-\dot q$. La primera versión del script derivaba la medición, y la prealimentación "no funcionaba" por eso.

### 4. Limitaciones

- $V$, $A$ y $J$ son los de **la articulación**, pero lo que el motor limita es el **par**, y el par depende de la postura y de las otras articulaciones (Bloque 14). Los límites se eligen para el peor caso, con margen (Bloque 16).
- Con varias articulaciones, cada una tendría su propio perfil más rápido, de distinta duración. Para que lleguen juntas, se estiran todas a la duración de la más lenta (Tema 19.4).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| En tramos cortos el brazo no llega o da un salto al final | Perfil trapezoidal sin el caso triangular ($D<V^2/a$) | Probar el perfil con un tramo muy corto | Velocidad pico $\sqrt{aD}$ cuando no alcanza $V$ |
| El driver satura, el brazo se pasa y tarda en asentarse | Se le mandan escalones al PID en lugar de trayectorias | Registrar $u$: pegado al límite al inicio de cada movimiento | Trayectoria con límites que el motor pueda cumplir |
| Con trayectoria y prealimentación, el brazo sigue yendo detrás | El PID deriva la medición: frena la velocidad planeada | Mirar el término D durante el movimiento | Derivar el error cuando la referencia es una trayectoria suave |
| Vibración de la estructura al final de cada movimiento rápido | Salto de aceleración (jerk infinito) que excita un modo de vibración | Graficar $\ddot q$ | Perfil en S, o quíntico |

### 6. Dónde más aparece la idea

Las impresoras 3D y las fresadoras CNC usan perfiles trapezoidales; las más finas además limitan el jerk o filtran la trayectoria para no excitar la resonancia de la estructura (*input shaping*). Los trenes y los metros limitan el jerk por comodidad del pasajero. En un ascensor, el "estómago que sube" es jerk.

### 7. Ejemplos resueltos

**Ejemplo 1 — Duración trapezoidal.** $D=1.5$ rad, $V=1$ rad/s, $a=2$ rad/s². Como $V^2/a=0.5<1.5$, alcanza $V$. $T=1.5/1+1/2=2.0$ s: 0.5 s acelerando, 1.0 s de crucero, 0.5 s frenando.

**Ejemplo 2 — Tramo corto.** $D=0.3$ rad con los mismos límites: $V^2/a=0.5>0.3$, así que es triangular. $V_p=\sqrt{2\cdot0.3}=0.775$ rad/s y $T=0.3/0.775+0.775/2=0.775$ s.

**Ejemplo 3 — Perfil en S.** $D=1.5$, $V=1$, $A=2$, $J=10$. $VJ=10\ge A^2=4$, así que alcanza $A$: $T_j=0.2$ s, $T_a=0.2+0.5=0.7$ s. $T_v=1.5/1-0.7=0.8$ s. $T=2(0.7)+0.8=2.2$ s: el jerk limitado alarga el movimiento 0.2 s respecto al trapezoidal del ejemplo 1. La calibración de la librería da $T=2.2000$ s.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué el trapezoidal es "el más rápido posible" con límites de $V$ y $a$?
- A2. Explicar con palabras qué es el jerk y por qué lo nota un pasajero y no lo nota un reloj.

**Serie B — Cálculo a mano**
- B1. Duración trapezoidal para $D=0.1$ rad, $V=1$, $a=2$.
- B2. Duración del perfil en S del ejemplo 3 con $J=100$ rad/s³. ¿A qué tiende cuando $J\to\infty$?

**Serie C — Laboratorio**
- C1. Graficar $q$, $\dot q$, $\ddot q$ de `perfil_s` para los tres casos: alcanza $V$ y $A$; no alcanza $V$; no alcanza $A$.
- C2. (`⚠ romperlo a propósito`) Correr `codigo/bloque_19/romper_escalon.py`. Cambiar la derivada a `"medicion"` en el caso con prealimentación y observar cómo vuelve el error.

---

## Tema 19.4 — Trayectorias con puntos intermedios: *splines*

### 1. El problema

Para esquivar el borde de la cubeta, la pinza tiene que pasar por dos puntos intermedios. Detenerse en cada uno funciona, pero es lento y da golpes. ¿Cómo se pasa **por** los puntos sin detenerse?

### 2. El mecanismo

Un ***spline* cúbico** usa un polinomio cúbico por tramo, entre cada par de puntos consecutivos. Cada cúbico queda definido por las posiciones y **velocidades** en sus dos extremos (Tema 19.2). Las posiciones en los puntos están dadas. Las velocidades en los puntos intermedios se eligen para que **la aceleración también sea continua**: donde termina un tramo y empieza el siguiente, las dos aceleraciones deben coincidir.

Para el tramo $i-1$ (de $t_{i-1}$ a $t_i$, duración $h_{i-1}$, avance $D_{i-1}=q_i-q_{i-1}$), la aceleración al final se obtiene evaluando $\ddot q=2a_2+6a_3t$ en $t=h_{i-1}$ con los coeficientes del Tema 19.2:

$$\ddot q_{fin} = \frac{-6D_{i-1} + (2v_{i-1}+4v_i)h_{i-1}}{h_{i-1}^2}$$

Para el tramo $i$, la aceleración al inicio es $2a_2$:

$$\ddot q_{ini} = \frac{6D_i - (4v_i+2v_{i+1})h_i}{h_i^2}$$

Igualándolas, multiplicando por $h_{i-1}h_i/2$ y agrupando por velocidades:

$$h_i\,v_{i-1} + 2(h_{i-1}+h_i)\,v_i + h_{i-1}\,v_{i+1} = 3\left(\frac{h_i}{h_{i-1}}D_{i-1} + \frac{h_{i-1}}{h_i}D_i\right)$$

Hay una ecuación por cada punto intermedio, y cada una solo involucra tres velocidades vecinas: un sistema **tridiagonal**. Las velocidades del primer y del último punto se fijan (cero, para arrancar y terminar quieto). `robotica.trayectorias.spline_cubica` arma y resuelve este sistema.

**Sincronización.** Con varias articulaciones, cada una recibe su propio spline con **los mismos instantes** $t_i$: todas pasan por su ángulo del punto $i$ en el mismo momento, así que la pinza pasa por el punto $i$. Si cada articulación usa su propio perfil más rápido (por ejemplo, trapezoidales independientes), llegan a su ángulo en instantes distintos y **la pinza no pasa por el punto**.

### 3. En la vida real

`codigo/bloque_19/spline_puntos_via.py`: cuatro puntos en el plano, pasados a ángulos con la inversa, spline por articulación en los instantes 0, 0.8, 1.4 y 2.2 s.

```
articulación 1: máx |propio - scipy| = 2.2e-16 rad, en q'' 8.9e-16
articulación 2: máx |propio - scipy| = 6.7e-16 rad, en q'' 4.4e-15

Velocidad al pasar por cada punto [rad/s] (spline):
  t = 0.8 s: θ1' = -0.630, θ2' = -0.289
  t = 1.4 s: θ1' = -0.973, θ2' = +1.004

Trapezoidal deteniéndose en cada punto, cada articulación con su propio reloj:
  articulación 1 termina en 1.90 s, articulación 2 en 2.01 s (el spline: 2.20 s)
  distancia mínima de la punta a cada punto intermedio:
    (0.40, +0.20): trapezoidal sin sincronizar  0.91 cm, spline  0.00 cm
    (0.40, +0.05): trapezoidal sin sincronizar  1.08 cm, spline  0.00 cm
```

El spline propio coincide con `scipy.interpolate.CubicSpline` (condición `"clamped"`) hasta el redondeo: la librería profesional resuelve el mismo sistema. Con los mismos límites, detenerse en cada punto no fue más lento aquí, porque el trapezoidal usa la aceleración máxima todo el tiempo y los instantes del spline los eligió una persona. Pero sin sincronizar, la punta pasó a 1 cm de los puntos: para un huevo, eso es la diferencia entre tomarlo y empujarlo.

### 4. Limitaciones

- El spline pasa por los puntos, pero **entre ellos puede pasarse** (sobreoscilar), sobre todo si los intervalos de tiempo son muy desiguales. Hay que verificar que no se salga de los límites articulares.
- Los instantes $t_i$ los elige quien planifica. Elegirlos para respetar $V$ y $A$ con el tiempo mínimo es un problema de optimización (fuera del alcance del curso).
- En el espacio articular, la pinza no sigue rectas entre los puntos (Tema 19.1).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La pinza no pasa por el punto intermedio, aunque cada motor pasa por su ángulo | Articulaciones sin sincronizar: cada una llega a su ángulo en otro instante | Calcular la directa en un eje de tiempo común y medir la distancia al punto | Mismos instantes para todas las articulaciones (spline con $t_i$ comunes, o estirar la más rápida) |
| Entre dos puntos cercanos, el brazo hace una "panza" o golpea un límite | Sobreoscilación del spline con intervalos de tiempo mal elegidos | Graficar $q(t)$ entre los puntos | Redistribuir los $t_i$ en proporción a la distancia |
| El brazo se detiene en cada punto intermedio | Se usaron interpoladores de reposo a reposo por tramo | Mirar $\dot q$ en los puntos intermedios: cero | Spline, o cúbicos con velocidades de paso |

### 6. Dónde más aparece la idea

Las curvas de las fuentes tipográficas y de los programas de dibujo vectorial (Bézier, B-splines); el trazado de carreteras y vías de tren (para que la curvatura no salte); la interpolación de datos en cualquier hoja de cálculo que "suaviza" una gráfica.

### 7. Ejemplos resueltos

**Ejemplo — Un solo punto intermedio, a mano.** Puntos $q=0,\,1,\,0$ en $t=0,\,1,\,2$ s, velocidades inicial y final cero. $h_0=h_1=1$, $D_0=1$, $D_1=-1$. La ecuación del punto intermedio es

$$1\cdot0 + 2(1+1)v_1 + 1\cdot0 = 3\left(1\cdot1 + 1\cdot(-1)\right) = 0 \quad\Longrightarrow\quad v_1 = 0$$

Por simetría, pasa por el punto alto con velocidad cero. Con $q=0,\,1,\,2$ (sigue subiendo): $4v_1=3(1+1)$, así que $v_1=1.5$ rad/s y pasa sin detenerse.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué el sistema de las velocidades es tridiagonal?
- A2. ¿Por qué sincronizar articulaciones no importa si solo interesan el inicio y el destino, pero sí con puntos intermedios?

**Serie B — Cálculo a mano**
- B1. Velocidad de paso para $q=0,\,1,\,3$ en $t=0,\,1,\,2$.
- B2. Lo mismo con $t=0,\,0.5,\,2$. ¿Por qué cambia?

**Serie C — Laboratorio**
- C1. Verificar B1 y B2 con `spline_cubica` y con `scipy.interpolate.CubicSpline`.
- C2. Correr `codigo/bloque_19/spline_puntos_via.py` y mover los instantes intermedios hasta que la punta pase a más de 2 cm de alguna recta entre puntos.

---

## Tema 19.5 — Línea recta cartesiana y singularidades

### 1. El problema

La pinza tiene que recorrer una recta, por ejemplo para bajar en vertical sobre el huevo o para barrer una fila de la cubeta. Se genera la recta con su ley temporal, se resuelve la inversa en cada instante y listo. ¿Qué puede salir mal?

### 2. El mecanismo

Una recta de $P_1$ a $P_2$ con una ley temporal $s(t)$ (de 0 a 1, por ejemplo quíntica):

$$P(t) = P_1 + s(t)\,(P_2 - P_1), \qquad \dot P(t) = \dot s(t)\,(P_2 - P_1)$$

En cada instante, $\vec q(t)=$ inversa$(P(t))$. La velocidad de las articulaciones es la de la Jacobiana (Bloque 13):

$$\dot{\vec q} = J(\vec q)^{-1}\,\dot P$$

Para el 2R, $\det J=L_1L_2\sin\theta_2$. Cerca de $\theta_2=0$ (brazo estirado) o de $\theta_2=\pi$ (brazo plegado), el determinante se acerca a cero, $J^{-1}$ se hace enorme, y una velocidad de la pinza modesta pide **velocidades articulares enormes**. Ninguna ley temporal lo arregla: la geometría pide girar mucho para avanzar poco.

Con $L_1=0.30$ y $L_2=0.20$, el brazo plegado alcanza como mínimo $L_1-L_2=0.10$ m del hombro: hay un **círculo interior que no se alcanza**. Una recta que pasa por encima del hombro, cerca de ese círculo, obliga a plegar el brazo casi del todo y a girar el hombro casi media vuelta en muy poco tiempo. Si la recta entra al círculo, la inversa no tiene solución a mitad de camino.

### 3. En la vida real

`codigo/bloque_19/romper_singularidad.py`, recta horizontal de $x=-0.3$ a $0.3$ m en 2 s, a distintas alturas:

```
 altura y   θ2 máx  |sin θ2| mín  |θ1'| máx  |θ2'| máx    J⁻¹ẋ en el pico
    0.300   109.5°         0.909       1.91       1.34              -1.91
    0.200   138.6°         0.661       2.82       1.49              -2.82
    0.130   160.5°         0.334       4.80       1.82              -4.80
    0.105   172.5°         0.130       7.43       2.09              -7.43
    0.090  sin solución en la muestra 1845 (x = -0.043 m, r = 0.100 m < 0.10)
```

La última columna calcula $\dot\theta_1$ con la Jacobiana en el instante del pico, y coincide con la derivada numérica de los ángulos (la misma cuenta por dos caminos). Un servo de aficionado típico gira a unos 5 rad/s: a $y=0.105$ m, la recta ya es imposible.

`resolver_trayectoria` (portado de manipuladores) devuelve `estado="sin_solucion"` y el índice del punto que falló, en lugar de devolver ángulos a medias.

### 4. Limitaciones

- La inversa geométrica elige una rama (codo arriba). Si se cambia de rama a mitad de camino, los ángulos saltan. Por eso `resolver_trayectoria` usa siempre la misma fila, y el script aplica `np.unwrap` para que $\theta_1$ no salte de $+\pi$ a $-\pi$.
- En brazos de 6 GDL las singularidades son más (muñeca, hombro, codo) y más difíciles de ver a ojo. La manipulabilidad del Bloque 13 permite vigilarlas punto a punto.
- Resolver la inversa en cada instante cuesta cálculo. En este curso se hace en el computador, que manda los ángulos al microcontrolador (Tema 19.6).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| En una recta, una articulación de pronto gira muy rápido y el brazo "da un latigazo" | Cerca de una singularidad: $\det J\to0$ | Calcular $\lvert\sin\theta_2\rvert$ o la manipulabilidad a lo largo del camino | Mover la recta, frenar cerca de la singularidad, o pasar a movimiento articular en ese tramo |
| La trayectoria cartesiana falla a mitad de camino aunque sus extremos son alcanzables | La recta entra en una zona no alcanzable | `resultado.indice_fallo` y la distancia al hombro | Otro camino |
| Los ángulos saltan casi $2\pi$ entre dos muestras | La inversa devuelve ángulos en $(-\pi,\pi]$ y el camino cruzó $\pm\pi$ | Buscar diferencias mayores que $\pi$ entre muestras | `np.unwrap` sobre la secuencia de ángulos |
| Los ángulos saltan a otra configuración | Cambio de rama de la inversa (codo arriba a codo abajo) | Comparar el signo de $\theta_2$ entre muestras | Fijar la rama, o elegir en cada punto la solución más cercana a la anterior |

### 6. Dónde más aparece la idea

El *gimbal lock* del Bloque 09 es la misma enfermedad en la orientación: cerca de la singularidad, un giro pequeño de la cámara pide girar mucho un cardán. En un brazo humano, intentar mover la mano en línea recta pasando cerca del hombro obliga a girar el brazo de golpe.

### 7. Ejemplos resueltos

**Ejemplo — Velocidad del hombro en el punto más cercano, a mano.** Recta a $y=0.13$ m. En $x=0$ la punta está a $r=0.13$ m del hombro. Ley del coseno (Bloque 01): $\cos\theta_2=\frac{r^2-L_1^2-L_2^2}{2L_1L_2}=\frac{0.0169-0.13}{0.12}=-0.943$, así que $\theta_2=160.5^\circ$ y $\sin\theta_2=0.334$, como la tabla. La velocidad de la punta en ese instante (mitad del recorrido, quíntica) es $1.875\cdot0.6/2=0.5625$ m/s, horizontal, es decir perpendicular a la línea hombro-punta. Escribiendo $\theta_1=\beta-\alpha$ como en la inversa del Bloque 12 ($\beta$: dirección de la punta vista desde el hombro; $\alpha$: cuánto la desvía el codo, que solo depende de $r$): en $x=0$ la distancia $r$ no cambia, así que $\dot\alpha=0$ y todo el giro es $\dot\beta=v/r=0.5625/0.13=4.33$ rad/s. La simulación da 4.327 en ese instante. El pico de la tabla, 4.80, llega un poco después ($x=+3$ cm), cuando $r$ empieza a crecer y el codo al desplegarse suma su $\dot\alpha$. A $y=0.2$ m la misma cuenta da $0.5625/0.2=2.81$ y la tabla, 2.82.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué ninguna ley temporal $s(t)$ elimina el problema de la singularidad, pero sí puede atenuarlo?
- A2. ¿Dónde están las singularidades del 2R dentro de su espacio de trabajo? ¿Cuáles puede cruzar una recta?

**Serie B — Cálculo a mano**
- B1. Repetir el ejemplo para $y=0.3$ m y comparar con la tabla. ¿Por qué ahí el pico queda más lejos de $v/r$?

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_19/romper_singularidad.py` y buscar la altura a partir de la cual el hombro pasa de 5 rad/s.
- C2. Modificar la ley temporal para que la recta vaya más despacio cerca de $x=0$ y mantenga $\lvert\dot\theta_1\rvert<5$ rad/s. ¿Cuánto se alarga el movimiento?

---

## Tema 19.6 — Muestreo de la trayectoria y periodo del controlador

### 1. El problema

La arquitectura del proyecto (Bloque 22) reparte el trabajo: el computador planifica (trayectorias, inversa) y el microcontrolador controla (el PID del Bloque 18, cada 1 ms). Entre los dos hay un enlace serie que no puede mandar mil puntos por segundo por cada motor. ¿Cada cuánto se manda la trayectoria, y qué hace el microcontrolador entre dos puntos?

### 2. El mecanismo

Si el computador manda un punto cada $T_e$ (**periodo de envío**) y el PID corre cada $t_s\ll T_e$, entre dos puntos el microcontrolador tiene que inventar la referencia:

- **Escalera (retener el último punto).** La referencia avanza a saltos de $\dot q\,T_e$. Cada salto es un pequeño escalón para el PID: el término P salta, y si se deriva el error, patea. Además la referencia va, en promedio, $T_e/2$ atrasada.
- **Interpolación lineal.** La trayectoria se conoce **de antemano**, así que el computador puede mandar cada punto un periodo antes de que se necesite. Con el punto actual y el siguiente, el microcontrolador interpola en línea recta en cada muestra: la referencia es una rampa suave, sin atraso.

El error de interpolar una curva con rectas de duración $T_e$ es del orden de $\frac18\ddot q\,T_e^2$: con la aceleración máxima de una quíntica de 1.5 rad en 1.5 s ($\approx3.8$ rad/s²) y $T_e=50$ ms, unos 1.2 mrad.

### 3. En la vida real

`codigo/bloque_19/muestreo_referencia.py`: la articulación del Bloque 18 sigue una quíntica de 1.5 rad en 1.5 s, con PID más prealimentación a 1 kHz:

```
   envío modo         error máx [mrad]  salto de u máx [V]
     1ms densa                    0.25               0.021
    20ms escalera                60.02              19.618
    20ms interpolada              0.22               0.044
    50ms escalera               241.56              18.082
    50ms interpolada              1.00               0.120
```

Con la escalera, cada punto nuevo produce un salto de casi 20 V en una muestra: el motor recibe un golpe cada 20 ms (un zumbido a 50 Hz). Interpolando, mandar cada 50 ms queda a 1 mrad del caso ideal, en línea con la estimación de 1.2 mrad.

### 4. Limitaciones

- Mandar puntos por adelantado exige un **búfer** en el microcontrolador y decidir qué hacer si se vacía (comunicación perdida). Es un tema de seguridad del Bloque 22.
- La interpolación lineal tiene velocidad discontinua en cada punto recibido. Si hiciera falta más suavidad, el computador puede mandar también la velocidad y el micro interpolar con cúbicos (Tema 19.2).
- El periodo de envío no puede ser tan largo que la interpolación lineal deforme la curva: la estimación $\frac18\ddot qT_e^2$ dice cuánto.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Zumbido a una frecuencia fija durante los movimientos, que desaparece en reposo | Referencia en escalera: cada punto nuevo es un escalón | La frecuencia del zumbido es $1/T_e$ | Interpolar en el microcontrolador |
| El brazo sigue bien la forma pero siempre va retrasado | Referencia retenida (escalera) o interpolada entre el punto anterior y el actual | Comparar el instante en que se pasa por cada punto con el planeado | Mandar los puntos con un periodo de adelanto |
| En movimientos rápidos, la pinza "corta las curvas" | $T_e$ demasiado largo para la curvatura de la trayectoria | Estimar $\frac18\ddot qT_e^2$ | Bajar $T_e$ o interpolar con cúbicos |

### 6. Dónde más aparece la idea

Los videojuegos en red reciben la posición de los otros jugadores 20-60 veces por segundo e **interpolan** entre paquetes para que se muevan suave. Si no, se ven "teletransportándose". El audio digital hace lo mismo al convertir muestras en sonido continuo.

### 7. Ejemplos resueltos

**Ejemplo — Cuánto se atrasa la escalera.** Con $T_e=20$ ms, la referencia retenida va en promedio 10 ms atrasada, y en el peor caso 20 ms. A la velocidad pico de la quíntica, $1.875\cdot1.5/1.5=1.875$ rad/s, 20 ms son $1.875\times0.02=37.5$ mrad. El error medido (60 mrad) es mayor porque cada salto además hace oscilar un poco el lazo.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. ¿Por qué se puede mandar la referencia "del futuro", y en qué caso no se podría?
- A2. ¿Qué debería hacer el microcontrolador si deja de recibir puntos a mitad de un movimiento?

**Serie B — Cálculo a mano**
- B1. Estimar el error de interpolación lineal con $T_e=100$ ms para la misma quíntica.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_19/muestreo_referencia.py` y agregar $T_e=100$ ms. Comparar con B1.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/trayectorias.py`:

| Función | Origen | Qué hace |
|---|---|---|
| `perfil_trapezoidal` | portada 1:1 de robotica-manipuladores | Un tramo trapezoidal (o triangular si es corto). |
| `interpolador_lineal`, `interpolador_trapezoidal` | portadas, con el tiempo corregido | Varios tramos, con el tiempo real de cada punto. |
| `linea`, `circulo`, `polilinea` | portadas 1:1 | Curvas cartesianas como arrays de puntos. |
| `resolver_trayectoria`, `ResultadoTrayectoria` | portadas, adaptadas | Inversa punto a punto, con estado y punto de falla. |
| `cubica`, `quintica` | originales | Polinomios con condiciones de velocidad (y aceleración) en los extremos. |
| `perfil_s` | original | Perfil de jerk limitado, siete fases integradas exactas. |
| `spline_cubica` | original | Spline cúbico con aceleración continua (sistema tridiagonal). |

Cambios respecto a manipuladores: radianes y metros; `interpolador_trapezoidal` ya no recibe `t` para reescalar, sino que encadena la duración real de cada tramo (el reescalado uniforme llevaba la velocidad a 1.65 rad/s con un límite de 1, ver `romper_ultimo_punto.py`); `resolver_trayectoria` recibe la inversa como función de un punto y los límites como array.

Verificación hecha antes de publicar: las funciones portadas dan **exactamente** los mismos valores que las de manipuladores, corriendo las dos. El spline propio coincide con `scipy.interpolate.CubicSpline` a $10^{-15}$. Cúbico y quíntico cumplen sus condiciones de borde, y sus derivadas coinciden con las numéricas. El perfil en S se probó en seis casos: llega exacto y respeta $V$, $A$ y $J$.

## Glosario del bloque

| Término | Definición |
|---|---|
| Trayectoria / camino | Posición en función del tiempo / solo la curva, sin horario. |
| Espacio articular / cartesiano | Interpolar los ángulos de los motores / la posición de la pinza. |
| Ley temporal $s(t)$ | Cómo se avanza a lo largo de un camino, de 0 a 1, en el tiempo. |
| Interpolador cúbico / quíntico | Polinomio de grado 3 / 5 que fija posición y velocidad / y además aceleración en los extremos. |
| Jerk | Derivada de la aceleración [rad/s³ o m/s³]; un salto de aceleración es jerk infinito. |
| Perfil trapezoidal | Acelerar a tope, crucero, frenar a tope: velocidad con forma de trapecio (o triángulo si el tramo es corto). |
| Perfil en S | Perfil con jerk limitado: la aceleración sube en rampa; siete fases. |
| Punto intermedio (de paso) | Punto por el que la trayectoria pasa sin necesariamente detenerse. |
| Spline cúbico | Un cúbico por tramo, con aceleración continua en los puntos de paso. |
| Sincronización | Hacer que todas las articulaciones lleguen a cada punto en el mismo instante. |
| Prealimentación (*feedforward*) | Acción calculada con el modelo a partir de la trayectoria, sumada a la del PID. |
| Periodo de envío $T_e$ | Cada cuánto el computador manda un punto de la trayectoria al microcontrolador. |
