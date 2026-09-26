# Bloque 20 — Control dinámico del brazo completo

> **Problema que abre el bloque:** con PID independientes, el brazo sigue bien en movimientos lentos y mal en rápidos, porque cada eslabón empuja a los otros.
>
> **Necesitas antes:** Bloque 19 (cierra la Parte V). · **Lectura:** Barrientos, cap. 7; Spong, Hutchinson & Vidyasagar, capítulos de control multivariable.

Este bloque cierra la Parte V reuniendo todo lo anterior: la dinámica completa de los Bloques 14-15,
el PID del Bloque 18, y una trayectoria del Bloque 19, simulados juntos sobre el 2R real (no
linealizado). Los laboratorios de este bloque son el primer lugar del curso donde se ve, con
números concretos, por qué el modelo dinámico completo importa para el control, no solo para el
dimensionamiento (Bloque 16).

## Tema 20.1 — Limitaciones del control independiente por articulación

### 1. El problema

El Bloque 18 diseñó un PID por articulación tratando el acoplamiento con las demás como una perturbación (Bloque 18, Tema 18.2). Hace falta ver, con números, qué tan bien —o mal— funciona esa aproximación cuando el brazo completo se mueve.

### 2. El mecanismo

Un PID independiente (Bloque 18) no usa ningún término del modelo dinámico (Bloques 14-15): reacciona únicamente al error de su propia articulación, sin saber que el movimiento de la otra articulación genera fuerzas de Coriolis y acoplamiento inercial que la empujan (Bloque 14, Tema 14.5, los términos fuera de la diagonal de $M(\vec q)$ y $C(\vec q,\dot{\vec q})$). Para movimientos **lentos**, esos términos son pequeños ($C$ es cuadrático en $\dot{\vec q}$) y el PID independiente se desempeña razonablemente; para movimientos **rápidos**, el acoplamiento deja de ser despreciable y el error de seguimiento crece — exactamente el problema que abre el bloque.

### 3. En la vida real

`codigo/bloque_20/control_comparado.py` simula el 2R real (dinámica completa, Bloques 14-15) siguiendo la misma trayectoria (perfil en S, Bloque 19) con PID independiente, para un movimiento lento (3 s) y uno rápido (0.4 s):

| Movimiento | Error RMS de $\theta_1$ (PID independiente) |
|---|---|
| Lento (3 s) | 3.78° |
| Rápido (0.4 s) | 22.59° |

El error crece casi 6 veces al acelerar el mismo movimiento — la manifestación numérica exacta del problema que abre el bloque.

### 4. Limitaciones

Esta comparación usa un solo brazo (el 2R) y una sola trayectoria representativa; el efecto sería aún más marcado en un brazo de más GDL, con más términos de acoplamiento (Bloque 14, Tema 14.5).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un PID independiente que funciona bien en pruebas lentas falla al acelerar la tarea en producción | El acoplamiento entre articulaciones (Bloque 14) deja de ser despreciable a esa velocidad | Repetir la prueba a la velocidad real de operación, no solo en pruebas lentas de laboratorio | Usar control basado en el modelo (Temas 20.2-20.3) para movimientos rápidos |

### 6. Dónde más aparece la idea

Cualquier sistema multivariable con lazos independientes (Bloque 18, Tema 18.2) degrada su desempeño cuando el acoplamiento entre canales deja de ser despreciable — el mismo patrón en control de procesos químicos con varias variables interactuando.

### 7. Ejemplos resueltos

