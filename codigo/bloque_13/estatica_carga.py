"""Par de sostenimiento para un huevo y para la pinza vacia, en varias
posturas del 2R en el plano vertical (Bloque 13, Tema 13.7).

Correr con:
    python codigo/bloque_13/estatica_carga.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.jacobiana import jacobiana_geometrica, par_estatico  # noqa: E402

L1, L2 = 0.30, 0.20
DH = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]  # plano vertical: x horizontal, y hacia arriba
G = 9.81


def par_para_sostener(theta1, theta2, masa_kg):
    J = jacobiana_geometrica(DH, [theta1, theta2])[:3, :]
    F = np.array([0.0, -masa_kg * G, 0.0])
    return par_estatico(J, F)


def main() -> None:
    theta1 = np.radians(40)
    theta2 = np.radians(30)

    tau_huevo = par_para_sostener(theta1, theta2, 0.060)
    tau_vacio = par_para_sostener(theta1, theta2, 0.0)
    print(f"θ1=40°, θ2=30°:")
    print(f"  par sosteniendo un huevo (60 g): {np.round(tau_huevo, 4)} N·m")
    print(f"  par con la pinza vacía:          {np.round(tau_vacio, 4)} N·m (debe ser ~0)")
    assert np.allclose(tau_vacio, 0.0, atol=1e-9)

    thetas2_deg = np.linspace(10, 170, 100)
    pares_hombro = [par_para_sostener(theta1, np.radians(t2), 0.060)[0] for t2 in thetas2_deg]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(thetas2_deg, pares_hombro, color="tab:purple")
    ax.set_xlabel("θ2 (codo) [°]")
    ax.set_ylabel("Par del hombro [N·m]")
    ax.set_title("Par necesario en el hombro para sostener 60 g, según la postura del codo")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
