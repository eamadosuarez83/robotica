# Bloque 23 — Programación de tareas

> **Problema que abre el bloque:** el brazo ya se mueve bien. Ahora tiene que hacer un trabajo repetido todo el día sin supervisión.
>
> **Necesitas antes:** Bloque 22. · **Lectura:** Barrientos, caps. 8 y 10.

## Tema 23.1 — Niveles de programación: guiado y textual

### 1. El problema

Todo el curso hasta aquí programó el brazo escribiendo Python. En la práctica industrial, buena parte de la programación de tareas se hace de una forma completamente distinta, sin escribir código en absoluto.

### 2. El mecanismo

Dos formas de programar una tarea:

- **Programación guiada** (*teach and playback*): un operador mueve físicamente el brazo (a mano, o con un control remoto) hasta cada posición relevante, y el sistema **graba** esa posición como un punto de enseñanza (Tema 23.2). La tarea completa es la secuencia de puntos grabados, reproducida después. No requiere saber programar, y es el método dominante en la industria para tareas repetitivas simples.
- **Programación textual**: la tarea se describe con código (como en este curso) o con un lenguaje específico del fabricante (RAPID de ABB, KRL de KUKA). Más flexible (permite lógica condicional, manejo de errores, Tema 23.4) pero requiere más entrenamiento.

En la práctica, la mayoría de las instalaciones reales combinan ambas: los puntos se enseñan guiando el brazo (más rápido y preciso que calcularlos a mano), y la lógica de la tarea (el orden, las condiciones, el manejo de errores) se programa textualmente.

### 3. En la vida real

`codigo/bloque_23/tarea_recoger_dejar.py` (Tema 23.3) usa el segundo enfoque —una máquina de estados en Python— pero sobre puntos que, en un brazo físico real, se habrían obtenido guiando el brazo (Tema 23.2), no calculándolos a mano.

### 4. Limitaciones

La programación guiada no escala bien a tareas con muchas variantes o mucha lógica condicional (Tema 23.4) — ahí la programación textual es prácticamente obligatoria.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una tarea programada de forma guiada falla cada vez que algo pequeño cambia (el objeto se desplaza unos milímetros) | La programación guiada graba posiciones absolutas, sin ninguna lógica de adaptación | Verificar si la tarea usa visión o algún sensor para ajustar la posición, o solo puntos fijos | Agregar sensado (Bloque 22, Tema 22.4) y lógica condicional (Tema 23.4), casi siempre programación textual |

### 6. Dónde más aparece la idea

Casi cualquier robot industrial de una línea de ensamblaje se programa así: guiado para las posiciones, texto para la lógica; el mismo patrón aparece en macros grabadas de software de oficina (guiado) contra escribir un script (textual).

### 7. Ejemplos resueltos

**Ejemplo:** los puntos `PUNTOS` de `codigo/bloque_23/tarea_recoger_dejar.py` (reposo, aproximación, recoger, depositar) representan exactamente el tipo de posiciones que un operador enseñaría guiando el brazo de acrílico de `robotica-manipuladores` (Bloque 07) a mano.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué una línea de ensamblaje con tareas muy repetitivas y estables favorece la programación guiada, mientras que una tarea de manipulación adaptativa (agarrar objetos en posiciones variables) favorece la textual.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Nada nuevo todavía; se practica en el Tema 23.2.

---

## Tema 23.2 — Puntos de enseñanza y trayectorias guardadas

### 1. El problema

Una vez que se tienen las posiciones relevantes de una tarea (por guiado, Tema 23.1, o calculadas), hace falta una forma de guardarlas y reutilizarlas sin recalcular nada cada vez.

### 2. El mecanismo

Un **punto de enseñanza** (*teach point*) es una posición (cartesiana o articular) guardada con un nombre, lista para usarse en cualquier trayectoria (Bloque 19) sin volver a calcularla. Una tarea completa se reduce, en su forma más simple, a una secuencia ordenada de puntos de enseñanza, cada uno alcanzado con el interpolador que corresponda (Bloque 19).

### 3. En la vida real

```python
PUNTOS = {
    "reposo": np.array([0.10, 0.00, 0.20]),
    "aprox_recoger": np.array([0.18, 0.05, 0.13]),
    "recoger": np.array([0.18, 0.05, 0.09]),
    "aprox_depositar": np.array([0.10, -0.15, 0.13]),
    "depositar": np.array([0.10, -0.15, 0.09]),
}
```