**Ejemplo:** ver la tabla de la sección 3, generada por `codigo/bloque_20/control_comparado.py`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el error de seguimiento de un PID independiente crece con la velocidad del movimiento, en términos de qué término de $M(\vec q)\ddot{\vec q}+C(\vec q,\dot{\vec q})\dot{\vec q}+G(\vec q)$ (Bloque 14) se vuelve significativo.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo: se verifica en simulación.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_20/control_comparado.py` y confirmar los números de la tabla de la sección 3.

---

## Tema 20.2 — Control PD con compensación de gravedad

### 1. El problema

Antes de usar el modelo dinámico completo (Tema 20.3), hay un paso intermedio simple y muy usado en la práctica: cancelar explícitamente **solo** el término de gravedad, el que más contribuye al error persistente de un brazo que sostiene su propio peso (Bloque 18, Tema 18.1 ya mostró esto para una articulación colgando).

### 2. El mecanismo

$$\vec\tau = K_p\vec e - K_d\dot{\vec q} + \hat G(\vec q)$$

con $\vec e=\vec q_d-\vec q$ y $\hat G(\vec q)$ el término de gravedad del modelo (Bloque 14, Tema 14.5), evaluado con la postura **actual** del brazo, sumado directamente a la señal de control. Esto no elimina el acoplamiento de inercia ni de Coriolis (Tema 20.1) — solo cancela la parte de la dinámica que **no depende de la velocidad**, la más fácil de calcular y la que más pesa en movimientos lentos o en posturas estáticas.

Se puede demostrar (con la teoría de estabilidad de Lyapunov, fuera del alcance de este curso) que, si $\hat G=G$ exactamente, el PD con compensación de gravedad converge globalmente a $\vec e=\vec0$ para *cualquier* postura deseada constante — una garantía más fuerte que la de un PD sin compensar, que en general deja algún error (Bloque 18, Tema 18.1).

### 3. En la vida real

```python
tau = Kp * error - Kd * qdot + G_hat(*q)   # G_hat: robotica.dinamica, Bloque 14
```

### 4. Limitaciones

Como en el Tema 20.1, no compensa Coriolis ni inercia — en la simulación de `control_comparado.py`, el PD con compensación de gravedad se desempeña de forma comparable al PID independiente (algo peor en este caso particular, porque no tiene acción integral): 4.45° en el movimiento lento, 27.13° en el rápido.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un PD con compensación de gravedad sostiene bien una postura fija pero sigue mal una trayectoria rápida | Solo se canceló $G(\vec q)$, no los términos de inercia y Coriolis, que dominan en movimientos rápidos (Tema 20.1) | Comparar el error en una postura fija (regulación) contra el error siguiendo una trayectoria rápida (seguimiento) | Usar par calculado (Tema 20.3) si el seguimiento en movimiento rápido importa |

### 6. Dónde más aparece la idea

Compensar el término más significativo y más fácil de calcular de una perturbación conocida, sin modelar todo el sistema, es una técnica común en control (compensación de fricción seca, por ejemplo, con el mismo espíritu).

### 7. Ejemplos resueltos

**Ejemplo:** ver la columna "PD + gravedad" de `codigo/bloque_20/control_comparado.py`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el PD con compensación de gravedad converge para *cualquier* postura deseada constante, mientras que la fórmula del Tema 20.1 (PID sin ningún término del modelo) no ofrece esa garantía.

**Serie B — Cálculo a mano**
- B1. Con $\vec e=(5°,-3°)$, $\dot{\vec q}=(0.1,0.05)$ rad/s, $K_p=80$, $K_d=10$, y $\hat G=(3.5,0.4)$ N·m, calcular $\vec\tau$.

**Serie C — Laboratorio**
- C1. Verificar B1 en Python y comparar contra el `par_calculado` del Tema 20.3 para la misma postura.

---

## Tema 20.3 — Par calculado (*computed torque*)

### 1. El problema

El PD con compensación de gravedad (Tema 20.2) deja sin cancelar los términos de inercia y Coriolis, los que más importan en movimientos rápidos (Tema 20.1). Hace falta una ley de control que use el modelo dinámico **completo**, no solo la gravedad.

### 2. El mecanismo

El **par calculado** propone:

$$\vec\tau = \hat M(\vec q)\big(\ddot{\vec q}_d+K_d\dot{\vec e}+K_p\vec e\big) + \hat C(\vec q,\dot{\vec q})\dot{\vec q} + \hat G(\vec q)$$

con $\hat M,\hat C,\hat G$ el modelo dinámico estimado (Bloque 14) y $\vec e=\vec q_d-\vec q$. Si el modelo es exacto ($\hat M=M$, etc.), sustituyendo esta ley en la dinámica real $M\ddot{\vec q}+C\dot{\vec q}+G=\vec\tau$ (Bloque 14, Tema 14.5) y simplificando:

$$M\ddot{\vec q} = M\big(\ddot{\vec q}_d+K_d\dot{\vec e}+K_p\vec e\big) \quad\Longrightarrow\quad \ddot{\vec e}+K_d\dot{\vec e}+K_p\vec e=\vec 0$$

— **la dinámica del error se vuelve lineal y desacoplada**, exactamente la ecuación de un sistema de segundo orden del Bloque 05 (Tema 5.4), una por cada articulación, ¡e independiente entre ellas! Este es el resultado central del bloque: el par calculado convierte al brazo no lineal y acoplado en $n$ sistemas lineales independientes, diseñables con las mismas herramientas del Bloque 17 (elegir $K_p,K_d$ para el tiempo de establecimiento y sobrepaso deseados, Bloque 17 Tema 17.4) — el brazo "se comporta como si" cada articulación fuera un sistema masa-resorte-amortiguador simple del Bloque 05, sin importar la postura ni la velocidad.

### 3. En la vida real

`codigo/bloque_20/control_comparado.py` implementa exactamente esta ley (`par_calculado`), reutilizando `robotica.dinamica` (Bloque 14):

| Movimiento | Error RMS de $\theta_1$ (par calculado) |
|---|---|
| Lento (3 s) | 0.01° |
| Rápido (0.4 s) | 0.01° |

El error es esencialmente el mismo —y casi nulo— sin importar la velocidad: la ecuación del error linealizado no tiene ningún término de velocidad no lineal que crezca con la rapidez del movimiento.

### 4. Limitaciones

Esta linealización **exacta** depende de que $\hat M,\hat C,\hat G$ coincidan con la dinámica real; el Tema 20.5 muestra qué pasa cuando no coinciden.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Par calculado con el modelo correcto sigue mostrando error de seguimiento notable | $K_p,K_d$ mal elegidos para la dinámica del error lineal resultante (Bloque 17, Tema 17.4), no un problema del método en sí | Verificar la respuesta de $\ddot e+K_de\dot{}+K_pe=0$ (Bloque 05, Tema 5.4) con los $K_p,K_d$ elegidos | Ajustar $K_p,K_d$ como se ajustaría cualquier sistema de segundo orden (Bloque 18, Tema 18.3) |

### 6. Dónde más aparece la idea

Linealización por realimentación (*feedback linearization*) es una técnica general de control no lineal, usada en robótica, aeronáutica (control de vuelo) y vehículos autónomos, siempre que se tenga un modelo dinámico razonablemente bueno del sistema.

### 7. Ejemplos resueltos

**Ejemplo:** ver la tabla de la sección 3.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, sin fórmulas, por qué el par calculado hace que el brazo "se sienta" como un sistema lineal simple para el diseñador del controlador, aunque físicamente el brazo siga siendo no lineal.

**Serie B — Cálculo a mano**
- B1. Con $\ddot e+K_d\dot e+K_pe=0$, elegir $K_p,K_d$ para un sistema críticamente amortiguado (Bloque 05, Tema 5.4) con frecuencia natural $\omega_n=10$ rad/s ($K_p=\omega_n^2$, $K_d=2\omega_n$).

**Serie C — Laboratorio**
- C1. Verificar B1 en `codigo/bloque_20/control_comparado.py` cambiando `Kp,Kd` de `par_calculado` y comparando el tiempo de establecimiento resultante.

---

## Tema 20.4 — Prealimentación más realimentación

### 1. El problema

Vale la pena entender la ley del Tema 20.3 en dos partes separadas, porque esa separación reaparece en casi cualquier controlador basado en modelo, no solo en robótica.

### 2. El mecanismo

$$\vec\tau = \underbrace{\hat M(\vec q)\ddot{\vec q}_d+\hat C(\vec q,\dot{\vec q})\dot{\vec q}+\hat G(\vec q)}_{\text{prealimentación (feedforward)}} + \underbrace{\hat M(\vec q)\big(K_d\dot{\vec e}+K_p\vec e\big)}_{\text{realimentación (feedback)}}$$

La **prealimentación** calcula, de antemano, el par que *debería* hacer falta si el modelo fuera perfecto y no hubiera ningún error — usa la trayectoria deseada $\vec q_d,\dot{\vec q}_d,\ddot{\vec q}_d$ (Bloque 19), no la medición real. La **realimentación** corrige lo que la prealimentación no pudo prever: errores de modelo, perturbaciones, condiciones iniciales distintas de las planeadas — exactamente el rol de la realimentación del Bloque 17 (Tema 17.1), ahora combinada con un término prealimentado que hace la mayor parte del trabajo.

Esta combinación explica por qué el par calculado funciona tan bien con un modelo preciso (la prealimentación ya hace casi todo el trabajo, y la realimentación solo pule el resto) y por qué se degrada con un modelo impreciso (Tema 20.5): la prealimentación calcula mal, y toda la carga de corregir cae en la realimentación, con las mismas limitaciones de cualquier lazo PD (Bloque 18).

### 3. En la vida real

Cualquier sistema con una acción "calculada de antemano" más una corrección basada en el error sigue este mismo patrón: un horno que precalienta según una receta conocida (prealimentación) y ajusta según el termómetro (realimentación).

### 4. Limitaciones

La prealimentación exige conocer $\vec q_d,\dot{\vec q}_d,\ddot{\vec q}_d$ completos, no solo la posición deseada — exactamente lo que un generador de trayectorias (Bloque 19) ya provee.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un controlador con prealimentación no mejora respecto a uno puramente realimentado | Falta $\ddot{\vec q}_d$ en la prealimentación (se usó solo posición y velocidad deseadas, sin aceleración) | Revisar si la ley de control usa los tres, posición/velocidad/aceleración deseadas | Generar la trayectoria completa con Bloque 19 (que ya da los tres) y usarlos todos |

### 6. Dónde más aparece la idea

Control de crucero adaptativo (prealimentación por el mapa de la ruta, realimentación por el radar), cualquier sistema de control moderno de alto desempeño combina ambas.

### 7. Ejemplos resueltos

**Ejemplo:** en `par_calculado` de `codigo/bloque_20/control_comparado.py`, el término `Mn @ qdd_d` es la parte de prealimentación de aceleración; `Mn @ (Kd*edot + Kp*e) + resto` es la realimentación más la compensación de gravedad/Coriolis.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un controlador con solo prealimentación (sin ningún término de realimentación) fallaría ante cualquier perturbación no prevista, por bueno que sea el modelo.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. En `codigo/bloque_20/control_comparado.py`, poner `Kp=Kd=0` en `par_calculado` (prealimentación pura) y medir cuánto crece el error de seguimiento sin ninguna corrección por realimentación.

---

## Tema 20.5 — Robustez: qué pasa cuando el modelo está mal

### 1. El problema

El huevo que recoge el brazo del proyecto (Bloque 24) tiene una masa que varía un poco de huevo a huevo, y el modelo dinámico (Bloque 14) nunca es perfecto. Hace falta saber qué tan sensible es el par calculado (Tema 20.3) a esos errores.

### 2. El mecanismo

Si $\hat M\neq M$ (u otro término del modelo es impreciso), la cancelación exacta del Tema 20.3 deja de ser exacta: sustituyendo la ley de control con un modelo erróneo en la dinámica real se obtiene una dinámica de error que **ya no es** $\ddot{\vec e}+K_d\dot{\vec e}+K_p\vec e=\vec0$, sino esa misma ecuación más un término residual proporcional al error del modelo — el sistema deja de comportarse como el conjunto de osciladores lineales desacoplados ideales, y el error de seguimiento deja de ser cero incluso en estado estacionario.

### 3. En la vida real

`codigo/bloque_20/romper_modelo_equivocado.py` simula par calculado con un modelo cuyas masas están un 30% equivocadas respecto a la planta real:

| Error del modelo | Error RMS $\theta_1$, lento | Error RMS $\theta_1$, rápido |
|---|---|---|
| 0% (modelo exacto) | 0.008° | 0.013° |
| 30% | 2.48° | 3.71° |

El error crece notoriamente con el 30% de error de masa, y crece más en el movimiento rápido —los términos de inercia y Coriolis, los más sensibles a un error de masa, pesan más ahí— consistente con el análisis del Tema 20.1.

### 4. Limitaciones

Este bloque no cubre técnicas específicas de robustificación (control robusto $H_\infty$, modos deslizantes) más allá de mencionar que existen; el Tema 20.6 menciona brevemente el control adaptativo como una alternativa.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un par calculado que funcionaba bien en simulación se desempeña peor con el brazo físico real | Los parámetros dinámicos del modelo (Bloque 16, Tema 16.5) no coinciden exactamente con el brazo real, o la carga (el huevo) no estaba en el modelo original | Medir el error de seguimiento real y compararlo contra la simulación con el modelo nominal | Remedir los parámetros dinámicos, o aumentar la ganancia de realimentación (Tema 20.4) para compensar más con el término reactivo |

### 6. Dónde más aparece la idea

Cualquier controlador basado en modelo en la práctica enfrenta esta brecha entre modelo y realidad; el diseño de márgenes de robustez es una parte central de la ingeniería de control profesional.

### 7. Ejemplos resueltos

**Ejemplo:** ver la tabla de la sección 3.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el error de seguimiento con 30% de error de masa es mayor en el movimiento rápido que en el lento, retomando el Tema 20.1.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_20/romper_modelo_equivocado.py` con distintos porcentajes de error de masa (10%, 20%, 50%) y graficar cómo crece el error de seguimiento.

