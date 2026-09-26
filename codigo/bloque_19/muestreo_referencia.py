"""El computador planifica, el microcontrolador controla: cada cuánto
mandar la referencia y qué hacer entre dos puntos (Bloque 19, Tema 19.6).

La articulación del Bloque 18 sigue una quíntica de 0 a 1.5 rad en
1.5 s, con PID (derivada del error) más prealimentación. El PID corre
cada 1 ms. El computador, por el enlace serie, manda puntos de la
trayectoria cada `periodo_envio`. Tres formas de usarlos:
  - escalera: el micro usa el último punto recibido hasta que llega otro;
  - interpolada: el computador manda cada punto un periodo antes (la
    trayectoria se conoce de antemano) y el micro interpola en línea
    recta entre el actual y el siguiente;
  - densa: la referencia a 1 kHz, como si el enlace fuera ideal.

Correr con:
    python codigo/bloque_19/muestreo_referencia.py

Salida esperada: la escalera produce escalones de voltaje en cada punto
nuevo, peores cuanto más lento el envío; interpolando, el resultado
queda muy cerca del caso ideal aun enviando cada 50 ms.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "bloque_18"))
from robotica.control import PID, pid_por_polos, simular_lazo  # noqa: E402
from robotica.trayectorias import quintica  # noqa: E402
from articulacion import B_EFF, J, K, TAU_G, U_MAX, dinamica  # noqa: E402

TS = 0.001
DESTINO, T = 1.5, 1.5


def referencia(t):
    return float(quintica(0.0, DESTINO, T, t)[0])


def prealimentacion(t):
    q, qd, qdd = quintica(0.0, DESTINO, T, t)
    return float((J * qdd + B_EFF * qd + TAU_G * np.cos(q)) / K)


class Micro:
    """Lo que corre en el microcontrolador: reconstruye la referencia a
    partir de los puntos recibidos y aplica prealimentación + PID."""

    def __init__(self, pid, periodo_envio, modo):
        self.pid, self.ts = pid, pid.ts
        self.periodo, self.modo = periodo_envio, modo
        self.k = 0

    def referencia_local(self, t):
        if self.modo == "densa":
            return referencia(t)
        n = np.floor(t / self.periodo + 1e-9)
        t_n = n * self.periodo
        if self.modo == "escalera":
            return referencia(t_n)
        # interpolada: ya tiene el punto n y el n+1
        r0, r1 = referencia(t_n), referencia(t_n + self.periodo)
        return r0 + (r1 - r0) * (t - t_n) / self.periodo

    def paso(self, _r, y):
        t = self.k * self.ts
        self.k += 1
        u_ff = prealimentacion(t)
        self.pid.u_min, self.pid.u_max = -U_MAX - u_ff, U_MAX - u_ff
        return u_ff + self.pid.paso(self.referencia_local(t), y)


def main() -> None:
    kp, ki, kd = pid_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8, p=4.0)
    print(f"{'envío':>8s} {'modo':<11s} {'error máx [mrad]':>17s} {'salto de u máx [V]':>19s}")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    casos = [(0.001, "densa"), (0.020, "escalera"), (0.020, "interpolada"),
             (0.050, "escalera"), (0.050, "interpolada")]
    for periodo, modo in casos:
        pid = PID(kp, ki, kd, ts=TS, tf=0.01, derivada_de="error")
        micro = Micro(pid, periodo, modo)
        t, X, U = simular_lazo(dinamica, micro, referencia, [0.0, 0.0], 2.0, subpasos=4)
        error = np.array([referencia(tk) for tk in t]) - X[:, 0]
        print(f"{periodo * 1000:>6.0f}ms {modo:<11s} {np.abs(error).max() * 1000:>17.2f} "
              f"{np.abs(np.diff(U[:-1])).max():>19.3f}")
        if periodo == 0.050 or modo == "densa":
            ax1.plot(t, error * 1000, label=f"{modo}, {periodo * 1000:.0f} ms")
            ax2.plot(t, U, label=f"{modo}, {periodo * 1000:.0f} ms")

    print("\n'salto de u' es el mayor cambio de voltaje entre dos muestras de 1 ms:")
    print("en la escalera, cada punto nuevo es un escalón para el PID (con derivada")
    print("del error, además, una patada). Interpolando, el micro ve una rampa suave.")

    ax1.set_ylabel("error [mrad]")
    ax1.set_title("Referencia enviada cada 50 ms: escalera contra interpolada")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax2.set_ylabel("u [V]")
    ax2.set_xlabel("t [s]")
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0.4, 0.8)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