— el diccionario `PUNTOS` de `codigo/bloque_23/tarea_recoger_dejar.py`, con los cinco puntos de enseñanza de la tarea completa.

### 4. Limitaciones

Puntos guardados en coordenadas cartesianas fijas no se adaptan solos si el objeto cambia de posición (Tema 23.1); una tarea más flexible calcularía el punto "recoger" a partir de un sensor (visión, Bloque 22) en vez de un valor fijo.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un punto de enseñanza guardado hace tiempo ya no corresponde a la posición real del objeto | La posición física cambió (se movió la banda, se recalibró el brazo, Bloque 22) desde que se guardó el punto | Verificar la posición real actual contra el punto guardado | Volver a enseñar el punto, o hacerlo dependiente de un sensor en vez de fijo |

### 6. Dónde más aparece la idea

Cualquier sistema con "posiciones guardadas" reutilizables: presets de una cámara de vigilancia motorizada, posiciones de memoria de un asiento de automóvil.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_23/tarea_recoger_dejar.py`, sección `PUNTOS`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar la diferencia entre guardar un punto de enseñanza en coordenadas cartesianas contra guardarlo en coordenadas articulares, y cuándo importa la diferencia (pista: Bloque 12, varias soluciones posibles para un mismo punto cartesiano).

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Agregar un sexto punto de enseñanza a `PUNTOS` (por ejemplo, una segunda posición de depósito) y verificar que sea alcanzable con `robotica.inversa`.

---

## Tema 23.3 — La tarea como máquina de estados

### 1. El problema

"Recoger un huevo y dejarlo en la cubeta" no es un solo movimiento: son varias fases distintas (acercarse, tomar, levantar, trasladar, dejar, regresar), cada una con su propia lógica y sus propias condiciones de éxito o fracaso. Escribir esto como código lineal sin estructura se vuelve inmanejable apenas hay que manejar errores (Tema 23.4).

### 2. El mecanismo

Una **máquina de estados** (*state machine*) describe la tarea como un conjunto de **estados** bien definidos (`ESPERANDO`, `APROXIMAR_RECOGER`, `RECOGER`, `LEVANTAR`, `TRASLADAR`, `DEJAR`, `REGRESAR`, más un estado `ERROR`, Tema 23.4) y **transiciones** entre ellos, cada una disparada por una condición concreta (llegó al punto destino, el agarre fue exitoso, se detectó un error). En cada instante, el sistema está en **un solo** estado, lo que hace el comportamiento predecible y fácil de razonar —muy distinto de una secuencia de `if` anidados sin estructura, donde no siempre es obvio "en qué parte de la tarea" está el sistema.

### 3. En la vida real

`codigo/bloque_23/tarea_recoger_dejar.py` implementa la máquina de estados con una enumeración `Estado` (Python `Enum`) y un método `ejecutar_ciclo()` que avanza de estado en estado, registrando cada transición en una lista de eventos con marca de tiempo (`Evento`) — el **registro de eventos** que pide el laboratorio del bloque, útil para depurar qué pasó exactamente en un ciclo que falló.

### 4. Limitaciones

Esta máquina de estados es secuencial (un estado a la vez, sin paralelismo); tareas más complejas con varios subsistemas moviéndose a la vez (por ejemplo, la banda transportadora y el brazo) necesitarían máquinas de estados concurrentes, fuera del alcance de este curso.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| No queda claro, al revisar el código de una tarea, en qué "fase" está el sistema en un momento dado | La tarea se escribió como código lineal sin una estructura explícita de estados | Verificar si existe una variable de estado explícita que se pueda consultar en cualquier momento | Reestructurar como máquina de estados, con el estado actual siempre consultable |

### 6. Dónde más aparece la idea

Cualquier proceso con fases bien definidas: un semáforo, el ciclo de una lavadora, un protocolo de red — la máquina de estados es una de las herramientas de modelado más usadas en ingeniería de software y de control.

### 7. Ejemplos resueltos

**Ejemplo:** corriendo `codigo/bloque_23/tarea_recoger_dejar.py` sin errores, el registro de eventos muestra la secuencia completa: `ESPERANDO → APROXIMAR_RECOGER → RECOGER → LEVANTAR → TRASLADAR → DEJAR → REGRESAR → TERMINADO`, cada uno con su marca de tiempo.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Dibujar (a mano, en papel) el diagrama de la máquina de estados de `tarea_recoger_dejar.py`, con sus estados y flechas de transición.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_23/tarea_recoger_dejar.py` y leer el registro de eventos de un ciclo completo.