---

## Tema 20.6 — Nociones de control adaptativo y de fuerza

### 1. El problema

El Tema 20.5 mostró que el par calculado se degrada si el modelo está mal. ¿Hay alguna forma de que el controlador **aprenda** los parámetros correctos sobre la marcha, en vez de depender de que estén bien medidos de antemano? Y hasta ahora todo el control fue de **posición** — ¿qué pasa cuando la tarea exige controlar una **fuerza** (por ejemplo, no romper el huevo al sujetarlo)?

### 2. El mecanismo

Dos menciones breves, hasta donde llega este curso:

- **Control adaptativo**: en vez de fijar $\hat M,\hat C,\hat G$ de antemano, el controlador **ajusta** sus parámetros en tiempo real a partir del error de seguimiento observado (con una ley de adaptación diseñada para garantizar que el ajuste converja, típicamente basada en la misma teoría de Lyapunov mencionada en el Tema 20.2) — resuelve, en principio, el problema del Tema 20.5 sin necesitar remedir el brazo cada vez que cambia la carga. El diseño completo de una ley adaptativa está fuera del alcance de este curso.
- **Control de fuerza**: todo este bloque controló **posición** ($\vec q$ sigue a $\vec q_d$). Hay tareas (sujetar un huevo sin romperlo, pulir una superficie con presión constante) donde lo que importa es controlar la **fuerza de contacto**, no la posición exacta — el llamado control híbrido posición/fuerza combina ambos: posición en las direcciones libres de movimiento, fuerza en la dirección de contacto. Mencionado aquí porque el Bloque 24 (recoger un huevo) roza este problema (no aplastar el huevo al cerrar la pinza), aunque se resuelve en el proyecto con un criterio más simple (límite de par en la pinza) que con control de fuerza completo.

