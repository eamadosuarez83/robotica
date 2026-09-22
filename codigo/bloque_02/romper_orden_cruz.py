"""Romperlo a proposito: invertir el orden del producto cruz.

Bloque 02, Tema 2.3. u x v = -(v x u): invertir el orden invierte el
sentido del torque resultante.

Correr con:
    python codigo/bloque_02/romper_orden_cruz.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica import vectores as vec  # noqa: E402


def main() -> None:
    r = np.array([0.20, 0.0, 0.0])
    F = np.array([0.0, 50.0, 0.0])

    tau_correcto = vec.torque(r, F)          # r x F: la definición física
    tau_invertido = vec.producto_cruz(F, r)  # F x r: orden invertido, INCORRECTO

    print(f"τ correcto   = r × F = {tau_correcto}  N·m")
    print(f"τ invertido  = F × r = {tau_invertido}  N·m")
    print("Son exactamente opuestos: invertir el orden invierte el sentido de giro.")

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="3d")
    origen = np.zeros(3)

    ax.quiver(*origen, *r, color="tab:blue", label="r")
    ax.quiver(*r, *F * 0.005, color="tab:red", label="F (escalada)")
    ax.quiver(*origen, *tau_correcto * 0.02, color="tab:green",
              label="r × F (correcto)")
    ax.quiver(*origen, *tau_invertido * 0.02, color="tab:purple",
              label="F × r (invertido, mal)")

    ax.set_xlim(-0.05, 0.25)
    ax.set_ylim(-0.05, 0.25)
    ax.set_zlim(-0.25, 0.25)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("Invertir el orden del producto cruz invierte el torque")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
