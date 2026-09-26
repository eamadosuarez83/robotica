"""Romperlo a proposito: componer las mismas dos rotaciones
premultiplicando (ejes fijos) y posmultiplicando (ejes moviles), y
construir una matriz con determinante -1 (Bloque 08, Temas 8.5 y 8.6).

Correr con:
    python codigo/bloque_08/romper_orden_rotaciones.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.rotaciones import rotx, rotz  # noqa: E402

COLOR_X, COLOR_Y, COLOR_Z = "tab:red", "tab:green", "tab:blue"


def dibujar_marco(ax, R, origen=(0, 0, 0), tam=1.0, etiqueta=""):
    origen = np.asarray(origen, dtype=float)
    for i, color in enumerate([COLOR_X, COLOR_Y, COLOR_Z]):
        eje = R[:, i] * tam
        ax.quiver(*origen, *eje, color=color, linewidth=2)
    if etiqueta:
        ax.text(*(origen + [0, 0, 1.2]), etiqueta, fontsize=10)


def parte1_orden_de_composicion():
    R1 = rotz(np.pi / 2)
    R2 = rotx(np.pi / 2)

    R_ejes_moviles = R1 @ R2   # R2 aplicada respecto al marco ya girado por R1
    R_ejes_fijos = R2 @ R1     # R2 aplicada respecto al marco original

    print("R1 = rotz(90°), R2 = rotx(90°)")
    print("Ejes móviles (R1 @ R2), eje x final:", R_ejes_moviles[:, 0])
    print("Ejes fijos   (R2 @ R1), eje x final:", R_ejes_fijos[:, 0])
    print("¿Son iguales?", np.allclose(R_ejes_moviles, R_ejes_fijos))

    fig = plt.figure(figsize=(11, 5.5))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")

    for ax, R, titulo in [(ax1, R_ejes_moviles, "Ejes móviles (R1 @ R2)"),
                           (ax2, R_ejes_fijos, "Ejes fijos (R2 @ R1)")]:
        dibujar_marco(ax, np.eye(3), etiqueta="original")
        dibujar_marco(ax, R, etiqueta="resultado")
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_zlim(-1.5, 1.5)
        ax.set_title(titulo)

    plt.tight_layout()
    plt.show()


def parte2_reflexion():
    R = rotz(np.radians(30))
    R_reflejada = R.copy()
    R_reflejada[:, 2] = -R_reflejada[:, 2]   # invierte el eje z: ya no es rotación

    print(f"\ndet(R) = {np.linalg.det(R):.2f} (rotación válida)")
    print(f"det(R con z invertido) = {np.linalg.det(R_reflejada):.2f} (reflexión, 'espejo')")

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection="3d")
    dibujar_marco(ax, R, etiqueta="rotación (det=+1)")
    dibujar_marco(ax, R_reflejada, origen=(2, 0, 0), etiqueta="reflexión (det=-1)")
    ax.set_xlim(-1.5, 3.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(-1.5, 1.5)
    ax.set_title("Rotación contra reflexión")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parte1_orden_de_composicion()
    parte2_reflexion()