---

## Tema 23.4 — Manejo de errores

### 1. El problema

En un turno de producción de horas, algo eventualmente sale mal: el huevo no está donde se esperaba, la pinza no lo sujeta bien, la cubeta ya está llena. Una tarea programada solo para el camino "feliz" (sin ningún error) se rompe o se queda colgada la primera vez que algo no sale exactamente como se planeó.

### 2. El mecanismo

Cada posible falla se maneja como una **transición más** de la máquina de estados (Tema 23.3), hacia un estado `ERROR` (o una familia de estados de error más específicos), en vez de dejar que el programa falle sin control:

- **Objeto no encontrado**: el sensor (Bloque 22, Tema 22.4) no detecta el huevo donde debería estar — la tarea no debe intentar cerrar la pinza sobre nada.
- **Fallo de agarre**: la pinza cerró pero el objeto no quedó sujeto (se detecta, por ejemplo, con un sensor de fuerza simple, Bloque 20 Tema 20.6, o verificando que el peso esperado esté presente) — la tarea no debe continuar "trasladando" un huevo que en realidad no está en la pinza.
- **Cubeta llena**: una condición externa a la mecánica del brazo, pero igual de relevante para decidir si continuar el ciclo o detenerse.

Cada uno de estos casos, en `codigo/bloque_23/tarea_recoger_dejar.py`, se modela como una probabilidad de fallo simulada, y el resultado se registra en el evento correspondiente — permitiendo, en el laboratorio, medir qué fracción de los ciclos falla y por qué, exactamente la información que un sistema de producción real necesita para diagnosticar problemas recurrentes.

### 3. En la vida real

Con `prob_objeto_no_encontrado=0.03` y `prob_fallo_agarre=0.05` simuladas, `codigo/bloque_23/tarea_recoger_dejar.py` reporta, sobre 200 ciclos, cuántos terminan con éxito y cuántos fallan por cada causa — un panorama estadístico, no solo un caso aislado.

### 4. Limitaciones

Este bloque no cubre estrategias de **recuperación** automática (reintentar, pedir ayuda a un operador, pasar al siguiente objeto) más allá de detectar y registrar el error — una extensión natural para quien quiera profundizar, mencionada pero no implementada aquí.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un brazo en producción se queda detenido indefinidamente tras un error, sin que nadie se entere hasta mucho después | No hay manejo explícito de errores: el programa "se cuelga" en vez de transicionar a un estado de error reportable | Verificar si cada posible falla tiene una transición explícita a un estado de error, no solo el camino feliz | Agregar transiciones de error para cada falla conocida, con registro (Tema 23.3) que permita detectarlas |

### 6. Dónde más aparece la idea

Cualquier sistema de producción automatizado (líneas de embotellado, clasificadoras) tiene manejo explícito de excepciones; el mismo patrón de "camino feliz + casos de error" aparece en el manejo de excepciones de cualquier lenguaje de programación.

### 7. Ejemplos resueltos

**Ejemplo:** ver la salida de `codigo/bloque_23/tarea_recoger_dejar.py` con 200 ciclos simulados: éxitos, fallos por objeto no encontrado y fallos de agarre, cada uno contado por separado.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Proponer una estrategia de recuperación razonable para cada uno de los tres errores mencionados (objeto no encontrado, fallo de agarre, cubeta llena).

