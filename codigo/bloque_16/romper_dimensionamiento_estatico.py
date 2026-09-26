"""Romperlo a proposito: elegir un motor SOLO por el par estatico de
sostenimiento (Bloque 13) -- sin mirar nunca el par dinamico pico
(Bloque 15) -- y ver como se satura en cuanto alguien pide un
movimiento mas rapido que el que se uso para "calcular a ojo"
(Bloque 16, Tema 16.6).

Correr con:
    python codigo/bloque_16/romper_dimensionamiento_estatico.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import newton_euler_plano  # noqa: E402
from robotica.jacobiana import jacobiana_geometrica, par_estatico  # noqa: E402
from hoja_dimensionamiento import movimiento_theta1, par_hombro, M1, M2, L1, L2  # noqa: E402


def par_estatico_hombro(theta1, theta2=0.0):
    """Par de sostenimiento (Bloque 13, Tema 13.7): solo gravedad, sin movimiento."""
    dh_m1 = [[0, 0, L1, 0, 0]]
    J1 = jacobiana_geometrica(dh_m1, [theta1])[:3, :]
    tau_m1 = par_estatico(J1, [0, -M1 * 9.81, 0])[0]

    dh_m2 = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]
    J2 = jacobiana_geometrica(dh_m2, [theta1, theta2])[:3, :]
    tau_m2 = par_estatico(J2, [0, -M2 * 9.81, 0])[0]
    return -(tau_m1 + tau_m2)   # motor debe dar el opuesto al que hace la gravedad


def main() -> None:
    theta1_ini, theta1_fin = np.radians(0), np.radians(90)

    # Dimensionamiento (equivocado) solo con el par estático:
    tau_estatico_max = max(abs(par_estatico_hombro(t)) for t in np.linspace(theta1_ini, theta1_fin, 50))
    margen = 1.4
    tau_motor_elegido = tau_estatico_max * margen
    print(f"Par estático máximo en el recorrido: {tau_estatico_max:.3f} N·m")
    print(f"Motor elegido (estático x {margen}): {tau_motor_elegido:.3f} N·m de par disponible\n")

    t_final = 0.3   # un operador pide un movimiento rápido: 90° en 0.3 s
    t_arr = np.linspace(0, t_final, 300)
    tau_dinamico = par_hombro(t_arr, t_final, theta1_ini, theta1_fin)
    tau_pico_dinamico = np.max(np.abs(tau_dinamico))

    print(f"Par PICO real durante el movimiento (Newton-Euler, Bloque 15): "
          f"{tau_pico_dinamico:.3f} N·m")
    print(f"¿El motor elegido por el criterio estático alcanza? "
          f"{'sí' if tau_motor_elegido >= tau_pico_dinamico else 'NO -- se satura'}")
    print(f"Déficit: {tau_pico_dinamico - tau_motor_elegido:.3f} N·m "
          f"({100*(tau_pico_dinamico/tau_motor_elegido - 1):.0f}% por encima de lo disponible)")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t_arr, tau_dinamico, color="tab:blue", label="τ real (dinámico, Newton-Euler)")
    ax.axhline(tau_estatico_max, color="tab:green", ls=":", label="τ estático máximo")
    ax.axhline(tau_motor_elegido, color="tab:red", ls="--",
               label=f"Motor elegido solo por estático (x{margen})")
    ax.fill_between(t_arr, tau_motor_elegido, tau_dinamico,
                     where=(tau_dinamico > tau_motor_elegido), color="red", alpha=0.2,
                     label="Zona de saturación / pasos perdidos")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("τ hombro [N·m]")
    ax.set_title("Dimensionar solo por par estático deja el motor corto en el movimiento rápido")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
