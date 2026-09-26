"""Romperlo a propósito: mandar un escalón en vez de una trayectoria
(Bloque 19, Tema 19.3).

La articulación del Bloque 18, con su PID (ubicación de polos,
anti-windup, derivada filtrada), sostenida en θ = 0, tiene que llegar a
1.5 rad. Tres referencias:
  - escalón: "ve a 1.5 rad ya";
  - quíntica en 1.5 s;
  - quíntica en 0.6 s (más rápida de lo que el motor puede).

Antes de mandar una trayectoria se puede saber si es posible: con el
modelo, el voltaje ideal es u = (J q'' + b q' + τg cos q) / K, y si
pasa de 12 V, la trayectoria no se puede seguir.

Correr con:
    python codigo/bloque_19/romper_escalon.py

Salida esperada: el escalón satura el driver 0.34 s (par pico = el
máximo del motor) y se pasa ~21 %. La quíntica de 1.5 s nunca satura,
pero el PID solo va detrás (~0.19 rad) y se pasa ~13 %: necesita error
para empujar. La de 0.6 s ya se sabe imposible en el cálculo previo, y
satura. Sumando la prealimentación del modelo (adelanto del Bloque 20),
la quíntica de 1.5 s se sigue con error prácticamente cero.
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
from articulacion import B_EFF, J, K, TAU_G, U_MAX, dinamica, metricas  # noqa: E402

TS = 0.001
DESTINO = 1.5


class ConPrealimentacion:
    """u = u_ff(t) + PID, con u_ff el voltaje que el modelo dice que
    hace falta para seguir la trayectoria (adelanto del Bloque 20).
    Los límites del PID se corren para que la suma no pase de ±U_MAX,
    así el anti-windup sigue viendo la saturación real."""

    def __init__(self, pid, T):
        self.pid, self.ts, self.T = pid, pid.ts, T
        self.k = 0

    def paso(self, r, y):
        q, qd, qdd = quintica(0.0, DESTINO, self.T, self.k * self.ts)
        self.k += 1
        u_ff = float((J * qdd + B_EFF * qd + TAU_G * np.cos(q)) / K)
        self.pid.u_min, self.pid.u_max = -U_MAX - u_ff, U_MAX - u_ff
        return u_ff + self.pid.paso(r, y)


def main() -> None:
    kp, ki, kd = pid_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8, p=4.0)
    referencias = {
        "escalón": lambda t: DESTINO,
        "quíntica 1.5 s": lambda t: quintica(0.0, DESTINO, 1.5, t)[0],
        "quíntica 0.6 s": lambda t: quintica(0.0, DESTINO, 0.6, t)[0],
        "quíntica 1.5 s + prealim.": lambda t: quintica(0.0, DESTINO, 1.5, t)[0],
    }

    print("Cálculo previo con el modelo: voltaje ideal para seguir cada quíntica")
    for T in (1.5, 0.6):
        t = np.linspace(0, T, 1001)
        q, qd, qdd = quintica(0.0, DESTINO, T, t)
        u_ideal = (J * qdd + B_EFF * qd + TAU_G * np.cos(q)) / K
        veredicto = "posible" if np.abs(u_ideal).max() <= U_MAX else "IMPOSIBLE: pasa de 12 V"
        print(f"  T = {T} s: u ideal máx = {np.abs(u_ideal).max():5.2f} V  -> {veredicto}")

    print(f"\n{'referencia':<26s} {'|u| máx':>8s} {'par pico':>9s} {'ms saturado':>12s} "
          f"{'error máx':>10s} {'sobrepaso':>10s} {'llega (2%)':>11s}")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    for nombre, r in referencias.items():
        # Con un escalón se deriva la medición (sin patada, Bloque 18). Con una
        # trayectoria suave no hay patada, y derivar la medición frenaría la
        # velocidad planeada: se deriva el error, q_ref' - q'.
        de = "medicion" if nombre == "escalón" else "error"
        pid = PID(kp, ki, kd, ts=TS, u_min=-U_MAX, u_max=U_MAX, tf=0.01, derivada_de=de)
        if "prealim" in nombre:
            controlador = ConPrealimentacion(pid, 1.5)   # la gravedad ya va en u_ff
        else:
            pid.integral = TAU_G / K                     # sostenía el eslabón en θ = 0
            controlador = pid
        t, X, U = simular_lazo(dinamica, controlador, r, [0.0, 0.0], 4.0, subpasos=4)
        y = X[:, 0]
        ref = np.array([r(tk) for tk in t])
        sobrepaso, t_est, _ = metricas(t, y, DESTINO)
        print(f"{nombre:<26s} {np.abs(U).max():>7.2f}V {K * np.abs(U).max():>7.3f}Nm "
              f"{np.sum(np.abs(U) >= U_MAX) * TS * 1000:>12.0f} {np.abs(ref - y).max():>10.3f} "
              f"{sobrepaso:>9.1f}% {t_est:>10.2f}s")
        linea, = ax1.plot(t, y, label=nombre)
        ax1.plot(t, ref, ls=":", color=linea.get_color())
        ax2.plot(t, U, color=linea.get_color(), label=nombre)

    print("\n'par pico' es K·|u| máx, del lado del motor. El escalón siempre lo lleva al")
    print("límite: el motor, no la trayectoria, decide cómo se mueve el brazo.")

    ax1.set_ylabel("θ [rad] (punteado: referencia)")
    ax1.set_title("Escalón contra trayectorias quínticas, mismo PID")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax2.axhline(U_MAX, color="gray", ls="--", lw=0.8)
    ax2.set_ylabel("u [V]")
    ax2.set_xlabel("t [s]")
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
