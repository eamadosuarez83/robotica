"""Cinematica directa del brazo plano 2R, a mano (Bloque 01, Tema 1.4).

Correr con:
    python codigo/bloque_01/cinematica_2r.py
"""

import numpy as np
import matplotlib.pyplot as plt

L1, L2 = 0.30, 0.20  # metros, el problema que abre el bloque


def cinematica_directa_2r(theta1: float, theta2: float,
                           L1: float = L1, L2: float = L2) -> tuple[float, float]:
    """Posicion (x, y) de la punta del brazo 2R.

    theta1, theta2 en RADIANES. theta2 es el angulo del segundo
    eslabon respecto al primero (no respecto al eje x fijo).
    """
    x = L1 * np.cos(theta1) + L2 * np.cos(theta1 + theta2)
    y = L1 * np.sin(theta1) + L2 * np.sin(theta1 + theta2)
    return x, y


def espacio_de_trabajo(n: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """Nube de puntos alcanzables, barriendo theta1 y theta2 en [-pi, pi]."""
    t1 = np.linspace(-np.pi, np.pi, n)
    t2 = np.linspace(-np.pi, np.pi, n)
    T1, T2 = np.meshgrid(t1, t2)
    X = L1 * np.cos(T1) + L2 * np.cos(T1 + T2)
    Y = L1 * np.sin(T1) + L2 * np.sin(T1 + T2)
    return X.ravel(), Y.ravel()


def main() -> None:
    theta1, theta2 = np.radians(40), np.radians(30)
    x, y = cinematica_directa_2r(theta1, theta2)
    print(f"theta1=40°, theta2=30° -> punta en ({x:.3f}, {y:.3f}) m")
    print("Valor esperado a mano (Tema 1.4): (0.298, 0.381) m")

    Xw, Yw = espacio_de_trabajo()

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))

    ax = axes[0]
    x_codo = L1 * np.cos(theta1)
    y_codo = L1 * np.sin(theta1)
    ax.plot([0, x_codo, x], [0, y_codo, y], "o-", lw=4, ms=10, color="tab:blue")
    ax.plot(0, 0, "s", ms=12, color="k")
    alcance = L1 + L2
    ax.set_xlim(-alcance * 1.1, alcance * 1.1)
    ax.set_ylim(-alcance * 1.1, alcance * 1.1)
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_title("Brazo 2R (θ1=40°, θ2=30°)")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")

    ax = axes[1]
    ax.scatter(Xw, Yw, s=1, alpha=0.3, color="tab:orange")
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_title("Espacio de trabajo (nube de puntos)")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
