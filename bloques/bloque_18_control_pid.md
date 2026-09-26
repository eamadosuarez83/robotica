# Bloque 18 — Control PID de una articulación

> **Problema que abre el bloque:** un controlador proporcional deja al brazo colgando un poco por debajo, y si se sube la ganancia empieza a vibrar.
>
> **Necesitas antes:** Bloque 17. · **Lectura:** Barrientos, cap. 7 (control monoarticular); Åström & Murray, capítulo de PID.

## Tema 18.1 — Acción proporcional, integral y derivativa

### 1. El problema

El Bloque 17 (Tema 17.4) ya mostró un controlador **proporcional** puro: $u=K_p e$. Funciona, pero dos problemas típicos aparecen en la práctica: el sistema se asienta un poco *por debajo* del valor pedido (un **error en estado estacionario** persistente, más notorio cuando hay una carga constante como la gravedad sobre un brazo colgando), y subir $K_p$ para corregirlo produce oscilaciones cada vez más marcadas.

### 2. El mecanismo

El controlador **PID** combina tres acciones sobre el error $e(t)=r(t)-y(t)$ (Bloque 17, Tema 17.1):

$$u(t) = \underbrace{K_pe(t)}_{\text{proporcional}} + \underbrace{K_i\int_0^te(\tau)\,d\tau}_{\text{integral}} + \underbrace{K_d\dot e(t)}_{\text{derivativa}}$$

- **Proporcional**: corrige en proporción al error actual — simple, pero dejar *algún* error es matemáticamente necesario para que $u\neq0$ se siga aplicando (si $e=0$, $u=K_pe=0$, y sin ninguna acción la gravedad o la fricción devuelven el sistema a un punto con $e\neq0$).
- **Integral**: acumula el error a lo largo del tiempo, así que sigue creciendo **mientras** haya error, sin importar qué tan pequeño — esto es lo que finalmente empuja el error en estado estacionario a cero (un error constante, integrado por siempre, produce una acción de control que crece sin límite hasta que el error desaparece). El costo: agrega "memoria" al sistema, que puede sobrepasarse y oscilar más (el problema del Tema 18.4).
- **Derivativa**: reacciona a qué tan rápido está cambiando el error, **anticipando** hacia dónde va (si el error se acerca rápido a cero, la derivada frena la acción antes de llegar, reduciendo el sobrepaso, Bloque 17 Tema 17.4) — actúa como amortiguamiento adicional (Bloque 05, Tema 5.4), sin necesitar rediseñar la planta física.

### 3. En la vida real

`robotica.control.PID` implementa las tres acciones en forma discreta (Tema 18.6), con anti-windup (Tema 18.4) y derivada sobre la medición (Tema 18.5).

```python
from robotica.control import PID
pid = PID(Kp=5.0, Ki=2.0, Kd=0.1, Ts=0.001, u_min=-10, u_max=10)
u = pid.actualizar(referencia, medicion)   # un paso, cada Ts segundos
```

### 4. Limitaciones

Un PID es un controlador **lineal**, diseñado sobre el modelo linealizado del Bloque 17; no usa el modelo dinámico completo del brazo (Bloques 14-15) — el Bloque 20 retoma esa información con el par calculado.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El sistema se asienta permanentemente por debajo del valor pedido | Falta acción integral (o $K_i$ demasiado pequeña) para eliminar el error en estado estacionario | Verificar si $K_i=0$ o muy pequeña | Agregar o aumentar $K_i$ (con cuidado del windup, Tema 18.4) |
| El sistema oscila cada vez más al subir $K_p$ | Ganancia proporcional demasiado alta para el amortiguamiento natural del sistema (Bloque 17, Tema 17.5: los polos en lazo cerrado se acercan al eje imaginario) | Reducir $K_p$ y ver si las oscilaciones disminuyen | Bajar $K_p$, o agregar acción derivativa para compensar (Tema 18.1, sección 2) |

### 6. Dónde más aparece la idea

El PID es, con diferencia, el controlador más usado en la industria (más del 90% de los lazos de control industrial, según estimaciones estándar del área): control de temperatura, de nivel de líquido, de velocidad de motores, de casi cualquier proceso con una sola entrada y una sola salida.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_18/pid_articulacion.py`, que compara P puro, PI y PID completo sobre la misma articulación del Bloque 17, mostrando cómo cada ganancia adicional corrige un problema distinto.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, sin fórmulas, por qué un controlador proporcional puro no puede eliminar completamente el error ante una carga constante (como la gravedad).

**Serie B — Cálculo a mano**
- B1. Si $e(t)$ es constante e igual a 0.1 rad durante 2 s, calcular cuánto contribuye el término integral a $u$ con $K_i=3$.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_18/pid_articulacion.py` y comparar las respuestas al escalón de P, PI y PID.

