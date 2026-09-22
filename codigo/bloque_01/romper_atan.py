"""Romperlo a proposito: atan contra atan2, y grados contra radianes.

Bloque 01, Tema 1.3. Correr con:
    python codigo/bloque_01/romper_atan.py
"""

import math
import numpy as np
import matplotlib.pyplot as plt

PUNTOS = [(1, 1), (-1, 1), (-1, -1), (1, -1), (-3, 4)]


def angulo_incorrecto_atan(x: float, y: float) -> float:
    """Version rota: usa atan(y/x), que pierde el cuadrante."""
    return math.atan(y / x)


def angulo_correcto_atan2(x: float, y: float) -> float:
    """Version correcta: atan2 respeta el signo de x e y."""
    return math.atan2(y, x)


def demo_atan_vs_atan2() -> None:
    print("=== atan(y/x)  vs  atan2(y,x) ===")
    print(f"{'punto':>12} | {'atan (°, MAL)':>15} | {'atan2 (°, bien)':>16}")
    for x, y in PUNTOS:
        malo = math.degrees(angulo_incorrecto_atan(x, y))
        bueno = math.degrees(angulo_correcto_atan2(x, y))
        print(f"{str((x, y)):>12} | {malo:15.1f} | {bueno:16.1f}")

    fig, ax = plt.subplots(figsize=(5, 5))
    for x, y in PUNTOS:
        malo = angulo_incorrecto_atan(x, y)
        bueno = angulo_correcto_atan2(x, y)
        ax.plot([0, x], [0, y], "o-", color="tab:blue", alpha=0.4)
        ax.plot([0, math.cos(malo)], [0, math.sin(malo)], "--", color="tab:red")
        ax.plot([0, math.cos(bueno)], [0, math.sin(bueno)], "-", color="tab:green")
    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_title("Rojo punteado = atan (mal) · Verde = atan2 (bien)")
    plt.show()


def demo_grados_vs_radianes() -> None:
    """Pasar un angulo en grados a una funcion que espera radianes."""
    theta1_deg, theta2_deg = 40.0, 30.0
    L1, L2 = 0.30, 0.20

    # Correcto: convertir a radianes antes de usar seno/coseno.
    t1, t2 = math.radians(theta1_deg), math.radians(theta2_deg)
    x_ok = L1 * math.cos(t1) + L2 * math.cos(t1 + t2)
    y_ok = L1 * math.sin(t1) + L2 * math.sin(t1 + t2)

    # Roto: se olvida la conversion y se usan los grados directamente.
    x_mal = L1 * math.cos(theta1_deg) + L2 * math.cos(theta1_deg + theta2_deg)
    y_mal = L1 * math.sin(theta1_deg) + L2 * math.sin(theta1_deg + theta2_deg)

    print("\n=== grados pasados directamente donde se esperan radianes ===")
    print(f"Correcto (convertido a radianes): ({x_ok:.3f}, {y_ok:.3f}) m")
    print(f"Roto (grados sin convertir):      ({x_mal:.3f}, {y_mal:.3f}) m")
    print("El brazo 'roto' termina en un punto sin relación con el pedido,")
    print("porque cos(40) y cos(0.698 rad) son números completamente distintos.")


if __name__ == "__main__":
    demo_atan_vs_atan2()
    demo_grados_vs_radianes()
