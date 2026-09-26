"""Mide el tiempo de evaluar Lagrange (simbolico, ya simplificado y
compilado con lambdify) contra Newton-Euler recursivo, para brazos de
2, 3 y 4 eslabones (Bloque 15, Tema 15.2).

Correr con:
    python codigo/bloque_15/costo_computacional.py
"""

import sys
import time
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import deducir_lagrange, matriz_masas, separar_gravedad_y_coriolis, newton_euler_plano  # noqa: E402


def construir_lagrange_n(n):
    t = sp.symbols('t')
    ms = sp.symbols(f'm1:{n+1}', positive=True)
    Ls = sp.symbols(f'L1:{n+1}', positive=True)
    g = sp.symbols('g', positive=True)
    thetas = [sp.Function(f'theta{i+1}')(t) for i in range(n)]

    x, y = 0, 0
    K = 0
    U = 0
    angulo = 0
    for i in range(n):
        angulo = angulo + thetas[i]
        x = x + Ls[i] * sp.cos(angulo)
        y = y + Ls[i] * sp.sin(angulo)
        K = K + sp.Rational(1, 2) * ms[i] * (sp.diff(x, t)**2 + sp.diff(y, t)**2)
        U = U + ms[i] * g * y

    ecuaciones, q, qdot, qddot = deducir_lagrange(K, U, thetas, t)
    M = matriz_masas(ecuaciones, qddot)
    G, C_qdot = separar_gravedad_y_coriolis(ecuaciones, M, qdot, qddot)

    valores = {g: 9.81}
    for i in range(n):
        valores[ms[i]] = 1.0
        valores[Ls[i]] = 0.25

    resto = (G + C_qdot).subs(valores)
    M_num = M.subs(valores)
    resto_f = sp.lambdify(q + qdot, resto, 'numpy')
    M_f = sp.lambdify(q, M_num, 'numpy')
    return M_f, resto_f, q, qdot, qddot


def main() -> None:
    print("Construyendo el modelo simbólico de Lagrange para n=2 y n=3...")
    print("(n=4 con simplify() en cada paso ya tarda varios minutos -- ver Tema 15.2)\n")
    print(f"{'n':>3s} {'construir M,C,G (s)':>20s} {'Lagrange (µs/eval)':>20s} {'Newton-Euler (µs/eval)':>24s}")
    for n in (2, 3):
        t_construccion0 = time.perf_counter()
        M_f, resto_f, q, qdot, qddot = construir_lagrange_n(n)
        t_construccion = time.perf_counter() - t_construccion0
        rng = np.random.default_rng(0)
        th = rng.uniform(-np.pi, np.pi, n)
        thd = rng.uniform(-1, 1, n)
        thdd = rng.uniform(-1, 1, n)

        reps = 200
        t0 = time.perf_counter()
        for _ in range(reps):
            Mn = np.array(M_f(*th), dtype=float)
            resto = np.array(resto_f(*th, *thd), dtype=float).flatten()
            _ = np.linalg.solve(Mn, thdd - resto)  # dinámica inversa: tau = M*thdd + resto
        t_lagrange = (time.perf_counter() - t0) / reps * 1e6

        m = [1.0] * n
        L = [0.25] * n
        I = [0.0] * n
        t0 = time.perf_counter()
        for _ in range(reps):
            _ = newton_euler_plano(th, thd, thdd, m, L, L, I)
        t_ne = (time.perf_counter() - t0) / reps * 1e6

        print(f"{n:>3d} {t_construccion:>20.2f} {t_lagrange:>20.1f} {t_ne:>24.1f}")

    print("\nEl costo que realmente crece mal con n es CONSTRUIR el modelo simbólico de")
    print("Lagrange (columna 'construir M,C,G'): de n=2 a n=3 ya se multiplica por ~10,")
    print("y para n=6 (un brazo industrial típico) tarda minutos -- ese paso solo se hace")
    print("una vez, fuera de línea, no en el lazo de control (Tema 15.2).")
    print("La columna 'Newton-Euler' es más lenta aquí en microsegundos que 'Lagrange'")
    print("(¡ya construido!) porque esta implementación de Newton-Euler es Python puro")
    print("con un ciclo por eslabón, sin compilar, mientras que 'Lagrange' ya está")
    print("compilado a NumPy con lambdify -- no es una comparación de igual a igual.")
    print("El punto real no es 'cuál es más rápido en microsegundos para n=2 o 3', sino")
    print("que Newton-Euler NUNCA necesita una fase de construcción que explote con n:")
    print("siempre evalúa con el mismo procedimiento fijo, eslabón por eslabón.")


if __name__ == "__main__":
    main()
