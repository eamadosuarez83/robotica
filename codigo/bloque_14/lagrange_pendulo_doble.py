"""Deduce el pendulo doble con Lagrange, lo simula con robotica.simular
(Bloque 05) y muestra sensibilidad a condiciones iniciales (caos) para
amplitudes grandes (Bloque 14, Tema 14.3).

Correr con:
    python codigo/bloque_14/lagrange_pendulo_doble.py
"""

import sys
from pathlib import Path

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import deducir_lagrange, matriz_masas, separar_gravedad_y_coriolis  # noqa: E402
from robotica.simular import rk4  # noqa: E402


def deducir_modelo():
    t = sp.symbols('t')
    m1, m2, L1, L2, g = sp.symbols('m1 m2 L1 L2 g', positive=True)
    theta1 = sp.Function('theta1')(t)
    theta2 = sp.Function('theta2')(t)

    x1 = L1 * sp.sin(theta1)
    y1 = -L1 * sp.cos(theta1)
    x2 = x1 + L2 * sp.sin(theta2)
    y2 = y1 - L2 * sp.cos(theta2)

    K = (sp.Rational(1, 2) * m1 * (sp.diff(x1, t)**2 + sp.diff(y1, t)**2)
         + sp.Rational(1, 2) * m2 * (sp.diff(x2, t)**2 + sp.diff(y2, t)**2))
    U = m1 * g * y1 + m2 * g * y2

    ecuaciones, q, qdot, qddot = deducir_lagrange(K, U, [theta1, theta2], t)
    M = matriz_masas(ecuaciones, qddot)
    G, C_qdot = separar_gravedad_y_coriolis(ecuaciones, M, qdot, qddot)
    return M, G, C_qdot, q, qdot, (m1, m2, L1, L2, g)


def main() -> None:
    M, G, C_qdot, q, qdot, params = deducir_modelo()
    m1, m2, L1, L2, g = params
    valores = {m1: 1.0, m2: 1.0, L1: 1.0, L2: 1.0, g: 9.81}

    M_f = sp.lambdify(list(q), M.subs(valores), 'numpy')
    resto_f = sp.lambdify(list(q) + list(qdot), (G + C_qdot).subs(valores), 'numpy')

    def f(t, z):
        t1, t2, w1, w2 = z
        Mn = np.array(M_f(t1, t2), dtype=float)
        resto = np.array(resto_f(t1, t2, w1, w2), dtype=float).flatten()
        alpha = np.linalg.solve(Mn, -resto)
        return [w1, w2, alpha[0], alpha[1]]

    t_arr = np.linspace(0, 20, 10000)

    z0_a = [np.radians(150), np.radians(150), 0.0, 0.0]
    z0_b = [np.radians(150) + 1e-3, np.radians(150), 0.0, 0.0]

    Za = rk4(f, z0_a, t_arr)
    Zb = rk4(f, z0_b, t_arr)

    diferencia = np.abs(Za[:, 0] - Zb[:, 0])
    print(f"Diferencia en θ1 al inicio: {diferencia[0]:.2e} rad")
    print(f"Diferencia en θ1 a t=2s:    {diferencia[np.searchsorted(t_arr, 2)]:.2e} rad")
    print(f"Diferencia en θ1 a t=10s:   {diferencia[np.searchsorted(t_arr, 10)]:.2e} rad")
    print(f"Diferencia en θ1 a t=20s:   {diferencia[-1]:.2e} rad")
    print("Con una diferencia inicial de 1e-3 rad, el péndulo doble amplifica")
    print("el error exponencialmente: comportamiento caótico (amplitud grande).")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.plot(t_arr, np.degrees(Za[:, 0]), label="condición A")
    ax1.plot(t_arr, np.degrees(Zb[:, 0]), label="condición B (+1e-3 rad)", alpha=0.7)
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("θ1 [°]")
    ax1.set_title("Dos condiciones iniciales casi idénticas")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.semilogy(t_arr, diferencia + 1e-12)
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("|Δθ1| [rad] (escala log)")
    ax2.set_title("Divergencia exponencial (caos)")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
