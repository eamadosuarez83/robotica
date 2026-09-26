"""El brazo 2R plano de los Bloques 15 y 16, compartido por los
scripts del Bloque 19: masas puntuales en la punta de cada eslabón.

No se corre solo: lo importan los demás scripts del bloque.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import newton_euler_plano  # noqa: E402
from robotica.inversa import inv_2r_geometrica  # noqa: E402

M1, M2 = 1.3, 0.7      # kg (Bloque 16)
L1, L2 = 0.30, 0.20    # m


def pares(Q, Qd, Qdd):
    """Par de cada motor [N·m] a lo largo de una trayectoria articular.

    Q, Qd, Qdd: arrays (k, 2). Devuelve (k, 2), por Newton-Euler (Bloque 15).
    """
    return np.array([newton_euler_plano(q, qd, qdd, [M1, M2], [L1, L2], [L1, L2], [0.0, 0.0])
                     for q, qd, qdd in zip(Q, Qd, Qdd)])


def inversa(P):
    """Inversa del 2R para un punto P = (x, y): array (2, 2) o None.
    Fila 0: codo arriba; fila 1: codo abajo (Bloque 12)."""
    return inv_2r_geometrica(P[0], P[1], L1, L2)


def directa(Q):
    """Posición de la punta para cada fila de Q (k, 2): array (k, 2)."""
    Q = np.atleast_2d(Q)
    x = L1 * np.cos(Q[:, 0]) + L2 * np.cos(Q[:, 0] + Q[:, 1])
    y = L1 * np.sin(Q[:, 0]) + L2 * np.sin(Q[:, 0] + Q[:, 1])
    return np.column_stack([x, y])
