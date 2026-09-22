"""Operaciones vectoriales propias del curso.

Bloque 02 -- Vectores. Cada funcion se implementa "a mano" (sumas y
productos elemento a elemento) para ver el mecanismo antes de usar
`numpy` directamente; el bloque compara ambos caminos.
"""

from __future__ import annotations

import numpy as np


def norma(v: np.ndarray) -> float:
    """Longitud (magnitud) del vector v."""
    v = np.asarray(v, dtype=float)
    return float(np.sqrt(np.sum(v * v)))


def vector_unitario(v: np.ndarray) -> np.ndarray:
    """Vector de longitud 1 en la direccion de v."""
    v = np.asarray(v, dtype=float)
    n = norma(v)
    if n == 0.0:
        raise ValueError("El vector cero no tiene direccion; no se puede unitarizar.")
    return v / n


def producto_punto(u: np.ndarray, v: np.ndarray) -> float:
    """Producto punto (escalar) entre u y v: cuanto de u va en la direccion de v."""
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    return float(np.sum(u * v))


def angulo_entre(u: np.ndarray, v: np.ndarray) -> float:
    """Angulo entre u y v, en radianes, usando el producto punto."""
    cos_theta = producto_punto(u, v) / (norma(u) * norma(v))
    cos_theta = float(np.clip(cos_theta, -1.0, 1.0))
    return float(np.arccos(cos_theta))


def son_ortogonales(u: np.ndarray, v: np.ndarray, tol: float = 1e-9) -> bool:
    """True si u y v son perpendiculares (dentro de una tolerancia)."""
    return abs(producto_punto(u, v)) < tol


def producto_cruz(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Producto cruz de dos vectores de 3 componentes.

    El resultado es perpendicular a u y a v; su magnitud es el area
    del paralelogramo que forman.
    """
    u = np.asarray(u, dtype=float)
    v = np.asarray(v, dtype=float)
    if u.shape != (3,) or v.shape != (3,):
        raise ValueError("producto_cruz requiere vectores de 3 componentes.")
    return np.array([
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    ])


def torque(r: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Torque tau = r x F producido por una fuerza F aplicada en r."""
    return producto_cruz(r, F)
