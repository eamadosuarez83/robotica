# Bloque 16 — Actuadores, transmisiones y dimensionamiento

> **Problema que abre el bloque:** el modelo dice que el hombro necesita 2,3 N·m. ¿Qué motor se compra y con qué reductor?
>
> **Necesitas antes:** Bloque 15 (cierra la Parte IV). · **Lectura:** Barrientos, caps. 2 y 5 (modelo de actuadores); hojas de datos de fabricantes.

El Bloque 07 (Temas 7.5–7.6) ya presentó actuadores y reductores de forma cualitativa, con los
servos reales de `robotica-manipuladores` como ejemplo. Este bloque retoma esos mismos conceptos
con el modelo matemático completo, y cierra la Parte IV conectando la dinámica (Bloques 14-15) con
una decisión de ingeniería concreta: qué motor comprar.

## Tema 16.1 — Modelo del motor DC: parte eléctrica y parte mecánica

### 1. El problema

Los Bloques 14 y 15 dan un par $\tau(t)$ requerido. Un motor no recibe "par": recibe voltaje. Hace falta el modelo que conecta ambos mundos.

### 2. El mecanismo

Un motor DC tiene dos ecuaciones acopladas, una eléctrica y una mecánica:

$$V = Ri + L\frac{di}{dt} + K_e\omega \qquad\text{(eléctrica)}$$
$$J_m\dot\omega = K_t i - \tau_{carga} - b\omega \qquad\text{(mecánica, Bloque 06 Tema 6.2)}$$

con $R,L$ la resistencia e inductancia del devanado, $i$ la corriente, $\omega$ la velocidad angular del eje, $K_e$ la **constante de fuerza contraelectromotriz** (el motor, al girar, genera un voltaje que se opone a la corriente — por eso $-K_e\omega$ resta voltaje disponible), $K_t$ la **constante de par** (el par es proporcional a la corriente), $J_m$ la inercia propia del rotor, y $b$ la fricción viscosa (Bloque 06, Tema 6.6).

Para el **régimen estacionario** (velocidad e inductancia despreciable, $di/dt\approx0$), despejando $i=(V-K_e\omega)/R$ y sustituyendo en $\tau=K_ti$, se obtiene la **curva par-velocidad** que aparece en cualquier datasheet:

$$\tau = \frac{K_tV}{R} - \frac{K_tK_e}{R}\omega = \tau_{parada}\left(1-\frac{\omega}{\omega_{vac}}\right)$$

una recta: **par de parada** $\tau_{parada}=K_tV/R$ (el máximo par, a velocidad cero) y **velocidad en vacío** $\omega_{vac}=V/K_e$ (la máxima velocidad, sin ninguna carga). Todo punto de operación real está en algún lugar de esta recta, nunca fuera de ella.

### 3. En la vida real

```python
def par_disponible(omega, V, Kt, Ke, R):
    tau_parada = Kt * V / R
    omega_vacio = V / Ke
    return tau_parada * (1 - omega / omega_vacio)
```

### 4. Limitaciones

El modelo estacionario ignora la inductancia $L$ (válida cuando los cambios de corriente son lentos comparados con la constante de tiempo eléctrica $L/R$, casi siempre cierto para motores pequeños de robótica) y asume $K_t=K_e$ en unidades consistentes (cierto por conservación de energía, pero con distintas unidades reportadas según el fabricante — hay que verificar).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un motor "se queda sin fuerza" a alta velocidad, aunque el par pico del datasheet parecía suficiente | Se comparó contra el par de parada ($\omega=0$), no contra el par disponible a la velocidad real de operación (Tema 16.6) | Evaluar la curva par-velocidad en la $\omega$ real, no solo en $\omega=0$ | Verificar el par disponible en todo el rango de velocidad de la tarea, no solo en reposo |

### 6. Dónde más aparece la idea

Cualquier motor eléctrico (de un taladro a un vehículo eléctrico) tiene esta misma curva par-velocidad lineal en su régimen normal de operación.

### 7. Ejemplos resueltos