---

## Tema 18.2 — Control monoarticular: cada motor con su propio lazo

### 1. El problema

Un brazo de $n$ GDL tiene $n$ motores acoplados dinámicamente (Bloque 14, Tema 14.5: los términos de Coriolis $C(\vec q,\dot{\vec q})$ mezclan las articulaciones entre sí). Diseñar un PID separado para cada articulación, ignorando ese acoplamiento, parece contradictorio — pero es, en la práctica, el punto de partida estándar.

### 2. El mecanismo

El **control monoarticular** trata cada articulación como un sistema independiente de una entrada y una salida (Bloque 17), con un PID propio (Tema 18.1), y considera el efecto de las demás articulaciones (los términos de Coriolis y el acoplamiento inercial fuera de la diagonal de $M(\vec q)$, Bloque 14) como una **perturbación externa** más, del mismo tipo que la fricción o una carga desconocida — algo que el propio lazo de realimentación (Bloque 17, Tema 17.1) debe tolerar sin necesitar modelarlo explícitamente.

Esto funciona razonablemente bien cuando los movimientos son **lentos** (los términos de Coriolis, cuadráticos en $\dot{\vec q}$, Bloque 14 Tema 14.5, son pequeños) o cuando el reductor de cada articulación (Bloque 16, Tema 16.2) es grande: un reductor grande reduce, por la reflexión de inercia $1/N^2$, la influencia relativa de lo que pasa en las demás articulaciones sobre cada motor individual. Para movimientos rápidos y reductores pequeños, el acoplamiento deja de ser una perturbación despreciable, y hace falta el control basado en el modelo completo del Bloque 20.

### 3. En la vida real

`codigo/bloque_18/pid_articulacion.py` diseña el PID de una sola articulación aislada; el Bloque 20 retoma el mismo brazo con las demás articulaciones moviéndose a la vez, para comparar cuánto empeora el control monoarticular frente al par calculado.

### 4. Limitaciones

Como se explicó, el control monoarticular degrada su desempeño cuanto más rápido y más acoplado es el movimiento — una limitación conocida y aceptada, no un error de diseño.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un PID que funciona bien en una articulación aislada se desempeña mal cuando el brazo completo se mueve rápido | El acoplamiento entre articulaciones (Coriolis, Bloque 14) ya no es una perturbación despreciable | Comparar el error de seguimiento con el brazo completo en movimiento contra la articulación aislada | Reducir la velocidad del movimiento, aumentar el reductor, o usar par calculado (Bloque 20) |

### 6. Dónde más aparece la idea

Cualquier sistema multivariable controlado con lazos independientes por canal (control de temperatura de varias zonas de un horno, cada una con su propio termostato, ignorando la transferencia de calor entre zonas).

### 7. Ejemplos resueltos

**Ejemplo:** con un reductor $N=100$ (Bloque 16), la inercia reflejada de un eslabón de $0.02$ kg·m² es solo $2\times10^{-6}$ kg·m² — mucho menor que la inercia propia del rotor del motor, así que el acoplamiento entre articulaciones apenas se nota del lado del motor.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un reductor grande hace que el control monoarticular sea una aproximación más razonable, retomando la reflexión de inercia del Bloque 16 (Tema 16.2).

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo: se retoma el cálculo de inercia reflejada del Bloque 16.

**Serie C — Laboratorio**
- C1. Nada nuevo todavía; se compara en el Bloque 20.

---

## Tema 18.3 — Sintonía: a mano, Ziegler-Nichols, por ubicación de polos

### 1. El problema

El PID tiene tres números que ajustar ($K_p,K_i,K_d$). Hace falta un procedimiento —no solo prueba y error indefinida— para elegirlos.

### 2. El mecanismo

Tres caminos, de más simple a más sistemático:

