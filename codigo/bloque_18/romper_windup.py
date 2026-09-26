"""Romperlo a proposito: saturar el actuador con un PID que tiene
integral pero SIN anti-windup, y comparar contra el mismo PID con
anti-windup (Bloque 18, Tema 18.4).

Correr con:
    python codigo/bloque_18/romper_windup.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID  # noqa: E402
from pid_articulacion import planta_discreta  # noqa: E402


class PIDSinAntiWindup(PID):
    """Mismo PID, pero integra SIEMPRE, incluso saturado (para comparar)."""

    def actualizar(self, referencia, medicion):
        error = referencia - medicion
        if self.medicion_anterior is None:
            d_medicion = 0.0
        else:
            d_medicion = (medicion - self.medicion_anterior) / self.Ts
        self.medicion_anterior = medicion
        termino_d = -self.Kd * d_medicion

        self.integral += error * self.Ts   # SIN condición de anti-windup
        u_sin_saturar = self.Kp * error + self.Ki * self.integral + termino_d
        return float(np.clip(u_sin_saturar, self.u_min, self.u_max))


def simular(pid, Ts, t_final, referencia_final):
    Gd = planta_discreta(Ts)
    n = int(t_final / Ts)
    x = np.zeros((Gd.A.shape[0], 1))
    t = np.zeros(n)
    y = np.zeros(n)
    for k in range(n):
        medicion = (Gd.C @ x).item()
        t[k] = k * Ts
        y[k] = medicion
        u = pid.actualizar(referencia_final, medicion)
        x = Gd.A @ x + Gd.B * u
    return t, y


def main() -> None:
    Ts = 0.001
    Kp, Ki, Kd = 5.0, 1.0, 0.02
    u_max = 1.0   # actuador MUY limitado: se satura fácilmente ante un escalón grande
    referencia = 3.0   # un escalón grande, para forzar la saturación

    pid_con = PID(Kp=Kp, Ki=Ki, Kd=Kd, Ts=Ts, u_min=-u_max, u_max=u_max)
    pid_sin = PIDSinAntiWindup(Kp=Kp, Ki=Ki, Kd=Kd, Ts=Ts, u_min=-u_max, u_max=u_max)

    t, y_con = simular(pid_con, Ts, 40.0, referencia)
    t, y_sin = simular(pid_sin, Ts, 40.0, referencia)

    sobrepaso_con = (np.max(y_con) - referencia) / referencia * 100
    sobrepaso_sin = (np.max(y_sin) - referencia) / referencia * 100
    print(f"Sobrepaso CON anti-windup: {sobrepaso_con:.1f}%")
    print(f"Sobrepaso SIN anti-windup: {sobrepaso_sin:.1f}%")

    t_establecido_con = t[np.argmax(np.abs(y_con - referencia) < 0.05 * referencia)]
    print(f"Se establece (± 5%) antes con anti-windup: {t_establecido_con:.2f} s")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t, y_con, label="con anti-windup")
    ax.plot(t, y_sin, label="SIN anti-windup", alpha=0.8)
    ax.axhline(referencia, color="gray", ls=":", label="referencia")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("θ [rad]")
    ax.set_title(f"Efecto windup: actuador saturado en ±{u_max} V")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
