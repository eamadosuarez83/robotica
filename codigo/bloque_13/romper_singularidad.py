"""Romperlo a proposito: llevar el 2R a brazo estirado (singularidad
de frontera) y pedir una velocidad hacia afuera; graficar como las
velocidades articulares se disparan (Bloque 13, Tema 13.5).

Correr con:
    python codigo/bloque_13/romper_singularidad.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.jacobiana import jacobiana_geometrica, manipulabilidad  # noqa: E402

L1, L2 = 0.30, 0.20
DH = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]


def main() -> None:
    theta1 = np.radians(40)
    thetas2_deg = np.linspace(30, 0.5, 200)   # acercándose a la singularidad (θ2=0)

    x_punto_deseado = np.array([0.05, 0.0])   # 5 cm/s "hacia afuera"

    normas_qpunto = []
    manipulabilidades = []
    for t2_deg in thetas2_deg:
        t2 = np.radians(t2_deg)
        J = jacobiana_geometrica(DH, [theta1, t2])[:2, :]
        q_punto = np.linalg.solve(J, x_punto_deseado)
        normas_qpunto.append(np.linalg.norm(q_punto))
        manipulabilidades.append(manipulabilidad(J))

    print(f"θ2=30°: |q̇| = {normas_qpunto[0]:.3f} rad/s, manipulabilidad = {manipulabilidades[0]:.4f}")
    print(f"θ2=0.5°: |q̇| = {normas_qpunto[-1]:.1f} rad/s, manipulabilidad = {manipulabilidades[-1]:.6f}")
    print("Las velocidades articulares se disparan al acercarse a θ2=0 (brazo estirado),")
    print("mientras la manipulabilidad cae a cero: la misma singularidad, dos síntomas.")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.semilogy(thetas2_deg, normas_qpunto, color="tab:red")
    ax1.set_xlabel("θ2 [°]  (→ 0 = brazo estirado)")
    ax1.set_ylabel("|q̇| [rad/s]  (escala log)")
    ax1.set_title("Velocidad articular necesaria\npara 5 cm/s 'hacia afuera'")
    ax1.grid(True, alpha=0.3)

    ax2.plot(thetas2_deg, manipulabilidades, color="tab:blue")
    ax2.set_xlabel("θ2 [°]")
    ax2.set_ylabel("Manipulabilidad w")
    ax2.set_title("Manipulabilidad → 0 en la singularidad")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