**Ejemplo:** motor con $V=12$ V, $K_t=0.05$ N·m/A, $K_e=0.05$ V·s/rad, $R=2\,\Omega$: $\tau_{parada}=0.05\times12/2=0.3$ N·m, $\omega_{vac}=12/0.05=240$ rad/s ($\approx2300$ rpm). A $\omega=120$ rad/s (la mitad de la velocidad en vacío), el par disponible es $0.3\times(1-120/240)=0.15$ N·m — la mitad del par de parada.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el par disponible de un motor DC siempre disminuye al aumentar la velocidad, en términos de la fuerza contraelectromotriz.

**Serie B — Cálculo a mano**
- B1. Para el motor del ejemplo, calcular el par disponible a 60 rad/s y a 200 rad/s.

**Serie C — Laboratorio**
- C1. Graficar la curva par-velocidad completa del ejemplo con Matplotlib, marcando $\tau_{parada}$ y $\omega_{vac}$.

---

## Tema 16.2 — Reductores: multiplicar par, dividir velocidad, reflejar inercia

### 1. El problema

El motor del Tema 16.1 da como máximo 0.3 N·m; una articulación puede necesitar varios N·m. El Bloque 07 (Tema 7.6) ya presentó la idea del reductor; aquí se usa cuantitativamente para dimensionar.

### 2. El mecanismo

Un reductor de relación $N$ (por cada $N$ vueltas del motor, el eslabón da 1) transforma, del lado del motor al lado de la carga:

$$\tau_{carga} = N\,\tau_{motor}, \qquad \omega_{carga}=\frac{\omega_{motor}}{N}$$

Y, el efecto menos intuitivo pero crucial para el dimensionamiento: la inercia de la carga, **vista desde el motor**, se divide entre $N^2$:

$$J_{reflejada} = \frac{J_{carga}}{N^2}$$

(consecuencia de que la energía cinética debe ser la misma vista desde cualquier lado del reductor: $\tfrac12J_{carga}\omega_{carga}^2=\tfrac12J_{reflejada}\omega_{motor}^2$, y $\omega_{carga}=\omega_{motor}/N$ da $J_{reflejada}=J_{carga}/N^2$). Un reductor grande no solo multiplica el par: también hace que la inercia del brazo sea mucho más fácil de mover para el motor, muchas veces más importante en la práctica que el propio aumento de par.

La **inercia de carga** que "ve" cada articulación, para el dimensionamiento, se estima con la diagonal de la matriz de masas $M(\vec q)$ del Bloque 14 (Tema 14.5): $M_{ii}$ es, aproximadamente, la inercia que la articulación $i$ debe acelerar (ignorando el acoplamiento con las demás, una aproximación razonable para una primera estimación).

### 3. En la vida real

```python
tau_motor_necesario = tau_carga / N
J_motor_efectiva = J_motor_propia + J_carga / N**2
```

### 4. Limitaciones

Un reductor real tiene eficiencia $\eta<1$ (pérdidas por fricción interna, Tema 16.5): $\tau_{carga}=\eta N\tau_{motor}$, típicamente $\eta\approx0.7$–$0.95$ según el tipo.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un motor dimensionado sin considerar el reductor parece necesitar mucho más par del que realmente hace falta en el eje del motor | Se olvidó dividir el par de carga entre $N$ (o, al revés, se aplicó $N$ del lado equivocado) | Verificar que $\tau_{motor}=\tau_{carga}/N$, no $\tau_{carga}\times N$ | Aplicar la relación de reducción del lado correcto: multiplica par de motor a carga, divide de carga a motor |

### 6. Dónde más aparece la idea

La misma reflexión de inercia $N^2$ explica por qué la marcha corta de una bicicleta facilita subir una cuesta (mucho más fácil de "acelerar" la rueda) a costa de pedalear más rápido para la misma velocidad.

### 7. Ejemplos resueltos

**Ejemplo:** carga de $J_{carga}=0.02$ kg·m² con un reductor $N=50$: $J_{reflejada}=0.02/2500=8\times10^{-6}$ kg·m² — miles de veces menor, comparable o menor que la inercia propia de muchos rotores pequeños.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué duplicar $N$ reduce la inercia reflejada a un cuarto, no a la mitad.

