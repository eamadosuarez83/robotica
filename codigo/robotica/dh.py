"""Denavit-Hartenberg y cinematica directa (Bloque 11).

Portado casi 1:1 de `dh.py` de robotica-manipuladores: su convencion
de radianes ya coincide con la de este curso.

Una tabla DH es una matriz de n x 5, una fila por articulacion:

    [theta, d, a, alpha, tipo]

* theta: offset del angulo en torno a Z (rad).
* d: desplazamiento a lo largo de Z.
* a: desplazamiento a lo largo de X.
* alpha: angulo en torno a X (rad).
* tipo: 0 = rotacional (q se suma a theta), 1 = prismatica (q se suma a d).
"""

from __future__ import annotations

import numpy as np

from .rotaciones import _seno_coseno

__all__ = ["matriz_dh", "directa", "marcos", "matriz_dh_simbolica", "directa_simbolica"]


def matriz_dh(theta: float, d: float, a: float, alpha: float) -> np.ndarray:
    """Matriz ``A(i-1 -> i)`` de Denavit-Hartenberg (Tema 11.4).

    ``A = rotz(theta) @ transl(0,0,d) @ transl(a,0,0) @ rotx(alpha)``
    """
    st, ct = _seno_coseno(theta)
    sa, ca = _seno_coseno(alpha)
    return np.array([[ct, -ca * st, sa * st, a * ct],
                     [st, ca * ct, -sa * ct, a * st],
                     [0, sa, ca, d],
                     [0, 0, 0, 1]], dtype=float)


def _fila(dh_i, qi):
    theta, d, a, alpha, tipo = dh_i
    if tipo == 0:
        return matriz_dh(theta + qi, d, a, alpha)
    return matriz_dh(theta, d + qi, a, alpha)


def directa(dh, q) -> np.ndarray:
    """Cinemática directa ``T = A01 @ A12 @ ... @ A(n-1)n``.

    Parámetros
    ----------
    dh : array (n, 5)
        Tabla de Denavit-Hartenberg.
    q : array (n,) o (k, n)
        Variables articulares en RADIANES (o unidades de longitud en
        las prismáticas). Con una matriz de k filas se calcula una
        trayectoria completa.
    """
    dh = np.atleast_2d(np.asarray(dh, dtype=float))
    q = np.asarray(q, dtype=float)
    n = dh.shape[0]
    if q.shape[-1] != n:
        raise ValueError(f"q tiene {q.shape[-1]} valores y la tabla DH {n} filas")
    if q.ndim == 2:
        return np.stack([directa(dh, qi) for qi in q])
    T = np.eye(4)
    for i in range(n):
        T = T @ _fila(dh[i], q[i])
    return T


def marcos(dh, q) -> list[np.ndarray]:
    """Lista ``[A00, A01, ..., A0n]`` con los sistemas de cada eslabón.

    ``A00`` es la identidad (la base). Útil para dibujar el brazo
    completo (Tema 11.5, animador de deslizadores).
    """
    dh = np.atleast_2d(np.asarray(dh, dtype=float))
    q = np.asarray(q, dtype=float).reshape(-1)
    T = np.eye(4)
    salida = [T.copy()]
    for i in range(dh.shape[0]):
        T = T @ _fila(dh[i], q[i])
        salida.append(T.copy())
    return salida


# ---------------------------------------------------------------- simbólica

def matriz_dh_simbolica(theta, d, a, alpha):
    """Matriz DH con SymPy; acepta símbolos o números."""
    import sympy as sp
    return sp.Matrix([[sp.cos(theta), -sp.cos(alpha) * sp.sin(theta), sp.sin(alpha) * sp.sin(theta), a * sp.cos(theta)],
                      [sp.sin(theta), sp.cos(alpha) * sp.cos(theta), -sp.sin(alpha) * sp.cos(theta), a * sp.sin(theta)],
                      [0, sp.sin(alpha), sp.cos(alpha), d],
                      [0, 0, 0, 1]])


def directa_simbolica(dh, q, simplificar: bool = True):
    """Cinemática directa simbólica (SymPy).

    ``dh`` puede mezclar números y símbolos (por ejemplo longitudes L1).
    """
    import sympy as sp

    def exacto(v):
        if isinstance(v, (int, float, np.floating)):
            return sp.nsimplify(float(v), [sp.pi])
        return v

    T = sp.eye(4)
    for fila, qi in zip(dh, q):
        theta, d, a, alpha, tipo = (exacto(v) for v in fila)
        if tipo == 0:
            T = T * matriz_dh_simbolica(theta + qi, d, a, alpha)
        else:
            T = T * matriz_dh_simbolica(theta, d + qi, a, alpha)
    return sp.simplify(T) if simplificar else T
