# Bloque 21 — Diseño mecánico y modelo digital

> **Problema que abre el bloque:** las tablas y ecuaciones describen un brazo ideal. Hay que diseñar uno que se pueda fabricar y cuyo modelo digital coincida con el real.
>
> **Necesitas antes:** Bloque 20 (cierra la Parte V, abre la Parte VI). · **Lectura:** documentación de build123d y de URDF.

## Tema 21.1 — Del requisito al diseño

### 1. El problema

Antes de dibujar cualquier pieza, hace falta traducir la tarea (Bloque 24: recoger huevos de una clasificadora) en números concretos que un diseño mecánico pueda satisfacer o no.

### 2. El mecanismo

Cuatro requisitos resumen casi cualquier especificación de un brazo:

- **Alcance**: la distancia máxima que debe cubrir el espacio de trabajo (Bloque 07, Tema 7.3) — determina las longitudes $L_i$ de los eslabones.
- **Carga**: el peso máximo que debe sostener y mover el efector final — determina, junto con el alcance, el par que necesitan los motores (Bloque 16).
- **Velocidad**: qué tan rápido debe completarse un ciclo (Bloque 19, Bloque 23) — junto con la carga, determina el par pico dinámico (Bloque 16, Tema 16.6), casi siempre más exigente que el par estático.
- **Precisión**: qué tan cerca del punto pedido debe llegar realmente (Bloque 07, Tema 7.8: repetibilidad contra exactitud) — determina la rigidez estructural necesaria (poca flexión bajo carga) y la calidad de los sensores (Bloque 07, Tema 7.7).

Estos cuatro requisitos, ya fijados, son los que alimentan cada bloque siguiente: las longitudes van a la tabla DH (Bloque 11), la carga y la velocidad al dimensionamiento de motores (Bloque 16), y todos juntos al diseño geométrico de este bloque.

### 3. En la vida real

Para el proyecto del Bloque 24 (recoger huevos de una clasificadora, acomodarlos en una cubeta de 30): alcance suficiente para cubrir la banda y la cubeta, carga de unos 60-70 g por huevo (con margen), velocidad fijada por el tiempo de ciclo deseado, precisión suficiente para no golpear el huevo contra el borde de la cubeta.

### 4. Limitaciones

Estos cuatro requisitos rara vez se optimizan todos a la vez: más alcance con la misma rigidez pide eslabones más pesados, lo que exige más par (Bloque 16), lo que exige motores más grandes y pesados — un compromiso de diseño, no un problema con una única respuesta correcta.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un diseño mecánico ya construido no puede cumplir la tarea (par insuficiente, no llega a algún punto) | Los requisitos no se fijaron con números concretos antes de diseñar, o se diseñó antes de dimensionar (Bloque 16) | Revisar si existe una especificación explícita de alcance/carga/velocidad/precisión anterior al diseño | Fijar los cuatro requisitos primero, y verificar el dimensionamiento (Bloque 16) antes de fabricar nada |

### 6. Dónde más aparece la idea

Cualquier proceso de diseño de ingeniería empieza fijando requisitos antes de diseñar; es la misma disciplina que un documento de especificación de software.

### 7. Ejemplos resueltos

**Ejemplo:** los brazos de acrílico de `robotica-manipuladores` (Bloque 07) tienen alcances de 20-40 cm y cargas de gramos, consistentes con ser prototipos de mesa, no brazos industriales — sus requisitos de origen explican su tamaño.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué "más alcance" casi nunca es gratis: qué otros requisitos empeora, típicamente.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Escribir, para el proyecto del Bloque 24, una tabla con los cuatro requisitos y un número concreto para cada uno (aunque sea una primera estimación).

---

## Tema 21.2 — Modelado paramétrico con build123d

### 1. El problema

Diseñar cada eslabón "a mano" en un programa de CAD, y tener que rehacerlo cada vez que cambia una longitud de la tabla DH (Bloque 11), es lento y propenso a que el modelo 3D y el modelo matemático se desincronicen.

### 2. El mecanismo

