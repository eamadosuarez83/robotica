"""Modelo del brazo del proyecto integrador: la tabla DH real de
`prototipo_4gdl` (robotica-manipuladores, Bloque 07/11), en metros, y
una estimacion razonable de masas por eslabon para dimensionamiento y
dinamica (Bloque 24).

`prototipo_4gdl` es un brazo de acrilico de 4 GDL YA CONSTRUIDO (no
solo diseñado) en robotica-manipuladores -- la decision de diseño que
docs/integracion_manipuladores.md dejaba pendiente para este bloque:
se usa como base real en vez de inventar una geometria nueva desde
cero (ver Bloque 24, seccion "Por que este robot").
"""

import numpy as np

# Tabla DH de prototipo_4gdl (docs/robots.md de robotica-manipuladores),
# convertida de cm a m. [theta_offset, d, a, alpha, tipo]
L1, L2, L3, L4 = 0.03, 0.13, 0.17, 0.02
DH = [
    [np.pi, L1, 0, -np.pi / 2, 0],
    [-np.pi / 2, 0, L2, np.pi, 0],
    [np.pi / 2, 0, L3, np.pi / 2, 0],
    [0, 0, L4, 0, 0],
]
LONGITUDES = [L1, L2, L3, L4]

# Masas estimadas por eslabon (kg) -- brazo de acrilico con servos de
# aficionado (Bloque 16 Tema 16.3); el ultimo eslabon incluye la pinza.
MASAS = [0.05, 0.08, 0.06, 0.03]

ALCANCE_MAXIMO = L2 + L3 + L4   # sin contar L1 (vertical, base)
