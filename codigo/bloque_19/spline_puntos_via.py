"""Pasar por varios puntos sin detenerse: spline cúbico en el espacio
articular, contra detenerse en cada punto con perfiles trapezoidales
(Bloque 19, Tema 19.4).

La punta del 2R va de un punto de inicio a uno de destino pasando por
dos puntos intermedios (por ejemplo, para esquivar el borde de la
cubeta). Los cuatro puntos se pasan a ángulos con la inversa (codo
arriba) y se interpola en el espacio articular.

También compara el spline propio (robotica.trayectorias.spline_cubica)
contra scipy.interpolate.CubicSpline: deben coincidir.

Correr con:
    python codigo/bloque_19/spline_puntos_via.py

Salida esperada: diferencia con scipy del orden de 1e-15; el spline
pasa exactamente por los puntos intermedios, con velocidad. El
trapezoidal por articulación, con los mismos límites, no es más lento
(usa la aceleración máxima todo el tiempo), pero como cada articulación
lleva su propio reloj, la punta pasa a ~1 cm de los puntos intermedios.
En ningún caso la punta recorre rectas: se interpoló en ángulos.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.trayectorias import interpolador_trapezoidal, resolver_trayectoria, spline_cubica  # noqa: E402
from brazo_2r import directa, inversa  # noqa: E402

PUNTOS = np.array([[0.20, 0.30], [0.40, 0.20], [0.40, 0.05], [0.30, -0.10]])   # m
TIEMPOS = np.array([0.0, 0.8, 1.4, 2.2])                                        # s


def main() -> None:
    res = resolver_trayectoria(PUNTOS, inversa, solucion=0)
    assert res.ok, res
    Qv = res.Q                                   # (4, 2) ángulos en los puntos
    print("Ángulos en los puntos de paso [°]:")
    for P, q in zip(PUNTOS, Qv):
        print(f"  ({P[0]:.2f}, {P[1]:+.2f}) m -> θ1 = {np.degrees(q[0]):7.2f}, θ2 = {np.degrees(q[1]):7.2f}")

    t = np.linspace(TIEMPOS[0], TIEMPOS[-1], 2201)
    Q = np.zeros((t.size, 2))
    Qd = np.zeros_like(Q)
    Qdd = np.zeros_like(Q)
    for j in range(2):
        Q[:, j], Qd[:, j], Qdd[:, j] = spline_cubica(TIEMPOS, Qv[:, j], t)
        cs = CubicSpline(TIEMPOS, Qv[:, j], bc_type="clamped")
        print(f"articulación {j + 1}: máx |propio - scipy| = "
              f"{np.max(np.abs(Q[:, j] - cs(t))):.1e} rad, en q'' {np.max(np.abs(Qdd[:, j] - cs(t, 2))):.1e}")

    print("\nVelocidad al pasar por cada punto [rad/s] (spline):")
    for k, tk in enumerate(TIEMPOS):
        i = np.argmin(np.abs(t - tk))
        print(f"  t = {tk:.1f} s: θ1' = {Qd[i, 0]:+.3f}, θ2' = {Qd[i, 1]:+.3f}")
    print(f"  a máx: {np.abs(Qdd).max():.2f} rad/s²")

    # Deteniéndose en cada punto, con los límites de velocidad y aceleración
    # que el spline llegó a usar (para comparar en igualdad de condiciones).
    V, a = np.abs(Qd).max(), np.abs(Qdd).max()
    t_trap, Q_trap = [], []
    for j in range(2):
        tn, qn = interpolador_trapezoidal(Qv[:, j], V=V, a=a, n_puntos=400)
        t_trap.append(tn)
        Q_trap.append(qn)
    print(f"\nTrapezoidal deteniéndose en cada punto (V = {V:.2f} rad/s, a = {a:.2f} rad/s²),")
    print("cada articulación con su propio reloj:")
    print(f"  articulación 1 termina en {t_trap[0][-1]:.2f} s, articulación 2 en "
          f"{t_trap[1][-1]:.2f} s (el spline: {TIEMPOS[-1]:.2f} s)")
    # ¿Por dónde pasa la punta? Las dos articulaciones en un mismo eje de tiempo.
    t_comun = np.linspace(0, max(t_trap[0][-1], t_trap[1][-1]), 4000)
    Q_sin_sinc = np.column_stack([np.interp(t_comun, t_trap[j], Q_trap[j]) for j in range(2)])
    punta_trap = directa(Q_sin_sinc)
    punta_spline = directa(Q)
    print("  distancia mínima de la punta a cada punto intermedio:")
    for P in PUNTOS[1:-1]:
        d_trap = np.min(np.linalg.norm(punta_trap - P, axis=1))
        d_spl = np.min(np.linalg.norm(punta_spline - P, axis=1))
        print(f"    ({P[0]:.2f}, {P[1]:+.2f}): trapezoidal sin sincronizar {d_trap * 100:5.2f} cm, "
              f"spline {d_spl * 100:5.2f} cm")
    print("  Sin sincronizar, cada articulación llega a su ángulo en otro instante: la")
    print("  punta nunca está en el punto intermedio. Hay que estirar la articulación")
    print("  rápida para que llegue junto con la lenta (Tema 19.4).")

    punta = punta_spline
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.plot(punta[:, 0], punta[:, 1], label="punta (spline articular)")
    ax1.plot(punta_trap[:, 0], punta_trap[:, 1], color="tab:orange",
             label="punta (trapezoidal sin sincronizar)")
    ax1.plot(PUNTOS[:, 0], PUNTOS[:, 1], "ko--", lw=0.8, label="puntos de paso y rectas")
    ax1.plot(0, 0, "ks")
    ax1.set_aspect("equal")
    ax1.set_xlabel("x [m]")
    ax1.set_ylabel("y [m]")
    ax1.set_title("Interpolar en ángulos no da rectas en x-y")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax2.plot(t, Q[:, 0], label="θ1")
    ax2.plot(t, Q[:, 1], label="θ2")
    ax2.plot(TIEMPOS, Qv[:, 0], "ko")
    ax2.plot(TIEMPOS, Qv[:, 1], "ko")
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("θ [rad]")
    ax2.set_title("Spline cúbico por los puntos de paso")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
