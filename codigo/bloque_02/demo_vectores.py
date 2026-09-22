"""Demo del Bloque 02: producto punto, producto cruz y torque de una llave.

Compara la libreria propia `robotica.vectores` con NumPy, y dibuja en
3D el torque que una fuerza produce al aplicarse en el mango de una
llave sobre una tuerca.

Correr con:
    python codigo/bloque_02/demo_vectores.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica import vectores as vec  # noqa: E402


def comparar_con_numpy() -> None:
    u = np.array([1.0, 2.0, 3.0])
    v = np.array([0.0, 1.0, -1.0])

    print("=== robotica.vectores contra NumPy ===")
    print(f"producto_punto propio: {vec.producto_punto(u, v):.4f}  "
          f"| np.dot: {np.dot(u, v):.4f}")
    print(f"producto_cruz propio:  {vec.producto_cruz(u, v)}  "
          f"| np.cross: {np.cross(u, v)}")
    print(f"norma propia:          {vec.norma(u):.4f}  "
          f"| np.linalg.norm: {np.linalg.norm(u):.4f}")
    print(f"ángulo entre u y v:    {np.degrees(vec.angulo_entre(u, v)):.2f}°")


def graficar_torque_llave() -> None:
    r = np.array([0.20, 0.0, 0.0])   # mango de la llave, 20 cm desde la tuerca
    F = np.array([0.0, 50.0, 0.0])   # fuerza perpendicular al mango, 50 N
    tau = vec.torque(r, F)
    print(f"\nTorque r x F = {tau} N·m  (magnitud {vec.norma(tau):.2f} N·m)")

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="3d")
    origen = np.zeros(3)

    ax.quiver(*origen, *r, color="tab:blue", label="r (mango)")
    ax.quiver(*r, *F * 0.005, color="tab:red", label="F (fuerza, escalada)")
    ax.quiver(*origen, *tau * 0.02, color="tab:green", label="τ = r × F (escalado)")

    ax.set_xlim(-0.05, 0.25)
    ax.set_ylim(-0.05, 0.25)
    ax.set_zlim(-0.05, 0.25)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("Torque de una llave sobre una tuerca")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    comparar_con_numpy()
    graficar_torque_llave()