**Serie B — Cálculo a mano**
- B1. Con las probabilidades de la sección 3, estimar cuántos ciclos de 200 se espera que fallen por cada causa (multiplicar la probabilidad por 200) y comparar contra el resultado real del laboratorio.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_23/tarea_recoger_dejar.py`, verificar B1, y repetir con probabilidades de error mayores para ver cómo cae la tasa de éxito.

---

## Tema 23.5 — Tiempo de ciclo y cómo reducirlo

### 1. El problema

Cada segundo que el brazo tarda de más en un ciclo es un segundo menos de producción en un turno completo. Hace falta saber medir el tiempo de ciclo real (no solo el tiempo que tarda el código en *calcular* la trayectoria, Bloque 19, sino el tiempo que el brazo físico tarda en *ejecutarla*) y qué margen hay para reducirlo.

### 2. El mecanismo

El tiempo de ejecución de un tramo entre dos puntos de enseñanza (Tema 23.2) está limitado por la articulación **más lenta** de ese tramo (Bloque 19, Tema 19.3: perfil trapezoidal con velocidad y aceleración máximas fijadas por el dimensionamiento, Bloque 16) — moverse "sincronizado" significa que todas las articulaciones empiezan y terminan el tramo juntas, a costa de que las más rápidas esperen a la más lenta. El tiempo de ciclo total es la suma de todos los tramos de la tarea.

Una forma directa —sin cambiar velocidades ni motores— de reducir el tiempo de ciclo es **eliminar tramos innecesarios**: si la tarea pasa por `reposo` entre cada recogida y cada depósito "por costumbre", pero no hay ninguna razón de seguridad que lo exija (por ejemplo, ningún obstáculo en el camino directo), saltarse ese regreso intermedio ahorra el tiempo completo de ir y volver a `reposo` sin ningún costo de seguridad.

### 3. En la vida real

`codigo/bloque_23/tiempo_de_ciclo.py` compara dos rutas para la misma tarea: una que regresa a `reposo` entre recoger y depositar ("segura") contra una que va directo de la zona de recogida a la de depósito:

| Ruta | Duración del ciclo | Ciclos por hora |
|---|---|---|
| Con regreso a reposo | 6.271 s | 574 |
| Directa | 5.313 s | 678 |

Un ahorro del 15.3 % por ciclo, **104 ciclos por hora más**, sin cambiar ni un motor ni una ganancia de control — solo replanificando la secuencia de puntos.

### 4. Limitaciones

Eliminar tramos "de seguridad" solo es válido si de verdad no hay ningún riesgo de colisión en el camino directo (Bloque 07, espacio de trabajo) — una decisión que depende del diseño físico de la celda de trabajo, no solo del cálculo de tiempos.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un ciclo de producción es más lento de lo esperado según las velocidades máximas de los motores (Bloque 16) | La ruta programada tiene tramos innecesarios (regresos a puntos intermedios sin razón de seguridad) | Contar los tramos de la ruta actual y verificar si todos son estrictamente necesarios | Eliminar tramos innecesarios, verificando primero que no haya riesgo de colisión en el camino resultante |

### 6. Dónde más aparece la idea

Optimización de rutas en cualquier proceso repetitivo: la ruta de un brazo de picking en un almacén, el recorrido de una máquina CNC entre operaciones — reducir movimientos sin necesidad es una de las optimizaciones más comunes y de mayor impacto en cualquier línea de producción automatizada.

### 7. Ejemplos resueltos

**Ejemplo:** ver la tabla de la sección 3, generada por `codigo/bloque_23/tiempo_de_ciclo.py`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué eliminar el regreso a `reposo` entre recoger y depositar es seguro en este caso concreto (pensar en si el camino directo entre `aprox_recoger` y `aprox_depositar` podría cruzar algún obstáculo).

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_23/tiempo_de_ciclo.py` y probar una tercera ruta propia, eliminando algún otro tramo que parezca innecesario, y medir el ahorro resultante.

## Lo que este bloque agrega a `codigo/robotica/`

Nada nuevo: este bloque combina `robotica.inversa` (Bloque 12) y `robotica.trayectorias` (Bloque 19) en una máquina de estados y un análisis de tiempo de ciclo, ambos específicos de la tarea del proyecto (`codigo/bloque_23/`), sin agregar módulos genéricos a la librería.

## Glosario del bloque

| Término | Definición |
|---|---|
| Programación guiada (*teach and playback*) | Enseñar posiciones moviendo físicamente el brazo, para reproducirlas después. |
| Punto de enseñanza (*teach point*) | Posición guardada con un nombre, lista para usarse en una trayectoria. |
| Máquina de estados | Modelo de una tarea como un conjunto de estados bien definidos y transiciones entre ellos, disparadas por condiciones concretas. |
| Movimiento sincronizado | Todas las articulaciones de un tramo empiezan y terminan juntas, limitadas por la más lenta. |
| Tiempo de ciclo | Duración total de una tarea repetitiva, de principio a fin. |
