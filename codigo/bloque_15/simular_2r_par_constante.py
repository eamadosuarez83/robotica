"""Simula el 2R con dinamica directa (par constante en cada motor),
integrando el espacio de estados z=(theta1,theta2,theta1p,theta2p)
con robotica.simular.rk4 (Bloque 15, Temas 15.3-15.4).

Correr con:
    python codigo/bloque_15/simular_2r_par_constante.py
"""

import sys
from pathlib import Path

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import deducir_lagrange, matriz_masas, separar_gravedad_y_coriolis  # noqa: E402
from robotica.simular import rk4  # noqa: E402


def construir_modelo():
    t = sp.symbols('t')
    m1, m2, L1, L2, g = sp.symbols('m1 m2 L1 L2 g', positive=True)
    theta1 = sp.Function('theta1')(t)
    theta2 = sp.Function('theta2')(t)
    x1, y1 = L1 * sp.cos(theta1), L1 * sp.sin(theta1)
    x2 = x1 + L2 * sp.cos(theta1 + theta2)
    y2 = y1 + L2 * sp.sin(theta1 + theta2)
    K = (sp.Rational(1, 2) * m1 * (sp.diff(x1, t)**2 + sp.diff(y1, t)**2)
         + sp.Rational(1, 2) * m2 * (sp.diff(x2, t)**2 + sp.diff(y2, t)**2))
    U = m1 * g * y1 + m2 * g * y2
    ecuaciones, q, qdot, qddot = deducir_lagrange(K, U, [theta1, theta2], t)
    M = matriz_masas(ecuaciones, qddot)
    G, C_qdot = separar_gravedad_y_coriolis(ecuaciones, qdot, qddot)

    valores = {m1: 1.3, m2: 0.7, L1: 0.30, L2: 0.20, g: 9.81}
    M_f = sp.lambdify(list(q), M.subs(valores), 'numpy')
    resto_f = sp.lambdify(list(q) + list(qdot), (G + C_qdot).subs(valores), 'numpy')
    return M_f, resto_f


def main() -> None:
    M_f, resto_f = construir_modelo()

    def dinamica_directa(t, z, tau):
        q, qdot = z[:2], z[2:]
        Mn = np.array(M_f(*q), dtype=float)
        resto = np.array(resto_f(*q, *qdot), dtype=float).flatten()
        qddot = np.linalg.solve(Mn, tau - resto)
        return np.concatenate([qdot, qddot])

    z0 = np.array([np.radians(10), np.radians(-10), 0.0, 0.0])
    t_arr = np.linspace(0, 4, 2000)

    tau_constante = np.array([2.0, 0.5])   # N·m, un escalón de par
    Z = rk4(lambda t, z: dinamica_directa(t, z, tau_constante), z0, t_arr)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t_arr, np.degrees(Z[:, 0]), label="θ1(t)")
    ax.plot(t_arr, np.degrees(Z[:, 1]), label="θ2(t)")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("ángulo [°]")
    ax.set_title(f"Dinámica directa del 2R con τ={tuple(tau_constante)} N·m constante")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    print(f"θ1 final: {np.degrees(Z[-1,0]):.1f}°, θ2 final: {np.degrees(Z[-1,1]):.1f}°")
    print("Con par constante y sin control, el brazo acelera sin límite (no hay nada")
    print("que lo frene): esto motiva el control del Bloque 18 en adelante.")


if __name__ == "__main__":
    main()
