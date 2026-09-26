"""Cinco maneras de mover el hombro del 2R de 0 a π/2 en 1.5 s:
posición, velocidad, aceleración, jerk y par requerido (Bloque 19,
Temas 19.2 y 19.3).

Perfiles: lineal (velocidad constante), cúbico, quíntico, trapezoidal
(1/3 del tiempo acelerando, 1/3 frenando) y en S (lo mismo, pero con
0.15 s de jerk en cada rampa). El codo queda fijo en 0, como en la
hoja de dimensionamiento del Bloque 16.

Correr con:
    python codigo/bloque_19/comparar_perfiles.py

Salida esperada: el lineal pide aceleración (y par) "infinita" en los
extremos: su pico crece al achicar el paso de tiempo. El cúbico y el
quíntico tienen pares pico parecidos, pero el cúbico arranca con un
salto de aceleración y el quíntico no. El trapezoidal tiene el menor
par pico, a cambio de saltos de aceleración; el en S los quita con un
pico algo mayor.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.trayectorias import cubica, perfil_s, perfil_trapezoidal, quintica  # noqa: E402
from brazo_2r import pares  # noqa: E402

D, T = np.pi / 2, 1.5


def perfiles(n):
    """Cada perfil muestreado en n puntos: dict nombre -> (t, q, qd, qdd)."""
    t = np.linspace(0, T, n)
    # Lineal: velocidad constante D/T; salta de 0 a D/T en t=0 y de vuelta en t=T.
    q_lin = D * t / T
    qd_lin = np.gradient(q_lin, t)
    qd_lin[0] = qd_lin[-1] = 0.0          # quieto antes y después
    qdd_lin = np.gradient(qd_lin, t)
    salida = {"lineal": (t, q_lin, qd_lin, qdd_lin)}
    salida["cúbico"] = (t, *cubica(0, D, T, t))
    salida["quíntico"] = (t, *quintica(0, D, T, t))
    # Trapezoidal con tao = T/3: V = D/(T - tao), a = V/tao
    tao = T / 3
    V = D / (T - tao)
    salida["trapezoidal"] = perfil_trapezoidal(0, D, V, V / tao, n)
    # En S con Tj = 0.15, Ta = T/3, sin cambiar la duración:
    Tj, Ta = 0.15, T / 3
    Vs = D / (T - Ta)
    As = Vs / (Ta - Tj)
    salida["en S"] = perfil_s(0, D, Vs, As, As / Tj, n)
    return salida


def main() -> None:
    print(f"Hombro de 0 a {np.degrees(D):.0f}° en {T} s, codo fijo en 0\n")
    print(f"{'perfil':<12s} {'v máx':>7s} {'a máx':>8s} {'salto de a':>11s} "
          f"{'τ pico':>8s} {'τ RMS':>7s} {'τ pico sin g':>13s}")
    print(f"{'':<12s} {'[rad/s]':>7s} {'[rad/s²]':>8s} {'en t=0':>11s} "
          f"{'[N·m]':>8s} {'[N·m]':>7s} {'[N·m]':>13s}")
    datos = perfiles(1501)                   # paso de 1 ms
    for nombre, (t, q, qd, qdd) in datos.items():
        Q = np.column_stack([q, np.zeros_like(q)])
        Qd = np.column_stack([qd, np.zeros_like(q)])
        Qdd = np.column_stack([qdd, np.zeros_like(q)])
        tau = pares(Q, Qd, Qdd)[:, 0]
        # Lo que pide la gravedad sola (quieto en cada postura), para separarlo
        tau_g = pares(Q, 0 * Qd, 0 * Qdd)[:, 0]
        salto = abs(qdd[0])                  # antes de t=0 estaba quieto: a=0
        print(f"{nombre:<12s} {np.abs(qd).max():>7.3f} {np.abs(qdd).max():>8.2f} "
              f"{salto:>11.2f} {np.abs(tau).max():>8.2f} {np.sqrt(np.mean(tau**2)):>7.2f} "
              f"{np.abs(tau - tau_g).max():>13.2f}")

    print("\nCon el brazo horizontal, la gravedad sola pide "
          f"{pares([[0, 0]], [[0, 0]], [[0, 0]])[0, 0]:.2f} N·m: domina el pico. La")
    print("última columna es lo que depende del perfil: inercia y Coriolis.")
    print("\nEl lineal, con pasos de tiempo cada vez más finos:")
    for n in (151, 1501, 15001):
        t, q, qd, qdd = perfiles(n)["lineal"]
        tau = pares(np.column_stack([q, 0 * q]), np.column_stack([qd, 0 * q]),
                    np.column_stack([qdd, 0 * q]))[:, 0]
        print(f"  dt = {T / (n - 1) * 1000:>5.1f} ms: a máx = {np.abs(qdd).max():>9.1f} rad/s², "
              f"τ pico = {np.abs(tau).max():>8.1f} N·m")
    print("  El pico crece como 1/dt: en el límite, aceleración y par infinitos.")

    print("\nA mano (Tema 19.2): a máx cúbico = 6D/T² = "
          f"{6 * D / T**2:.2f}; quíntico = (10√3/3) D/T² = {10 * np.sqrt(3) / 3 * D / T**2:.2f}; "
          f"trapezoidal (tao = T/3) = 4.5 D/T² = {4.5 * D / T**2:.2f} rad/s²")

    fig, ejes = plt.subplots(4, 1, figsize=(9, 10), sharex=True)
    for nombre, (t, q, qd, qdd) in datos.items():
        if nombre == "lineal":
            continue                         # su aceleración aplasta la escala
        jerk = np.gradient(qdd, t)
        for ax, y in zip(ejes, (q, qd, qdd, jerk)):
            ax.plot(t, y, label=nombre)
    t, q, qd, _ = datos["lineal"]
    ejes[0].plot(t, q, "k--", lw=0.8, label="lineal")
    ejes[1].plot(t, qd, "k--", lw=0.8, label="lineal")
    for ax, nombre in zip(ejes, ("q [rad]", "q' [rad/s]", "q'' [rad/s²]", "jerk [rad/s³]")):
        ax.set_ylabel(nombre)
        ax.grid(True, alpha=0.3)
    ejes[3].set_ylim(-60, 60)
    ejes[0].legend(fontsize=8)
    ejes[3].set_xlabel("t [s]")
    ejes[0].set_title("Mismo movimiento, misma duración, cinco perfiles")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
