"""Romperlo a propósito: una recta cartesiana que pasa cerca de una
singularidad (Bloque 19, Tema 19.5).

La punta del 2R recorre una recta horizontal de x = -0.3 a x = 0.3 m,
a una altura y fija, en 2 s con ley temporal quíntica. En cada instante
se resuelve la inversa (codo arriba). Si la recta pasa cerca del
hombro, el brazo tiene que plegarse casi por completo (θ2 → π): ahí
det J = L1 L2 sin θ2 → 0, y el hombro tiene que girar casi media vuelta
en muy poco tiempo.

Correr con:
    python codigo/bloque_19/romper_singularidad.py

Salida esperada: a y = 0.30 m, velocidades articulares moderadas; al
bajar la recta hacia 0.105 m, la velocidad pico del hombro se dispara;
a y = 0.09 m la recta entra en la zona que el brazo no alcanza (r < L1 -
L2 = 0.1 m) y la inversa falla a mitad de camino. Interpolando en el
espacio articular, los mismos extremos piden velocidades pequeñas.
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.trayectorias import linea, quintica, resolver_trayectoria  # noqa: E402
from brazo_2r import L1, L2, directa, inversa  # noqa: E402

T = 2.0
N = 4001


def jacobiana_2r(q):
    s1, c1 = np.sin(q[0]), np.cos(q[0])
    s12, c12 = np.sin(q[0] + q[1]), np.cos(q[0] + q[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12],
                     [L1 * c1 + L2 * c12, L2 * c12]])


def recta(y):
    """Resuelve la recta a altura y. Devuelve (t, Q, Qd, P, resultado)."""
    t = np.linspace(0, T, N)
    s, sd, _ = quintica(0.0, 1.0, T, t)            # avance de 0 a 1 a lo largo de la recta
    P1, P2 = np.array([-0.3, y]), np.array([0.3, y])
    P = P1 + s[:, None] * (P2 - P1)
    res = resolver_trayectoria(P, inversa, solucion=0)
    if not res.ok:
        return t, None, None, P, res
    Q = np.unwrap(res.Q, axis=0)                    # θ1 no debe saltar de +π a -π
    Qd = np.gradient(Q, t, axis=0)
    # Calibración: q' = J⁻¹ x' (Bloque 13), en la muestra de velocidad máxima
    k = np.argmax(np.abs(Qd[:, 0]))
    xd = (P2 - P1) * sd[k]
    qd_jac = np.linalg.solve(jacobiana_2r(Q[k]), xd)
    return t, Q, Qd, P, (res, k, qd_jac)


def main() -> None:
    print(f"Recta horizontal de x = -0.3 a 0.3 m en {T} s. Zona muerta: r < {L1 - L2:.2f} m\n")
    print(f"{'altura y':>9s} {'θ2 máx':>8s} {'|sin θ2| mín':>13s} {'|θ1\'| máx':>10s} "
          f"{'|θ2\'| máx':>10s} {'J⁻¹ẋ en el pico':>18s}")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    for y in (0.30, 0.20, 0.13, 0.105, 0.09):
        t, Q, Qd, P, extra = recta(y)
        if Q is None:
            res = extra
            Pf = P[res.indice_fallo]
            print(f"{y:>9.3f}  sin solución en la muestra {res.indice_fallo} "
                  f"(x = {Pf[0]:+.3f} m, r = {np.hypot(*Pf):.3f} m < {L1 - L2:.2f})")
            continue
        _, k, qd_jac = extra
        print(f"{y:>9.3f} {np.degrees(np.abs(Q[:, 1]).max()):>7.1f}° "
              f"{np.abs(np.sin(Q[:, 1])).min():>13.3f} {np.abs(Qd[:, 0]).max():>10.2f} "
              f"{np.abs(Qd[:, 1]).max():>10.2f} {qd_jac[0]:>+18.2f}")
        ax1.plot(t, Qd[:, 0], label=f"y = {y} m")
        ax2.plot(P[:, 0], P[:, 1], label=f"y = {y} m")
    print("  (la última columna es θ1' calculada con la Jacobiana: coincide con la")
    print("   derivada numérica de la columna anterior, con su signo)")

    # Los mismos extremos de la recta más baja, interpolados en ángulos
    y = 0.105
    q_ini = inversa([-0.3, y])[0]
    q_fin = inversa([0.3, y])[0]
    q_fin[0] = q_ini[0] + np.angle(np.exp(1j * (q_fin[0] - q_ini[0])))   # el camino corto
    t = np.linspace(0, T, N)
    Qa = np.column_stack([quintica(q_ini[j], q_fin[j], T, t)[0] for j in range(2)])
    Qad = np.column_stack([quintica(q_ini[j], q_fin[j], T, t)[1] for j in range(2)])
    punta = directa(Qa)
    print(f"\nMismos extremos (y = {y}), interpolando en el espacio articular:")
    print(f"  |θ1'| máx = {np.abs(Qad[:, 0]).max():.2f} rad/s, |θ2'| máx = {np.abs(Qad[:, 1]).max():.2f} rad/s")
    print(f"  pero la punta se aparta de la recta hasta {np.abs(punta[:, 1] - y).max() * 100:.1f} cm")
    ax2.plot(punta[:, 0], punta[:, 1], "k--", label="articular (y = 0.105)")

    circ = plt.Circle((0, 0), L1 - L2, color="gray", alpha=0.3, label="no alcanzable")
    ax2.add_patch(circ)
    ax2.plot(0, 0, "ks")
    ax2.set_aspect("equal")
    ax2.set_xlim(-0.35, 0.35)
    ax2.set_ylim(-0.25, 0.4)
    ax2.set_xlabel("x [m]")
    ax2.set_ylabel("y [m]")
    ax2.set_title("Recorridos de la punta")
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.3)
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("θ1' [rad/s]")
    ax1.set_title("Velocidad del hombro para seguir la recta")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
