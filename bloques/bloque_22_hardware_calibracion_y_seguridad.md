# Bloque 22 — Hardware, calibración y seguridad

> **Problema que abre el bloque:** el modelo dice 0°, el servo dice 0°, y el brazo físico está torcido 7°.
>
> **Necesitas antes:** Bloque 21. · **Lectura:** Barrientos, cap. 9 (criterios de implantación y seguridad).

## Tema 22.1 — Arquitectura: computador y microcontrolador

### 1. El problema

Todo el curso hasta aquí corrió en un computador de escritorio, con Python y tiempo de cómputo casi ilimitado. Un brazo real necesita un lazo de control corriendo a un periodo de muestreo fijo y confiable (Bloque 18, Tema 18.6), algo que un sistema operativo de propósito general (con otros programas compitiendo por el procesador) no garantiza bien.

### 2. El mecanismo

La arquitectura típica de un brazo de este curso divide el trabajo en dos partes:

- **Computador** (Python): planificación de alto nivel — cinemática inversa (Bloque 12), generación de trayectorias (Bloque 19), la máquina de estados de la tarea (Bloque 23). No necesita tiempo real estricto: unos milisegundos de más al planificar no rompen nada.
- **Microcontrolador** (C o C++, a veces MicroPython): el lazo de control de bajo nivel (Bloque 18, el PID discreto) y la lectura de sensores (Tema 22.4), corriendo con un periodo de muestreo fijo y confiable — el microcontrolador no hace nada más, así que puede garantizar ese periodo de una forma que un computador de escritorio no puede.

Ambos se comunican por un canal serie (Tema 22.2): el computador manda referencias (ángulos deseados, Bloque 19), el microcontrolador devuelve el estado medido (Tema 22.4).

### 3. En la vida real

Los brazos de acrílico de `robotica-manipuladores` (Bloque 07) siguen exactamente esta arquitectura: MATLAB/Python en la computadora, Arduino como microcontrolador, comunicados por el protocolo del Tema 22.2.

### 4. Limitaciones

Para un servo de aficionado (Bloque 16, Tema 16.3), el propio servo ya trae su microcontrolador interno con el lazo PID incluido — en ese caso, "el microcontrolador" del sistema completo se reduce a generar la señal de pulso (PWM), sin implementar el PID propio del Bloque 18 explícitamente.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un lazo de control implementado en el computador (no en el microcontrolador) tiene un periodo de muestreo irregular | El sistema operativo interrumpe el proceso de Python para atender otras tareas | Medir el intervalo real entre actualizaciones sucesivas del lazo | Mover el lazo de control de bajo nivel al microcontrolador, o usar un sistema operativo de tiempo real si debe quedarse en el computador |

### 6. Dónde más aparece la idea

Cualquier sistema embebido con una parte de planificación (más lenta, más compleja) y una de control en tiempo real (más simple, más estricta): drones, impresoras 3D, electrodomésticos inteligentes.

### 7. Ejemplos resueltos

**Ejemplo:** `tercer_corte_3gdl` (Bloque 07) recibe, por cada servo, 4 bytes `[255, id, 240, ángulo]` desde la computadora — la comunicación mínima que hace falta para que el microcontrolador sepa qué ángulo mantener, sin que la computadora tenga que preocuparse del lazo de control interno del servo.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el periodo de muestreo del Bloque 18 es más fácil de garantizar en un microcontrolador dedicado que en un computador de escritorio con otros programas corriendo.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Nada nuevo todavía; se practica en el Tema 22.2.

---

## Tema 22.2 — Comunicación serie: protocolo simple

### 1. El problema

El computador y el microcontrolador (Tema 22.1) se comunican por un cable serie: una secuencia de bytes, sin ninguna estructura implícita. Hace falta un formato acordado de antemano —un protocolo— para que ambos lados sepan interpretar la misma secuencia de bytes de la misma forma, y para detectar si algo se corrompió en el camino.

### 2. El mecanismo

Un protocolo simple y suficiente para este curso, con tres partes:

