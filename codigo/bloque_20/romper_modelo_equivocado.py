"""Romperlo a proposito: par calculado con una masa del modelo 30%
equivocada -- el controlador usa M_hat, resto_hat de un modelo con
masas incorrectas, pero la PLANTA real sigue teniendo las masas
verdaderas (Bloque 20, Tema 20.5, robustez).

Correr con:
    python codigo/bloque_20/romper_modelo_equivocado.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modelo_2r import M1, M2, construir_modelo  # noqa: E402
from control_comparado import error_rms, par_calculado, simular_control  # noqa: E402


def main() -> None:
    M_real, resto_real, _ = construir_modelo(M1, M2)   # planta real (ya es la que usa simular_control)

    print(f"Masas reales: m1={M1} kg, m2={M2} kg\n")
    print(f"{'error del modelo':>20s} {'RMS θ1 lento':>14s} {'RMS θ1 rápido':>15s}")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for error_pct, ax in zip([0, 30], axes):
        m1_modelo = M1 * (1 + error_pct / 100)
        m2_modelo = M2 * (1 + error_pct / 100)
        M_hat, resto_hat, _ = construir_modelo(m1_modelo, m2_modelo)

        for T, color, etiqueta in [(3.0, "tab:blue", "lento"), (0.4, "tab:red", "rápido")]:
            ley = par_calculado(M_hat=M_hat, resto_hat=resto_hat)
            t, Q, Qd = simular_control(ley, T)
            rms = np.degrees(error_rms(Q, Qd))
            if T == 3.0:
                print(f"{error_pct:>18d}% {rms[0]:>13.3f}° ", end="")
            else:
                print(f"{rms[0]:>14.3f}°")
            ax.plot(t, np.degrees(Q[:, 0] - Qd[:, 0]), color=color,
                     label=f"{etiqueta} (rms={rms[0]:.2f}°)")
        ax.set_xlabel("t [s]")
        ax.set_ylabel("error θ1 [°]")
        ax.set_title(f"Modelo con {error_pct}% de error en la masa")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    print("\nCon el modelo correcto, el par calculado sigue casi perfecto (Tema 20.3);")
    print("con 30% de error en la masa, el error de seguimiento crece notoriamente,")
    print("sobre todo en el movimiento rápido (donde los términos de inercia y")
    print("Coriolis -- los más sensibles al error de masa -- dominan más).")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
