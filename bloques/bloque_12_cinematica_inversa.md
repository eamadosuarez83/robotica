# Bloque 12 — Cinemática inversa

> **Problema que abre el bloque:** el huevo está en un punto de la cubeta. ¿Cuánto debe girar cada motor? Esta es la pregunta que de verdad hace quien usa un robot.
>
> **Necesitas antes:** Bloque 11. · **Lectura:** Barrientos, cap. 4 (cinemática inversa); Lynch & Park, *Modern Robotics*, cap. 6.

Este es el bloque que más se beneficia de [`robotica-manipuladores`](https://github.com/eamadosuarez83/robotica-manipuladores):
sus `inversa/geometrica.py` y `inversa/desacoplo.py` (deducidas y verificadas para 5 robots reales)
se portan casi completas, y dos de sus errores reales documentados en `docs/correcciones.md` se
reutilizan directamente como material de diagnóstico. Ver
[docs/integracion_manipuladores.md](../docs/integracion_manipuladores.md). Una diferencia de
convención: allá las inversas devuelven **grados** (`docs/convenciones.md`); aquí devuelven
**radianes**, como el resto del código del curso (FILOSOFIA.md).

## Tema 12.1 — Por qué la inversa es más difícil que la directa

### 1. El problema

La cinemática directa (Bloque 11) es una función: se dan los ángulos, sale una única pose. Pedirle lo contrario —dar la pose, obtener los ángulos— no tiene garantizada ni una respuesta única ni, siquiera, alguna respuesta.

### 2. El mecanismo

Tres cosas distinguen a la inversa de la directa:

- **Puede haber varias soluciones.** El brazo 2R del Bloque 01 alcanza un mismo punto con el codo "arriba" o "abajo" (Tema 12.2) — dos configuraciones articulares distintas para la misma pose de la pinza.
- **Puede haber infinitas soluciones.** Un brazo redundante (Bloque 07, Tema 7.2: más GDL que los estrictamente necesarios) tiene, para una misma pose, todo un continuo de posturas articulares válidas.
- **Puede no haber solución.** Un punto fuera del espacio de trabajo (Bloque 07, Tema 7.3) simplemente no es alcanzable, sin importar cómo se combinen los ángulos (Tema 12.7).

Mientras que la directa es una simple evaluación de una fórmula (Bloque 11, Tema 11.4), la inversa es, en general, **resolver un sistema de ecuaciones no lineales** (los senos y cosenos de la tabla DH mezclados entre sí) — de ahí que, salvo para geometrías simples (Tema 12.2), no siempre exista una fórmula cerrada, y haga falta recurrir a métodos numéricos (Tema 12.5).

### 3. En la vida real

La convención de este curso, heredada de `robotica-manipuladores`: cada función de cinemática inversa devuelve un arreglo con **todas** las soluciones encontradas (una fila por solución), o `None` si el punto no es alcanzable — nunca un único ángulo "adivinado" sin decir que había otras opciones.

### 4. Limitaciones

Ninguna nueva: esta es la naturaleza del problema, no una aproximación evitable.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Una función de cinemática inversa devuelve solo una solución cuando el robot claramente tiene más de una configuración posible para ese punto | La implementación descarta soluciones válidas en vez de reportarlas todas | Contar cuántas raíces reales tiene la ecuación (Tema 12.2: la ley de cosenos da típicamente 2) | Devolver todas las soluciones válidas, y dejar la elección (Tema 12.6) a un paso posterior explícito |

### 6. Dónde más aparece la idea

Resolver "¿qué combinación de ingredientes da este sabor?" (varias respuestas posibles), un sistema de ecuaciones con más incógnitas que ecuaciones (infinitas soluciones), pedir un número negativo como resultado de una raíz cuadrada real (ninguna solución).

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R del Bloque 01 con $L_1=0.30,L_2=0.20$ m, el punto $(0.30,0.30)$ tiene (al menos) dos soluciones articulares distintas; el punto $(0.60,0)$ tiene exactamente una (brazo totalmente estirado); el punto $(1.0,0)$ no tiene ninguna (fuera de alcance, $L_1+L_2=0.50$ m).

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un brazo con más GDL que los necesarios para su tarea (redundante) tiene, en general, infinitas soluciones de cinemática inversa para una misma pose.

**Serie B — Cálculo a mano**
- B1. Para el 2R de $L_1=0.30,L_2=0.20$ m, calcular el alcance máximo y el mínimo (si $L_1\neq L_2$, hay un "agujero" cerca de la base, Bloque 01).

**Serie C — Laboratorio**
- C1. Nada nuevo todavía: este tema se verifica en los Temas 12.2 y 12.7.

---

## Tema 12.2 — Método geométrico: el brazo 2R con ley de cosenos

### 1. El problema

Para el 2R del Bloque 01, ¿cómo se despeja $\theta_1,\theta_2$ a partir de $(x,y)$, sin recurrir todavía a ningún método numérico?

### 2. El mecanismo

El hombro, el codo y la punta forman un triángulo de lados conocidos: $L_1$, $L_2$, y $r=\sqrt{x^2+y^2}$ (la distancia del hombro a la punta pedida). La **ley de cosenos** (Bloque 01, Tema 1.2) despeja el ángulo del codo:

$$\cos\theta_2 = \frac{r^2-L_1^2-L_2^2}{2L_1L_2}$$

Si $|\cos\theta_2|>1$, el punto está fuera de alcance (Tema 12.7): no hay triángulo posible con esos lados. Si $|\cos\theta_2|\leq1$, hay **dos** valores de $\theta_2$ que dan el mismo coseno (positivo y negativo de $\sin\theta_2$, vía `atan2`, Bloque 01 Tema 1.3): las dos configuraciones **codo arriba** y **codo abajo**. Para cada una, $\theta_1$ se obtiene descomponiendo el ángulo hacia el punto pedido ($\beta=\text{atan2}(y,x)$) menos el ángulo que aporta el antebrazo dentro del triángulo ($\alpha$, otra vez por ley de cosenos o, de forma equivalente, por la fórmula de `atan2` con el seno y coseno de $\theta_2$ ya conocidos):

$$\theta_1 = \beta-\alpha, \qquad \alpha=\text{atan2}(L_2\sin\theta_2,\ L_1+L_2\cos\theta_2)$$

Este mismo patrón —desacoplar el ángulo de la base con `atan2`, resolver el resto con ley de cosenos en el plano que queda— es exactamente el que `robotica-manipuladores` usa para brazos 3R espaciales (Tema 12.3), solo que ahí primero hay que separar la rotación de la base ($\theta_1=\text{atan2}(p_y,p_x)$) antes de quedar con un problema 2R plano equivalente.

### 3. En la vida real

`robotica/inversa.py` implementa `inv_2r_geometrica(x, y, L1, L2)`, que devuelve las dos soluciones (codo arriba, codo abajo) en radianes, o `None` si el punto no es alcanzable.

### 4. Limitaciones

Este método es específico de la geometría 2R (o 3R desacoplable en un 2R plano, Tema 12.3); no generaliza directamente a brazos sin esa estructura particular.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Solo se reporta una de las dos soluciones (codo arriba o abajo) | Se tomó solo la raíz positiva de $\sin\theta_2=\pm\sqrt{1-\cos^2\theta_2}$, descartando la negativa | Verificar que ambas raíces den, al aplicar la directa, el mismo punto $(x,y)$ | Calcular ambas soluciones y devolver las dos |
| `cos_theta2` calculado está ligeramente fuera de $[-1,1]$ por redondeo, en un punto que debería ser justo alcanzable | Error de punto flotante en el borde del espacio de trabajo (Bloque 04, Tema 4.6) | Comprobar qué tan cerca de $\pm1$ está el valor | Recortar (`np.clip`) antes de comparar, con una tolerancia razonable |

### 6. Dónde más aparece la idea

Cualquier triangulación (GPS, topografía: ubicar un punto conocidas las distancias a dos referencias), el mismo patrón geométrico en brazos de excavadoras y grúas de dos segmentos.

### 7. Ejemplos resueltos

**Ejemplo (el problema del Bloque 01, verificado en reversa):** $(x,y)=(0.298,0.381)$, $L_1=0.30,L_2=0.20$. `inv_2r_geometrica` debe devolver, entre sus soluciones, $(\theta_1,\theta_2)\approx(40°,30°)$ — el mismo par que produjo ese punto en el Bloque 01.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué codo arriba y codo abajo dan la **misma** posición de la punta pero, en general, una orientación distinta del segundo eslabón.

**Serie B — Cálculo a mano**
- B1. Para $L_1=L_2=0.25$ m y el punto $(0.25,0.25)$, calcular las dos soluciones de $\theta_1,\theta_2$.

**Serie C — Laboratorio**
- C1. Verificar B1 con `robotica.inversa.inv_2r_geometrica`, y cerrar el ciclo aplicando `directa` (Bloque 11) a cada solución para confirmar que ambas reproducen $(0.25,0.25)$.

---

## Tema 12.3 — Método a partir de la matriz de transformación homogénea

### 1. El problema

Para un brazo espacial (no plano), la pose deseada no es solo un punto $(x,y,z)$: es una matriz homogénea completa $T_d$ (Bloque 10), con orientación incluida. Hace falta un procedimiento para extraer los ángulos articulares igualando esa matriz deseada con la expresión simbólica de la cinemática directa.

### 2. El mecanismo

La idea central: escribir $T_d = {}^0A_1(\theta_1)\,{}^1A_2(\theta_2)\cdots{}^{n-1}A_n(\theta_n)$ (Bloque 11) e **igualar elemento a elemento** ambos lados. Como cada $\theta_i$ aparece dentro de senos y cosenos anidados, la estrategia práctica es despejar de adentro hacia afuera: premultiplicar ambos lados por $({}^0A_1)^{-1}$ (inversa de una homogénea, Bloque 10 Tema 10.5) deja una ecuación donde $\theta_1$ ya no aparece del lado derecho, permitiendo despejar $\theta_2,\ldots,\theta_n$ de esa ecuación más simple, y así sucesivamente.

Este procedimiento es, en esencia, una generalización sistemática del método geométrico (Tema 12.2): en vez de razonar el triángulo a ojo, se deja que el álgebra de matrices "encuentre" las mismas relaciones trigonométricas, elemento por elemento de la matriz. Para geometrías con estructura favorable (como una muñeca esférica, Tema 12.4), este despeje se simplifica enormemente.

### 3. En la vida real

`robotica.dh.directa_simbolica` (Bloque 11) es la herramienta natural para plantear $T_d={}^0A_1\cdots{}^{n-1}A_n$ simbólicamente con SymPy y explorar, término a término, qué ecuaciones trigonométricas resultan.

### 4. Limitaciones

Para más de 3-4 GDL sin estructura especial, el álgebra resultante crece muy rápido y se vuelve impracticable a mano — la razón de ser del desacoplo cinemático (Tema 12.4) y de los métodos numéricos (Tema 12.5).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El despeje "de adentro hacia afuera" da una ecuación sin solución real para un punto que debería ser alcanzable | Error de álgebra al premultiplicar por la inversa equivocada, o al elegir qué elemento de la matriz igualar primero | Verificar la igualación con un caso numérico conocido (una pose calculada con la directa) antes de generalizar | Revisar el orden de las inversas premultiplicadas y qué elementos de la matriz conviene igualar primero (los más simples, con menos términos) |

### 6. Dónde más aparece la idea

Es el método "de libro de texto" que aparece en la mayoría de los textos clásicos de robótica (incluido Barrientos) antes de introducir el desacoplo como atajo práctico.

### 7. Ejemplos resueltos

**Ejemplo:** igualar la componente $z$ de la posición ($T_d[2,3]$) con la expresión simbólica de $^0A_1{}^1A_2T[2,3]$ para el 2R vertical del Tema 11.5 da directamente una ecuación en $\theta_1,\theta_2$ equivalente a la que se dedujo geométricamente en el Tema 12.2 — mismos ángulos, distinto camino para llegar a ellos.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué "despejar de adentro hacia afuera" (premultiplicar por inversas) es más manejable que intentar resolver las $n$ ecuaciones simultáneamente sin ese orden.

**Serie B — Cálculo a mano**
- B1. Para el 2R del Tema 12.2, escribir la ecuación que resulta de igualar la componente $x$ de $T_d$ con la de $^0A_1{}^1A_2$, y verificar que es consistente con la fórmula de cinemática directa del Bloque 01.

**Serie C — Laboratorio**
- C1. Con `robotica.dh.directa_simbolica`, plantear $T$ simbólica del 2R y confirmar, sustituyendo $\theta_1=40°,\theta_2=30°$, que reproduce el resultado numérico del Bloque 01.

---

## Tema 12.4 — Desacoplo cinemático: muñeca esférica

### 1. El problema

Un brazo de 6 GDL con el método del Tema 12.3 produce un sistema de ecuaciones considerable. Pero muchos robots industriales (incluido el ABB IRB 6600 del Bloque 07) están diseñados, a propósito, con una estructura que simplifica esto enormemente: una **muñeca esférica**, donde los tres últimos ejes se cruzan en un único punto.

### 2. El mecanismo

Cuando la muñeca es esférica, la posición de la pinza **no depende** de la orientación final que se le quiera dar: mover solo los tres ejes de la muñeca cambia la orientación pero no la posición del punto donde se cruzan esos ejes (el **centro de la muñeca**, $\vec p_m$). Esto permite **desacoplar** el problema en dos partes independientes:

1. **Posición** (los primeros 3 GDL, "el brazo"): se calcula primero el centro de la muñeca, retrocediendo desde la pose deseada de la pinza a lo largo de su propio eje z, una distancia conocida (la longitud de la muñeca): $\vec p_m = \vec p_d - d_6\,\vec a_d$ (con $\vec a_d$ el eje z de la orientación deseada, Bloque 08). Con $\vec p_m$ conocido, los primeros 3 ángulos se resuelven con el método geométrico (Tema 12.2) o el de la matriz (Tema 12.3), **ignorando la orientación por completo**.
2. **Orientación** (los últimos 3 GDL, "la muñeca"): una vez conocidos los primeros 3 ángulos, se calcula la orientación que ya aportan (${}^0R_3$, Bloque 08) y se despeja la que falta para completar la orientación deseada:

$$R_{36} = ({}^0R_3)^{-1}\,R_d = ({}^0R_3)^T R_d$$

(usando que ${}^0R_3$ es ortogonal, Bloque 08 Tema 8.6). $R_{36}$ es la orientación que deben aportar, juntas, las tres últimas articulaciones; se resuelve con los ángulos de Euler ZXZ del Bloque 09 (o RPY, según cómo esté armada la muñeca), típicamente con **dos** soluciones más (muñeca "arriba" o "abajo", análogas al codo arriba/abajo del Tema 12.2) — de ahí que un brazo de 6 GDL con muñeca esférica tenga, en general, **hasta 4 soluciones** combinando las 2 del brazo con las 2 de la muñeca.

### 3. En la vida real

`robotica/inversa.py` porta `inv_curso_6gdl` e `inv_abb_6gdl` de `inversa/desacoplo.py` de `robotica-manipuladores` (adaptadas a radianes), verificadas contra la directa del Bloque 11 para el catálogo real de robots.

### 4. Limitaciones

Esto solo funciona si la muñeca es realmente esférica (los tres ejes se cruzan en un punto); brazos sin esa estructura necesitan el método general del Tema 12.3 o numérico (Tema 12.5).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El centro de la muñeca calculado está en un lugar físicamente absurdo | Se usó el eje equivocado de $R_d$ (x o y en vez de z) para retroceder desde la pinza, o el signo de $d_6$ está invertido | Verificar, para una orientación deseada simple (identidad), que $\vec p_m$ quede exactamente a $d_6$ de $\vec p_d$ a lo largo de z | Revisar qué columna de $R_d$ corresponde al eje z (Bloque 08, Tema 8.3) |

### 6. Dónde más aparece la idea

Es el método estándar en la industria para robots de 6 GDL con muñeca esférica (la mayoría de los brazos antropomórficos comerciales, incluidos ABB y KUKA); el mismo principio de "desacoplar posición de orientación" aparece en control de actitud de satélites.

### 7. Ejemplos resueltos

**Ejemplo:** para `curso_6gdl` (Bloque 11, catálogo real) en la postura de referencia $q=\vec 0$, la muñeca esférica está en $\vec p_m=(L_2,0,L_1)$: la posición depende solo de $L_1,L_2$ (los eslabones "de brazo"), no de $L_4$ (el de la muñeca) — justo el desacoplo que predice la teoría.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué un brazo de 6 GDL con muñeca esférica puede tener hasta 4 soluciones (y no, por ejemplo, 2 o 8), combinando las opciones del brazo y de la muñeca.

**Serie B — Cálculo a mano**
- B1. Con $R_d=I$ (orientación deseada: sin giro) y $d_6=0.05$ m, calcular $\vec p_m$ a partir de $\vec p_d=(0.40,0.10,0.20)$.

**Serie C — Laboratorio**
- C1. Verificar B1 en Python con `robotica.inversa.inv_curso_6gdl` (o `inv_abb_6gdl`) y confirmar, aplicando `directa` (Bloque 11), que cada una de las hasta 4 soluciones reproduce la pose deseada $T_d$.

---

## Tema 12.5 — Métodos numéricos: cuando no hay atajo geométrico

### 1. El problema

Muchos brazos (sin muñeca esférica, o con más GDL de los que el desacoplo puede aprovechar) no tienen una fórmula cerrada razonable. Hace falta un método que funcione para **cualquier** tabla DH, a costa de no dar una fórmula exacta sino una aproximación iterativa.

### 2. El mecanismo

La idea es la misma de Newton-Raphson (Bloque 04, Tema 4.6), aplicada al sistema $f(\vec q)=\vec p(\vec q)-\vec p_d=\vec 0$ (el error de posición en función de los ángulos articulares):

$$\vec q_{n+1} = \vec q_n - J(\vec q_n)^{+}\,f(\vec q_n)$$

donde $J$ es la **matriz Jacobiana** de la cinemática directa (el Bloque 13 la deduce en detalle; por ahora basta con la definición mínima: $J$ recoge, en cada columna, cómo cambia la posición de la pinza al mover un poco cada articulación por separado — exactamente la matriz de derivadas parciales del Bloque 04, Tema 4.3 — y $J^+$ es su pseudo-inversa, Bloque 03 Tema 3.6). Tres variantes prácticas de este mismo esquema:

- **Newton-Raphson / Gauss-Newton** (pseudo-inversa completa): converge rápido cerca de la solución, pero es inestable cerca de una singularidad (Bloque 13: cuando $J$ pierde rango, $J^+$ amplifica el error).
- **Jacobiana transpuesta** (la más simple y barata): $\vec q_{n+1}=\vec q_n-\alpha J^T f(\vec q_n)$, sin invertir nada — más lenta para converger, pero nunca "explota" cerca de una singularidad.
- **Mínimos cuadrados amortiguados** (*damped least squares*, un término medio): $\vec q_{n+1}=\vec q_n-J^T(JJ^T+\lambda^2I)^{-1}f(\vec q_n)$, con $\lambda$ un factor de amortiguamiento pequeño que evita la explosión de la pseudo-inversa cerca de singularidades sin perder toda la velocidad de convergencia de Newton-Raphson — el método preferido en la práctica.

Como todavía no se dedujo $J$ analíticamente (Bloque 13), este bloque la estima por **diferencias finitas** (Bloque 04, Tema 4.6): mover cada articulación un $h$ pequeño y medir cuánto cambia la posición de la pinza — suficiente para que el método funcione, aunque más costoso que la versión analítica del Bloque 13.

### 3. En la vida real

`robotica/inversa.py` implementa `inversa_numerica(dh, objetivo, q0, metodo=...)` con las tres variantes, portando el enfoque general de `inversa_numerica` de `robotica-manipuladores` (que usa `scipy.optimize.fsolve`) pero con una implementación propia de Newton amortiguado, para ver el mecanismo antes de usar una caja negra.

```python
q, convergio = inversa_numerica(dh, p_deseado, q0, metodo="amortiguado")
```

### 4. Limitaciones

Ningún método numérico garantiza encontrar **todas** las soluciones (a diferencia del método geométrico, Tema 12.2): converge a *una* solución, la más cercana a la semilla inicial $\vec q_0$ (Tema 12.6) — y puede no converger en absoluto si la semilla es mala o el punto no es alcanzable (Tema 12.7).

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El método numérico converge a una solución "rara" (postura poco natural) para un punto con solución obvia | La semilla inicial estaba lejos de la solución esperada, y el método convergió a otra solución válida pero distinta | Repetir con una semilla más cercana a la postura esperada | Elegir una semilla razonable (por ejemplo, la postura actual del robot, Tema 12.6) |
| El método diverge o el error deja de disminuir | Se está cerca de una singularidad (Bloque 13) y se usó Newton-Raphson puro sin amortiguamiento | Revisar el determinante de $JJ^T$ a lo largo de las iteraciones | Cambiar a mínimos cuadrados amortiguados, o a Jacobiana transpuesta |
| Un criterio de convergencia mal escrito acepta una solución que en realidad no lo es | Se comparó cada componente del error por separado en vez de su norma (el error #9 de `robotica-manipuladores`: `if fval <= Error` con `fval` vector, que acepta residuos negativos grandes) | Revisar si el criterio usa `norm(f(q))` o compara componente a componente | Usar siempre `norm(f(q)) < tol`, nunca comparar un vector directamente con un escalar |

### 6. Dónde más aparece la idea

Métodos de optimización basados en gradiente en aprendizaje automático (la Jacobiana transpuesta es, esencialmente, descenso de gradiente), cualquier sistema de ecuaciones no lineales sin solución cerrada.

### 7. Ejemplos resueltos

**Ejemplo:** para el 2R del Tema 12.2, `inversa_numerica` partiendo de $q_0=(0,0)$ hacia el punto $(0.298,0.381)$ debe converger, en pocas iteraciones, a $(\theta_1,\theta_2)\approx(40°,30°)$ (o a la solución codo abajo, según la semilla) — se verifica en el laboratorio contra la solución geométrica exacta del Tema 12.2.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar, en una frase, por qué la Jacobiana transpuesta "nunca explota" cerca de una singularidad, a diferencia de la pseudo-inversa completa (pista: no hay ninguna inversión de matriz en su fórmula).

**Serie B — Cálculo a mano**
- B1. Para el 2R del Tema 12.2, escribir una iteración de Jacobiana transpuesta a mano (sin calcular $J$ explícitamente, solo la estructura de la fórmula) partiendo de $q_0=(0,0)$ hacia $(0.1,0.1)$.

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_12/romper_newton_raphson.py`: arranca `inversa_numerica` desde varias semillas, incluida una deliberadamente mala (por ejemplo, una postura ya en el límite articular), y compara cuántas convergen y a qué solución.

---

## Tema 12.6 — Elegir entre varias soluciones

### 1. El problema

El método geométrico (Tema 12.2) o el desacoplo (Tema 12.4) devuelven **varias** soluciones válidas para el mismo punto. Un controlador real, sin embargo, tiene que enviar **una sola** orden a los motores: hace falta un criterio para elegir.

### 2. El mecanismo

Dos criterios cubren la mayoría de los casos prácticos:

- **Límites articulares** (Bloque 07, Tema 7.1): descartar de plano cualquier solución que viole los límites físicos de algún motor (por ejemplo, los servos de los brazos de acrílico, limitados a $\pm90°$, Bloque 07). Esto puede dejar una sola solución válida, aunque geométricamente hubiera dos.
- **Cercanía a la postura actual**: de las soluciones que sí respetan los límites, preferir la que requiere el **menor movimiento** desde donde está el robot en ese instante (por ejemplo, mínima distancia articular, $\|\vec q_{sol}-\vec q_{actual}\|$) — evita movimientos bruscos o innecesarios, y es la base de la generación de trayectorias suaves del Bloque 19.

### 3. En la vida real

```python
soluciones = [s for s in todas_las_soluciones if brazo.dentro_de_limites(np.degrees(s))]
mejor = min(soluciones, key=lambda s: np.linalg.norm(s - q_actual))
```

### 4. Limitaciones

Minimizar la distancia articular es un criterio razonable pero no el único posible (también se podría minimizar el tiempo de movimiento, la energía consumida, o evitar posturas cercanas a una singularidad, Bloque 13); este bloque usa el más simple y directo.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| El robot elige, entre dos soluciones válidas, la que produce un movimiento brusco e innecesario | No se comparó contra la postura *actual*, sino que se tomó siempre "la primera" solución de la lista por convención arbitraria | Calcular la distancia articular de cada solución candidata a la postura actual antes de elegir | Elegir explícitamente la solución más cercana a la postura actual, no la primera de la lista |

### 6. Dónde más aparece la idea

Cualquier sistema con múltiples soluciones válidas para una tarea (rutas de navegación, asignación de recursos): elegir según un criterio explícito, no arbitrariamente.

### 7. Ejemplos resueltos

**Ejemplo:** si el robot está en $q_{actual}=(35°,25°)$ y las dos soluciones geométricas para el siguiente punto son $(40°,30°)$ y $(75°,-30°)$ (codo arriba y codo abajo, respectivamente, para este caso), la primera es mucho más cercana y se prefiere, aunque ambas sean válidas.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué, en una trayectoria continua (Bloque 19), cambiar de "codo arriba" a "codo abajo" entre dos puntos consecutivos suele ser indeseable aunque ambos puntos sean alcanzables con cualquiera de las dos configuraciones.

**Serie B — Cálculo a mano**
- B1. Con $q_{actual}=(10°,80°)$ y dos soluciones candidatas $(15°,75°)$ y $(150°,-70°)$, calcular la distancia articular (norma euclidiana en grados, o en radianes de forma consistente) de cada una y elegir la mejor.

**Serie C — Laboratorio**
- C1. Implementar en Python el criterio de la sección 3 sobre las dos soluciones de `inv_2r_geometrica` para varios puntos consecutivos de una trayectoria simple, y graficar cómo cambia (o no) la configuración elegida a lo largo del camino.

---

## Tema 12.7 — Puntos fuera del espacio de trabajo

### 1. El problema

Si se le pide al robot un punto que no puede alcanzar, hace falta saberlo **antes** de mandar cualquier orden a los motores — no después de que el brazo intente, sin éxito, llegar ahí.

### 2. El mecanismo

Cada método de este bloque tiene su propia forma de señalar "no alcanzable", y conviene revisarlas todas antes de confiar ciegamente en un resultado:

- **Geométrico** (Tema 12.2): $|\cos\theta_2|>1$ — no hay triángulo posible con esos lados. La convención de este curso (heredada de `robotica-manipuladores`) es devolver `None`, nunca un número inventado.
- **Desacoplo** (Tema 12.4): el mismo chequeo aparece al resolver la parte de posición (los primeros 3 GDL), con la misma condición de la ley de cosenos.
- **Numérico** (Tema 12.5): el residuo $\|f(\vec q)\|$ deja de disminuir y se estanca por encima de la tolerancia, sin importar cuántas iteraciones se le den — la señal de que no existe ningún $\vec q$ que resuelva el problema, no que hiciera falta iterar más.

### 3. En la vida real

```python
sol = inv_2r_geometrica(x, y, L1, L2)
if sol is None:
    print("Punto fuera de alcance")
```

Verificar el alcance **antes** de intentar la inversa (comparando la distancia al punto contra $L_1+L_2$ y $|L_1-L_2|$, Bloque 01) es más barato que esperar a que el método falle, y permite dar un mensaje de error claro en vez de un resultado numérico sin sentido.

### 4. Limitaciones

Un punto "casi" alcanzable (justo en el borde del espacio de trabajo) es especialmente sensible al redondeo numérico (Bloque 04, Tema 4.6): puede alternar entre "alcanzable" y "no alcanzable" según la tolerancia usada.

### 5. Fallas típicas y diagnóstico

| Síntoma | Causa probable | Cómo verificar | Corrección |
|---|---|---|---|
| Un método numérico "converge" a una solución para un punto fuera de alcance | El criterio de convergencia usó una tolerancia demasiado laxa, aceptando un residuo grande como si fuera cero | Revisar el residuo final: `norm(f(q))` debería ser pequeño (Tema 12.5); si no lo es, no convergió de verdad | Endurecer la tolerancia, o verificar el alcance geométricamente antes de intentar el método numérico |

### 6. Dónde más aparece la idea

Cualquier sistema que deba distinguir "no tengo la respuesta todavía" de "esto no tiene respuesta": validación de entradas en general, antes de invertir tiempo de cómputo en un problema sin solución.

### 7. Ejemplos resueltos

**Ejemplo (el problema del Tema 12.1):** $(1.0,0)$ para el 2R con $L_1+L_2=0.50$ m está claramente fuera de alcance; `inv_2r_geometrica(1.0, 0, 0.30, 0.20)` debe devolver `None`.

### 8. Ejercicios

**Serie A — Conceptuales**
- A1. Explicar por qué comprobar el alcance geométricamente *antes* de llamar a un método numérico es más eficiente que dejar que el método numérico "descubra" que no hay solución.

**Serie B — Cálculo a mano**
- B1. Para el 2R con $L_1=0.30,L_2=0.20$ m, dar el rango de distancias $r=\sqrt{x^2+y^2}$ alcanzables (mínimo y máximo).

**Serie C — Laboratorio** (`⚠ romperlo a propósito`)
- C1. Correr `codigo/bloque_12/romper_punto_fuera_de_alcance.py`: pide un punto fuera del espacio de trabajo del 2R al método geométrico y al numérico, y compara qué devuelve cada uno (`None` limpio contra un resultado numérico que no converge).

## Lo que este bloque agrega a `codigo/robotica/`

`robotica/inversa.py`: `inv_2r_geometrica`, `inv_3r_geometrica` (método geométrico, Temas 12.2–12.3), `inv_curso_6gdl`, `inv_abb_6gdl` (desacoplo cinemático, Tema 12.4, portadas de `robotica-manipuladores`), `jacobiana_numerica_posicion`, `inversa_numerica` (método numérico con tres variantes, Tema 12.5).

## Glosario del bloque

| Término | Definición |
|---|---|
| Codo arriba / codo abajo | Las dos configuraciones articulares de un brazo 2R (o 3R desacoplable) que alcanzan la misma posición de la punta. |
| Muñeca esférica | Estructura donde los tres últimos ejes de un brazo de 6 GDL se cruzan en un punto común, permitiendo desacoplar posición de orientación. |
| Desacoplo cinemático | Resolver primero la posición (los GDL de "brazo") y luego la orientación (los GDL de "muñeca") por separado, aprovechando una muñeca esférica. |
| Jacobiana (definición mínima) | Matriz de derivadas parciales de la posición de la pinza respecto a cada articulación; se deduce en detalle en el Bloque 13. |
| Mínimos cuadrados amortiguados (*damped least squares*) | Variante de Newton-Raphson para cinemática inversa numérica, robusta cerca de singularidades gracias a un término de amortiguamiento $\lambda$. |
| Espacio de trabajo | Conjunto de puntos alcanzables por el efector final (Bloque 07); fuera de él, la cinemática inversa no tiene solución. |
