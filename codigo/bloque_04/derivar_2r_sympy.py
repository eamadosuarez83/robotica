"""Deriva simbolicamente la posicion del brazo 2R con SymPy y verifica
la velocidad de la punta con diferencias finitas en NumPy.

Bloque 04, Temas 4.3 y 4.4. Correr con:
    python codigo/bloque_04/derivar_2r_sympy.py
"""

import numpy as np
import sympy as sp


def deducir_simbolico():
    t = sp.symbols('t')
    L1, L2 = sp.symbols('L1 L2', positive=True)
    theta1 = sp.Function('theta1')(t)
    theta2 = sp.Function('theta2')(t)

    x = L1 * sp.cos(theta1) + L2 * sp.cos(theta1 + theta2)
    y = L1 * sp.sin(theta1) + L2 * sp.sin(theta1 + theta2)

    dx_dtheta1 = sp.diff(x, theta1)
    dx_dtheta2 = sp.diff(x, theta2)
    dy_dtheta1 = sp.diff(y, theta1)
    dy_dtheta2 = sp.diff(y, theta2)

    print("=== Derivadas parciales (Tema 4.3) ===")
    print("∂x/∂θ1 =", dx_dtheta1)
    print("∂x/∂θ2 =", dx_dtheta2)
    print("∂y/∂θ1 =", dy_dtheta1)
    print("∂y/∂θ2 =", dy_dtheta2)

    # Regla de la cadena: dx/dt y dy/dt con theta1(t), theta2(t)
    dx_dt = sp.diff(x, t)
    dy_dt = sp.diff(y, t)

    print("\n=== Velocidad de la punta, regla de la cadena (Tema 4.4) ===")
    print("dx/dt =", dx_dt)
    print("dy/dt =", dy_dt)

    return x, y, dx_dt, dy_dt, theta1, theta2, t, L1, L2


def verificar_numericamente(dx_dt, dy_dt, theta1, theta2, t, L1, L2):
    """Sustituye valores numéricos y compara con diferencias finitas."""
    theta1_dot, theta2_dot = sp.symbols('theta1_dot theta2_dot')
    subs_deriv = {
        sp.diff(theta1, t): theta1_dot,
        sp.diff(theta2, t): theta2_dot,
    }
    subs_valores = {
        theta1: sp.rad(40), theta2: sp.rad(30),
        theta1_dot: 1.0, theta2_dot: 0.5,
        L1: 0.30, L2: 0.20,
    }

    dx_analitica = float(dx_dt.subs(subs_deriv).subs(subs_valores))
    dy_analitica = float(dy_dt.subs(subs_deriv).subs(subs_valores))

    print(f"\nVelocidad analítica en θ1=40°,θ2=30°, "
          f"θ1'=1 rad/s, θ2'=0.5 rad/s:")
    print(f"  dx/dt = {dx_analitica:.4f} m/s")
    print(f"  dy/dt = {dy_analitica:.4f} m/s")

    # Diferencias finitas: mover theta1, theta2 un pasito según sus
    # velocidades y comparar (x(t+h)-x(t))/h con NumPy puro.
    def punta(t1, t2, L1v=0.30, L2v=0.20):
        x = L1v * np.cos(t1) + L2v * np.cos(t1 + t2)
        y = L1v * np.sin(t1) + L2v * np.sin(t1 + t2)
        return x, y

    t1_0, t2_0 = np.radians(40), np.radians(30)
    t1_dot, t2_dot = 1.0, 0.5
    h = 1e-6

    x0, y0 = punta(t1_0, t2_0)
    x1, y1 = punta(t1_0 + t1_dot * h, t2_0 + t2_dot * h)

    dx_numerica = (x1 - x0) / h
    dy_numerica = (y1 - y0) / h

    print(f"\nVelocidad por diferencias finitas (h={h}):")
    print(f"  dx/dt = {dx_numerica:.4f} m/s")
    print(f"  dy/dt = {dy_numerica:.4f} m/s")

    assert abs(dx_analitica - dx_numerica) < 1e-4
    assert abs(dy_analitica - dy_numerica) < 1e-4
    print("\nOK: la derivada simbólica coincide con las diferencias finitas.")


if __name__ == "__main__":
    x, y, dx_dt, dy_dt, theta1, theta2, t, L1, L2 = deducir_simbolico()
    verificar_numericamente(dx_dt, dy_dt, theta1, theta2, t, L1, L2)
