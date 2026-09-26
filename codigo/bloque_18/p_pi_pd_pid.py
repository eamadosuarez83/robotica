"""El problema que abre el bloque: el control proporcional deja el
eslabón colgando por debajo, y al subir la ganancia vibra. Qué aporta
y qué rompe cada acción: P, PI, PD, PID (Bloque 18, Temas 18.1 y 18.2).

La articulación arranca horizontal (θ = 0) y se le pide θ = 0.5 rad.
La gravedad es la perturbación que el lazo tiene que vencer.

Correr con:
    python codigo/bloque_18/p_pi_pd_pid.py

Salida esperada (tabla):
  P  (kp=20):  se queda ~0.19 rad por debajo, como predice la fórmula.
  P  (kp=80):  se queda ~0.05 rad por debajo, pero con 45 % de sobrepaso.
  PI:          el error debía irse a cero; aquí oscila sin parar, saturado.
  PD:          no vibra, pero sigue colgando.
  PID:         error final cero, sin vibrar.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID, pd_por_polos, pid_por_polos, simular_lazo  # noqa: E402
from articulacion import B_EFF, J, K, TAU_G, U_MAX, dinamica, metricas  # noqa: E402

REF = 0.5
TS = 0.001


def main() -> None:
    kp_pd, kd_pd = pd_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8)
    kp, ki, kd = pid_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8, p=4.0)
    casos = {
        "P  (kp=20)": (20.0, 0.0, 0.0),
        "P  (kp=80)": (80.0, 0.0, 0.0),
        "PI": (kp, ki, 0.0),
        "PD": (kp_pd, 0.0, kd_pd),
        "PID": (kp, ki, kd),
    }

    print(f"Articulación: J={J}, b_eff={B_EFF}, K={K} N·m/V, τ_g={TAU_G} N·m, "
          f"u en ±{U_MAX} V\n")
    print("Error final esperado con P, a mano (Tema 18.2): e = τ_g cos θ / (K kp)")
    for kp_p in (20.0, 80.0):
        # Punto fijo: e = τ_g cos(REF - e) / (K kp)
        e = 0.0
        for _ in range(50):
            e = TAU_G * np.cos(REF - e) / (K * kp_p)
        print(f"  kp={kp_p:>4.0f}: e = {e:.4f} rad ({np.degrees(e):.1f}°)")

    print(f"\n{'control':<11s} {'kp':>7s} {'ki':>7s} {'kd':>6s} "
          f"{'error medio':>12s} {'oscilación':>11s} {'sobrepaso':>10s} {'|u| máx':>8s}")
    print(f"{'':<34s}{'(últimos 2 s)':>12s} {'pico a pico':>11s}")
    fig, ax = plt.subplots(figsize=(9, 5))
    for nombre, (p, i, d) in casos.items():
        pid = PID(p, i, d, ts=TS, u_min=-U_MAX, u_max=U_MAX)
        t, X, U = simular_lazo(dinamica, pid, lambda t: REF, [0.0, 0.0], 20.0, subpasos=4)
        y = X[:, 0]
        sobrepaso, _, _ = metricas(t, y, REF)
        # Si todavía oscila, "el error final" es el centro de la oscilación.
        cola = y[t > t[-1] - 2]
        print(f"{nombre:<11s} {p:>7.2f} {i:>7.2f} {d:>6.2f} {REF - cola.mean():>12.4f} "
              f"{np.ptp(cola):>11.4f} {sobrepaso:>9.1f}% {np.max(np.abs(U)):>8.2f}")
        ax.plot(t, y, label=nombre)

    # PI: por qué es inestable (Routh para a3 s³ + a2 s² + a1 s + a0)
    a3, a2, a1, a0 = J, B_EFF, K * kp, K * ki
    print(f"\nCon solo P, la parte real de los polos es -b_eff/(2J) = {-B_EFF / (2 * J):.3f} 1/s")
    print("  sin importar kp: subir kp no amortigua nada, solo sube la frecuencia.")
    print(f"\nPI, criterio de Routh: a2·a1 = {a2 * a1:.4f}  frente a  a3·a0 = {a3 * a0:.4f}")
    print("  estable solo si a2·a1 > a3·a0: aquí no. Sin derivada, casi no hay")
    print("  amortiguamiento (b_eff es pequeño) y la integral lo empuja a oscilar.")

    ax.axhline(REF, color="gray", ls=":", label="referencia")
    ax.set_ylim(-0.2, 1.2)
    ax.set_xlim(0, 10)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("θ [rad]")
    ax.set_title("Articulación con gravedad: P cuelga, P alto vibra, PI se desestabiliza,\n"
                 "PD amortigua pero cuelga, PID llega")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
