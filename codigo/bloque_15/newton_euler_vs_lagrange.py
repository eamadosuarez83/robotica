"""Compara newton_euler_plano contra las ecuaciones de Lagrange del
Bloque 14, con masas puntuales y con varillas uniformes de inercia
distribuida, en posturas aleatorias (Bloque 15, Tema 15.1).

Correr con:
    python codigo/bloque_15/newton_euler_vs_lagrange.py
"""

import sys
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import deducir_lagrange, newton_euler_plano  # noqa: E402


def lagrange_2r_puntual(vals):
    t = sp.symbols('t')
    m1, m2, L1, L2, g = sp.symbols('m1 m2 L1 L2 g', positive=True)
    th1 = sp.Function('theta1')(t)
    th2 = sp.Function('theta2')(t)
    x1, y1 = L1 * sp.cos(th1), L1 * sp.sin(th1)
    x2 = x1 + L2 * sp.cos(th1 + th2)
    y2 = y1 + L2 * sp.sin(th1 + th2)
    K = (sp.Rational(1, 2) * m1 * (sp.diff(x1, t)**2 + sp.diff(y1, t)**2)
         + sp.Rational(1, 2) * m2 * (sp.diff(x2, t)**2 + sp.diff(y2, t)**2))
    U = m1 * g * y1 + m2 * g * y2
    ecs, q, qd, qdd = deducir_lagrange(K, U, [th1, th2], t)
    subs = {m1: vals['m1'], m2: vals['m2'], L1: vals['L1'], L2: vals['L2'], g: vals['g']}
    return [sp.lambdify([q[0], q[1], qd[0], qd[1], qdd[0], qdd[1]], e.subs(subs), 'numpy')
            for e in ecs]


def lagrange_2r_varilla(vals):
    t = sp.symbols('t')
    m1, m2, L1, L2, g, Ic1, Ic2 = sp.symbols('m1 m2 L1 L2 g Ic1 Ic2', positive=True)
    th1 = sp.Function('theta1')(t)
    th2 = sp.Function('theta2')(t)
    xc1, yc1 = (L1 / 2) * sp.cos(th1), (L1 / 2) * sp.sin(th1)
    xc2 = L1 * sp.cos(th1) + (L2 / 2) * sp.cos(th1 + th2)
    yc2 = L1 * sp.sin(th1) + (L2 / 2) * sp.sin(th1 + th2)
    w1, w2 = sp.diff(th1, t), sp.diff(th1 + th2, t)
    K = (sp.Rational(1, 2) * m1 * (sp.diff(xc1, t)**2 + sp.diff(yc1, t)**2) + sp.Rational(1, 2) * Ic1 * w1**2
         + sp.Rational(1, 2) * m2 * (sp.diff(xc2, t)**2 + sp.diff(yc2, t)**2) + sp.Rational(1, 2) * Ic2 * w2**2)
    U = m1 * g * yc1 + m2 * g * yc2
    ecs, q, qd, qdd = deducir_lagrange(K, U, [th1, th2], t)
    subs = {m1: vals['m1'], m2: vals['m2'], L1: vals['L1'], L2: vals['L2'],
            g: vals['g'], Ic1: vals['Ic1'], Ic2: vals['Ic2']}
    return [sp.lambdify([q[0], q[1], qd[0], qd[1], qdd[0], qdd[1]], e.subs(subs), 'numpy')
            for e in ecs]


def comparar(nombre, ecs_f, m, L, lc, I, n=30, seed=0):
    rng = np.random.default_rng(seed)
    maxerr = 0.0
    for _ in range(n):
        th = rng.uniform(-np.pi, np.pi, 2)
        thd = rng.uniform(-2, 2, 2)
        thdd = rng.uniform(-3, 3, 2)
        tau_lag = np.array([f(th[0], th[1], thd[0], thd[1], thdd[0], thdd[1]) for f in ecs_f])
        tau_ne = newton_euler_plano(th, thd, thdd, m, L, lc, I)
        maxerr = max(maxerr, np.max(np.abs(tau_lag - tau_ne)))
    print(f"{nombre}: error máx. Newton-Euler vs. Lagrange en {n} posturas aleatorias: {maxerr:.2e}")
    assert maxerr < 1e-9


def main() -> None:
    m1v, m2v, L1v, L2v, gv = 1.3, 0.7, 0.30, 0.20, 9.81

    print("=== Masas puntuales en la punta de cada eslabón ===")
    ecs_puntual = lagrange_2r_puntual(dict(m1=m1v, m2=m2v, L1=L1v, L2=L2v, g=gv))
    comparar("Puntual", ecs_puntual, [m1v, m2v], [L1v, L2v], [L1v, L2v], [0.0, 0.0])

    print("\n=== Varillas uniformes (centro de masa en L/2, inercia distribuida) ===")
    Ic1v, Ic2v = (1 / 12) * m1v * L1v**2, (1 / 12) * m2v * L2v**2
    ecs_varilla = lagrange_2r_varilla(dict(m1=m1v, m2=m2v, L1=L1v, L2=L2v, g=gv, Ic1=Ic1v, Ic2=Ic2v))
    comparar("Varilla uniforme", ecs_varilla, [m1v, m2v], [L1v, L2v],
              [L1v / 2, L2v / 2], [Ic1v, Ic2v])

    # Ejemplo resuelto del Tema 15.1
    print("\n=== Ejemplo resuelto (Tema 15.1) ===")
    th = [np.radians(30), np.radians(45)]
    tau = newton_euler_plano(th, [0.5, 0.3], [0.1, -0.2], [m1v, m2v], [L1v, L2v], [L1v, L2v], [0.0, 0.0])
    print(f"tau = {np.round(tau, 3)} N·m (esperado ≈ (5.457, 0.363))")


if __name__ == "__main__":
    main()
