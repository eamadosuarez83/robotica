"""Compara Euler, RK4 (propios) y solve_ivp para el pendulo no lineal
sin friccion (Bloque 05, Tema 5.5).

Correr con:
    python codigo/bloque_05/simular_pendulo.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.simular import euler, rk4  # noqa: E402

G, L = 9.81, 1.0


def f_pendulo(t, z):
    theta, omega = z
    return [omega, -(G / L) * np.sin(theta)]


def main() -> None:
    theta0 = np.radians(30)
    z0 = [theta0, 0.0]
    t = np.linspace(0, 10, 500)   # paso h razonable, mismo para los tres métodos

    Z_euler = euler(f_pendulo, z0, t)
    Z_rk4 = rk4(f_pendulo, z0, t)
    sol = solve_ivp(f_pendulo, [t[0], t[-1]], z0, t_eval=t, method="RK45", rtol=1e-9)

    error_rk4 = np.max(np.abs(Z_rk4[:, 0] - sol.y[0]))
    error_euler = np.max(np.abs(Z_euler[:, 0] - sol.y[0]))
    print(f"Error máximo en θ(t), Euler  vs. solve_ivp: {error_euler:.4f} rad")
    print(f"Error máximo en θ(t), RK4    vs. solve_ivp: {error_rk4:.4f} rad")
    print("RK4 debería quedar mucho más cerca de solve_ivp que Euler, con el mismo paso.")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t, np.degrees(Z_euler[:, 0]), "--", color="tab:red", label="Euler (propio)")
    ax.plot(t, np.degrees(Z_rk4[:, 0]), "-", color="tab:blue", label="RK4 (propio)")
    ax.plot(t, np.degrees(sol.y[0]), ":", color="k", lw=2, label="solve_ivp (RK45)")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("θ(t) [°]")
    ax.set_title(f"Péndulo no lineal, θ0=30°, mismo paso h={t[1]-t[0]:.3f} s")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