**build123d** es una librería de Python para modelado CAD paramétrico: en vez de dibujar formas con el mouse, se describen con código, en función de variables — cambiar una longitud es cambiar un número en el script y volver a correrlo, no rehacer el dibujo. Para un eslabón simplificado como un prisma rectangular (Bloque 06, Tema 6.4, el mismo prisma cuyo tensor de inercia ya se dedujo ahí), el largo es directamente el parámetro $a_i$ de la tabla DH (Bloque 11) — el modelo 3D queda **atado** a la tabla DH: cambiar la cinemática cambia automáticamente la geometría.

```python
from build123d import BuildPart, Box
with BuildPart() as eslabon:
    Box(a_i, ancho, alto)   # a_i: parámetro DH del Bloque 11
```

### 3. En la vida real

`codigo/bloque_21/eslabon_parametrico.py` construye un eslabón como prisma con build123d, parametrizado por el largo $a$ de la tabla DH de `curso_3gdl` (Bloque 11).

### 4. Limitaciones

Un prisma es una simplificación considerable de un eslabón real (que puede tener agujeros, redondeos, piezas de sujeción); sirve para el propósito de este bloque (ligar geometría a la tabla DH y calcular masas, Tema 21.3) sin pretender ser un diseño final de fabricación.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El modelo CAD y la tabla DH quedan con longitudes distintas tras un cambio | El eslabón se modeló con un número fijo en vez de leer el parámetro de la tabla DH | Verificar que la longitud del modelo CAD provenga de la misma variable que alimenta `robotica.dh` | Parametrizar el CAD directamente con los valores de la tabla DH, nunca duplicar el número |

### 6. Dónde más aparece la idea

Cualquier flujo de diseño paramétrico (CAD generativo, diseño de PCB por código) evita la desincronización entre el modelo y sus parámetros de origen.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_21/eslabon_parametrico.py`, que genera los tres eslabones de `curso_3gdl` con sus longitudes $L_1,L_2,L_3$ (Bloque 11) directamente como parámetros de build123d.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un modelo paramétrico reduce el riesgo de que la tabla DH y el modelo CAD "se desincronicen" con el tiempo.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_21/eslabon_parametrico.py`, cambiar una longitud y confirmar que el volumen reportado cambia proporcionalmente.

---

## Tema 21.3 — Masas, centros de masa e inercias desde el CAD

### 1. El problema

Los Bloques 14-16 necesitan masa, centro de masa y tensor de inercia de cada eslabón (Bloque 16, Tema 16.5: "del CAD" era una de las tres formas de obtenerlos, mencionada pero no desarrollada hasta ahora).

### 2. El mecanismo

build123d calcula estas propiedades por integración exacta sobre la geometría (el mismo cálculo del Bloque 06, Tema 6.4, hecho por el software en vez de a mano). Un detalle de implementación importante: `Part.matrix_of_inertia` de build123d devuelve el tensor de inercia **geométrico** (equivalente a integrar con densidad 1), no el físico — hay que multiplicarlo por la densidad real del material para obtener kg·m²:

```python
densidad = 2700.0  # kg/m³, aluminio
masa = eslabon.part.volume * densidad
tensor_inercia = np.array(eslabon.part.matrix_of_inertia) * densidad
```

Verificado en el laboratorio: para el mismo prisma del Bloque 06 (Tema 6.4), el tensor de inercia que da build123d (ya multiplicado por la densidad) coincide con la fórmula analítica $\tfrac1{12}m(w^2+h^2)$ del Bloque 06 hasta el redondeo de punto flotante.

### 3. En la vida real

`codigo/bloque_21/eslabon_parametrico.py` calcula masa, centro de masa y tensor de inercia de cada eslabón de `curso_3gdl` con build123d y los compara contra la fórmula analítica del Bloque 06.

### 4. Limitaciones

Esto da las propiedades de la geometría **modelada**; si el eslabón real difiere del modelo (agujeros no modelados, piezas añadidas como motores o cableado, Bloque 06 Tema 6.1), hace falta sumar esas masas aparte o medir directamente (Bloque 16, Tema 16.5).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| La masa o inercia calculada por build123d es miles de veces menor o mayor de lo esperado | Se olvidó multiplicar por la densidad (el tensor de build123d es geométrico, no físico) | Comparar el orden de magnitud contra una estimación a mano | Multiplicar `matrix_of_inertia` y `volume` por la densidad real del material |

