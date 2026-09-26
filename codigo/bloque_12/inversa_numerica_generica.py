"""Cinematica inversa numerica generica: compara Newton-Raphson
(pseudo-inversa), Jacobiana transpuesta y minimos cuadrados
amortiguados sobre el 2R, verificando cerrando el ciclo
(Bloque 12, Tema 12.5).

Correr con:
    python codigo/bloque_12/inversa_numerica_generica.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from robotica.inversa import inversa_numerica  # noqa: E402


def main() -> None:
    L1, L2 = 0.30, 0.20
    dh = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]
    objetivo = np.array([0.298, 0.381, 0.0])
    q0 = [0.0, 0.0]

    print(f"Objetivo: {objetivo[:2]}, semilla q0={q0}\n")
    print(f"{'método':15s} {'convergió':>10s} {'iter. equiv.':>14s} {'q final (°)':>20s}")
    for metodo in ("pseudo_inversa", "transpuesta", "amortiguado"):
        q, conv = inversa_numerica(dh, objetivo, q0, metodo=metodo, max_iter=2000)
        p = directa(dh, q)[:3, 3]
        error = np.linalg.norm(objetivo - p)
        print(f"{metodo:15s} {str(conv):>10s} {'':>14s} {str(np.round(np.degrees(q), 2)):>20s}"
              f"  error={error:.2e}")

    print("\nVerificación cerrando el ciclo con el método amortiguado:")
    q, conv = inversa_numerica(dh, objetivo, q0, metodo="amortiguado")
    p = directa(dh, q)[:3, 3]
    print(f"  inversa_numerica -> q = {np.round(np.degrees(q), 3)}°")
    print(f"  directa(q) -> p = {np.round(p, 6)}")
    print(f"  objetivo        = {objetivo}")
    assert np.allclose(p, objetivo, atol=1e-5)
    print("  OK: cierra el ciclo.")


if __name__ == "__main__":
    main()