- **A mano** (prueba y error guiada): subir $K_p$ hasta que la respuesta sea razonablemente rápida con algo de sobrepaso tolerable; agregar $K_i$ pequeño para eliminar el error en estado estacionario (Tema 18.1), vigilando que no aparezcan oscilaciones nuevas; agregar $K_d$ para amortiguar el sobrepaso que quede. Funciona bien con algo de experiencia e intuición sobre el sistema.
- **Ziegler-Nichols** (el método clásico, de 1942, todavía citado en cualquier texto): subir $K_p$ (con $K_i=K_d=0$) hasta que el sistema oscile de forma sostenida (ni crece ni decae) ante una perturbación pequeña — esa ganancia crítica $K_u$ y el período de oscilación $T_u$ resultante se usan en una tabla de fórmulas (por ejemplo, para PID: $K_p=0.6K_u$, $K_i=2K_p/T_u$, $K_d=K_pT_u/8$) que da un punto de partida razonable, no óptimo, para refinar a mano después.
- **Por ubicación de polos** (el más sistemático, ligado directamente al Bloque 17): elegir dónde se quiere que estén los polos del sistema en lazo cerrado (Bloque 17, Tema 17.5 — por ejemplo, para lograr un cierto tiempo de establecimiento y sobrepaso, Tema 17.4) y despejar $K_p,K_i,K_d$ algebraicamente para que el denominador de la función de transferencia en lazo cerrado tenga esas raíces exactas.

### 3. En la vida real

```python
import control
# ubicación de polos con control.tf: se construye el lazo cerrado
# simbólicamente en función de Kp,Ki,Kd y se comparan sus polos contra
# los deseados, o se usa control.sisotool para ajustar interactivamente.
```

### 4. Limitaciones

Ziegler-Nichols da un punto de partida, casi nunca la sintonía final; llevar un sistema real al borde de la oscilación sostenida (necesario para hallar $K_u,T_u$) puede ser riesgoso en un brazo físico y se prefiere hacerlo primero en simulación.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Las ganancias de Ziegler-Nichols producen un sobrepaso mayor al deseado | Es un punto de partida, no una sintonía fina — la tabla clásica prioriza velocidad de respuesta sobre sobrepaso mínimo | Verificar la respuesta al escalón resultante (Bloque 17, Tema 17.4) contra la especificación real | Ajustar manualmente a partir del punto de Ziegler-Nichols, típicamente reduciendo $K_p$ o aumentando $K_d$ |

### 6. Dónde más aparece la idea