### 6. Dónde más aparece la idea

Cualquier software de CAD (SolidWorks, Fusion 360, FreeCAD) calcula propiedades de masa de la misma forma; es una función estándar en cualquier herramienta de diseño mecánico.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_21/eslabon_parametrico.py`, que reporta el error entre el tensor de build123d y la fórmula analítica del Bloque 06 para el mismo prisma (esencialmente cero, ambos son cálculos exactos del mismo sólido).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué el tensor "geométrico" (densidad 1) de build123d, multiplicado por la densidad real, da el tensor físico correcto (pista: la integral de inercia es lineal en la densidad si esta es uniforme).

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo: ya se hizo en el Bloque 06.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_21/eslabon_parametrico.py` con otro material (por ejemplo, PLA de impresión 3D, densidad ≈1250 kg/m³) y comparar la masa resultante.

---

## Tema 21.4 — Formato URDF

### 1. El problema

Los simuladores de robots (PyBullet, Tema 21.5; también Gazebo, RViz, MoveIt en el ecosistema ROS) no leen tablas DH ni código Python directamente: esperan un archivo de descripción en un formato estándar.

### 2. El mecanismo

**URDF** (*Unified Robot Description Format*) describe un robot como una lista de `<link>` (cada eslabón, con su geometría visual, de colisión, y sus propiedades de masa/inercia, Tema 21.3) conectados por `<joint>` (cada articulación, con su tipo —`revolute`, `prismatic`, `fixed`— su eje de giro, y un `<origin>` fijo que ubica el marco del joint respecto a su padre).

La sutileza central de este tema: la transformación DH estándar (Bloque 11) es $A_i=R_z(\theta_i)T_z(d_i)T_x(a_i)R_x(\alpha_i)$ — la rotación variable $R_z(\theta_i)$ va **primero**. URDF, en cambio, espera un origen **fijo** seguido de una rotación pura alrededor del eje del joint — el orden opuesto. La solución (verificada numéricamente en el laboratorio, coincide con `directa` del Bloque 11 hasta precisión de máquina) es una traslación de índices: el origen del joint $i$ en URDF se arma con $d_{i-1},a_{i-1},\alpha_{i-1}$ (los parámetros de la fila **anterior** de la tabla DH), y el joint $i$ rota puro alrededor de su z local — la misma reindexación que separa la convención DH estándar de la modificada (Bloque 11, Tema 11.6), que aquí deja de ser una curiosidad teórica y se vuelve necesaria para exportar a URDF.

### 3. En la vida real

`codigo/bloque_21/generar_urdf.py` construye el URDF de `curso_3gdl` a partir de su tabla DH estándar (Bloque 11) con esta reindexación, usando las masas e inercias del Tema 21.3.

### 4. Limitaciones

Esta conversión asume articulaciones puramente rotacionales con el eje $z$ de cada joint (la convención DH, Bloque 11); joints prismáticos siguen un patrón análogo, con `type="prismatic"` en vez de `"revolute"`.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El robot cargado desde un URDF generado se ve "torcido" o con las proporciones equivocadas respecto al modelo DH | Se usaron los parámetros de la fila incorrecta al armar el origen de cada joint (falta la reindexación de la sección 2) | Comparar la cinemática directa de PyBullet contra `robotica.dh.directa` para varias posturas (Tema 21.5) | Aplicar la reindexación: origen del joint $i$ usa $d_{i-1},a_{i-1},\alpha_{i-1}$, no $d_i,a_i,\alpha_i$ |

### 6. Dónde más aparece la idea

