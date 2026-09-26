"""Modelo dinamico del 2R (Bloques 14-15) reutilizado por los
laboratorios del Bloque 20: matriz de masas, gravedad+Coriolis, y una
funcion de dinamica directa lista para simular con robotica.simular.

No es parte de codigo/robotica/ (el Bloque 20 no agrega modulos a la
libreria, ver ESTRUCTURA.md): es utilidad compartida entre los
scripts de este bloque.
"""

import sys
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import deducir_lagrange, matriz_masas, separar_gravedad_y_coriolis  # noqa: E402

M1, M2, L1, L2, G_GRAV = 1.3, 0.7, 0.30, 0.20, 9.81


def construir_modelo(m1_val=M1, m2_val=M2):
    """Devuelve (M_f, resto_f, G_f): M(q), (C q̇+G)(q,q̇) y G(q), como
    funciones numpy listas para evaluar."""
    t = sp.symbols('t')
    m1, m2, L1s, L2s, g = sp.symbols('m1 m2 L1 L2 g', positive=True)
    theta1 = sp.Function('theta1')(t)
    theta2 = sp.Function('theta2')(t)
    x1, y1 = L1s * sp.cos(theta1), L1s * sp.sin(theta1)
    x2 = x1 + L2s * sp.cos(theta1 + theta2)
    y2 = y1 + L2s * sp.sin(theta1 + theta2)
    K = (sp.Rational(1, 2) * m1 * (sp.diff(x1, t)**2 + sp.diff(y1, t)**2)
         + sp.Rational(1, 2) * m2 * (sp.diff(x2, t)**2 + sp.diff(y2, t)**2))
    U = m1 * g * y1 + m2 * g * y2
    ecuaciones, q, qdot, qddot = deducir_lagrange(K, U, [theta1, theta2], t)
    M = matriz_masas(ecuaciones, qddot)
    Gv, C_qdot = separar_gravedad_y_coriolis(ecuaciones, M, qdot, qddot)

    valores = {m1: m1_val, m2: m2_val, L1s: L1, L2s: L2, g: G_GRAV}
    M_f = sp.lambdify(list(q), M.subs(valores), 'numpy')
    resto_f = sp.lambdify(list(q) + list(qdot), (Gv + C_qdot).subs(valores), 'numpy')
    G_f = sp.lambdify(list(q), Gv.subs(valores), 'numpy')
    return M_f, resto_f, G_f


def dinamica_directa(M_f, resto_f):
    """f(t, z, tau) -> dz/dt para z=(theta1,theta2,theta1p,theta2p),
    dinamica directa real de la planta (Bloque 15, Tema 15.3)."""
    def f(t, z, tau):
        q, qdot = z[:2], z[2:]
        Mn = np.array(M_f(*q), dtype=float)
        resto = np.array(resto_f(*q, *qdot), dtype=float).flatten()
        qddot = np.linalg.solve(Mn, np.asarray(tau) - resto)
        return np.concatenate([qdot, qddot])
    return f
