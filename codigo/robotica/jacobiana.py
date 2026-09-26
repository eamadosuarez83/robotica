"""Jacobiana geometrica, manipulabilidad y estatica (Bloque 13).

Original de este curso: robotica-manipuladores no tiene cinematica
diferencial (ver docs/integracion_manipuladores.md).
"""

from __future__ import annotations

import numpy as np

from .dh import marcos

__all__ = ["jacobiana_geometrica", "jacobiana_posicion", "manipulabilidad", "par_estatico"]


def jacobiana_geometrica(dh, q) -> np.ndarray:
    """Jacobiana geométrica (6, n): filas 0-2 velocidad lineal, 3-5 angular.

    Para la articulación i (rotacional): Jv_i = z_{i-1} x (p_e - p_{i-1}),
    Jw_i = z_{i-1}. Para prismática: Jv_i = z_{i-1}, Jw_i = 0. z_{i-1} y
    p_{i-1} son el eje z y el origen del marco i-1 (Bloque 11); p_e es la
    posición del efector final.
    """
    dh = np.atleast_2d(np.asarray(dh, dtype=float))
    n = dh.shape[0]
    Ms = marcos(dh, q)   # [A00, A01, ..., A0n]
    p_e = Ms[n][:3, 3]

    J = np.zeros((6, n))
    for i in range(n):
        z_prev = Ms[i][:3, 2]
        p_prev = Ms[i][:3, 3]
        tipo = dh[i, 4]
        if tipo == 0:
            Jv = np.cross(z_prev, p_e - p_prev)
            Jw = z_prev
        else:
            Jv = z_prev
            Jw = np.zeros(3)
        J[:3, i] = Jv
        J[3:, i] = Jw
    return J


def jacobiana_posicion(dh, q) -> np.ndarray:
    """Solo las 3 primeras filas de la Jacobiana geométrica (velocidad lineal)."""
    return jacobiana_geometrica(dh, q)[:3, :]


def manipulabilidad(J: np.ndarray) -> float:
    """Medida de manipulabilidad de Yoshikawa: sqrt(det(J @ J.T)).

    Cero exacto en una singularidad (Bloque 13, Tema 13.5); mayor valor,
    más "cómoda" la postura para moverse en cualquier dirección.
    """
    J = np.atleast_2d(np.asarray(J, dtype=float))
    return float(np.sqrt(max(np.linalg.det(J @ J.T), 0.0)))


def par_estatico(J: np.ndarray, F: np.ndarray) -> np.ndarray:
    """tau = J^T F: par articular necesario para sostener una fuerza F
    aplicada en el efector final (Bloque 13, Tema 13.7)."""
    return np.asarray(J, dtype=float).T @ np.asarray(F, dtype=float)
