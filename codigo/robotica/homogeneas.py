"""Matrices de transformacion homogenea 4x4 (Bloque 10).

Porta `transl` y `es_homogenea` de `transformaciones.py` de
robotica-manipuladores; agrega la combinacion/separacion explicita
rotacion+traslacion (rt2homogenea/homogenea2rt) y la inversa cerrada
(inversa_homogenea), sin equivalente directo alla porque ese repo no
separa rotacion (Bloque 08) de traslacion como aqui.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "transl", "es_homogenea", "rt2homogenea", "homogenea2rt", "inversa_homogenea",
]


def es_homogenea(T) -> bool:
    """True si T es una matriz 4x4 con última fila (0,0,0,1)."""
    T = np.asarray(T, dtype=float)
    return T.shape == (4, 4) and np.allclose(T[3, :], [0, 0, 0, 1])


def transl(x, y=None, z=None) -> np.ndarray:
    """Traslación homogénea pura (sin rotación).

    * ``transl(x, y, z)`` o ``transl([x, y, z])`` devuelven la matriz 4x4.
    * ``transl(T)`` con T 4x4 devuelve el vector de posición T[:3, 3].
    """
    if y is None and z is None:
        x = np.asarray(x, dtype=float)
        if es_homogenea(x):
            return x[:3, 3].copy()
        v = x.reshape(3)
    else:
        v = np.array([x, y, z], dtype=float)
    T = np.eye(4)
    T[:3, 3] = v
    return T


def rt2homogenea(R: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Combina una rotación 3x3 (Bloque 08) y una posición p en una T 4x4."""
    R = np.asarray(R, dtype=float)
    p = np.asarray(p, dtype=float).reshape(3)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p
    return T


def homogenea2rt(T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Separa T (4x4) en su rotación R (3x3) y su posición p (3,)."""
    T = np.asarray(T, dtype=float)
    return T[:3, :3].copy(), T[:3, 3].copy()


def inversa_homogenea(T: np.ndarray) -> np.ndarray:
    """Inversa de una transformación homogénea sin invertir la 4x4 completa.

    T^-1 = [[R^T, -R^T p], [0, 1]] -- Bloque 10, Tema 10.5. No es T.T:
    solo el bloque de rotación se transpone.
    """
    R, p = homogenea2rt(T)
    return rt2homogenea(R.T, -R.T @ p)