**Serie B — Cálculo a mano**
- B1. Con $\tau_{carga}=2.3$ N·m (el problema que abre el bloque) y $N=50$, calcular el par que debe entregar el motor.

**Serie C — Laboratorio**
- C1. Usando la $M(\vec q)$ del Bloque 14 (`codigo/bloque_14/lagrange_2r.py`), estimar $J_{carga}$ del hombro del 2R en varias posturas y calcular la inercia reflejada para $N=20,50,100$.

---

## Tema 16.3 — Servomotores de aficionado por dentro

### 1. El problema

Los brazos de acrílico de `robotica-manipuladores` (Bloque 07) usan servos de hobby como caja negra: se les pide un ángulo y lo alcanzan. Vale la pena abrir esa caja para entender sus límites.

### 2. El mecanismo

Un servo de aficionado integra, en una sola caja: un motor DC pequeño (Tema 16.1), un reductor de engranajes plásticos o metálicos (Tema 16.2, $N$ típicamente entre 100 y 300), un **potenciómetro** (Bloque 07, Tema 7.7) acoplado al eje de salida que mide su posición, y un circuito controlador con un lazo de control **proporcional** simple: compara el ángulo pedido (codificado en el ancho de un pulso eléctrico, típicamente 1-2 ms) contra el que mide el potenciómetro, y aplica al motor un voltaje proporcional a esa diferencia (un adelanto del control P del Bloque 18).

Esto explica varias de sus limitaciones prácticas: la resolución angular está limitada por el potenciómetro (unos 0.3°-1° típico), el par disponible cae fuertemente si se le pide mantener una posición contra una carga externa grande (el error nunca llega exactamente a cero con control puramente proporcional, Bloque 18), y el rango de movimiento está limitado mecánicamente (0°-180° típico) por el propio potenciómetro, no por el motor.

### 3. En la vida real

La convención de los servos de `robotica-manipuladores` (`docs/especificaciones.md`, Bloque 07): `ángulo_servo = q + 90°`, limitando cada articulación a $q\in[-90°,90°]$ — una limitación de este diseño particular de servo, no de la cinemática del brazo.

### 4. Limitaciones

El controlador interno del servo no es accesible ni configurable en los modelos de aficionado más simples: no se puede, por ejemplo, cambiar la ganancia proporcional ni añadir compensación de gravedad (Bloque 20) sin reemplazar la electrónica interna.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un servo "tiembla" o vibra sosteniendo una carga que debería estar dentro de su rango de par | Ganancia proporcional interna demasiado alta para esa carga, o la carga se acerca al par máximo del servo (Tema 16.6) | Reducir la carga y ver si el temblor desaparece | Elegir un servo con más margen de par, o reforzar mecánicamente la carga para reducir su inercia efectiva (Tema 16.2) |

### 6. Dónde más aparece la idea

Cualquier servo de aeromodelismo o de electrónica de aficionado sigue este mismo diseño interno; es el actuador más común en proyectos de robótica de bajo costo.

### 7. Ejemplos resueltos

**Ejemplo:** el servo de la pinza de `tercer_corte_3gdl` (Bloque 07) usa el mismo diseño interno que los de las articulaciones, solo que su rango se interpreta como "cerrado" (0°) a "abierto" (90°) en vez de como un ángulo de eslabón.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué la resolución angular de un servo de aficionado está limitada por su potenciómetro y no por su motor DC interno.

**Serie B — Cálculo a mano**
- B1. Si un servo tiene un reductor interno $N=254$ y su motor DC tiene $\tau_{parada}=0.02$ N·m, estimar el par de parada disponible en el eje de salida (ignorando pérdidas).

**Serie C — Laboratorio**
- C1. Comparar, con las especificaciones de `robotica-manipuladores` (`docs/especificaciones.md`), el par y la velocidad de un servo típico contra lo que exige sostener el peso de un huevo (60 g) en la punta del brazo de acrílico (Bloque 13, Tema 13.7).

---

## Tema 16.4 — Motores paso a paso: pasos perdidos

### 1. El problema