Cualquier sintonía de controlador en la industria empieza con alguna heurística estándar (Ziegler-Nichols u otras variantes) y se refina en el sistema real; el método de ubicación de polos es el mismo principio que el diseño de filtros y osciladores electrónicos.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_18/pid_articulacion.py`, que sintoniza la articulación del Bloque 17 a mano hasta lograr un sobrepaso menor al 15% y verifica el resultado con `control.step_info`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué llevar un sistema real a oscilación sostenida (para Ziegler-Nichols) es más seguro hacerlo primero en simulación que directamente en el brazo físico.

**Serie B — Cálculo a mano**
- B1. Con $K_u=8$ y $T_u=0.5$ s, calcular $K_p,K_i,K_d$ con las fórmulas de Ziegler-Nichols de la sección 2.

**Serie C — Laboratorio**
- C1. Verificar B1 en `codigo/bloque_18/pid_articulacion.py` y comparar la respuesta resultante contra la sintonía "a mano" del ejemplo resuelto.

---

## Tema 18.4 — Saturación del actuador y efecto *windup*

### 1. El problema

Ningún motor real da par infinito (Bloque 16): hay un límite físico de saturación. Cuando el error es grande y persiste (por ejemplo, al arrancar lejos del punto deseado), el término integral (Tema 18.1) sigue acumulando **aunque el actuador ya esté saturado y no pueda aplicar más**, y ese exceso acumulado ("*windup*") causa un sobrepaso grande y lento de corregir cuando el sistema finalmente se acerca al punto deseado.

### 2. El mecanismo

Mientras el actuador está saturado, el sistema real recibe siempre el mismo $u_{max}$ (o $u_{min}$), sin importar cuánto más crezca la salida "ideal" no saturada del PID — pero el término integral, si no se le avisa de esto, sigue sumando error como si su salida sí se estuviera aplicando. Cuando el error finalmente cambia de signo (el sistema ya alcanzó o pasó el punto deseado), esa integral acumulada de más tarda en "descargarse", manteniendo la salida saturada mucho después de que debería haber empezado a corregir — un sobrepaso grande y una respuesta visiblemente más lenta de lo esperado.

El **anti-windup** más simple (integración condicional, el que implementa `robotica.control.PID`): dejar de acumular en la integral mientras la salida esté saturada **y** seguir acumulando empujaría más en esa misma dirección — en cuanto el error cambia de signo (o el actuador deja de estar saturado), la integral vuelve a acumular con normalidad, sin ningún exceso que descargar.

### 3. En la vida real

```python
pid = PID(Kp=5.0, Ki=2.0, Kd=0.1, Ts=0.001, u_min=-2.0, u_max=2.0)  # límites de par (Bloque 16)
```

### 4. Limitaciones

La integración condicional es la técnica más simple de anti-windup; existen variantes más sofisticadas (*back-calculation*, con una realimentación explícita del exceso de saturación) que responden más suave en algunos casos, fuera del alcance de este curso.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un PID con actuador saturable sobrepasa mucho más de lo que predice la simulación sin límites de saturación | Efecto *windup*: la integral se acumuló de más mientras el actuador estaba saturado | Comparar la respuesta con y sin anti-windup activado para el mismo caso saturado | Activar anti-windup (límites `u_min,u_max` en `PID`, Tema 18.4) |

### 6. Dónde más aparece la idea

Cualquier controlador PID sobre un actuador real (válvulas, motores, calefactores) necesita anti-windup en la práctica; es uno de los errores de sintonía más comunes en sistemas industriales reales.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_18/romper_windup.py`, que compara la misma sintonía PID con y sin anti-windup ante un escalón grande que satura el actuador — sin anti-windup, el sobrepaso es visiblemente mayor y tarda mucho más en asentarse.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, en una frase, por qué el *windup* solo es un problema cuando el actuador está realmente saturado, no en operación normal.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo: es un efecto que se observa mejor simulando que calculando a mano.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_18/romper_windup.py` y medir cuánto mayor es el sobrepaso y el tiempo de establecimiento sin anti-windup.

---

## Tema 18.5 — Derivada del error contra derivada de la medición

### 1. El problema

Cambiar la referencia $r(t)$ de golpe (un escalón, Bloque 17 Tema 17.4) hace que $\dot e=\dot r-\dot y$ tenga un pico enorme en el instante del cambio (porque $\dot r$ es, en principio, infinito en un escalón ideal) — un "golpe derivativo" (*derivative kick*) que puede saturar el actuador innecesariamente, sin que el sistema realmente lo necesite.

### 2. El mecanismo

Como $\dot e=\dot r-\dot y$, y normalmente $r(t)$ cambia a saltos (una nueva referencia) mientras que $y(t)$ (la medición real) siempre cambia de forma continua (un brazo físico no puede teletransportarse), es preferible calcular el término derivativo usando **solo** $-\dot y$ (derivada de la medición, con signo cambiado) en vez de $\dot e$ completo — matemáticamente equivalente en régimen permanente (cuando $r$ ya no cambia, $\dot e=-\dot y$), pero sin el pico espurio al cambiar de referencia.

Además, derivar una señal medida **amplifica el ruido** (Bloque 04, Tema 4.6: la derivada de una señal ruidosa es mucho más ruidosa que la señal misma) — por eso `robotica.control.PID` incluye un **filtro de paso bajo** opcional sobre la derivada (parámetro `N_filtro`, Tema 18.5), que suaviza el ruido de alta frecuencia sin introducir mucho retraso en la parte útil de la señal.

### 3. En la vida real

`robotica.control.PID.actualizar` ya calcula la derivada sobre la medición por diseño (no sobre el error), con filtro opcional — la implementación por defecto de este curso ya incorpora esta buena práctica.

### 4. Limitaciones

Un filtro de paso bajo introduce algo de retraso (Bloque 17, Tema 17.5: un polo adicional en el lazo) — hay un compromiso entre filtrar bien el ruido y no desestabilizar el lazo con retraso adicional (el mismo fenómeno del Bloque 17, Tema 17.5, "romper a propósito").

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El actuador da un pico brusco de esfuerzo justo al cambiar la referencia, aunque el sistema estaba en reposo | Derivada calculada sobre el error completo ($\dot e$), no sobre la medición | Comparar la señal de control con derivada-sobre-error contra derivada-sobre-medición para el mismo escalón | Calcular la derivada solo sobre la medición (ya implementado en `robotica.control.PID`) |
| La señal de control es visiblemente ruidosa, con el motor "temblando" | Derivada sin filtrar amplificando el ruido del sensor | Activar el filtro (`N_filtro`) y comparar | Ajustar `N_filtro` (más bajo = más filtrado, pero más retraso) |

### 6. Dónde más aparece la idea

Cualquier controlador PID industrial real implementa "derivada sobre la medición" y algún filtro; es una de las diferencias más comunes entre la fórmula de libro de texto y una implementación de calidad de producción.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_18/pid_articulacion.py`, que compara la señal de control con y sin derivada-sobre-medición ante un cambio de referencia en escalón.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, en régimen permanente (referencia constante), da exactamente lo mismo derivar el error completo o solo la medición.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Agregar ruido gaussiano pequeño a la medición en `codigo/bloque_18/pid_articulacion.py` y comparar la señal de control con y sin `N_filtro`.

---

