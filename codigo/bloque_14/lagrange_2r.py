"""Deduce M, C*qdot, G del brazo 2R con Lagrange, verifica simetria y
definitud positiva de M, y compara G contra la estatica del Bloque 13
(Bloque 14, Temas 14.4-14.6).

Correr con:
    python codigo/bloque_14/lagrange_2r.py
"""

import sys
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import deducir_lagrange, matriz_masas, separar_gravedad_y_coriolis  # noqa: E402
from robotica.jacobiana import jacobiana_geometrica, par_estatico  # noqa: E402


def deducir_2r():
    t = sp.symbols('t')
    m1, m2, L1, L2, g = sp.symbols('m1 m2 L1 L2 g', positive=True)
    theta1 = sp.Function('theta1')(t)
    theta2 = sp.Function('theta2')(t)

    x1 = L1 * sp.cos(theta1)
    y1 = L1 * sp.sin(theta1)
    x2 = x1 + L2 * sp.cos(theta1 + theta2)
    y2 = y1 + L2 * sp.sin(theta1 + theta2)

    K = (sp.Rational(1, 2) * m1 * (sp.diff(x1, t)**2 + sp.diff(y1, t)**2)
         + sp.Rational(1, 2) * m2 * (sp.diff(x2, t)**2 + sp.diff(y2, t)**2))
    U = m1 * g * y1 + m2 * g * y2

    ecuaciones, q, qdot, qddot = deducir_lagrange(K, U, [theta1, theta2], t)
    M = matriz_masas(ecuaciones, qddot)
    G, C_qdot = separar_gravedad_y_coriolis(ecuaciones, qdot, qddot)
    return M, G, C_qdot, q, qdot, qddot, (m1, m2, L1, L2, g)


def main() -> None:
    M, G, C_qdot, q, qdot, qddot, params = deducir_2r()
    m1, m2, L1, L2, g = params

    print("M(θ) =")
    sp.pprint(M)
    print("\nG(θ) =")
    sp.pprint(G)
    print("\nC(θ,θ̇)θ̇ =")
    sp.pprint(C_qdot)

    valores = {m1: 1.0, m2: 0.5, L1: 0.30, L2: 0.20, g: 9.81}
    Mf = sp.lambdify([q[0], q[1]], M.subs(valores), 'numpy')
    Gf = sp.lambdify([q[0], q[1]], G.subs(valores), 'numpy')

    print("\n=== Verificación: M simétrica y definida positiva (Tema 14.6) ===")
    rng = np.random.default_rng(0)
    for _ in range(20):
        t1, t2 = rng.uniform(-np.pi, np.pi, 2)
        Mn = np.array(Mf(t1, t2), dtype=float)
        simetrica = np.allclose(Mn, Mn.T)
        autovalores = np.linalg.eigvalsh(Mn)
        assert simetrica and np.all(autovalores > 0)
    print("OK: simétrica y definida positiva en 20 posturas aleatorias.")

    print("\n=== Verificación: G(θ) coincide con la estática del Bloque 13 ===")
    theta1v, theta2v = np.radians(30), np.radians(45)
    Gn = np.array(Gf(theta1v, theta2v), dtype=float).flatten()

    # Bloque 13: J^T F para el peso de cada masa, en el marco de cada una.
    dh_m1 = [[0, 0, 0.30, 0, 0]]
    J1 = jacobiana_geometrica(dh_m1, [theta1v])[:3, :]
    tau_m1 = par_estatico(J1, [0, -1.0 * 9.81, 0])

    dh_m2 = [[0, 0, 0.30, 0, 0], [0, 0, 0.20, 0, 0]]
    J2 = jacobiana_geometrica(dh_m2, [theta1v, theta2v])[:3, :]
    tau_m2 = par_estatico(J2, [0, -0.5 * 9.81, 0])

    tau_total = np.array([tau_m1[0] + tau_m2[0], tau_m2[1]])
    print(f"G(θ) [Lagrange]:        {np.round(Gn, 4)}")
    print(f"-J1^T F1 - J2^T F2 [Bloque 13]: {np.round(-tau_total, 4)}")
    assert np.allclose(Gn, -tau_total, atol=1e-9)
    print("OK: coinciden (G es el par que HACE la gravedad; el motor debe dar el opuesto).")

    print("\n=== Ejercicio B1, Tema 14.5: G en brazo horizontal vs. vertical ===")
    g1_horizontal = np.array(Gf(0, 0), dtype=float).flatten()[0]
    g1_vertical = np.array(Gf(np.pi / 2, 0), dtype=float).flatten()[0]
    print(f"G1(θ1=0°,θ2=0°)  = {g1_horizontal:.4f} (horizontal, máximo brazo de palanca)")
    print(f"G1(θ1=90°,θ2=0°) = {g1_vertical:.4f} (vertical, ~0 esperado)")


if __name__ == "__main__":
    main()