El Bloque 07 (Tema 7.5) mencionó que un motor paso a paso "pierde pasos sin avisar". Hace falta entender el mecanismo para poder dimensionar de forma que eso no ocurra.

### 2. El mecanismo

Un motor paso a paso avanza en incrementos fijos alineando sus polos magnéticos con cada pulso eléctrico recibido; en principio, **conoce** su posición contando pulsos, sin necesitar un sensor de posición (Bloque 07, Tema 7.7) — su ventaja principal. El problema: si el par que exige la carga en un instante supera el **par máximo** que el motor puede producir a esa velocidad (una curva par-velocidad similar a la del Tema 16.1, aunque de forma distinta), el rotor no alcanza a alinearse con el siguiente pulso antes de que llegue el que sigue, y **pierde uno o más pasos** — sin ningún mecanismo interno que lo detecte ni lo reporte: el controlador sigue contando pulsos enviados, pero la posición real del eje ya no coincide.

Esto es exactamente el peligro que ilustra el "romper a propósito" del Bloque 16 (Tema 16.6): dimensionar un motor paso a paso solo por el par que hace falta en reposo, sin verificar el par disponible durante el movimiento rápido, deja el sistema expuesto a perder pasos justo cuando más se necesita precisión.

### 3. En la vida real

Los motores paso a paso, al carecer de retroalimentación de posición (a menos que se les añada un encoder aparte, Bloque 07 Tema 7.7), no pueden "darse cuenta" de un paso perdido: el error se acumula silenciosamente hasta la siguiente referencia de posición conocida (por ejemplo, un final de carrera, Bloque 07).

### 4. Limitaciones

Este bloque no cubre el modelo electromagnético detallado del motor paso a paso (torque de detención, resonancia); el punto clave para el dimensionamiento es solo que existe un par máximo dependiente de la velocidad, análogo al del motor DC.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un mecanismo con motor paso a paso pierde precisión progresivamente durante una tarea larga, sin ningún error reportado | Pasos perdidos acumulados por exceder el par disponible en algún tramo del movimiento | Añadir un sensor de posición externo (encoder, Bloque 07) y comparar contra la posición "esperada" por conteo de pulsos | Reducir la velocidad/aceleración en los tramos críticos, o sobredimensionar el motor con más margen |

### 6. Dónde más aparece la idea

Impresoras 3D y máquinas CNC de bajo costo (motores paso a paso sin retroalimentación), donde una capa "desalineada" en una impresión suele ser síntoma de pasos perdidos.

### 7. Ejemplos resueltos

**Ejemplo:** un motor paso a paso dimensionado con un margen de solo 10% sobre el par estático de sostenimiento, al pedirle una aceleración rápida (Tema 16.6, par pico dinámico), puede fácilmente superar su par disponible a esa velocidad y perder pasos, incluso si el par estático parecía suficiente.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un motor paso a paso "no sabe" que perdió un paso, a diferencia de un motor DC con encoder.

**Serie B — Cálculo a mano**
- B1. Si un motor paso a paso avanza 1.8° por paso, ¿cuántos pasos hacen falta para una vuelta completa? ¿Y con un reductor $N=10$ adicional?

**Serie C — Laboratorio**
- C1. Nada nuevo: se retoma en el laboratorio del Tema 16.6 (romper a propósito).

---

## Tema 16.5 — Fricción, juego mecánico y rigidez

### 1. El problema

El Bloque 06 (Tema 6.6) ya modeló la fricción viscosa y seca en la ecuación de movimiento; el Bloque 07 (Tema 7.6) mencionó el juego mecánico (*backlash*). Para dimensionar un actuador real hace falta cuantificar cuánto par adicional hay que reservar por estos efectos, que ningún modelo dinámico idealizado (Bloques 14-15) incluye por defecto.

### 2. El mecanismo

Tres efectos que consumen par sin mover el brazo:

- **Fricción** (Bloque 06, Tema 6.6): viscosa y seca en cada rodamiento y en el propio reductor; un reductor con eficiencia $\eta=0.8$ significa que el 20% del par del motor se pierde en fricción interna antes de llegar a la carga.
- **Juego mecánico** (*backlash*, Bloque 07 Tema 7.6): además del retraso al invertir el sentido de giro, el juego permite que la carga "golpee" ligeramente contra los dientes del engranaje en movimientos oscilatorios, generando picos de par transitorios que un modelo idealizado no predice.
- **Rigidez**: ningún eslabón ni reductor es perfectamente rígido; bajo carga, se flexionan una cantidad pequeña pero no nula, lo que puede hacer que la posición real de la pinza difiera de la calculada por la cinemática (Bloque 11) incluso con los ángulos articulares "correctos" — otra fuente de error que la calibración del Bloque 22 debe corregir.

### 3. En la vida real

Un **margen de seguridad** (Tema 16.6) del 30%-50% sobre el par calculado por Newton-Euler (Bloque 15) es la forma práctica y estándar de absorber estos efectos sin modelarlos uno por uno en detalle.

### 4. Limitaciones

Modelar estos efectos con precisión requiere datos del fabricante (eficiencia del reductor, juego especificado) o medición directa; en su ausencia, el margen de seguridad de la sección 3 es la aproximación razonable para este curso.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un motor dimensionado exactamente al par calculado por el modelo dinámico resulta insuficiente en la práctica | No se reservó margen para fricción, juego mecánico y otras pérdidas no modeladas | Comparar el par realmente necesario (medido) contra el calculado por el modelo idealizado | Aplicar un margen de seguridad (Tema 16.6) sobre el cálculo idealizado, nunca dimensionar al límite exacto |

### 6. Dónde más aparece la idea

Cualquier diseño de ingeniería reserva margen entre lo que el modelo predice y lo que se especifica (factor de seguridad en estructuras, sobredimensionamiento de fuentes de poder).

### 7. Ejemplos resueltos

**Ejemplo:** con un reductor de $\eta=0.85$ y un par de carga calculado de 2 N·m, el motor debe entregar, del lado del reductor, al menos $2/0.85\approx2.35$ N·m antes de aplicar ningún margen adicional por fricción externa o backlash.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un margen de seguridad "cubre" simultáneamente varios efectos no modelados en vez de requerir un modelo separado para cada uno.

**Serie B — Cálculo a mano**
- B1. Con $\tau_{carga}=2.3$ N·m, $\eta=0.85$ y un margen de seguridad del 40%, calcular el par mínimo que debe poder entregar el motor.

**Serie C — Laboratorio**
- C1. Nada nuevo: se aplica directamente en la hoja de dimensionamiento del Tema 16.6.

---

## Tema 16.6 — Dimensionamiento: par pico, RMS, velocidad, margen de seguridad

### 1. El problema

Con todos los ingredientes anteriores, falta el procedimiento completo: de una trayectoria deseada (Bloque 19, adelantado aquí de forma simplificada) y el modelo dinámico (Bloques 14-15), llegar a la especificación de motor y reductor que hace falta comprar.

### 2. El mecanismo

1. **Par requerido a lo largo del tiempo**, $\tau(t)$: se calcula con Newton-Euler (Bloque 15) evaluado en cada instante de la trayectoria deseada $\vec q(t),\dot{\vec q}(t),\ddot{\vec q}(t)$.
2. **Par pico**, $\tau_{pico}=\max_t|\tau(t)|$: el motor (con su reductor) debe poder entregarlo en el punto de la curva par-velocidad (Tema 16.1) correspondiente a la velocidad en ese mismo instante — no basta con que el par de parada sea suficiente si la velocidad en ese instante no es cero (la advertencia del Tema 16.1).
3. **Par eficaz o RMS** (*root mean square*), $\tau_{RMS}=\sqrt{\frac1T\int_0^T\tau(t)^2\,dt}$: relevante para el calentamiento del motor por efecto Joule (el calor disipado es proporcional a $i^2\propto\tau^2$, Tema 16.1) en un ciclo de trabajo repetido — un motor puede tolerar picos breves muy por encima de su par nominal continuo, pero no un $\tau_{RMS}$ sostenido por encima de él.
4. **Margen de seguridad** (Tema 16.5): multiplicar $\tau_{pico}$ y $\tau_{RMS}$ por un factor (típicamente 1.3-1.5) antes de comparar contra las especificaciones del motor candidato.
5. **Elegir $N$ (reductor) y el motor**: de forma que el par de parada del motor, multiplicado por $N$ y por la eficiencia $\eta$ (Tema 16.5), supere $\tau_{pico}$ con margen; que la velocidad en vacío del motor, dividida por $N$, supere la velocidad angular máxima requerida; y que el par continuo del motor supere $\tau_{RMS}$ con margen.

