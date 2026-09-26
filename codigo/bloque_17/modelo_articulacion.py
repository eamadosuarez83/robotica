"""Modelo de una articulacion (motor + reductor + eslabon) con
python-control: funcion de transferencia, polos, respuesta al escalon
en lazo abierto y cerrado (Bloque 17, Temas 17.3, 17.4 y 17.6).

Correr con:
    python codigo/bloque_17/modelo_articulacion.py
"""

import control
import numpy as np
import matplotlib.pyplot as plt


def main() -> None:
    # Motor + reductor + eslabon (Bloque 16): J y b ya incluyen lo
    # reflejado por el reductor (Bloque 16, Tema 16.2).
    J, b = 0.02, 0.01       # kg·m², N·m·s
    Kt, Ke, R = 0.05, 0.05, 2.0   # N·m/A, V·s/rad, Ohm

    b_eff = b + Kt * Ke / R
    G = control.tf([Kt / R], [J, b_eff, 0])
    print("G(s) =", G)
    print("Polos de la planta (lazo abierto):", G.poles())

    # Lazo cerrado con control proporcional simple (adelanto del Bloque 18)
    Kp = 5.0
    C = control.tf([Kp], [1])
    lazo_cerrado = control.feedback(C * G, 1)
    print(f"\nControlador proporcional Kp={Kp}")
    print("Polos en lazo cerrado:", lazo_cerrado.poles())

    t = np.linspace(0, 5, 1000)
    t_ol, y_ol = control.step_response(G, T=t)
    t_cl, y_cl = control.step_response(lazo_cerrado, T=t)

    info = control.step_info(lazo_cerrado)
    print("\nMétricas de la respuesta al escalón en lazo cerrado (Tema 17.4):")
    for clave in ("RiseTime", "Overshoot", "SettlingTime", "SteadyStateValue"):
        print(f"  {clave}: {info[clave]:.4f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.plot(t_ol, y_ol, color="tab:red")
    ax1.set_title("Lazo abierto: ante un escalón de voltaje,\nel ángulo crece sin límite (polo en s=0)")
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("θ [rad]")
    ax1.grid(True, alpha=0.3)

    ax2.plot(t_cl, y_cl, color="tab:blue")
    ax2.axhline(1.0, color="gray", ls=":", label="referencia")
    ax2.set_title(f"Lazo cerrado (P, Kp={Kp}):\nse asienta cerca de la referencia")
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("θ [rad]")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
