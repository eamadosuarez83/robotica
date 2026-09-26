"""Dinamica por Lagrange, simbolica con SymPy (Bloque 14).

Original de este curso: robotica-manipuladores solo tiene el tensor
de inercia de un prisma (que va al Bloque 06), no dinamica de
manipuladores completa.
"""

from __future__ import annotations

import sympy as sp

__all__ = ["deducir_lagrange", "matriz_masas", "separar_gravedad_y_coriolis"]


def deducir_lagrange(K, U, coords, t):
    """Deduce las ecuaciones de Lagrange d/dt(dL/dq̇_i) - dL/dq_i = tau_i.

    `K`, `U`: energía cinética y potencial (expresiones de SymPy) en
    función de `coords` (lista de `sp.Function('nombre')(t)`, funciones
    del tiempo) y sus derivadas.
    `t`: el símbolo del tiempo.

    Devuelve `(ecuaciones, q, qdot, qddot)`: las n ecuaciones (lado
    izquierdo; tau_i queda implícito del lado derecho) ya expresadas
    en símbolos algebraicos limpios `q_i`, `q_ip` (q̇_i), `q_ipp` (q̈_i),
    en vez de funciones del tiempo.
    """
    nombres = [str(c.func) for c in coords]
    q = list(sp.symbols(nombres))
    qdot = list(sp.symbols([n + "p" for n in nombres]))
    qddot = list(sp.symbols([n + "pp" for n in nombres]))

    L = K - U
    ecuaciones = []
    for qi_t in coords:
        qi_dot_t = sp.diff(qi_t, t)
        dL_dqidot = sp.diff(L, qi_dot_t)
        d_dt_termino = sp.diff(dL_dqidot, t)
        dL_dqi = sp.diff(L, qi_t)
        ecuaciones.append(sp.expand(d_dt_termino - dL_dqi))

    subs = {}
    for qi_t, qs, qd, qdd in zip(coords, q, qdot, qddot):
        subs[sp.diff(qi_t, t, 2)] = qdd
        subs[sp.diff(qi_t, t)] = qd
        subs[qi_t] = qs
    ecuaciones = [sp.simplify(eq.subs(subs)) for eq in ecuaciones]
    return ecuaciones, q, qdot, qddot


def matriz_masas(ecuaciones, qddot) -> sp.Matrix:
    """M(q): matriz de masas/inercia, los coeficientes de q̈ en cada ecuación.

    Simétrica y definida positiva (Bloque 14, Tema 14.6) para cualquier
    sistema físico bien formado.
    """
    n = len(ecuaciones)
    M = sp.zeros(n, n)
    for i, eq in enumerate(ecuaciones):
        for j, qddj in enumerate(qddot):
            M[i, j] = sp.diff(eq, qddj)
    return sp.simplify(M)


def separar_gravedad_y_coriolis(ecuaciones, M, qdot, qddot) -> tuple[sp.Matrix, sp.Matrix]:
    """Separa lo que queda de cada ecuación tras restar M(q)q̈ en G(q)
    (evaluando en q̇=0) y C(q,q̇)q̇ (el resto): M(q)q̈ + C(q,q̇)q̇ + G(q) = tau.
    """
    n = len(ecuaciones)
    resto = [sp.expand(ecuaciones[i] - sum(M[i, j] * qddot[j] for j in range(n)))
             for i in range(n)]
    ceros = {qd: 0 for qd in qdot}
    G = sp.Matrix([r.subs(ceros) for r in resto])
    C_qdot = sp.Matrix([sp.simplify(resto[i] - G[i]) for i in range(n)])
    return G, C_qdot
