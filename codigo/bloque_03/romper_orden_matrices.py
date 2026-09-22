"""Romperlo a proposito: aplicar dos transformaciones en orden invertido
a la imagen de una casita, y comparar (Bloque 03, Tema 3.2).

Correr con:
    python codigo/bloque_03/romper_orden_matrices.py
"""

import numpy as np
import matplotlib.pyplot as plt

# Una "casita" asimetrica: base cuadrada + techo triangular, para que el
# orden de las transformaciones sea visualmente evidente.
CASITA = np.array([
    [0, 2, 2, 1, 0, 0],
    [0, 0, 1.5, 2.5, 1.5, 0],
])

A = np.array([[0, -1], [1, 0]])   # rotacion 90°
B = np.array([[1, 0], [0, -1]])   # reflexion en el eje x


def dibujar(ax, figura, color, titulo):
    ax.plot(figura[0], figura[1], "o-", color=color, lw=2)
    ax.fill(figura[0], figura[1], color=color, alpha=0.2)
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_title(titulo)


def main() -> None:
    primero_A_luego_B = B @ (A @ CASITA)   # aplica A y despues B: matriz BA
    primero_B_luego_A = A @ (B @ CASITA)   # aplica B y despues A: matriz AB

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    dibujar(axes[0], CASITA, "tab:blue", "Original")
    dibujar(axes[1], primero_A_luego_B, "tab:green",
            "Primero rota 90°, luego refleja\n(matriz BA)")
    dibujar(axes[2], primero_B_luego_A, "tab:red",
            "Primero refleja, luego rota 90°\n(matriz AB)")

    plt.tight_layout()
    plt.show()

    print("BA =\n", B @ A)
    print("AB =\n", A @ B)
    print("¿BA == AB?", np.allclose(B @ A, A @ B))


if __name__ == "__main__":
    main()
