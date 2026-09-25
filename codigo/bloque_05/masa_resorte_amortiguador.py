"""Solucion analitica del resorte-amortiguador: sub, critico y
sobreamortiguado, verificada contra solve_ivp (Bloque 05, Tema 5.4).

Correr con:
    python codigo/bloque_05/masa_resorte_amortiguador.py
"""

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def resolver_simbolico(m, b, k, x0=1.0, v0=0.0):
    """Resuelve m x'' + b x' + k x = 0 con SymPy, en forma exacta.

    `b` y `k` se aceptan como expresiones exactas de SymPy (enteros,
    racionales, sp.sqrt(...)) para evitar el caso críticamente
    amortiguado con un discriminante flotante "casi cero": con b, k
    exactos el discriminante es EXACTAMENTE cero y dsolve no arrastra
    error de redondeo al resolver las constantes.
    """
    t = sp.symbols('t')
    x = sp.Function('x')
    edo = sp.Eq(m * x(t).diff(t, 2) + b * x(t).diff(t) + k * x(t), 0)
    sol = sp.dsolve(edo, x(t), ics={x(0): x0, x(t).diff(t).subs(t, 0): v0})
    return sp.lambdify(t, sp.re(sol.rhs), 'numpy')


def f(t, z, m, b, k):
    x, xdot = z
    return [xdot, -(b * xdot + k * x) / m]


def main() -> None:
    m = 1
    k = 10
    x0, v0 = 1.0, 0.0
    t = np.linspace(0, 6, 400)

    # b exacto (SymPy) para cada caso: evita el discriminante "casi cero"
    # de la sección 5 del bloque.
    casos = {
        "Subamortiguado (b²<4mk)":   dict(b=sp.Integer(2), color="tab:blue"),
        "Crítico (b²=4mk)":          dict(b=2 * sp.sqrt(m * k), color="tab:green"),
        "Sobreamortiguado (b²>4mk)": dict(b=sp.Integer(8), color="tab:red"),
    }

    fig, ax = plt.subplots(figsize=(8, 5))

    for nombre, params in casos.items():
        b, color = params["b"], params["color"]
        b_num = float(b)
        disc = b_num**2 - 4 * m * k
        print(f"{nombre}: b={b_num:.3f}, k={k}, discriminante={disc:.3f}")

        x_analitica = resolver_simbolico(m, b, k, x0, v0)
        x_num = x_analitica(t)
        ax.plot(t, x_num, color=color, label=nombre)

        sol = solve_ivp(f, [t[0], t[-1]], [x0, v0], t_eval=t, args=(m, b_num, k))
        error = np.max(np.abs(sol.y[0] - x_num))
        print(f"  error máx. vs. solve_ivp: {error:.2e}")

    ax.axhline(0, color="gray", lw=0.5)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("x(t)")
    ax.set_title("Resorte-amortiguador: los tres regímenes")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