- **Encabezado** (*header*): un byte fijo (por ejemplo, `255`) que marca "aquí empieza una trama nueva" — permite resincronizar si se perdió algún byte anterior.
- **Datos**: los bytes con la información real (a qué articulación, qué comando, qué valor) — la misma idea de `[255, id, 240, ángulo]` del Bloque 07.
- **Verificación** (*checksum*): un byte calculado a partir de los datos (por ejemplo, el complemento de su suma) que el receptor recalcula y compara; si no coincide, la trama se descarta en vez de ejecutarse con datos corrompidos.

Sin verificación, un solo bit alterado por ruido eléctrico en el cable (perfectamente posible, sobre todo con motores cerca) podría convertir "gira 10°" en "gira 200°" sin que nada lo detecte.

### 3. En la vida real

`codigo/bloque_22/protocolo_serie.py` implementa `codificar`/`decodificar` con esta estructura, verificado con una trama corrompida a propósito (Tema 22.2, laboratorio): el receptor la rechaza en vez de ejecutarla.

```python
from protocolo_serie import codificar, decodificar   # codigo/bloque_22/
trama = codificar(id_servo=2, comando=240, dato=130)
# ... enviar trama por pyserial (Serial.write) ...
# ... en el microcontrolador (o, en Python, al recibir): ...
mensaje, error = decodificar(trama_recibida)
```

### 4. Limitaciones

Un checksum simple (como la suma complementada) detecta la mayoría de los errores de un solo bit, pero no todos los patrones posibles de corrupción; protocolos más robustos (CRC) dan mejores garantías a cambio de algo más de cómputo — de sobra disponible en cualquier microcontrolador moderno, pero fuera del alcance de este curso.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El brazo ejecuta movimientos erráticos ocasionales, sin relación con lo que se le pidió | Tramas corrompidas por ruido eléctrico se están ejecutando sin verificación | Revisar si el protocolo de comunicación incluye y verifica un checksum | Agregar verificación y descartar (no ejecutar) las tramas que no coincidan |

### 6. Dónde más aparece la idea

Cualquier protocolo de comunicación serio (TCP/IP, USB, I2C) incluye verificación de integridad; es un principio universal de comunicación confiable sobre un canal que puede introducir errores.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_22/protocolo_serie.py`, que codifica, corrompe un bit a propósito, y confirma que `decodificar` lo rechaza.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el encabezado fijo (`255`) ayuda a "resincronizar" la comunicación si se perdió algún byte anterior.

**Serie B — Cálculo a mano**
- B1. Calcular a mano el checksum (complemento de la suma, módulo 256) de la trama de datos `[2, 240, 90]`.

**Serie C — Laboratorio**
- C1. Verificar B1 con `codigo/bloque_22/protocolo_serie.py` y confirmar que corromper cualquiera de los tres bytes de datos cambia el checksum esperado.

---

## Tema 22.3 — Calibración: ceros, sentido de giro, relación señal-ángulo

### 1. El problema

El problema que abre el bloque: el modelo (Bloque 11) dice que $\theta_1=0°$ corresponde a una postura concreta, pero el servo físico, al recibir la señal que "debería" ser $0°$, tiene el brazo torcido 7° — el cero del modelo y el cero mecánico real no coinciden, y nada en el software lo sabe hasta que se calibra.

### 2. El mecanismo

Tres números por articulación conectan el modelo (Bloque 11) con el hardware real:

- **Cero (offset)**: el desfase entre el ángulo que el modelo llama $0°$ y la posición física real del servo en ese instante — se mide llevando la articulación a una referencia física conocida (un tope mecánico, una marca) y registrando qué valor de señal corresponde a esa referencia.
- **Sentido de giro (signo)**: si la señal creciente hace que la articulación gire en el sentido que el modelo asume como positivo (Bloque 02, Tema 2.3: la regla de la mano derecha) o en el sentido contrario — se detecta comandando un cambio pequeño y conocido y observando hacia dónde se mueve realmente.
- **Relación señal-ángulo**: la conversión entre la unidad que entiende el actuador (por ejemplo, un valor de 0 a 255 para un servo de aficionado, Bloque 16 Tema 16.3) y el ángulo en radianes que usa el resto del modelo (Bloque 01: la conversión de unidades, ahora con una escala y un offset propios de cada servo, no solo $\pi/180$).

$$\theta_{modelo} = signo\times(\theta_{fisico}-\theta_{cero})$$

### 3. En la vida real

`codigo/bloque_22/calibracion.py` simula un brazo con un offset y verifica un procedimiento de calibración: comandar la articulación a $0°$ nominal, medir dónde queda realmente, y usar esa diferencia como offset — recuperando el offset "real" simulado con precisión numérica exacta, porque en la simulación se conoce la verdad de fondo.

### 4. Limitaciones

En un brazo físico real, "medir dónde queda realmente" no es tan directo como en la simulación: requiere algún método externo (una regla, un ángulo visual, un tope mecánico con posición conocida) — la simulación de este bloque verifica el *procedimiento*, no elimina la necesidad de medir algo físico en la práctica.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La cinemática directa (Bloque 11) predice una posición y el brazo físico llega sistemáticamente a otra, con un desfase aproximadamente constante | Falta calibrar el offset de una o más articulaciones | Comandar $\vec q=\vec0$ y medir la postura física real; comparar contra la postura de referencia del modelo | Calibrar el offset: $\theta_{cero}=$ la señal que corresponde a la referencia física conocida |
| El brazo se mueve en el sentido contrario al pedido | El signo de una articulación está invertido en la calibración | Comandar un cambio pequeño y positivo y verificar el sentido real del movimiento | Invertir el signo en la calibración de esa articulación (Tema 22.6, romper a propósito) |

### 6. Dónde más aparece la idea

Calibrar el cero de cualquier instrumento de medición (una balanza, un sensor de posición) antes de confiar en sus lecturas; el mismo principio en impresoras 3D (*homing* de los ejes).

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_22/calibracion.py`, que recupera un offset de $7°$ simulado con error menor a $10^{-6}$°.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué calibrar el offset sin verificar también el signo puede dejar una articulación "calibrada" pero moviéndose al revés.

