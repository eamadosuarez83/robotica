"""PID propio (robotica.control.PID) sobre la articulacion simulada
del Bloque 17: compara P, PI y PID completo (Bloque 18, Temas 18.1,
18.3 y 18.5).

Correr con:
    python codigo/bloque_18/pid_articulacion.py
"""

import sys
from pathlib import Path

import control as ctl
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID  # noqa: E402

J, b, Kt, Ke, R = 0.02, 0.01, 0.05, 0.05, 2.0
B_EFF = b + Kt * Ke / R


def planta_discreta(Ts):
    G = ctl.tf([Kt / R], [J, B_EFF, 0])
    return ctl.tf2ss(ctl.c2d(G, Ts, method="zoh"))


def simular(Kp, Ki, Kd, Ts, t_final=40.0, referencia=1.0, perturbacion=0.0):
    """Simula el lazo con una perturbacion constante (equivalente a una
    carga externa, p. ej. gravedad) sumada a la senal de control --
    la razon real por la que P solo deja un error permanente (Tema
    18.1): la planta SOLA (sin perturbacion) ya tiene un integrador
    propio (motor: voltaje -> angulo) y sigue una referencia en
    escalon sin error incluso con P puro; es la perturbacion constante
    la que un P puro no puede cancelar del todo."""
    Gd = planta_discreta(Ts)
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
        x = Gd.A @ x + Gd.B * (u + perturbacion)
    return t, y


def main() -> None:
    Ts = 0.001
    perturbacion = -0.3   # V equivalentes: una carga externa constante
    casos = {
        "P (Kp=5)": dict(Kp=5.0, Ki=0.0, Kd=0.0),
        "PI (Kp=5, Ki=1)": dict(Kp=5.0, Ki=1.0, Kd=0.0),
        "PID (Kp=5, Ki=1, Kd=0.02)": dict(Kp=5.0, Ki=1.0, Kd=0.02),
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    for nombre, ganancias in casos.items():
        t, y = simular(Ts=Ts, perturbacion=perturbacion, **ganancias)
        error_final = 1.0 - y[-1]
        print(f"{nombre:28s} error final ante perturbación = {error_final:+.4f} rad")
        ax.plot(t, y, label=nombre)

    ax.axhline(1.0, color="gray", ls=":", label="referencia")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("θ [rad]")
    ax.set_title("P vs. PI vs. PID sobre la misma articulación")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