### 3. En la vida real

El límite de par de la pinza al cerrar sobre el huevo (Bloque 24) es la versión simplificada, sin necesitar control de fuerza completo, de lo que se menciona en esta sección: saturar el par del actuador de la pinza (Bloque 16, Tema 16.1) es una forma barata de evitar romper el huevo sin implementar un lazo de fuerza dedicado.

### 4. Limitaciones

Esta sección es deliberadamente una mención, no un desarrollo completo — ambos temas (control adaptativo y de fuerza) son, cada uno, el contenido de un curso de control avanzado aparte.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Se intenta usar control de posición puro para una tarea que en realidad necesita limitar una fuerza de contacto | La tarea exige controlar fuerza (o al menos limitarla), no solo posición | Preguntar si un exceso de posición (llegar "un poco más allá" de lo esperado) puede dañar algo físicamente | Agregar al menos un límite de par/fuerza (como en el Bloque 24), si no un control de fuerza completo |

### 6. Dónde más aparece la idea

Control adaptativo: pilotos automáticos que ajustan su comportamiento a distintas cargas de un avión; control de fuerza: cualquier robot que ensambla piezas con ajuste fino, pule superficies, o manipula objetos frágiles.

### 7. Ejemplos resueltos

**Ejemplo:** el Bloque 24 (proyecto integrador) limita el par del servo de la pinza a un valor máximo conocido para no aplastar el huevo — la versión más simple posible de "controlar" una fuerza, sin necesitar un sensor de fuerza dedicado ni un lazo de control de fuerza completo.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar la diferencia entre "limitar el par de la pinza" (lo que hace el Bloque 24) y un "control de fuerza" completo (lo que se menciona en este tema), y por qué la primera opción es una simplificación razonable para el proyecto de este curso.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Ninguno nuevo: este tema es introductorio, sin laboratorio propio.

