"""Visualizador 3D de marcos de referencia, colores fijos x-rojo,
y-verde, z-azul. Compara robotica.rotaciones con
scipy.spatial.transform.Rotation (Bloque 08, Tema 8.4).

Correr con:
    python codigo/bloque_08/visualizador_marcos_3d.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.rotaciones import es_rotacion, rotx, roty, rotz  # noqa: E402

COLOR_X, COLOR_Y, COLOR_Z = "tab:red", "tab:green", "tab:blue"


def dibujar_marco(ax, R, origen=(0, 0, 0), tam=1.0, etiqueta=""):
    origen = np.asarray(origen, dtype=float)
    for i, color in enumerate([COLOR_X, COLOR_Y, COLOR_Z]):
        eje = R[:, i] * tam
        ax.quiver(*origen, *eje, color=color, linewidth=2)
    if etiqueta:
        ax.text(*(origen + 0.1), etiqueta, fontsize=10)


def main() -> None:
    angulo = np.radians(40)

    # Comparación robotica.rotaciones contra scipy, para los tres ejes.
    for nombre, R_propia, eje_scipy in [
        ("rotx", rotx(angulo), "x"),
        ("roty", roty(angulo), "y"),
        ("rotz", rotz(angulo), "z"),
    ]:
        R_scipy = Rotation.from_euler(eje_scipy, angulo).as_matrix()
        error = np.max(np.abs(R_propia - R_scipy))
        print(f"{nombre}(40°): error máx. vs. scipy = {error:.2e}, "
              f"es_rotacion={es_rotacion(R_propia)}")

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(projection="3d")

    dibujar_marco(ax, np.eye(3), etiqueta="fijo")
    dibujar_marco(ax, rotz(angulo) @ rotx(np.radians(30)),
                  origen=(1.5, 0, 0), etiqueta="girado")

    ax.set_xlim(-1, 3)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(-1.5, 1.5)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("Marcos de referencia (x rojo, y verde, z azul)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
