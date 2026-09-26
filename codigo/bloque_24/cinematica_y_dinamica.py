"""Entregables 2 y 3 del proyecto integrador: tabla DH, cinematica
directa e inversa con verificacion cruzada, Jacobiana, y modelo
dinamico completo (masas puntuales, Bloque 14) con verificacion de
M simetrica y definida positiva.

Tarda ~2 minutos (la deduccion simbolica de Lagrange para 4 GDL
espaciales, Bloque 15 Tema 15.2: el costo de CONSTRUIR crece mal con
n). Correr con:
    python codigo/bloque_24/cinematica_y_dinamica.py
"""

import sys
import time
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa, matriz_dh_simbolica  # noqa: E402
from robotica.dinamica import deducir_lagrange, matriz_masas, separar_gravedad_y_coriolis  # noqa: E402
from robotica.inversa import inversa_numerica  # noqa: E402
from robotica.jacobiana import jacobiana_geometrica, manipulabilidad  # noqa: E402
from modelo_proyecto import DH, MASAS, ALCANCE_MAXIMO  # noqa: E402


def parte_cinematica():
    print("=== Entregable 2: cinemática directa, inversa, Jacobiana ===\n")
    T0 = directa(DH, [0, 0, 0, 0])
    print(f"Pinza en q=0: {np.round(T0[:3,3], 4)} m")
    print(f"Alcance máximo aproximado: {ALCANCE_MAXIMO:.3f} m\n")

    rng = np.random.default_rng(2)
    print(f"{'objetivo':>30s} {'convergió':>10s} {'error (mm)':>12s} {'manipulabilidad':>16s}")
    for _ in range(8):
        q_real = rng.uniform(-np.pi / 3, np.pi / 3, 4)
        objetivo = directa(DH, q_real)[:3, 3]
        q, conv = inversa_numerica(DH, objetivo, np.zeros(4), metodo="amortiguado", max_iter=3000)
        p_check = directa(DH, q)[:3, 3]
        error_mm = np.linalg.norm(p_check - objetivo) * 1000
        J = jacobiana_geometrica(DH, q)[:3, :]
        w = manipulabilidad(J)
        print(f"{str(np.round(objetivo, 3)):>30s} {str(conv):>10s} {error_mm:>12.4f} {w:>16.5f}")
        assert conv and error_mm < 1.0


def parte_dinamica():
    print("\n=== Entregable 3: modelo dinámico (Lagrange, masas puntuales) ===\n")
    t0 = time.time()
    t = sp.symbols('t')
    Ls = sp.symbols('L1 L2 L3 L4', positive=True)
    ms = sp.symbols('m1 m2 m3 m4', positive=True)
    g = sp.symbols('g', positive=True)
    qs_t = [sp.Function(f'q{i}')(t) for i in range(1, 5)]

    offsets = [np.pi, -np.pi / 2, np.pi / 2, 0]
    alphas = [-sp.pi / 2, sp.pi, sp.pi / 2, 0]
    ds = [Ls[0], 0, 0, 0]
    as_ = [0, Ls[1], Ls[2], Ls[3]]

    Tacc = sp.eye(4)
    posiciones = []
    for i in range(4):
        theta = offsets[i] + qs_t[i]
        Tacc = sp.simplify(Tacc * matriz_dh_simbolica(theta, ds[i], as_[i], alphas[i]))
        posiciones.append(Tacc[:3, 3])

    K, U = 0, 0
    for pos, m in zip(posiciones, ms):
        vel = sp.Matrix([sp.diff(c, t) for c in pos])
        K += sp.Rational(1, 2) * m * (vel.T * vel)[0]
        U += m * g * pos[2]

    ecuaciones, q, qdot, qddot = deducir_lagrange(K, U, qs_t, t)
    M = matriz_masas(ecuaciones, qddot)
    Gv, C_qdot = separar_gravedad_y_coriolis(ecuaciones, qdot, qddot)
    print(f"Modelo construido en {time.time()-t0:.1f} s "
          "(compárese con ~2 s / ~17 s para 2 / 3 eslabones, Bloque 15 Tema 15.2 "
          "-- el tiempo exacto varía con la carga de la máquina)")

    valores = {ms[i]: MASAS[i] for i in range(4)}
    valores.update({Ls[0]: DH[0][1], Ls[1]: DH[1][2], Ls[2]: DH[2][2], Ls[3]: DH[3][2], g: 9.81})
    M_f = sp.lambdify(q, M.subs(valores), 'numpy')
    G_f = sp.lambdify(q, Gv.subs(valores), 'numpy')

    rng = np.random.default_rng(3)
    ok = True
    for _ in range(30):
        qs_val = rng.uniform(-np.pi, np.pi, 4)
        Mn = np.array(M_f(*qs_val), dtype=float)
        simetrica = np.allclose(Mn, Mn.T)
        positiva = np.all(np.linalg.eigvalsh(Mn) > 0)
        ok = ok and simetrica and positiva
    print(f"M simétrica y definida positiva en 30 posturas aleatorias: {ok}")
    assert ok

    g_max = np.max([np.linalg.norm(G_f(*rng.uniform(-np.pi, np.pi, 4)))
                     for _ in range(200)])
    print(f"Par de gravedad máximo observado (200 posturas aleatorias): {g_max:.3f} N·m "
          "-- punto de partida para el dimensionamiento (Bloque 16)")


if __name__ == "__main__":
    parte_cinematica()
    parte_dinamica()
