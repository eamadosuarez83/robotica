"""Deduce con Lagrange la ecuacion del pendulo simple y la compara
contra la deducida con Newton en el Bloque 05 (Bloque 14, Tema 14.2).

Correr con:
    python codigo/bloque_14/lagrange_pendulo.py
"""

import sys
from pathlib import Path

import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import deducir_lagrange  # noqa: E402


def main() -> None:
    t = sp.symbols('t')
    m, L, g = sp.symbols('m L g', positive=True)
    theta = sp.Function('theta')(t)

    K = sp.Rational(1, 2) * m * L**2 * sp.diff(theta, t)**2
    U = -m * g * L * sp.cos(theta)   # theta=0 hacia abajo (Bloque 05)

    ecuaciones, q, qdot, qddot = deducir_lagrange(K, U, [theta], t)
    ec = sp.simplify(ecuaciones[0])

    print("Ecuación deducida con Lagrange (= 0, péndulo libre):")
    sp.pprint(ec)

    # Comparar contra m L^2 theta'' + m g L sin(theta) = 0 (Bloque 05, Tema 5.3)
    esperada = m * L**2 * qddot[0] + m * g * L * sp.sin(q[0])
    diferencia = sp.simplify(ec - esperada)
    print(f"\nDiferencia con la ecuación de Newton del Bloque 05: {diferencia}")
    assert diferencia == 0
    print("OK: Lagrange reproduce exactamente la ecuación de Newton.")


if __name__ == "__main__":
    main()
