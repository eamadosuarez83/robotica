"""Romperlo a proposito: agregar un retardo de transporte al lazo
cerrado y aumentarlo hasta que un sistema antes estable empiece a
oscilar sin decaer (Bloque 17, Tema 17.5).

El retardo puro e^(-Ls) no es racional; se aproxima con Pade
(control.pade), estandar para este analisis.

Correr con:
    python codigo/bloque_17/romper_retardo.py
"""

import control
import numpy as np
import matplotlib.pyplot as plt


def main() -> None:
    J, b, Kt, Ke, R = 0.02, 0.01, 0.05, 0.05, 2.0
    b_eff = b + Kt * Ke / R
    G = control.tf([Kt / R], [J, b_eff, 0])

    Kp = 5.0
    C = control.tf([Kp], [1])

    print(f"{'retardo L [s]':>15s} {'polo dominante (parte real)':>30s} {'estable':>10s}")
    retardos = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    resultados = []
    for L in retardos:
        if L == 0.0:
            lazo = control.feedback(C * G, 1)
        else:
            num_pade, den_pade = control.pade(L, 3)
            retraso = control.tf(num_pade, den_pade)
            lazo = control.feedback(C * G * retraso, 1)
        polos = lazo.poles()
        parte_real_max = np.max(polos.real)
        estable = parte_real_max < 0
        resultados.append((L, lazo))
        print(f"{L:>15.2f} {parte_real_max:>30.4f} {str(estable):>10s}")

    print("\nA medida que crece el retardo, el polo dominante se acerca al eje")
    print("imaginario y lo cruza: el mismo controlador que era estable sin retardo")
    print("deja de serlo -- un retardo (por ejemplo, de comunicación o de un filtro")
    print("del sensor) puede desestabilizar un lazo que en papel se ve bien.")

    fig, ax = plt.subplots(figsize=(8, 5))
    t = np.linspace(0, 8, 2000)
    for L, lazo in resultados:
        try:
            t_r, y = control.step_response(lazo, T=t)
            ax.plot(t_r, y, label=f"L={L:.2f} s")
        except Exception:
            pass
    ax.axhline(1.0, color="gray", ls=":")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("θ [rad]")
    ax.set_title("Respuesta al escalón al aumentar el retardo en el lazo")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1, 3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
