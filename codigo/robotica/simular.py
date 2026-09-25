"""Integradores numéricos propios de sistemas de primer orden.

Bloque 05 -- Ecuaciones diferenciales y simulación. `f(t, z)` debe
devolver dz/dt como un array del mismo tamaño que el estado `z`.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def euler(f: Callable, x0, t: np.ndarray) -> np.ndarray:
    """Integra dz/dt = f(t, z) con el método de Euler.

    Devuelve un array (len(t), len(x0)) con el estado en cada instante de `t`.
    """
    t = np.asarray(t, dtype=float)
    x0 = np.atleast_1d(np.asarray(x0, dtype=float))
    X = np.zeros((len(t), x0.size))
    X[0] = x0
    for i in range(len(t) - 1):
        h = t[i + 1] - t[i]
        X[i + 1] = X[i] + h * np.asarray(f(t[i], X[i]), dtype=float)
    return X


def rk4(f: Callable, x0, t: np.ndarray) -> np.ndarray:
    """Integra dz/dt = f(t, z) con Runge-Kutta de cuarto orden.

    Devuelve un array (len(t), len(x0)) con el estado en cada instante de `t`.
    """
    t = np.asarray(t, dtype=float)
    x0 = np.atleast_1d(np.asarray(x0, dtype=float))
    X = np.zeros((len(t), x0.size))
    X[0] = x0
    for i in range(len(t) - 1):
        h = t[i + 1] - t[i]
        ti, xi = t[i], X[i]
        k1 = np.asarray(f(ti, xi), dtype=float)
        k2 = np.asarray(f(ti + h / 2, xi + h / 2 * k1), dtype=float)
        k3 = np.asarray(f(ti + h / 2, xi + h / 2 * k2), dtype=float)
        k4 = np.asarray(f(ti + h, xi + h * k3), dtype=float)
        X[i + 1] = xi + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return X
