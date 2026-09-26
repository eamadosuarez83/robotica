"""Deduce con SymPy el tensor de inercia de un eslabon (prisma
homogeneo) y verifica con Steiner (Bloque 06, Temas 6.3 y 6.4).

Mismo calculo que robotica-manipuladores/python/notebooks/09_tensor_de_inercia.ipynb
(ver docs/integracion_manipuladores.md), hecho aqui desde cero para
este bloque.

Correr con:
    python codigo/bloque_06/tensor_inercia_eslabon.py
"""

import numpy as np
import sympy as sp


def tensor_inercia_prisma_simbolico():
    """Tensor de inercia de un prisma homogeneo respecto a su centro,
    con ejes alineados a sus lados (ancho w, alto h, largo d)."""
    x, y, z = sp.symbols('x y z')
    w, h, d, m = sp.symbols('w h d m', positive=True)
    V = w * h * d
    rho = m / V

    # Origen en una esquina; se integra y se traslada al centro al final
    # con Steiner (mas simple que centrar los limites de integracion).
    Ixx = sp.integrate(rho * (y**2 + z**2), (x, 0, w), (y, 0, h), (z, 0, d))
    Iyy = sp.integrate(rho * (x**2 + z**2), (x, 0, w), (y, 0, h), (z, 0, d))
    Izz = sp.integrate(rho * (x**2 + y**2), (x, 0, w), (y, 0, h), (z, 0, d))
    Ixy = sp.integrate(rho * x * y, (x, 0, w), (y, 0, h), (z, 0, d))
    Ixz = sp.integrate(rho * x * z, (x, 0, w), (y, 0, h), (z, 0, d))
    Iyz = sp.integrate(rho * y * z, (x, 0, w), (y, 0, h), (z, 0, d))

    I_esquina = sp.Matrix([[Ixx, -Ixy, -Ixz],
                            [-Ixy, Iyy, -Iyz],
                            [-Ixz, -Iyz, Izz]])

    # Steiner en forma matricial para trasladar del origen (esquina) al
    # centro de masa, en (w/2, h/2, d/2):
    r = sp.Matrix([w / 2, h / 2, d / 2])
    I_steiner_resta = m * (r.dot(r) * sp.eye(3) - r * r.T)
    I_cm = sp.simplify(I_esquina - I_steiner_resta)

    return I_cm, (w, h, d, m)


def main() -> None:
    I_cm_sym, (w, h, d, m) = tensor_inercia_prisma_simbolico()
    print("Tensor de inercia respecto al centro de masa (simbólico):")
    sp.pprint(I_cm_sym)

    # Valores numéricos: eslabón de 3x2x30 cm, 0.3 kg
    valores = {w: 0.03, h: 0.02, d: 0.30, m: 0.3}
    I_cm = np.array(I_cm_sym.subs(valores), dtype=float)
    print("\nTensor numérico (w=3cm, h=2cm, d=30cm, m=0.3kg):")
    print(I_cm)

    # Verificación B1 del Tema 6.4: I respecto al eje paralelo a d,
    # por el centro, es (1/12) m (w^2+h^2)
    I_dd_esperado = (1 / 12) * 0.3 * (0.03**2 + 0.02**2)
    print(f"\nI_dd (eje largo) calculado: {I_cm[2,2]:.6e}")
    print(f"I_dd esperado (1/12 m(w²+h²)): {I_dd_esperado:.6e}")
    assert abs(I_cm[2, 2] - I_dd_esperado) < 1e-9

    print("\n¿Es diagonal (ejes principales = ejes del prisma)?",
          np.allclose(I_cm - np.diag(np.diag(I_cm)), 0))

    valores_propios, ejes_principales = np.linalg.eigh(I_cm)
    print("Valores propios (momentos de inercia principales):", valores_propios)


if __name__ == "__main__":
    main()
