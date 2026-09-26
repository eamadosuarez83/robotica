# Bloque 07 — Morfología del robot

> **Problema que abre el bloque:** antes de calcular nada, hay que poder nombrar las piezas y saber qué puede hacer cada tipo de brazo.
>
> **Necesitas antes:** Bloque 06 (cierra la Parte I). · **Lectura:** Barrientos, cap. 2.

Este bloque abre la Parte II y es el primero donde el curso se apoya en
[`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores): los robots
reales que aparecen aquí (brazos de acrílico, ABB IRB 6600, KUKA KR6) vienen de ahí, con sus
medidas de datasheet — no son inventados. Ver
[docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md).

## Tema 7.1 — Eslabones, articulaciones y cadenas cinemáticas

### 1. El problema

Para hablar de un brazo hace falta poder nombrar sus partes sin ambigüedad: "el segundo pedazo" o "la unión de en medio" no alcanzan cuando el resto del curso va a referirse a cada pieza con precisión, articulación por articulación.

### 2. El mecanismo

Un manipulador se construye con dos tipos de piezas alternadas:

- **Eslabones** (*links*): las piezas rígidas (Bloque 06) que forman la estructura. Se numeran desde la base (eslabón 0, fijo) hasta el efector final.
- **Articulaciones** (*joints*): las uniones entre eslabones consecutivos que permiten movimiento relativo. Dos tipos cubren la enorme mayoría de los robots industriales:
  - **Rotacional** (*revolute*, "R"): gira alrededor de un eje: un solo número (el ángulo $\theta$) describe su posición.
  - **Prismática** (*prismatic*, "P"): se desliza en línea recta: un solo número (el desplazamiento $d$) describe su posición.

Encadenando eslabones y articulaciones se obtiene una **cadena cinemática**. Es **abierta** cuando cada eslabón se conecta solo con el siguiente (una secuencia simple, como el brazo humano desde el hombro hasta la mano) — el caso que cubre casi todo este curso. Es **cerrada** cuando hay un ciclo (un eslabón se conecta con dos otros que a su vez se conectan entre sí, como el mecanismo de cuatro barras de un limpiaparabrisas): más rígida y con más capacidad de carga, pero mucho más difícil de analizar, y fuera del alcance de este curso salvo menciones puntuales.

### 3. En la vida real

La tabla de Denavit-Hartenberg del Bloque 11 describe exactamente esta secuencia de eslabones y articulaciones con cuatro números por fila; el tipo de articulación (R o P) es la quinta columna que ya aparece en `robotica/dh.py` cuando se llegue ahí (columna `tipo`: 0 rotacional, 1 prismática, siguiendo la convención de `robotica-manipuladores`).

### 4. Limitaciones

Esta descripción asume articulaciones ideales (sin holgura, Tema 7.6) y eslabones perfectamente rígidos (Bloque 06).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Al describir un brazo se cuenta un eslabón o una articulación de más o de menos | No se contó la base (eslabón 0, fijo) como eslabón, o se confundió el efector final con una articulación | Recorrer el brazo desde la base numerando alternadamente eslabón-articulación-eslabón | Ser explícito: $n$ articulaciones implican $n+1$ eslabones (incluida la base) |

### 6. Dónde más aparece la idea

El esqueleto humano (huesos = eslabones, articulaciones anatómicas), cualquier mecanismo de bisagras, grúas.

### 7. Ejemplos resueltos

**Ejemplo:** un brazo de 3 GDL con tres articulaciones rotacionales tiene 4 eslabones (0, 1, 2, 3) y cadena "RRR" — la notación abreviada que Barrientos usa para describir la secuencia de tipos de articulación.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Dar la notación (R/P) de un brazo cartesiano de 3 GDL que se mueve en x, y, z mediante tres deslizamientos.

**Serie B — Cálculo a mano**
- B1. Para una cadena cinemática abierta de 6 articulaciones, ¿cuántos eslabones tiene, incluida la base?

**Serie C — Laboratorio**
- C1. Consultar `robotica-manipuladores/docs/robots.md` y anotar la notación (R/P) de `tercer_corte_3gdl` y de `abb_6gdl`.

---

## Tema 7.2 — Grados de libertad

### 1. El problema

Ubicar y orientar completamente un objeto rígido en el espacio (por ejemplo, la pinza sosteniendo una pieza) necesita cierta cantidad mínima de números independientes. Antes de diseñar un brazo hay que saber cuántos son, para entender qué se gana y qué se pierde al usar menos articulaciones.

### 2. El mecanismo

Un cuerpo rígido libre en el espacio tiene **6 grados de libertad (GDL)**: 3 para su posición ($x,y,z$) y 3 para su orientación (Bloque 09: por ejemplo, los tres ángulos roll-pitch-yaw). Esto no es una convención sino una consecuencia geométrica: son exactamente los números independientes que hacen falta para fijar, sin ambigüedad, dónde está y hacia dónde apunta un objeto rígido.

Cada articulación de un manipulador de cadena abierta aporta **un** grado de libertad (un ángulo o un desplazamiento). Por eso:

- Con **menos de 6 articulaciones**, el brazo no puede alcanzar cualquier posición *y* orientación arbitrarias simultáneamente — pero eso no lo vuelve inútil: un brazo de 3 o 4 GDL (como los brazos de acrílico de `robotica-manipuladores`) alcanza cualquier **posición** dentro de su espacio de trabajo, aunque no cualquier orientación en ese punto, y muchas tareas (recoger y depositar un objeto, Bloque 24) no necesitan más que eso.
- Con **más de 6 articulaciones** el brazo es **redundante**: hay infinitas formas de llegar a la misma pose, útil para evitar obstáculos o posturas incómodas, pero fuera del alcance de este curso (la cinemática inversa del Bloque 12 asume, salvo que se diga lo contrario, brazos con GDL $\leq$ 6).

### 3. En la vida real

El catálogo de `robotica-manipuladores` (`python/robotica/robots.py`) tiene ejemplos de ambos casos: los brazos de acrílico (3–4 GDL, alcanzan posición pero no cualquier orientación) y el ABB/KUKA (6 GDL, alcanzan cualquier pose dentro de su espacio de trabajo).

### 4. Limitaciones

"6 GDL alcanzan cualquier pose" es cierto solo *dentro del espacio de trabajo* del brazo (Tema 7.3) y lejos de singularidades (Bloque 13); no hay ninguna garantía cerca de los límites articulares o en posturas degeneradas.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Se le pide a un brazo de 3 GDL una posición *y* una orientación específica y no hay solución | El brazo no tiene suficientes GDL para controlar orientación de forma independiente de la posición | Contar los GDL del brazo y compararlos con los GDL que la tarea realmente necesita | Relajar el requisito de orientación, o usar un brazo con más GDL |

### 6. Dónde más aparece la idea

Por qué un dron necesita al menos 4 actuadores independientes para controlar posición 3D y guiñada, por qué un robot humanoide tiene decenas de GDL (redundancia para posturas naturales), videojuegos (cámaras con menos GDL que un objeto libre).

### 7. Ejemplos resueltos

**Ejemplo:** el brazo `tercer_corte_3gdl` (3 articulaciones rotacionales) tiene 3 GDL: alcanza cualquier punto dentro de su espacio de trabajo, pero la orientación de su pinza en ese punto queda determinada por la propia postura, no se puede elegir libremente.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un brazo de 6 GDL con muñeca esférica (Bloque 12, Tema desacoplo) separa naturalmente "3 GDL para posición" y "3 GDL para orientación".

**Serie B — Cálculo a mano**
- B1. ¿Cuántos GDL le faltan a un brazo de 4 GDL para poder orientar libremente su efector final en cualquier dirección?

**Serie C — Laboratorio**
- C1. Contar los GDL de `prototipo_4gdl` y `abb_6gdl` en `robotica-manipuladores/docs/robots.md` y confirmar contra la tabla DH de cada uno.

---

## Tema 7.3 — Configuraciones clásicas y su espacio de trabajo

### 1. El problema

No todos los brazos se parecen: algunos se mueven en línea recta, otros giran. La forma en que se combinan articulaciones rotacionales y prismáticas define familias completas de robots, cada una con ventajas para cierto tipo de tarea, y todas comparten nombre con lo que describen: la forma de su espacio de trabajo.

### 2. El mecanismo

Las configuraciones clásicas se distinguen por sus primeras articulaciones (las que dan la posición; la muñeca, Tema 7.4, se agrega después):

- **Cartesiana** (PPP): tres articulaciones prismáticas en ejes perpendiculares. Espacio de trabajo: un paralelepípedo (una caja). Muy precisa (sin brazos largos que flexionen) pero voluminosa; típica de máquinas de control numérico e impresoras 3D.
- **Cilíndrica** (RPP): una rotación en la base más dos deslizamientos (radial y vertical). Espacio de trabajo: un cilindro hueco.
- **Polar o esférica** (RRP): dos rotaciones más un deslizamiento radial. Espacio de trabajo: una porción de esfera hueca.
- **SCARA** (*Selective Compliance Assembly Robot Arm*, RRP): dos articulaciones rotacionales en un plano horizontal más una prismática vertical. Espacio de trabajo: un anillo (cilindro con un agujero central) en planta. Rígida verticalmente y flexible horizontalmente (de ahí "*compliance*" selectiva) — ideal para ensamblar e insertar piezas verticalmente a alta velocidad.
- **Angular o antropomórfica** (RRR): tres articulaciones rotacionales, imitando hombro-codo-muñeca del brazo humano. Espacio de trabajo: una región compleja, aproximadamente esférica pero con un hueco cerca de la base y lóbulos según los límites articulares (exactamente lo que se calculó, para el caso plano 2R, en el Bloque 01, Tema 1.4). Es la configuración más versátil y la más común en robots industriales de propósito general — y la que usan **todos** los robots reales de `robotica-manipuladores` (brazos de acrílico, ABB IRB 6600, KUKA KR6) y, por lo tanto, casi todo lo que resta del curso.

### 3. En la vida real

El espacio de trabajo de cualquier configuración se obtiene igual que en el Bloque 01: barrer los rangos articulares y graficar los puntos alcanzados (`codigo/bloque_07/espacios_de_trabajo.py` lo hace para las tres formas —caja, anillo, región angular— sin necesitar todavía la cinemática directa completa del Bloque 11).

### 4. Limitaciones

Estas cinco son las configuraciones "de libro"; muchos robots reales son variaciones o combinaciones (por ejemplo, un SCARA con una muñeca de varios GDL al final).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Se elige una configuración cartesiana para una tarea que necesita alta velocidad angular en un espacio reducido | No se consideró que las configuraciones angulares suelen ser más rápidas y compactas para el mismo alcance, a costa de precisión | Comparar velocidades y repetibilidad de datasheets de cada familia (Tema 7.8) | Elegir la configuración según la tarea: cartesiana para precisión lineal, angular para velocidad y alcance |

### 6. Dónde más aparece la idea

Grúas (cilíndricas o polares), impresoras 3D y fresadoras CNC (cartesianas), líneas de ensamblaje electrónico (SCARA), la gran mayoría de los brazos que aparecen en videos de fábricas (angulares).

### 7. Ejemplos resueltos

**Ejemplo:** el ABB IRB 6600 (`abb_6gdl`) es angular (RRR en sus primeros tres ejes, más una muñeca esférica de 3 GDL): alcance de 2,55 m con la geometría modelada, capacidad de carga de hasta 225 kg según la versión — la configuración angular permite ese alcance sin necesitar una estructura cartesiana enorme.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un SCARA es buena elección para insertar componentes electrónicos en una placa, pero mala elección para soldar puntos en la carrocería de un auto.

**Serie B — Cálculo a mano**
- B1. Dibujar (a mano, en un corte transversal) el espacio de trabajo de un brazo cilíndrico con radio de deslizamiento entre 20 y 50 cm y altura entre 0 y 80 cm.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_07/espacios_de_trabajo.py`: grafica el espacio de trabajo de un brazo cartesiano, uno SCARA y uno angular (2R plano, reutilizando el Bloque 01) lado a lado, y compararlos con B1.

---

## Tema 7.4 — Muñeca, efector final y TCP

### 1. El problema

Un brazo que solo ubica un punto en el espacio no sirve de mucho: hace falta algo en la punta que sostenga, suelde, pinte o corte, y hace falta poder decir con precisión *qué punto exacto* de esa herramienta es el que se está controlando.

### 2. El mecanismo

La **muñeca** es el conjunto de articulaciones (generalmente rotacionales) más cercano al extremo del brazo, dedicado a orientar el **efector final** (*end-effector*) sin mover mucho la posición — una muñeca **esférica** (sus tres ejes se cruzan en un punto común) permite, como se ve en el Bloque 12, desacoplar el problema de orientar de el de posicionar.

El efector final es la herramienta propiamente dicha: pinzas (de dedos, para sujetar objetos rígidos), ventosas (por vacío, para superficies lisas), o herramientas de proceso (soplete de soldadura, pistola de pintura, broca). El **TCP** (*Tool Center Point*, punto central de la herramienta) es el punto de referencia específico de esa herramienta —la punta de la broca, el centro entre los dedos de la pinza— respecto al cual se especifican todas las posiciones deseadas: cambiar de herramienta, en general, cambia dónde está el TCP respecto a la brida del robot, y hay que recalibrarlo.

### 3. En la vida real

El TCP se describe con una transformación homogénea fija (Bloque 10) entre la brida (el último marco de la tabla DH, Bloque 11) y la punta de la herramienta; cambiar de herramienta es, en código, cambiar esa única matriz sin tocar el resto del modelo.

### 4. Limitaciones

Este bloque no cubre el diseño mecánico de pinzas ni la mecánica del agarre (fuerzas de contacto, fricción entre dedos y objeto); son temas de un curso de manipulación aparte.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El robot llega a la posición "correcta" según el modelo, pero la herramienta real toca el objeto en un punto distinto | El TCP configurado no corresponde a la herramienta física instalada (offset de calibración desactualizado) | Medir la distancia real entre la brida y la punta de la herramienta y comparar con el TCP configurado | Recalibrar el TCP cada vez que se cambia de herramienta (Bloque 22) |

### 6. Dónde más aparece la idea

Cambio de herramientas automático en centros de mecanizado, la calibración de la punta de un destornillador eléctrico, cualquier instrumento donde "el punto que importa" no es donde se sujeta el instrumento.

### 7. Ejemplos resueltos

**Ejemplo:** el brazo `tercer_corte_3gdl` de `robotica-manipuladores` tiene "un servo de pinza (se cierra en 0°, se abre en 90°)": el TCP de ese brazo es el punto medio entre los dedos de la pinza cuando está cerrada, no la brida donde se atornilla el servo.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué cambiar de pinza a ventosa en el mismo brazo obliga a redefinir el TCP, aunque la cinemática del brazo (Bloques 08–13) no cambie en absoluto.

**Serie B — Cálculo a mano**
- B1. Si el TCP de una herramienta está desplazado 5 cm hacia adelante respecto a la brida (a lo largo de su eje z), escribir la matriz de transformación homogénea (Bloque 10, cuando se llegue ahí) que lo describe.

**Serie C — Laboratorio**
- C1. Anotar, de `docs/especificaciones.md` de `robotica-manipuladores`, qué actuador cumple el rol de efector final en cada uno de los tres brazos de acrílico.

---

## Tema 7.5 — Actuadores

### 1. El problema

Cada articulación necesita algo que la mueva. La elección del actuador (qué tan preciso, qué tan fuerte, qué tan rápido) condiciona todo lo que el brazo puede hacer, y distintas tecnologías resuelven ese problema de formas muy distintas.

### 2. El mecanismo

- **Motores DC**: giran continuamente mientras se les aplica voltaje; su velocidad es aproximadamente proporcional al voltaje y su par al corriente (el Bloque 16 deduce el modelo completo). Necesitan un sensor de posición aparte (Tema 7.7) para saber dónde están.
- **Motores paso a paso** (*stepper*): avanzan en incrementos discretos y fijos (por ejemplo, 1.8° por paso) contando pulsos eléctricos, sin necesitar sensor de posición en el caso ideal — pero si se les pide más par del que pueden dar, "pierden pasos" sin avisar (Bloque 16).
- **Servomotores de aficionado**: un motor DC pequeño, un reductor (Tema 7.6) y un potenciómetro (Tema 7.7) leído por un controlador proporcional simple, todo integrado en una sola caja que recibe una señal de ancho de pulso y mantiene un ángulo. Son los actuadores de los brazos de acrílico de `robotica-manipuladores` (rango de 0° a 180°, controlados por Arduino).
- **Actuadores neumáticos e hidráulicos**: usan la presión de un fluido (aire o aceite) para generar fuerza lineal o rotacional; entregan mucha fuerza en poco volumen (hidráulicos especialmente) pero son más difíciles de controlar con precisión que un motor eléctrico.

### 3. En la vida real

`docs/especificaciones.md` de `robotica-manipuladores` documenta la convención de los servos de sus brazos de acrílico: `ángulo_servo = q + 90°`, así que $q=0$ es la mitad del recorrido y cada articulación queda limitada a $q\in[-90°,90°]$ — una limitación de actuador, no de la cinemática del brazo.

### 4. Limitaciones

Este bloque describe los actuadores de forma cualitativa; el modelo matemático completo (constantes de par y de velocidad, saturación) es el Bloque 16.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un motor paso a paso deja de seguir los comandos enviados sin ningún mensaje de error | Perdió pasos por exceso de carga o de velocidad (par insuficiente) | Comparar la posición comandada contra la posición real medida con un sensor externo | Reducir velocidad/carga o usar un motor con más par; añadir un sensor de posición si la aplicación lo permite |

### 6. Dónde más aparece la idea

Motores de impresoras 3D (paso a paso), servos de aeromodelismo, cilindros neumáticos en líneas de ensamblaje, gatos hidráulicos.

### 7. Ejemplos resueltos

**Ejemplo:** el brazo `tercer_corte_3gdl` usa 3 servos para las articulaciones más un servo de pinza — 4 actuadores idénticos en tecnología, cada uno con su propio controlador P interno.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un motor paso a paso "perdiendo pasos" es un tipo de error que un motor DC con encoder (Tema 7.7) no puede tener de la misma forma.

**Serie B — Cálculo a mano**
- B1. Si un servo tiene un rango físico de 0° a 180° y la convención es `ángulo_servo = q + 90°`, ¿qué rango de `q` corresponde a un rango físico de 10° a 170°?

**Serie C — Laboratorio**
- C1. Revisar `matlab/extras/serial_arduino` y `ArduinoIO` de `robotica-manipuladores` y describir, en un párrafo, cómo se envía un ángulo a un servo por el puerto serie.

---

## Tema 7.6 — Transmisiones y reductores

### 1. El problema

Un motor eléctrico pequeño gira rápido pero con poco par; una articulación de un brazo necesita, casi siempre, lo contrario: girar lento pero con mucho par. Hace falta algo que convierta uno en el otro.

### 2. El mecanismo

Un **reductor** (engranajes, correas, o mecanismos armónicos) conecta el motor al eslabón con una relación de transmisión $N$ (por cada $N$ vueltas del motor, el eslabón da 1). Esto **multiplica el par por $N$** y **divide la velocidad por $N$** (la potencia, en un reductor ideal sin pérdidas, se conserva) — y, un efecto menos obvio pero crucial para el Bloque 15, **reduce la inercia que el motor "siente"** en un factor de $N^2$: es mucho más fácil para un motor acelerar un eslabón pesado a través de un reductor grande que directamente.

El costo de un reductor es el **juego mecánico** (*backlash*): una pequeña holgura entre los dientes de los engranajes que hace que, al invertir el sentido de giro, el eslabón no se mueva de inmediato hasta que esa holgura se "consume". Los reductores armónicos (*harmonic drives*), más caros, casi eliminan este juego y son los preferidos en robots de precisión.

### 3. En la vida real

Los brazos de acrílico de `robotica-manipuladores` usan servos con reductor integrado (engranajes plásticos internos); el juego mecánico de esos engranajes de bajo costo es una de las fuentes de error de posición que el notebook 08 (trayectorias) atribuye, junto con el redondeo de ángulos, a la diferencia entre la posición comandada y la medida.

### 4. Limitaciones

Este bloque no cubre el diseño mecánico de los propios reductores (dentado, materiales); el Bloque 16 retoma la reflexión de inercia ($N^2$) para el dimensionamiento de motores.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una articulación no responde de inmediato al invertir el sentido de giro, aunque el motor ya está girando en el sentido correcto | Juego mecánico (*backlash*) del reductor: hay que "consumir" la holgura antes de que se transmita movimiento | Medir cuánto gira el motor antes de que el eslabón empiece a moverse, al invertir el sentido | Usar un reductor con menos juego, o compensar en el control (fuera del alcance de este curso) |

### 6. Dónde más aparece la idea

La caja de cambios de un automóvil (multiplica par a costa de velocidad), la relación de piñones de una bicicleta, cualquier reductor de un electrodoméstico.

### 7. Ejemplos resueltos

**Ejemplo:** un reductor $N=50$ conectado a un motor que entrega 0.1 N·m a 3000 rpm da, idealmente, $0.1\times50=5$ N·m a $3000/50=60$ rpm en el eslabón — y la inercia que el motor "siente" del eslabón se divide entre $50^2=2500$.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, en términos de conservación de potencia ($P=\tau\omega$), por qué un reductor no puede multiplicar el par sin dividir la velocidad en la misma proporción.

**Serie B — Cálculo a mano**
- B1. Un motor entrega 0.05 N·m a 5000 rpm. ¿Qué relación de reducción $N$ hace falta para obtener 2 N·m en el eslabón? ¿A qué velocidad quedaría girando el eslabón?

**Serie C — Laboratorio**
- C1. Calcular en Python, para varios valores de $N$ (10, 50, 100), el par, la velocidad de salida y el factor de reducción de inercia ($N^2$), y graficar cómo cambian los tres con $N$.

---

## Tema 7.7 — Sensores internos

### 1. El problema

Un controlador (Parte V) necesita saber dónde está realmente cada articulación para poder corregir el error entre lo pedido y lo alcanzado. Hace falta algo que mida esa posición (o su cambio) de forma confiable.

### 2. El mecanismo

- **Potenciómetro**: una resistencia variable cuyo valor depende del ángulo del eje; económico y simple (es lo que usa internamente un servo de aficionado), pero se desgasta con el uso (contacto físico) y tiene resolución limitada.
- **Encoder incremental**: cuenta pulsos generados al girar (típicamente con un disco ranurado y un sensor óptico); da **cambios** de posición con alta resolución, pero no sabe la posición absoluta al encender — necesita un procedimiento de referencia (*homing*) al inicio.
- **Encoder absoluto**: da directamente la posición actual sin necesitar referencia (usa un patrón codificado, por ejemplo en binario Gray, en vez de contar pulsos); más caro que el incremental, pero evita el problema de "no saber dónde está" al arrancar.
- **Finales de carrera** (*limit switches*): no miden posición continua, solo detectan "se llegó al límite físico"; se usan para detección de referencia (*homing*) y como protección de última instancia contra un movimiento excesivo (Bloque 22).

### 3. En la vida real

Los brazos de acrílico de `robotica-manipuladores` usan el potenciómetro interno del propio servo (no hay un sensor añadido): la posición que "cree" tener el brazo es la que el controlador interno del servo reporta, no una medición independiente — una limitación real que el Bloque 22 retoma al hablar de calibración.

### 4. Limitaciones

Ningún sensor es perfecto: todos tienen ruido, y los incrementales además tienen el problema de la referencia inicial ya mencionado.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un encoder incremental reporta una posición sin sentido justo después de encender el sistema | Todavía no se hizo el procedimiento de referencia (*homing*); el conteo empieza en 0 desde donde sea que estuviera el eje al encender, no desde una posición conocida | Revisar si se ejecutó una rutina de *homing* antes de confiar en la lectura | Añadir (o ejecutar) el procedimiento de referencia antes de operar |

### 6. Dónde más aparece la idea

El mouse óptico de una computadora (encoder incremental), el volante de un automóvil con sensor de ángulo absoluto, el sensor de nivel de combustible (potenciómetro).

### 7. Ejemplos resueltos

**Ejemplo:** un encoder incremental de 1000 pulsos por vuelta da una resolución de $360°/1000=0.36°$ por pulso — suficiente para muchas aplicaciones, pero requiere contar pulsos correctamente desde una referencia conocida.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un encoder absoluto no necesita *homing* pero uno incremental sí, pensando en qué información da cada uno al encenderlo.

**Serie B — Cálculo a mano**
- B1. ¿Cuántos pulsos por vuelta hacen falta para una resolución angular de al menos 0.1°?

**Serie C — Laboratorio**
- C1. Simular en Python la lectura de un encoder incremental: contar pulsos a partir de una velocidad angular simulada (Bloque 05) e integrar para obtener la posición, comparando contra la posición "real" simulada.

---

## Tema 7.8 — Repetibilidad contra exactitud

### 1. El problema

Un datasheet de robot da dos números que suenan parecido pero significan cosas muy distintas, y confundirlos lleva a expectativas equivocadas sobre lo que el robot puede hacer.

### 2. El mecanismo

- **Repetibilidad**: qué tan cerca vuelve el robot al *mismo* punto comandado, repetidas veces. Mide la consistencia del propio robot (juego mecánico, ruido de sensores, Tema 7.6 y 7.7).
- **Exactitud** (*accuracy*): qué tan cerca está el robot del punto *verdadero* que se le pidió, según el modelo matemático (la cinemática del Bloque 11). Depende de qué tan bien el modelo (tabla DH, calibración) coincide con la geometría real del robot.

Un robot puede ser muy **repetible** pero poco **exacto**: si su tabla DH tiene un pequeño error sistemático (por ejemplo, una longitud mal medida), volverá una y otra vez al mismo punto equivocado con gran consistencia. La calibración (Bloque 22) es precisamente el proceso de corregir la exactitud sin tocar la repetibilidad, que es una propiedad física del robot.

### 3. En la vida real

Comparar datasheets reales: el ABB IRB 6600 (`abb_6gdl`) especifica una repetibilidad de posición de 0.1 mm; el KUKA KR 6 AGILUS (`kuka_6gdl`), según su norma ISO 9283, especifica ±0.03 mm — una diferencia de más de 3 veces, a pesar de que ambos son robots industriales de 6 GDL de la misma familia general de configuración angular.

### 4. Limitaciones

Ninguna de las dos métricas dice nada sobre velocidad, carga o alcance — son ejes de comparación independientes entre sí y de las demás especificaciones.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un robot con excelente repetibilidad en el datasheet llega sistemáticamente a un punto distinto del pedido en la aplicación real | Problema de exactitud (modelo/calibración), no de repetibilidad (el robot es consistente, solo que consistente en el lugar equivocado) | Repetir el mismo movimiento varias veces: si siempre cae en el mismo punto equivocado, es un problema de exactitud, no de repetibilidad | Recalibrar el modelo (tabla DH, offsets) en vez de sospechar del hardware |

### 6. Dónde más aparece la idea

Un reloj puede ser muy preciso (repetible: siempre se adelanta lo mismo) sin ser exacto (no da la hora correcta); un arma de fuego puede agrupar tiros muy juntos (repetible) sin dar en el blanco (exacto) si la mira está mal calibrada.

### 7. Ejemplos resueltos

**Ejemplo:** si `tercer_corte_3gdl` se comanda 100 veces al mismo punto y cae siempre dentro de una región de 2 mm de diámetro, pero ese punto está en realidad 8 mm del punto pedido (por una longitud $L_2$ mal medida en la tabla DH), el robot es repetible (2 mm) pero no exacto (8 mm de error respecto al objetivo).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Proponer un experimento simple para medir por separado la repetibilidad y la exactitud de un brazo de acrílico con una hoja cuadriculada y un lápiz en la pinza.

**Serie B — Cálculo a mano**
- B1. Si un robot repite el mismo punto dentro de un círculo de 0.5 mm de radio pero el centro de ese círculo está 3 mm del punto verdadero, dar sus valores de repetibilidad y de exactitud (error).

**Serie C — Laboratorio**
- C1. Anotar, de `docs/robots.md` y `docs/especificaciones.md` de `robotica-manipuladores`, la repetibilidad del ABB y del KUKA, y clasificar los tres brazos de acrílico y los dos industriales por familia de configuración (todos angulares, Tema 7.3) y por escala (hobby/industrial) usando alcance, carga y repetibilidad.

## Lo que este bloque agrega a `codigo/robotica/`

Nada todavía: este bloque es descriptivo. La librería retoma su crecimiento en el Bloque 08 con `robotica/rotaciones.py`.

## Glosario del bloque

| Término | Definición |
|---|---|
| Eslabón (*link*) | Pieza rígida de la estructura de un manipulador. |
| Articulación (*joint*) | Unión entre dos eslabones que permite movimiento relativo: rotacional (R) o prismática (P). |
| Cadena cinemática abierta / cerrada | Secuencia de eslabones sin ciclos (abierta) o con al menos un ciclo (cerrada). |
| Grados de libertad (GDL) | Número de movimientos independientes; 6 ubican y orientan completamente un cuerpo rígido en el espacio. |
| Redundante | Un manipulador con más GDL que los estrictamente necesarios para su tarea. |
| SCARA | Configuración RRP con dos rotaciones horizontales y una prismática vertical; espacio de trabajo en forma de anillo. |
| Angular / antropomórfica | Configuración RRR que imita hombro-codo-muñeca; la más común en robots industriales. |
| Muñeca esférica | Conjunto de articulaciones de orientación cuyos ejes se cruzan en un punto común. |
| TCP (*Tool Center Point*) | Punto de referencia de la herramienta respecto al cual se especifican las posiciones deseadas. |
| Backlash (juego mecánico) | Holgura en un reductor que retrasa la transmisión de movimiento al invertir el sentido de giro. |
| Encoder incremental / absoluto | Sensor de posición angular que cuenta cambios (incremental, necesita referencia inicial) o da la posición directamente (absoluto). |
| Repetibilidad | Consistencia del robot al volver al mismo punto comandado. |
| Exactitud | Cercanía entre el punto alcanzado y el punto verdadero pedido, según el modelo. |
