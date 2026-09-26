"""Romperlo a propósito: muestrear demasiado lento (Bloque 18, Tema 18.6).

El mismo PID (mismas ganancias continuas) se corre con periodos de
muestreo cada vez más largos. Entre muestras el voltaje se queda
congelado (retenedor de orden cero): el controlador está "ciego" ts
segundos, que en la práctica es un retardo de más o menos ts/2.

Correr con:
    python codigo/bloque_18/romper_muestreo_lento.py

Salida esperada: hasta ts ≈ 0.1 s la respuesta casi no cambia; a
0.15 s ya no se asienta y a 0.2 s oscila con amplitud enorme.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID, pid_por_polos, simular_lazo  # noqa: E402
from articulacion import B_EFF, J, K, TAU_G, U_MAX, dinamica  # noqa: E402

REF, THETA0 = 0.5, 0.3


def main() -> None:
    wn = 4.0
    kp, ki, kd = pid_por_polos(J, B_EFF, K, wn=wn, zeta=0.8, p=4.0)
    periodo_lazo = 2 * np.pi / wn
    print(f"PID: kp={kp:.2f}, ki={ki:.2f}, kd={kd:.2f}. Lazo cerrado: ωn = {wn} rad/s, "
          f"periodo natural ≈ {periodo_lazo:.2f} s\n")
    print(f"{'ts [s]':>7s} {'muestras por periodo':>21s} {'máx θ':>7s} "
          f"{'error en los últimos 2 s':>25s}")

    fig, ax = plt.subplots(figsize=(9, 5))
    for ts in (0.001, 0.01, 0.05, 0.1, 0.15, 0.2):
        pid = PID(kp, ki, kd, ts=ts, u_min=-U_MAX, u_max=U_MAX)
        pid.integral = TAU_G * np.cos(THETA0) / K
        # Muchos subpasos: la planta sigue siendo continua aunque el
        # controlador solo mire cada ts.
        t, X, _ = simular_lazo(dinamica, pid, lambda t: REF, [THETA0, 0.0], 8.0,
                               subpasos=max(4, int(ts / 0.001)))
        y = X[:, 0]
        cola = np.abs(y[t > t[-1] - 2] - REF).max()
        print(f"{ts:>7.3f} {periodo_lazo / ts:>21.0f} {y.max():>7.3f} {cola:>25.4f}")
        ax.step(t, y, where="post", label=f"ts = {ts} s")

    print("\nRegla práctica: 20 o más muestras por periodo natural del lazo")
    print("cerrado (aquí, ts ≤ ~0.08 s). Con motores de robot, lazos de 1 a 10 ms.")

    ax.axhline(REF, color="gray", ls=":")
    ax.set_ylim(-0.6, 1.4)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("θ [rad]")
    ax.set_title("El mismo PID, muestreado cada vez más lento")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
