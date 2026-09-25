"""Romperlo a proposito: pendulo sin friccion simulado con Euler y un
paso h grande. La energia (que deberia ser constante) crece con el
tiempo -- un artefacto puramente numerico (Bloque 05, Tema 5.6).

Correr con:
    python codigo/bloque_05/romper_euler_paso_grande.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.simular import euler, rk4  # noqa: E402

G, L, M = 9.81, 1.0, 1.0


def f_pendulo(t, z):
    theta, omega = z
    return [omega, -(G / L) * np.sin(theta)]


def energia(Z):
    theta, omega = Z[:, 0], Z[:, 1]
    K = 0.5 * M * (L * omega) ** 2
    U = M * G * L * (1 - np.cos(theta))
    return K + U


def main() -> None:
    theta0 = np.radians(30)
    z0 = [theta0, 0.0]
    t_final = 15.0

    pasos = [0.2, 0.05, 0.01]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for h in pasos:
        t = np.arange(0, t_final, h)
        Z = euler(f_pendulo, z0, t)
        E = energia(Z)
        ax1.plot(t, E, label=f"Euler, h={h}")
        print(f"Euler h={h}: energía inicial={E[0]:.4f} J, "
              f"energía final={E[-1]:.4f} J, crecimiento={100*(E[-1]/E[0]-1):.1f}%")

    h_grande = pasos[0]
    t = np.arange(0, t_final, h_grande)
    Z_rk4 = rk4(f_pendulo, z0, t)
    E_rk4 = energia(Z_rk4)
    ax1.plot(t, E_rk4, "k--", lw=2, label=f"RK4, h={h_grande} (referencia)")
    print(f"RK4   h={h_grande}: energía inicial={E_rk4[0]:.4f} J, "
          f"energía final={E_rk4[-1]:.4f} J, crecimiento={100*(E_rk4[-1]/E_rk4[0]-1):.1f}%")

    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("Energía mecánica [J]")
    ax1.set_title("Energía del péndulo sin fricción (debería ser constante)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    t = np.arange(0, t_final, pasos[0])
    Z = euler(f_pendulo, z0, t)
    ax2.plot(t, np.degrees(Z[:, 0]), color="tab:red")
    ax2.axhline(30, color="gray", ls=":", label="amplitud inicial (30°)")
    ax2.axhline(-30, color="gray", ls=":")
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("θ(t) [°]")
    ax2.set_title(f"Euler con h={pasos[0]}: la amplitud crece sola")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