## Lo que este bloque agrega a `codigo/robotica/`

Nada nuevo: este bloque combina `robotica.dinamica` (Bloque 14), `robotica.control.PID` (Bloque 18) y `robotica.trayectorias` (Bloque 19) en los scripts de `codigo/bloque_20/`, sin agregar módulos nuevos a la librería.

## Glosario del bloque

| Término | Definición |
|---|---|
| Control independiente por articulación | Un PID por cada motor, sin usar el modelo dinámico ni saber de las demás articulaciones. |
| PD con compensación de gravedad | $\tau=K_pe-K_d\dot q+\hat G(q)$: cancela solo el término de gravedad del modelo. |
| Par calculado (*computed torque*) | Ley de control que usa el modelo dinámico completo para linealizar y desacoplar el error de seguimiento en $n$ sistemas lineales independientes. |
| Prealimentación (*feedforward*) | Parte de la señal de control calculada de antemano a partir de la trayectoria deseada, sin usar la medición. |
| Realimentación (*feedback*) | Parte de la señal de control que corrige a partir del error medido (Bloque 17). |
| Control adaptativo | Controlador que ajusta sus propios parámetros del modelo en tiempo real a partir del error observado. |
| Control de fuerza | Controlar la fuerza de contacto del efector final en vez de (o junto con) su posición. |