## Tema 18.6 — Control digital: periodo de muestreo y discretización

### 1. El problema

Todo lo anterior se pensó en tiempo continuo, pero el controlador real corre en un microcontrolador (Bloque 22), que mide y actúa en instantes discretos separados por un **periodo de muestreo** $T_s$, no continuamente.

### 2. El mecanismo

La versión discreta del PID reemplaza la integral por una suma acumulada y la derivada por una diferencia entre muestras consecutivas — exactamente el método de Euler del Bloque 05 (Tema 5.5), aplicado aquí a la ley de control en vez de a una simulación:

$$u_k = K_pe_k + K_i\sum_{j=0}^ke_jT_s + K_d\frac{y_k-y_{k-1}}{T_s}$$

(la forma exacta que implementa `robotica.control.PID`, con la salvedad de derivar $y$ en vez de $e$, Tema 18.5). El **periodo de muestreo** $T_s$ no es un detalle de implementación menor: si es demasiado grande respecto a la dinámica del sistema (la misma idea del Bloque 05, Tema 5.6 — el paso de integración debe ser pequeño frente a la escala de tiempo del sistema), el controlador "ve" el sistema con retraso efectivo de hasta $T_s$, exactamente el mecanismo desestabilizador del Bloque 17 (Tema 17.5, romper a propósito con retardo): un $T_s$ demasiado grande puede desestabilizar un lazo que, en tiempo continuo, sería perfectamente estable.

Una regla práctica común: elegir $T_s$ al menos 10 veces más rápido que la dinámica más rápida que se quiere controlar (por ejemplo, si el sistema en lazo cerrado tiene un tiempo de establecimiento de 0.5 s, $T_s\lesssim0.05$ s es un punto de partida razonable).

### 3. En la vida real

`codigo/bloque_18/pid_articulacion.py` corre el mismo `robotica.control.PID` con distintos $T_s$ para mostrar el efecto; el mismo código Python del PID, casi línea por línea, se traduce después a C para el microcontrolador real (Bloque 22) — la estructura discreta ya está pensada para eso desde este bloque.

### 4. Limitaciones

Este bloque no cubre el diseño de controladores directamente en el dominio discreto (transformada Z); se diseña en continuo (Bloque 17-18) y se discretiza, válido mientras $T_s$ sea razonablemente pequeño frente a la dinámica del sistema.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un controlador que se ve estable en simulación continua oscila o se vuelve inestable al implementarse en un microcontrolador real | Periodo de muestreo demasiado grande respecto a la dinámica del lazo cerrado | Reducir $T_s$ en la simulación y ver si el problema desaparece | Elegir un $T_s$ más pequeño (más frecuencia de muestreo), o rediseñar el controlador considerando el muestreo desde el inicio |

### 6. Dónde más aparece la idea

Todo controlador digital real (desde un termostato programable hasta el control de un dron) enfrenta esta misma decisión de periodo de muestreo; es análogo al teorema de muestreo de Nyquist en procesamiento de señales.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_18/romper_muestreo_lento.py`, que aumenta $T_s$ progresivamente sobre el mismo PID bien sintonizado hasta que la respuesta, antes suave, empieza a oscilar.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un $T_s$ demasiado grande actúa, en la práctica, de forma similar al retardo de transporte del Bloque 17 (Tema 17.5).

**Serie B — Cálculo a mano**
- B1. Si el lazo cerrado tiene un tiempo de establecimiento de 0.2 s, estimar un $T_s$ razonable con la regla práctica de la sección 2.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_18/romper_muestreo_lento.py` y encontrar, por prueba, el $T_s$ aproximado donde el sistema deja de ser bien comportado.

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/control.py`: clase `PID` — control proporcional-integral-derivativo discreto, con anti-windup por integración condicional y derivada sobre la medición con filtro opcional.

## Glosario del bloque

| Término | Definición |
|---|---|
| PID | Controlador que combina acción proporcional, integral y derivativa sobre el error. |
| Control monoarticular | Diseñar un lazo de control independiente para cada articulación de un brazo, tratando el acoplamiento con las demás como perturbación. |
| Ziegler-Nichols | Método clásico de sintonía de PID a partir de la ganancia y el período de oscilación sostenida en lazo cerrado. |
| Windup | Acumulación excesiva del término integral mientras el actuador está saturado; anti-windup la evita. |
| Derivada sobre la medición | Calcular el término derivativo a partir de $-\dot y$ en vez de $\dot e$, para evitar el golpe derivativo ante un cambio de referencia. |
| Periodo de muestreo ($T_s$) | Intervalo de tiempo entre dos actualizaciones sucesivas de un controlador digital. |
