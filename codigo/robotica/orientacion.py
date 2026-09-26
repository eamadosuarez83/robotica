"""Representaciones de orientacion: Euler (RPY, ZXZ), eje-angulo y
cuaterniones (Bloque 09).

RPY y ZXZ se portan de `transformaciones.py` de robotica-manipuladores,
adaptadas a radianes (alla trabajan en grados; ver nota al inicio del
Bloque 09 en bloques/bloque_09_...md). Eje-angulo y cuaterniones son
originales de este curso.
"""

from __future__ import annotations

import numpy as np

from .rotaciones import rotx, roty, rotz

__all__ = [
    "rpy2mat", "mat2rpy", "zxz2mat", "mat2zxz",
    "eje_angulo2mat", "mat2eje_angulo",
    "cuaternion_desde_eje_angulo", "cuaternion2mat", "mat2cuaternion",
    "slerp",
]


# ---------------------------------------------------------------- Euler RPY

def rpy2mat(alf: float, bet: float, gam: float) -> np.ndarray:
    """Matriz de rotación a partir de ángulos Roll-Pitch-Yaw, en RADIANES.

    ``R = rotz(gam) @ roty(bet) @ rotx(alf)``: alf (roll) en X, bet
    (pitch) en Y, gam (yaw) en Z, respecto a ejes fijos.
    """
    return rotz(gam) @ roty(bet) @ rotx(alf)


def mat2rpy(R) -> tuple[float, float, float]:
    """Ángulos RPY ``(alf, bet, gam)`` en radianes de una matriz de rotación.

    ``rpy2mat(*mat2rpy(R))`` reproduce ``R`` (salvo cerca de un
    bloqueo del cardán, Bloque 09 Tema 9.2).
    """
    R = np.asarray(R, dtype=float)
    nx, ny, nz = R[0, 0], R[1, 0], R[2, 0]
    sx, sy = R[0, 1], R[1, 1]
    ax, ay = R[0, 2], R[1, 2]
    gam = np.arctan2(ny, nx)
    bet = np.arctan2(-nz, nx * np.cos(gam) + ny * np.sin(gam))
    alf = np.arctan2(ax * np.sin(gam) - ay * np.cos(gam),
                      -sx * np.sin(gam) + sy * np.cos(gam))
    return float(alf), float(bet), float(gam)


# ---------------------------------------------------------------- Euler ZXZ

def zxz2mat(phi: float, beta: float, alfa: float) -> np.ndarray:
    """Matriz de rotación a partir de ángulos de Euler ZXZ, en RADIANES.

    ``R = rotz(phi) @ rotx(beta) @ rotz(alfa)``.
    """
    return rotz(phi) @ rotx(beta) @ rotz(alfa)


def mat2zxz(R) -> tuple[float, float, float]:
    """Ángulos de Euler ZXZ ``(phi, beta, alfa)`` en radianes."""
    R = np.asarray(R, dtype=float)
    nx, ny = R[0, 0], R[1, 0]
    sx, sy = R[0, 1], R[1, 1]
    ax, ay, az = R[0, 2], R[1, 2], R[2, 2]
    phi = np.arctan2(-ax, ay)
    beta = np.arctan2(ax * np.sin(phi) - ay * np.cos(phi), az)
    alfa = np.arctan2(-sx * np.cos(phi) - sy * np.sin(phi),
                       nx * np.cos(phi) + ny * np.sin(phi))
    return float(phi), float(beta), float(alfa)


# ------------------------------------------------------------- eje-ángulo

def _antisimetrica(k: np.ndarray) -> np.ndarray:
    """[k]_x tal que [k]_x @ v == k x v (Bloque 02)."""
    kx, ky, kz = k
    return np.array([[0, -kz, ky],
                      [kz, 0, -kx],
                      [-ky, kx, 0]], dtype=float)


def eje_angulo2mat(k: np.ndarray, theta: float) -> np.ndarray:
    """Fórmula de Rodrigues: matriz de rotación de `theta` radianes
    alrededor del eje unitario `k`."""
    k = np.asarray(k, dtype=float)
    k = k / np.linalg.norm(k)
    K = _antisimetrica(k)
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)


def mat2eje_angulo(R, eps: float = 1e-8) -> tuple[np.ndarray, float]:
    """Eje unitario y ángulo (radianes) equivalentes a la rotación `R`.

    Válido para theta lejos de 0 y de pi (ver Bloque 09, Tema 9.3,
    Limitaciones: cerca de theta=0 el eje queda mal condicionado).
    """
    R = np.asarray(R, dtype=float)
    theta = np.arccos(np.clip((np.trace(R) - 1) / 2, -1.0, 1.0))
    if theta < eps:
        return np.array([1.0, 0.0, 0.0]), 0.0
    k = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    k = k / (2 * np.sin(theta))
    return k, float(theta)


# ------------------------------------------------------------- cuaterniones

def cuaternion_desde_eje_angulo(k: np.ndarray, theta: float) -> np.ndarray:
    """Cuaternión (w,x,y,z) de la rotación `theta` alrededor del eje unitario `k`."""
    k = np.asarray(k, dtype=float)
    k = k / np.linalg.norm(k)
    w = np.cos(theta / 2)
    xyz = k * np.sin(theta / 2)
    return np.array([w, *xyz])


def cuaternion2mat(q: np.ndarray) -> np.ndarray:
    """Matriz de rotación equivalente al cuaternión unitario q=(w,x,y,z)."""
    w, x, y, z = np.asarray(q, dtype=float) / np.linalg.norm(q)
    return np.array([
        [1 - 2 * (y**2 + z**2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x**2 + z**2), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x**2 + y**2)],
    ])


def mat2cuaternion(R) -> np.ndarray:
    """Cuaternión (w,x,y,z) equivalente a la matriz de rotación R.

    Método robusto (Shepperd): elige la expresión numéricamente estable
    según el mayor de traza y diagonal, para evitar dividir por un
    número cercano a cero.
    """
    R = np.asarray(R, dtype=float)
    tr = np.trace(R)
    if tr > 0:
        s = 0.5 / np.sqrt(tr + 1.0)
        w = 0.25 / s
        x = (R[2, 1] - R[1, 2]) * s
        y = (R[0, 2] - R[2, 0]) * s
        z = (R[1, 0] - R[0, 1]) * s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    q = np.array([w, x, y, z])
    return q / np.linalg.norm(q)


def slerp(q0: np.ndarray, q1: np.ndarray, t: float) -> np.ndarray:
    """Interpolación esférica lineal entre dos cuaterniones unitarios."""
    q0 = np.asarray(q0, dtype=float) / np.linalg.norm(q0)
    q1 = np.asarray(q1, dtype=float) / np.linalg.norm(q1)

    dot = np.dot(q0, q1)
    if dot < 0.0:
        q1, dot = -q1, -dot   # camino más corto (Tema 9.6, Limitaciones)

    if dot > 0.9995:
        q = q0 + t * (q1 - q0)
        return q / np.linalg.norm(q)

    omega = np.arccos(np.clip(dot, -1.0, 1.0))
    return (np.sin((1 - t) * omega) * q0 + np.sin(t * omega) * q1) / np.sin(omega)
