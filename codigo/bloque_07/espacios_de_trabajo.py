"""Espacio de trabajo de tres configuraciones clasicas: cartesiana,
SCARA y angular (Bloque 07, Tema 7.3).

El caso angular reutiliza la cinematica directa del brazo 2R del
Bloque 01 (Tema 1.4).

Correr con:
    python codigo/bloque_07/espacios_de_trabajo.py
"""

import numpy as np
import matplotlib.pyplot as plt


def espacio_cartesiano(ax):
    """PPP: una caja. Corte en el plano x-z para un rango dado de y."""
    x_min, x_max = 0.1, 0.5
    z_min, z_max = 0.0, 0.4
    ax.add_patch(plt.Rectangle((x_min, z_min), x_max - x_min, z_max - z_min,
                                facecolor="tab:blue", alpha=0.3, edgecolor="tab:blue"))
    ax.set_xlim(-0.1, 0.7)
    ax.set_ylim(-0.1, 0.5)
    ax.set_aspect("equal")
    ax.set_title("Cartesiano (PPP)\ncorte x-z: una caja")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("z [m]")
    ax.grid(True, alpha=0.3)


def espacio_scara(ax):
    """RRP: un anillo en planta (vista superior, plano x-y)."""
    L1, L2 = 0.30, 0.25
    n = 300
    t1 = np.linspace(-np.pi, np.pi, n)
    t2 = np.linspace(-np.pi, np.pi, n)
    T1, T2 = np.meshgrid(t1, t2)
    X = L1 * np.cos(T1) + L2 * np.cos(T1 + T2)
    Y = L1 * np.sin(T1) + L2 * np.sin(T1 + T2)
    ax.scatter(X.ravel(), Y.ravel(), s=1, alpha=0.2, color="tab:green")
    ax.set_aspect("equal")
    ax.set_title("SCARA (RRP)\nvista superior: un anillo")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.grid(True, alpha=0.3)


def espacio_angular_2r(ax):
    """RRR simplificado a 2R plano (Bloque 01): región con un hueco cerca
    de la base cuando L1 != L2."""
    L1, L2 = 0.30, 0.20
    n = 300
    t1 = np.linspace(-np.pi, np.pi, n)
    t2 = np.linspace(-np.pi, np.pi, n)
    T1, T2 = np.meshgrid(t1, t2)
    X = L1 * np.cos(T1) + L2 * np.cos(T1 + T2)
    Y = L1 * np.sin(T1) + L2 * np.sin(T1 + T2)
    ax.scatter(X.ravel(), Y.ravel(), s=1, alpha=0.2, color="tab:orange")
    ax.set_aspect("equal")
    ax.set_title("Angular / antropomórfico (RRR)\nplano 2R: hueco cerca de la base")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.grid(True, alpha=0.3)


def main() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    espacio_cartesiano(axes[0])
    espacio_scara(axes[1])
    espacio_angular_2r(axes[2])
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