**Serie B — Cálculo a mano**
- B1. Si el servo reporta $83°$ cuando el modelo debería estar en $90°$, calcular el offset.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_22/calibracion.py` y verificar B1 con la función de calibración del script.

---

## Tema 22.4 — Lectura de sensores: potenciómetros, encoders, ruido

### 1. El problema

El Bloque 07 (Tema 7.7) ya presentó los tipos de sensores de posición; falta ver cómo su lectura real —con ruido incluido— afecta al lazo de control (Bloque 18) y qué hacer al respecto.

### 2. El mecanismo

Ningún sensor da una lectura perfecta: un potenciómetro tiene ruido de contacto, un encoder puede perder pulsos por vibración eléctrica. El ruido de medición se modela típicamente como un valor aleatorio pequeño sumado a la lectura verdadera —el mismo tipo de ruido que ya motivó, sin nombrarlo así, el filtro de la derivada del Bloque 18 (Tema 18.5): derivar una señal ruidosa amplifica el ruido, por eso ese filtro importa en la práctica y no solo en la teoría.

### 3. En la vida real

```python
lectura_ruidosa = lectura_real + np.random.normal(0, sigma_ruido)
```

`codigo/bloque_22/calibracion.py` agrega ruido gaussiano pequeño a las mediciones simuladas para verificar que el procedimiento de calibración (Tema 22.3) sigue siendo razonablemente preciso incluso sin mediciones perfectas.

### 4. Limitaciones

El ruido gaussiano es un modelo simplificado; el ruido real de un sensor puede tener otras características (picos ocasionales grandes, deriva lenta) no capturadas por este modelo simple.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una calibración (Tema 22.3) da resultados distintos cada vez que se repite | El ruido de la medición no se promedió sobre varias lecturas | Repetir la medición varias veces y comparar la dispersión de los resultados | Promediar varias lecturas antes de usarlas para calibrar |

### 6. Dónde más aparece la idea

Cualquier sensor real en cualquier sistema de instrumentación tiene ruido; promediar mediciones repetidas para reducirlo es una técnica universal.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_22/calibracion.py`, que compara el offset calibrado con una sola lectura contra el promedio de 20 lecturas ruidosas.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué promediar $N$ lecturas independientes reduce el ruido en un factor de $\sqrt N$ (relacionarlo con la desviación estándar de un promedio).

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_22/calibracion.py` variando el número de lecturas promediadas y graficar cómo mejora la precisión del offset calibrado.

---

## Tema 22.5 — Errores que el modelo no ve

### 1. El problema

Incluso con una calibración perfecta (Tema 22.3), el brazo físico real se desvía del modelo por efectos que ningún bloque anterior modeló explícitamente.

### 2. El mecanismo

Tres fuentes recurrentes, ya mencionadas puntualmente en bloques anteriores y reunidas aquí:

- **Juego mecánico** (*backlash*, Bloque 07 Tema 7.6, Bloque 16 Tema 16.5): retraso al invertir el sentido de giro.
- **Flexión estructural** (Bloque 16, Tema 16.5): los eslabones y el propio reductor no son perfectamente rígidos; bajo carga, se doblan una cantidad pequeña pero no nula, desplazando la posición real de la pinza respecto a la calculada con la cinemática (Bloque 11).
- **Alimentación insuficiente**: si la fuente de poder no puede entregar suficiente corriente a todos los motores a la vez (por ejemplo, varios servos moviéndose simultáneamente, Bloque 16 Tema 16.1: más corriente significa más par), el voltaje disponible cae, y con él el par disponible — un motor puede "verse" con menos par del que su datasheet promete, no porque esté mal dimensionado, sino porque no está recibiendo el voltaje nominal.

### 3. En la vida real

Ninguno de estos efectos tiene una "solución de código" limpia; se mitigan con margen de diseño (Bloque 16, Tema 16.5: el margen de seguridad ya cubre implícitamente parte de esto) y, cuando el error importa, con calibración adicional específica para el efecto (por ejemplo, una tabla de corrección de flexión medida empíricamente).

### 4. Limitaciones

Este tema es deliberadamente un recordatorio y una lista de causas a revisar, no un desarrollo matemático nuevo — cada efecto ya se mencionó con más detalle en su bloque de origen.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El error de posición del brazo crece notoriamente cuando varios motores se mueven a la vez, comparado con moverlos uno por uno | Alimentación insuficiente para la corriente total demandada | Medir el voltaje de alimentación real durante el movimiento simultáneo | Usar una fuente de mayor capacidad de corriente, o secuenciar movimientos que antes eran simultáneos |
| El error de posición depende de la carga en la pinza, incluso con la calibración de ceros ya hecha | Flexión estructural bajo carga, no capturada por la cinemática rígida (Bloque 11) | Medir el error de posición con y sin carga, en la misma postura | Reforzar la estructura, o medir y corregir la flexión empíricamente si no se puede rediseñar |

### 6. Dónde más aparece la idea

Cualquier máquina real se desvía de su modelo ideal por estas mismas tres causas genéricas: backlash, flexión, alimentación — la lista corta que un técnico de mantenimiento revisa primero ante un error de posición inexplicado.

### 7. Ejemplos resueltos

**Ejemplo:** el `notas` de `tercer_corte_3gdl` en `robotica-manipuladores` (Bloque 07) ya documenta una fuente de error de este tipo: "el error de posición resultante [por redondear los ángulos de los servos a enteros] es menos de 0.5 cm" — un error del propio proceso de comandar el servo, no de la cinemática.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Proponer un experimento simple para distinguir si un error de posición se debe a flexión (depende de la carga) o a un offset de calibración mal hecho (no depende de la carga).

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Nada nuevo: se retoma en el laboratorio final del bloque (rejilla de puntos).

---

## Tema 22.6 — Seguridad: límites, parada de emergencia, pérdida de comunicación

### 1. El problema

Un brazo con motores reales puede lastimar a alguien o dañarse a sí mismo si un error de software (o de calibración, Tema 22.3) le pide algo peligroso. El software no puede ser la única línea de defensa.

### 2. El mecanismo

Tres medidas de seguridad, cada una independiente de que el resto del software esté funcionando correctamente:

- **Límites articulares por software**: verificar, antes de enviar cualquier comando, que esté dentro de los límites físicos conocidos (Bloque 07, Tema 7.1; ya usado en `Brazo.dentro_de_limites`, Bloque 11) — la primera línea de defensa, pero **no la única**, porque depende de que el propio software esté libre de errores.
- **Parada de emergencia**: un mecanismo —idealmente físico, no solo de software— que corta la energía a los motores inmediatamente, sin depender de que ningún programa siga respondiendo. Un botón de emergencia por software (una tecla que envía un comando de parada) es mejor que nada, pero un corte físico de alimentación es la protección real de última instancia.
- **Qué hacer al perder comunicación** (Tema 22.2): si el microcontrolador deja de recibir comandos del computador (cable desconectado, programa de la computadora colgado), **no debe** simplemente mantener el último comando indefinidamente — un timeout que, tras cierto tiempo sin recibir una trama válida, lleva el brazo a un estado seguro (detenerse, o ir a una postura de reposo conocida) es el comportamiento esperado.

### 3. En la vida real

```python
def comando_seguro(q_deseado, robot, ultimo_mensaje_hace_s):
    if ultimo_mensaje_hace_s > TIMEOUT:
        return None   # perdió comunicación: no enviar nada, mantener parada
    if not robot.dentro_de_limites(np.degrees(q_deseado)):
        return None   # fuera de límites: no enviar
    return q_deseado
