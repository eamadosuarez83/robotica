"""Romperlo a proposito: llevar el cabeceo (pitch) a 90 grados y
tratar de girar la guiñada (yaw) por separado del alabeo (roll) --
el bloqueo del cardan (Bloque 09, Tema 9.2).

Correr con:
    python codigo/bloque_09/romper_gimbal_lock.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.orientacion import mat2rpy, rpy2mat  # noqa: E402

COLOR_X, COLOR_Y, COLOR_Z = "tab:red", "tab:green", "tab:blue"


def dibujar_marco(ax, R, origen=(0, 0, 0), etiqueta=""):
    origen = np.asarray(origen, dtype=float)
    for i, color in enumerate([COLOR_X, COLOR_Y, COLOR_Z]):
        ax.quiver(*origen, *R[:, i], color=color, linewidth=2)
    if etiqueta:
        ax.text(*(origen + [0, 0, 1.2]), etiqueta, fontsize=9)


def main() -> None:
    pitch = np.radians(90)   # cabeceo en el bloqueo del cardán

    print("Con pitch=90°, variar roll y yaw POR SEPARADO manteniendo (yaw - roll) fija:")
    print(f"{'roll':>8} {'yaw':>8} | marco resultante (columnas x,y,z)")
    marcos = []
    for roll_deg, yaw_deg in [(0, 30), (10, 40), (-10, 20), (20, 50)]:
        R = rpy2mat(np.radians(roll_deg), pitch, np.radians(yaw_deg))
        marcos.append((roll_deg, yaw_deg, R))
        print(f"{roll_deg:>7}° {yaw_deg:>7}° | {np.round(R, 3).tolist()}")
    print("El marco completo es IDÉNTICO en las cuatro filas: con pitch=90°, solo importa")
    print("(yaw - roll); roll y yaw por separado ya no son recuperables.")

    # Recuperar roll/pitch/yaw con mat2rpy: infinitas soluciones válidas,
    # mat2rpy siempre reporta la misma convención (roll=-(yaw-roll), yaw=0).
    R = marcos[1][2]
    roll_rec, pitch_rec, yaw_rec = mat2rpy(R)
    print(f"\nmat2rpy recupera: roll={np.degrees(roll_rec):.1f}°, "
          f"pitch={np.degrees(pitch_rec):.1f}°, yaw={np.degrees(yaw_rec):.1f}°")
    print("(no necesariamente (10°,90°,40°): cualquier pareja con la misma "
          "diferencia yaw-roll=30° sirve)")

    fig, axes_list = plt.subplots(1, 4, figsize=(16, 4.5),
                                    subplot_kw={"projection": "3d"})
    for ax, (roll_deg, yaw_deg, R) in zip(axes_list, marcos):
        dibujar_marco(ax, R)
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_zlim(-1.2, 1.2)
        ax.set_title(f"roll={roll_deg}°, yaw={yaw_deg}°\n(pitch=90° fijo)")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
