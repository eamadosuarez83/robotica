"""Sintonía de un PID: ubicación de polos contra Ziegler-Nichols
(Bloque 18, Tema 18.3).

La articulación real tiene un retardo (filtro del sensor, cálculo,
comunicación: Bloque 17, Tema 17.5). Aquí se modela con L = 20 ms,
como un retardo exacto de 20 muestras de 1 ms dentro del lazo.

1. Ziegler-Nichols necesita la ganancia última ku y su periodo tu. Se
   calculan con python-control (margen de ganancia de G·e^(-Ls), con
   Padé) y se comprueban simulando: con kp = ku el lazo oscila sin
   crecer ni decaer.
2. Se comparan tres PID sobre un escalón de 0.2 rad con gravedad:
   Ziegler-Nichols, ubicación de polos, y ubicación de polos más lenta.

Correr con:
    python codigo/bloque_18/sintonia.py

Salida esperada: ku ≈ 22.5 V/rad, tu ≈ 1.19 s; la oscilación con
kp = ku casi no cambia de amplitud de un ciclo al siguiente; Ziegler-
Nichols da un sobrepaso enorme (~87 %: es agresivo por diseño); la
ubicación de polos, ~31 % por culpa del cero del PI; con el filtro de
la referencia que cancela ese cero, casi nada.
"""

import sys
from collections import deque
from pathlib import Path

import control
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID, pid_por_polos, simular_lazo, ziegler_nichols  # noqa: E402
from articulacion import B_EFF, G, J, K, TAU_G, U_MAX, dinamica, metricas  # noqa: E402

TS = 0.001
L = 0.020


class FiltroReferencia:
    """Pasa la referencia por 1/(τ s + 1) antes del PID, con τ = kp/ki:
    cancela el cero que el PI pone en s = -ki/kp (Tema 18.3)."""

    def __init__(self, controlador, tau, r0):
        self.c, self.ts = controlador, controlador.ts
        self.tau, self.rf = tau, r0

    def paso(self, r, y):
        self.rf = (self.tau * self.rf + self.ts * r) / (self.tau + self.ts)
        return self.c.paso(self.rf, y)


class ConRetardo:
    """La acción calculada llega a la planta `n` muestras después."""

    def __init__(self, controlador, n, u0=0.0):
        self.c, self.ts = controlador, controlador.ts
        self.cola = deque([u0] * n)

    def paso(self, r, y):
        self.cola.append(self.c.paso(r, y))
        return self.cola.popleft()


def main() -> None:
    n_retardo = int(round(L / TS))

    # 1. Ganancia y periodo últimos, con python-control
    num, den = control.pade(L, 3)
    ku, _, w180, _ = control.margin(G * control.tf(num, den))
    tu = 2 * np.pi / w180
    print(f"Retardo en el lazo: L = {L * 1000:.0f} ms")
    print(f"python-control: ku = {ku:.2f} V/rad, tu = {tu:.3f} s")

    # ... y comprobado simulando: kp = ku, sin gravedad, pequeño empujón
    lineal = lambda x, u: dinamica(x, u, tau_g=0.0)  # noqa: E731
    p_ku = ConRetardo(PID(ku, ts=TS), n_retardo)
    t, X, _ = simular_lazo(lineal, p_ku, lambda t: 0.05, [0.0, 0.0], 12.0, subpasos=2)
    y = X[:, 0] - 0.05
    picos = [y[k] for k in range(1, len(y) - 1)
             if y[k] > y[k - 1] and y[k] >= y[k + 1] and t[k] > 2]
    periodos = np.diff([t[k] for k in range(1, len(y) - 1)
                        if y[k] > y[k - 1] and y[k] >= y[k + 1] and t[k] > 2])
    print(f"simulado con kp = ku: periodo medido = {periodos.mean():.3f} s, "
          f"cociente entre picos sucesivos = {picos[-1] / picos[-2]:.4f} (1 = sostenida)")

    # 2. Tres sintonías
    sintonias = {
        "Ziegler-Nichols": ziegler_nichols(ku, tu),
        "polos ωn=4, ζ=0.8": pid_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8, p=4.0),
        "polos + filtro de r": pid_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8, p=4.0),
    }
    # Antes del escalón, el lazo ya sostenía el eslabón en theta0: la
    # integral guardaba el voltaje que equilibra la gravedad (Tema 18.2).
    ref, theta0 = 0.2, 0.0
    u_sostener = TAU_G * np.cos(theta0) / K
    print(f"\nIntegral inicial = voltaje que sostiene el eslabón = {u_sostener:.2f} V")
    print(f"Escalón de {ref} rad con gravedad y retardo de {L * 1000:.0f} ms:")
    print(f"{'sintonía':<20s} {'kp':>7s} {'ki':>7s} {'kd':>6s} "
          f"{'sobrepaso':>10s} {'t_est 2%':>9s} {'|u| máx':>8s}")
    fig, ax = plt.subplots(figsize=(9, 5))
    for nombre, (kp, ki, kd) in sintonias.items():
        pid = PID(kp, ki, kd, ts=TS, u_min=-U_MAX, u_max=U_MAX, tf=0.005)
        pid.integral = u_sostener
        if "filtro" in nombre:
            pid = FiltroReferencia(pid, tau=kp / ki, r0=theta0)
        lazo = ConRetardo(pid, n_retardo, u0=u_sostener)
        t, X, U = simular_lazo(dinamica, lazo, lambda t: ref, [theta0, 0.0], 10.0, subpasos=2)
        sobrepaso, t_est, _ = metricas(t, X[:, 0], ref)
        print(f"{nombre:<20s} {kp:>7.2f} {ki:>7.2f} {kd:>6.2f} "
              f"{sobrepaso:>9.1f}% {t_est:>8.2f}s {np.max(np.abs(U)):>8.2f}")
        ax.plot(t, X[:, 0], label=nombre)

    kp, ki, _ = sintonias["polos ωn=4, ζ=0.8"]
    print(f"\nLos polos piden ζ = 0.8, pero el PI agrega un cero en s = -ki/kp = {-ki / kp:.2f}:")
    print("ese cero, más lento que los polos, es el que produce el sobrepaso.")
    print("Filtrar la referencia con 1/((kp/ki) s + 1) lo cancela.")
    print("\nZiegler-Nichols no usa el modelo: solo dos números medidos en la")
    print("articulación real. Por eso sirve cuando no hay modelo, y por eso")
    print("hay que retocarlo después. La ubicación de polos usa J, b y K: si el")
    print("modelo es bueno, se elige la respuesta en vez de aceptar la que salga.")

    ax.axhline(ref, color="gray", ls=":", label="referencia")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("θ [rad]")
    ax.set_title(f"Tres sintonías del mismo PID (retardo {L * 1000:.0f} ms, con gravedad)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