```

### 4. Limitaciones

Ninguna medida de seguridad por software reemplaza completamente una protección física (un botón de emergencia físico, un fusible); el software reduce el riesgo, no lo elimina.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El brazo sigue ejecutando el último comando recibido, sin límite de tiempo, tras desconectarse el cable de comunicación | No hay timeout de pérdida de comunicación implementado en el microcontrolador | Desconectar el cable a propósito (en un entorno controlado) y observar el comportamiento | Implementar un timeout que detenga el brazo si no llega un comando válido dentro de un tiempo razonable |

### 6. Dónde más aparece la idea

Cualquier sistema con capacidad de causar daño físico (maquinaria industrial, vehículos autónomos, ascensores) implementa exactamente este tipo de defensas en capas independientes, ninguna dependiendo únicamente de que el software de más alto nivel funcione bien.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_22/romper_signo_invertido.py` (romper a propósito): un signo de calibración invertido en una sola articulación (Tema 22.3) hace que el brazo, al perseguir un objetivo calculado con cinemática inversa (Bloque 12), llegue a casi 11 cm del punto pedido — exactamente el tipo de error que los límites articulares (que sí verifican rango, pero no verifican que el signo sea el correcto) no habrían detectado por sí solos.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué los límites articulares por software, por sí solos, no habrían evitado el error del ejemplo resuelto (el ángulo comandado, con signo invertido, puede seguir estando dentro del rango permitido).

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_22/romper_signo_invertido.py` y confirmar el error de posición resultante de invertir el signo de calibración de una sola articulación.

## Laboratorio final del bloque: calibrar y medir en una rejilla de puntos

Con `codigo/bloque_22/calibracion.py` (Tema 22.3) y el brazo simulado con offset y ruido (Tema 22.4), calibrar las tres articulaciones de `curso_3gdl`, y luego comandar una rejilla de puntos conocidos (por ejemplo, un plano a $z$ constante, Bloque 19 Tema 19.4) verificando el error de posición resultante en cada uno — el mismo procedimiento, en simulación, que se haría con el brazo físico del Bloque 24.

## Lo que este bloque agrega a `codigo/robotica/`

Nada a la librería principal: los módulos de este bloque (`protocolo_serie.py`, `calibracion.py`) son específicos de hardware y viven en `codigo/bloque_22/`, no en `codigo/robotica/` (que reúne herramientas de modelado, no de comunicación con hardware específico).

## Glosario del bloque

| Término | Definición |
|---|---|
| Checksum | Byte de verificación calculado a partir de los datos de una trama, para detectar corrupción en la comunicación. |
| Offset (cero de calibración) | Desfase entre el ángulo que asume el modelo y la posición física real de una articulación. |
| Timeout de comunicación | Tiempo máximo sin recibir un comando válido antes de que el sistema pase a un estado seguro. |
| Backlash (juego mecánico) | Holgura en un reductor que retrasa la transmisión de movimiento al invertir el sentido de giro (Bloque 07, Bloque 16). |