### 3. En la vida real

`codigo/bloque_16/hoja_dimensionamiento.py` implementa este procedimiento completo para el hombro del 2R: genera un movimiento simple punto a punto, calcula $\tau(t)$ con `robotica.dinamica.newton_euler_plano` (Bloque 15), obtiene $\tau_{pico}$ y $\tau_{RMS}$, y evalúa varios pares motor+reductor candidatos contra esos requisitos.

### 4. Limitaciones

Este procedimiento dimensiona **una** articulación con **una** trayectoria representativa; un dimensionamiento riguroso repite el cálculo para varias trayectorias y posturas (las más exigentes del espacio de trabajo, Bloque 07) antes de decidir.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un motor elegido solo por el par estático de sostenimiento se satura o pierde pasos en movimientos rápidos | No se calculó el par pico dinámico (que incluye inercia y Coriolis, Bloque 14, además de gravedad) — el estático es solo el término $G(\vec q)$, casi siempre menor que el par pico real | Comparar $\tau_{pico}$ (dinámico completo, Newton-Euler) contra el par estático $J^T\vec F$ (Bloque 13) para la misma postura | Dimensionar siempre por el par pico dinámico de la trayectoria más exigente, nunca solo por el estático |

### 6. Dónde más aparece la idea

Dimensionar cualquier actuador (motores de vehículos eléctricos, compresores, bombas) sigue el mismo patrón: pico para no saturar en el peor instante, RMS para no sobrecalentar en operación continua.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_16/romper_dimensionamiento_estatico.py` — el mismo hombro del 2R, dimensionado únicamente con el par estático de sostenimiento (Bloque 13), se satura claramente al pedirle un movimiento rápido, mientras que el mismo motor dimensionado con el par pico dinámico (este tema) tiene margen de sobra.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el par RMS puede ser mucho menor que el par pico, y por qué ambos son necesarios (uno para no saturar en el peor instante, el otro para no sobrecalentar).

**Serie B — Cálculo a mano**
- B1. Para un par que vale 3 N·m durante el 10% de un ciclo y 0.5 N·m el resto, estimar $\tau_{RMS}$ a mano.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_16/hoja_dimensionamiento.py` y `codigo/bloque_16/romper_dimensionamiento_estatico.py`, comparando ambos criterios de dimensionamiento para el mismo movimiento.

## Lo que este bloque agrega a `codigo/robotica/`

Nada nuevo: este bloque combina herramientas ya construidas (`robotica.dinamica.newton_euler_plano`, Bloque 15; `robotica.jacobiana.par_estatico`, Bloque 13) en un procedimiento de ingeniería, sin agregar funciones nuevas a la librería.

## Glosario del bloque

| Término | Definición |
|---|---|
| Constante de par / de velocidad ($K_t$, $K_e$) | Constantes que relacionan corriente con par, y velocidad con voltaje contraelectromotriz, en un motor DC. |
| Par de parada / velocidad en vacío | Los dos extremos de la curva par-velocidad lineal de un motor DC: máximo par (a $\omega=0$) y máxima velocidad (a $\tau=0$). |
| Inercia reflejada | Inercia de la carga, vista desde el motor a través de un reductor: $J_{carga}/N^2$. |
| Par pico | Máximo par requerido en cualquier instante de una trayectoria. |
| Par RMS (eficaz) | Raíz cuadrática media del par a lo largo de un ciclo; relevante para el calentamiento del motor. |
| Margen de seguridad | Factor multiplicativo (típicamente 1.3-1.5) aplicado al par calculado para absorber fricción, juego mecánico y otros efectos no modelados. |