Cualquier robot descrito en ROS (la enorme mayoría de la robótica académica e industrial que usa software libre) tiene su URDF; es el formato de facto para intercambiar descripciones de robots entre herramientas.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_21/generar_urdf.py`, que genera y guarda el URDF de `curso_3gdl`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, con la fórmula $A_i=R_z(\theta_i)T_z(d_i)T_x(a_i)R_x(\alpha_i)$, por qué $T_z(d_i)T_x(a_i)R_x(\alpha_i)$ termina siendo el origen del **siguiente** joint en vez del propio.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo: la deducción algebraica completa está en la sección 2.

**Serie C — Laboratorio**
- C1. Abrir el URDF generado en un editor de texto e identificar, en el XML, dónde está codificada la reindexación de la sección 2.

---

## Tema 21.5 — Simulación en PyBullet

### 1. El problema

Con el URDF (Tema 21.4) ya generado, falta la verificación final: confirmar que el modelo digital completo (geometría, masas, cinemática) es **consistente** con la librería propia del curso, antes de confiar en él para nada más.

### 2. El mecanismo

**PyBullet** es un motor de simulación física de código abierto, capaz de cargar un URDF y calcular su cinemática y dinámica. Cargando el URDF de `curso_3gdl` (Tema 21.4) y fijando los mismos ángulos articulares que se usarían con `robotica.dh.directa` (Bloque 11), la posición del efector final que reporta PyBullet debe coincidir con la de la librería propia — y, siguiendo el patrón de FILOSOFIA.md ("a mano, propia, con librería profesional"), también con `roboticstoolbox.DHRobot` (Bloque 11), cerrando un triángulo de verificación con tres implementaciones independientes.

### 3. En la vida real

`codigo/bloque_21/verificar_pybullet.py` carga el URDF generado, calcula la posición del efector final con PyBullet (modo `DIRECT`, sin ventana gráfica) para varias posturas aleatorias, y la compara contra `robotica.dh.directa` y `roboticstoolbox.DHRobot.fkine`.

### 4. Limitaciones

Esta verificación cubre solo la **cinemática**; verificar que la **dinámica** (masas, inercias) también coincida requeriría comparar contra Newton-Euler (Bloque 15) con el brazo en caída libre o bajo un par conocido — una extensión natural, no desarrollada en el laboratorio de este bloque.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| PyBullet reporta una posición del efector final distinta de `robotica.dh.directa` para la misma postura | Error en la conversión DH→URDF (Tema 21.4), o unidades inconsistentes (URDF espera metros; Bloque 11 a veces trabajó en cm) | Comparar ambas para $\vec q=\vec0$ primero (el caso más fácil de verificar a mano) | Revisar la reindexación del Tema 21.4 y las unidades de longitud |

### 6. Dónde más aparece la idea

Cualquier pipeline de robótica que combina un modelo matemático propio con un simulador físico externo necesita esta misma verificación cruzada antes de confiar en ninguno de los dos por separado.

### 7. Ejemplos resueltos

**Ejemplo:** ver `codigo/bloque_21/verificar_pybullet.py`, que reporta el error máximo entre las tres implementaciones (propia, PyBullet, Robotics Toolbox) para varias posturas aleatorias.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué verificar contra dos librerías independientes (PyBullet y Robotics Toolbox) da más confianza que verificar contra una sola.

**Serie B — Cálculo a mano**
- B1. Ninguno nuevo.

**Serie C — Laboratorio**
- C1. Correr `codigo/bloque_21/verificar_pybullet.py` y confirmar que las tres implementaciones coinciden dentro de una tolerancia numérica razonable.

## Lo que este bloque agrega a `codigo/robotica/`

Nada nuevo: este bloque usa build123d y PyBullet como herramientas externas (FILOSOFIA.md), sin agregar módulos propios a la librería.

## Glosario del bloque

| Término | Definición |
|---|---|
| Modelado paramétrico | Describir geometría en función de variables (código), en vez de dibujarla directamente, para que cambiar un parámetro actualice el modelo completo. |
| Tensor de inercia geométrico | El tensor de inercia calculado con densidad 1 (proporcional al volumen, no a la masa); se multiplica por la densidad real para obtener el tensor físico. |
| URDF (*Unified Robot Description Format*) | Formato estándar (XML) para describir un robot —eslabones, articulaciones, masas— a simuladores y herramientas de robótica. |
| PyBullet | Motor de simulación física de código abierto, capaz de cargar URDF y calcular cinemática y dinámica. |
