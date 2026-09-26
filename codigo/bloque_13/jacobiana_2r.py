"""Jacobiana simbolica (SymPy) y geometrica (propia) del 2R, verificadas
entre si y contra diferencias finitas; y para curso_3gdl (Bloque 13,
Temas 13.1-13.3).

Correr con:
    python codigo/bloque_13/jacobiana_2r.py
"""

import sys
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from robotica.jacobiana import jacobiana_geometrica  # noqa: E402


def jacobiana_diferencias_finitas(dh, q, h=1e-6):
    q = np.asarray(q, dtype=float)
    n = len(q)
    J = np.zeros((3, n))
    p0 = directa(dh, q)[:3, 3]
    for j in range(n):
        dq = np.zeros(n)
        dq[j] = h
        p1 = directa(dh, q + dq)[:3, 3]
        J[:, j] = (p1 - p0) / h
    return J


def jacobiana_simbolica_2r():
    t1, t2, L1, L2 = sp.symbols('theta1 theta2 L1 L2')
    x = L1 * sp.cos(t1) + L2 * sp.cos(t1 + t2)
    y = L1 * sp.sin(t1) + L2 * sp.sin(t1 + t2)
    J = sp.Matrix([[sp.diff(x, t1), sp.diff(x, t2)],
                   [sp.diff(y, t1), sp.diff(y, t2)]])
    return sp.simplify(J), (t1, t2, L1, L2)


def main() -> None:
    L1v, L2v = 0.30, 0.20
    theta1v, theta2v = np.radians(40), np.radians(30)

    print("=== Jacobiana simbólica (SymPy) del 2R ===")
    Jsym, (t1, t2, L1, L2) = jacobiana_simbolica_2r()
    sp.pprint(Jsym)
    J_sym_num = np.array(Jsym.subs({t1: theta1v, t2: theta2v, L1: L1v, L2: L2v}), dtype=float)

    dh = [[0, 0, L1v, 0, 0], [0, 0, L2v, 0, 0]]
    J_geo = jacobiana_geometrica(dh, [theta1v, theta2v])[:2, :]
    J_fd = jacobiana_diferencias_finitas(dh, [theta1v, theta2v])[:2, :]

    print(f"\nJacobiana simbólica evaluada:\n{np.round(J_sym_num, 5)}")
    print(f"Jacobiana geométrica (propia):\n{np.round(J_geo, 5)}")
    print(f"Jacobiana por diferencias finitas:\n{np.round(J_fd, 5)}")
    assert np.max(np.abs(J_sym_num - J_geo)) < 1e-9
    assert np.max(np.abs(J_geo - J_fd)) < 1e-4
    print("OK: las tres coinciden.\n")

    # Ejemplo resuelto del Tema 13.1
    q_punto = np.array([1.0, 0.5])
    x_punto = J_geo @ q_punto
    print(f"Con θ1̇=1, θ2̇=0.5 rad/s: ẋ = {np.round(x_punto, 3)} m/s "
          f"(esperado ≈ (-0.475, 0.332), Bloque 04 Tema 4.4)")

    # curso_3gdl
    print("\n=== curso_3gdl (3R antropomórfico, Bloque 11) ===")
    L1c, L2c, L3c = 15.0, 12.0, 10.0
    dh3 = [[0, L1c, 0, np.pi / 2, 0], [0, 0, L2c, 0, 0], [0, 0, L3c, 0, 0]]
    q3 = np.radians([30, 45, -20])
    J3_geo = jacobiana_geometrica(dh3, q3)[:3, :]
    J3_fd = jacobiana_diferencias_finitas(dh3, q3)
    error = np.max(np.abs(J3_geo - J3_fd))
    print(f"Error máx. geométrica vs. diferencias finitas: {error:.2e}")
    assert error < 1e-3


if __name__ == "__main__":
    main()
