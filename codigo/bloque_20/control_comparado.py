"""Compara PID independiente, PD+gravedad y par calculado siguiendo
la misma trayectoria sobre el 2R real (dinamica no lineal completa,
Bloques 14-15), para un movimiento lento y uno rapido (Bloque 20,
Temas 20.1-20.3).

Correr con:
    python codigo/bloque_20/control_comparado.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID  # noqa: E402
from robotica.simular import rk4  # noqa: E402
from robotica.trayectorias import perfil_s  # noqa: E402
from modelo_2r import construir_modelo, dinamica_directa  # noqa: E402

M_f, RESTO_f, G_f = construir_modelo()
PLANTA = dinamica_directa(M_f, RESTO_f)


def trayectoria_deseada(T, n):
    t, q1, qd1, qdd1 = perfil_s(np.radians(10), np.radians(100), T, n_puntos=n)
    _, q2, qd2, qdd2 = perfil_s(np.radians(-10), np.radians(-80), T, n_puntos=n)
    return t, np.column_stack([q1, q2]), np.column_stack([qd1, qd2]), np.column_stack([qdd1, qdd2])


def simular_control(ley_control, T, n=2000, u_max=40.0):
    t, Qd, Qdd, Qddd = trayectoria_deseada(T, n)
    Ts = t[1] - t[0]
    z = np.array([Qd[0, 0], Qd[0, 1], 0.0, 0.0])
    Q = np.zeros((n, 2))
    for k in range(n):
        Q[k] = z[:2]
        tau = ley_control(z, Qd[k], Qdd[k], Qddd[k])
        tau = np.clip(tau, -u_max, u_max)
        z = rk4(lambda tt, zz: PLANTA(tt, zz, tau), z, [t[k], t[k] + Ts])[-1]
    return t, Q, Qd


def pid_independiente(Ts, Kp=100.0, Ki=50.0, Kd=8.0):
    """Control monoarticular (Bloque 20, Tema 20.1): un robotica.control.PID
    (Bloque 18) independiente por articulación, sin ningún término del
    modelo dinámico -- cada motor "no sabe" que el otro existe."""
    pid1 = PID(Kp=Kp, Ki=Ki, Kd=Kd, Ts=Ts, u_min=-40, u_max=40)
    pid2 = PID(Kp=Kp, Ki=Ki, Kd=Kd, Ts=Ts, u_min=-40, u_max=40)

    def ley(z, qd, _qd_d, _qdd_d):
        q = z[:2]
        u1 = pid1.actualizar(qd[0], q[0])
        u2 = pid2.actualizar(qd[1], q[1])
        return np.array([u1, u2])
    return ley


def pd_gravedad(Kp=80.0, Kd=10.0):
    def ley(z, qd, _qd_d, _qdd_d):
        q, qdot = z[:2], z[2:]
        e = qd - q
        return Kp * e - Kd * qdot + np.array(G_f(*q)).flatten()
    return ley


def par_calculado(Kp=100.0, Kd=20.0, M_hat=None, resto_hat=None):
    M_hat = M_hat or M_f
    resto_hat = resto_hat or RESTO_f

    def ley(z, qd, qd_d, qdd_d):
        q, qdot = z[:2], z[2:]
        e = qd - q
        edot = qd_d - qdot
        Mn = np.array(M_hat(*q), dtype=float)
        resto = np.array(resto_hat(*q, *qdot), dtype=float).flatten()
        return Mn @ (qdd_d + Kd * edot + Kp * e) + resto
    return ley


def error_rms(Q, Qd):
    return np.sqrt(np.mean((Q - Qd) ** 2, axis=0))


def main() -> None:
    n = 2000
    for T, etiqueta in [(3.0, "LENTO (T=3 s)"), (0.4, "RÁPIDO (T=0.4 s)")]:
        print(f"\n=== Movimiento {etiqueta} ===")
        Ts = T / (n - 1)
        controladores = {
            "PID independiente": pid_independiente(Ts),
            "PD + gravedad": pd_gravedad(),
            "Par calculado": par_calculado(),
        }
        resultados = {}
        for nombre, ley in controladores.items():
            t, Q, Qd = simular_control(ley, T)
            rms = error_rms(Q, Qd)
            resultados[nombre] = (t, Q, Qd)
            print(f"  {nombre:20s} error RMS = ({np.degrees(rms[0]):.2f}°, "
                  f"{np.degrees(rms[1]):.2f}°)")

        fig, ax = plt.subplots(figsize=(8, 5))
        for nombre, (t, Q, Qd) in resultados.items():
            ax.plot(t, np.degrees(Q[:, 0]), label=nombre)
        ax.plot(t, np.degrees(Qd[:, 0]), "k--", label="deseado", lw=1)
        ax.set_xlabel("t [s]")
        ax.set_ylabel("θ1 [°]")
        ax.set_title(f"Seguimiento de θ1 -- movimiento {etiqueta}")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
