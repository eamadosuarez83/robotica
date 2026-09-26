"""Romperlo a propósito: saturar el actuador con integral y sin
anti-windup (Bloque 18, Tema 18.4).

La articulación, sostenida en θ = 0, recibe un escalón grande (1.5 rad).
El PID pide mucho más que los 12 V que el driver puede dar, así que
satura. Sin anti-windup, la integral sigue acumulando error durante
toda la subida; cuando el eslabón llega, esa integral inflada lo empuja
de largo.

Correr con:
    python codigo/bloque_18/romper_windup.py

Salida esperada: sin anti-windup, un sobrepaso cerca del 60 % y una
integral que sube a unos 33 V; con anti-windup, cerca del 22 % (lo
que queda es el cero del PI, Tema 18.3) y la integral no pasa de 12 V.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID, pid_por_polos, simular_lazo  # noqa: E402
from articulacion import B_EFF, J, K, TAU_G, U_MAX, dinamica, metricas  # noqa: E402

TS = 0.001
REF = 1.5


class Espia:
    """Deja pasar el PID y anota su integral en cada muestra."""

    def __init__(self, pid):
        self.pid, self.ts = pid, pid.ts
        self.integrales = []

    def paso(self, r, y):
        u = self.pid.paso(r, y)
        self.integrales.append(self.pid.integral)
        return u


def main() -> None:
    kp, ki, kd = pid_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8, p=4.0)
    print(f"PID: kp={kp:.2f}, ki={ki:.2f}, kd={kd:.2f}; escalón de 0 a {REF} rad; "
          f"u en ±{U_MAX} V")
    print(f"Al arrancar, kp·e = {kp * REF:.0f} V: el driver solo da {U_MAX:.0f} V.\n")
    print(f"{'anti-windup':<12s} {'sobrepaso':>10s} {'t_est 2%':>9s} "
          f"{'tiempo saturado':>16s} {'integral máx':>13s}")

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
    for aw, color in ((False, "tab:red"), (True, "tab:blue")):
        pid = PID(kp, ki, kd, ts=TS, u_min=-U_MAX, u_max=U_MAX, anti_windup=aw)
        pid.integral = TAU_G / K     # ya sostenía el eslabón horizontal
        espia = Espia(pid)
        t, X, U = simular_lazo(dinamica, espia, lambda t: REF, [0.0, 0.0], 6.0, subpasos=4)
        integ = np.array(espia.integrales + [espia.integrales[-1]])
        sobrepaso, t_est, _ = metricas(t, X[:, 0], REF)
        t_sat = np.sum(np.abs(U) >= U_MAX) * TS
        print(f"{'sí' if aw else 'no':<12s} {sobrepaso:>9.1f}% {t_est:>8.2f}s "
              f"{t_sat:>15.2f}s {integ.max():>12.1f}V")
        etiqueta = "con anti-windup" if aw else "sin anti-windup"
        ax1.plot(t, X[:, 0], color=color, label=etiqueta)
        ax2.plot(t, U, color=color, label=etiqueta)
        ax3.plot(t, integ, color=color, label=etiqueta)

    print(f"\nLa gravedad en θ = {REF} rad pide {TAU_G * np.cos(REF) / K:.2f} V: es lo que")
    print("la integral debería guardar al final. Sin anti-windup guarda mucho más")
    print("durante la subida, y hay que 'descargarla' pasándose de la referencia.")

    ax1.axhline(REF, color="gray", ls=":")
    ax1.set_ylabel("θ [rad]")
    ax1.set_title("Windup: la integral acumula mientras el actuador está saturado")
    ax2.axhline(U_MAX, color="gray", ls="--", lw=0.8)
    ax2.axhline(-U_MAX, color="gray", ls="--", lw=0.8)
    ax2.set_ylabel("u [V]")
    ax3.set_ylabel("integral [V]")
    ax3.set_xlabel("t [s]")
    for ax in (ax1, ax2, ax3):
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
