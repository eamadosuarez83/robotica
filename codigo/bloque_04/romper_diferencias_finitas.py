"""Romperlo a proposito: derivada analitica contra derivada numerica,
con pasos h muy grandes y muy pequeños (Bloque 04, Tema 4.6).

Con h grande domina el error de truncamiento (la aproximacion en si
es mala). Con h demasiado pequeño domina el error de redondeo de
punto flotante (f(x+h)-f(x) resta dos numeros casi iguales y pierde
precision). El error total tiene forma de V en escala log-log.

Correr con:
    python codigo/bloque_04/romper_diferencias_finitas.py
"""

import numpy as np
import matplotlib.pyplot as plt


def f(x):
    return np.sin(x)


def f_prime_exacta(x):
    return np.cos(x)


def derivada_numerica(f, x, h):
    return (f(x + h) - f(x)) / h


def main() -> None:
    x0 = 1.0  # punto donde se evalúa la derivada
    exacta = f_prime_exacta(x0)

    hs = np.logspace(-16, 0, 200)
    numericas = np.array([derivada_numerica(f, x0, h) for h in hs])
    error = np.abs(numericas - exacta)

    h_optimo = hs[np.argmin(error)]
    print(f"Derivada exacta en x0={x0}: cos({x0}) = {exacta:.10f}")
    print(f"Menor error obtenido: {error.min():.2e}, con h = {h_optimo:.2e}")
    print("Para h > ~1e-8: domina el error de truncamiento (aproximación mala).")
    print("Para h < ~1e-8: domina el error de redondeo (resta de números casi iguales).")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.loglog(hs, error, color="tab:blue")
    ax.axvline(h_optimo, color="tab:red", ls="--",
               label=f"h óptimo ≈ {h_optimo:.1e}")
    ax.set_xlabel("h (paso de la diferencia finita)")
    ax.set_ylabel("|derivada numérica − derivada exacta|")
    ax.set_title("Error de la derivada numérica vs. h (forma de V)")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
