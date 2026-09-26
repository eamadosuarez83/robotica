"""Matrices de rotacion basicas (3x3).

Bloque 08 -- Localizacion espacial I. Adaptado de `transformaciones.py`
de robotica-manipuladores: alla `rotx/roty/rotz` devuelven matrices
homogeneas 4x4 (ese repo no separa rotacion de traslacion); aqui
devuelven matrices de rotacion 3x3 puras, porque el curso reserva la
combinacion con traslacion para el Bloque 10. Misma convencion de
unidades: radianes.
"""

from __future__ import annotations

import numpy as np

__all__ = ["rotx", "roty", "rotz", "es_rotacion"]

_EPS = 1e-12


def _seno_coseno(t: float) -> tuple[float, float]:
    """Seno y coseno con ceros exactos en multiplos de pi/2.

    Sin esto, cos(pi/2) da 6.1e-17 en vez de 0.0, y ese "casi cero" se
    arrastra en cálculos posteriores (por ejemplo, al comparar con
    `np.allclose` usando una tolerancia ajustada).
    """
    s, c = np.sin(t), np.cos(t)
    return (0.0 if abs(s) < _EPS else float(s)), (0.0 if abs(c) < _EPS else float(c))


def rotx(t: float) -> np.ndarray:
    """Matriz de rotación de `t` radianes alrededor del eje X."""
    s, c = _seno_coseno(t)
    return np.array([[1, 0, 0],
                     [0, c, -s],
                     [0, s, c]], dtype=float)


def roty(t: float) -> np.ndarray:
    """Matriz de rotación de `t` radianes alrededor del eje Y."""
    s, c = _seno_coseno(t)
    return np.array([[c, 0, s],
                     [0, 1, 0],
                     [-s, 0, c]], dtype=float)


def rotz(t: float) -> np.ndarray:
    """Matriz de rotación de `t` radianes alrededor del eje Z."""
    s, c = _seno_coseno(t)
    return np.array([[c, -s, 0],
                     [s, c, 0],
                     [0, 0, 1]], dtype=float)


def es_rotacion(R: np.ndarray, tol: float = 1e-9) -> bool:
    """True si `R` es una matriz de rotación válida: ortogonal y det=+1."""
    R = np.asarray(R, dtype=float)
    if R.shape != (3, 3):
        return False
    ortogonal = np.allclose(R.T @ R, np.eye(3), atol=tol)
    return ortogonal and abs(np.linalg.det(R) - 1.0) < tol
