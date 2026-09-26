"""Romperlo a proposito: aumentar el periodo de muestreo Ts de un PID
bien sintonizado hasta que la respuesta, antes suave, empiece a
oscilar o se desestabilice (Bloque 18, Tema 18.6).

Correr con:
    python codigo/bloque_18/romper_muestreo_lento.py
"""

import sys
from pathlib import Path

import numpy as np
import control as ctl
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID  # noqa: E402

J, b, Kt, Ke, R = 0.02, 0.01, 0.05, 0.05, 2.0
B_EFF = b + Kt * Ke / R


def simular(Ts, t_final=10.0, Kp=5.0, Ki=1.0, Kd=0.02, referencia=1.0):
    G = ctl.tf([Kt / R], [J, B_EFF, 0])
    Gd = ctl.tf2ss(ctl.c2d(G, Ts, method="zoh"))
    pid = PID(Kp=Kp, Ki=Ki, Kd=Kd, Ts=Ts, u_min=-20, u_max=20)
    n = int(t_final / Ts)
    x = np.zeros((Gd.A.shape[0], 1))
    t = np.zeros(n)
    y = np.zeros(n)
    for k in range(n):
        medicion = (Gd.C @ x).item()
        t[k] = k * Ts
        y[k] = medicion
        u = pid.actualizar(referencia, medicion)
        x = Gd.A @ x + Gd.B * u
    return t, y


def main() -> None:
    periodos = [0.001, 0.05, 0.15, 0.30]

    fig, ax = plt.subplots(figsize=(8, 5))
    for Ts in periodos:
        t, y = simular(Ts)
        sobrepaso = (np.max(y) - 1.0) * 100
        print(f"Ts={Ts:.3f} s: sobrepaso = {sobrepaso:5.1f}%, "
              f"valor máximo = {np.max(y):.2f}")
        ax.plot(t, y, label=f"Ts={Ts:.3f} s")

    ax.axhline(1.0, color="gray", ls=":")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("θ [rad]")
    ax.set_title("Mismo PID, distinto periodo de muestreo")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1, 4)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
