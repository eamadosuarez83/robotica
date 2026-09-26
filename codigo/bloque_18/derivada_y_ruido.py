"""Derivada del error contra derivada de la medición, y el ruido del
sensor amplificado por la derivada (Bloque 18, Tema 18.5).

Parte 1: escalón de 0.2 rad en t = 0.5 s. Derivar el error produce una
"patada" (el error salta de golpe, su derivada es enorme); derivar la
medición no, porque la medición no salta.

Parte 2: la articulación quieta en 0.5 rad, con ruido de medición de
0.002 rad (≈ 0.1°, un potenciómetro bueno). Con ts = 1 ms, la derivada
sin filtro multiplica ese ruido por kd/ts ≈ 7870 V/rad.

Correr con:
    python codigo/bloque_18/derivada_y_ruido.py

Salida esperada: con derivada del error, u pegado a 12 V unos 40 ms
justo después del escalón; con derivada de la medición, sin pico.
Con ruido y sin filtro, u satura más de la mitad del tiempo; con
tf = 10 ms, nunca.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID, pid_por_polos, simular_lazo  # noqa: E402
from articulacion import B_EFF, J, K, TAU_G, U_MAX, dinamica, metricas  # noqa: E402

TS = 0.001


class ConRuido:
    """Le suma ruido gaussiano a la medición antes de dársela al PID."""

    def __init__(self, pid, sigma, semilla=0):
        self.pid, self.ts = pid, pid.ts
        self.sigma = sigma
        self.rng = np.random.default_rng(semilla)

    def paso(self, r, y):
        return self.pid.paso(r, y + self.rng.normal(0.0, self.sigma))


def main() -> None:
    kp, ki, kd = pid_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8, p=4.0)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7))

    # Parte 1: la patada derivativa
    print("Parte 1 — escalón de 0 a 0.2 rad en t = 0.5 s")
    tf = 0.01   # la derivada siempre va filtrada (Parte 2)
    print(f"  kd·Δe/(tf+ts) = {kd:.2f}·0.2/{tf + TS} = {kd * 0.2 / (tf + TS):.0f} V "
          f"pedidos de golpe, que decaen con tf = {tf * 1000:.0f} ms\n")
    print(f"  {'derivada de':<12s} {'|u| máx':>8s} {'ms saturado':>12s} {'sobrepaso':>10s}")
    for de, color in (("error", "tab:red"), ("medicion", "tab:blue")):
        pid = PID(kp, ki, kd, ts=TS, u_min=-U_MAX, u_max=U_MAX, derivada_de=de, tf=tf)
        pid.integral = TAU_G / K
        t, X, U = simular_lazo(dinamica, pid, lambda t: 0.2 * (t >= 0.5),
                               [0.0, 0.0], 3.0, subpasos=4)
        despues = t >= 0.5
        sobrepaso, _, _ = metricas(t[despues], X[despues, 0], 0.2)
        print(f"  {de:<12s} {np.max(np.abs(U)):>8.2f} "
              f"{np.sum(np.abs(U) >= U_MAX) * TS * 1000:>12.0f} {sobrepaso:>9.1f}%")
        ax1.plot(t, U, color=color, label=f"derivada del {de}" if de == "error"
                 else "derivada de la medición")
    ax1.set_xlim(0.4, 1.5)
    ax1.set_ylabel("u [V]")
    ax1.set_title("Patada derivativa: derivar el error ante un escalón")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Parte 2: ruido y filtro de la derivada
    print("  La patada no es 'mala' para θ (aquí hasta baja el sobrepaso): su costo")
    print("  es el driver pegado al máximo decenas de ms, un golpe de corriente y de")
    print("  par en el reductor en cada cambio de referencia.")
    print("\nParte 2 — quieta en 0.5 rad, ruido de medición σ = 0.002 rad")
    print(f"  {'tf [ms]':>8s} {'desv. de u [V]':>15s} {'% del tiempo saturado':>22s}")
    for tf, color in ((0.0, "tab:red"), (0.01, "tab:orange"), (0.03, "tab:blue")):
        pid = PID(kp, ki, kd, ts=TS, u_min=-U_MAX, u_max=U_MAX, tf=tf)
        pid.integral = TAU_G * np.cos(0.5) / K
        t, X, U = simular_lazo(dinamica, ConRuido(pid, 0.002), lambda t: 0.5,
                               [0.5, 0.0], 2.0, subpasos=4)
        print(f"  {tf * 1000:>8.0f} {U.std():>15.2f} "
              f"{100 * np.mean(np.abs(U) >= U_MAX):>21.1f}%")
        ax2.plot(t, U, color=color, lw=0.6, label=f"tf = {tf * 1000:.0f} ms")
    print("\nEl filtro no es gratis: tf es un retardo más en el lazo (Bloque 17,")
    print("Tema 17.5). Se elige mucho menor que 1/ωn del lazo (aquí 1/ωn = 250 ms,")
    print("y 10 ms basta para quitar la saturación).")

    ax2.set_xlim(0.5, 1.0)
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("u [V]")
    ax2.set_title("Ruido del sensor amplificado por la derivada, con y sin filtro")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
