"""Control PID discreto de una articulación (Bloque 18).

Original de este curso: robotica-manipuladores no tiene control.

La clase `PID` está escrita para portarse línea por línea a C
(`codigo/bloque_18/pid.c`): solo sumas, productos y comparaciones,
sin NumPy dentro de `paso`. No depende de python-control; ese se usa
en los laboratorios para comparar.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .simular import rk4

__all__ = [
    "PID", "ziegler_nichols", "pid_por_polos", "pd_por_polos",
    "simular_lazo",
]


class PID:
    """Controlador PID discreto con saturación, anti-windup y derivada filtrada.

    Parámetros
    ----------
    kp, ki, kd : ganancias proporcional [u/rad], integral [u/(rad·s)]
        y derivativa [u·s/rad], donde `u` es la unidad de la salida
        (voltios en los ejemplos del curso).
    ts : periodo de muestreo [s].
    u_min, u_max : límites del actuador. La salida nunca sale de ahí.
    anti_windup : si es True, la integral deja de acumular mientras la
        salida está saturada y el error empuja hacia afuera del límite
        (integración condicional, Tema 18.4).
    derivada_de : "medicion" (por defecto) deriva -y; "error" deriva
        e = r - y y produce la patada derivativa ante un escalón (Tema 18.5).
    tf : constante de tiempo del filtro de primer orden de la derivada
        [s]. 0 = sin filtro.

    La derivada filtrada es kd·s/(tf·s + 1) discretizada con Euler
    hacia atrás; la integral también es Euler hacia atrás (Tema 18.6).
    """

    def __init__(self, kp: float, ki: float = 0.0, kd: float = 0.0, *,
                 ts: float, u_min: float = -np.inf, u_max: float = np.inf,
                 anti_windup: bool = True, derivada_de: str = "medicion",
                 tf: float = 0.0):
        if ts <= 0:
            raise ValueError("ts debe ser positivo")
        if derivada_de not in ("medicion", "error"):
            raise ValueError("derivada_de debe ser 'medicion' o 'error'")
        self.kp, self.ki, self.kd = kp, ki, kd
        self.ts = ts
        self.u_min, self.u_max = u_min, u_max
        self.anti_windup = anti_windup
        self.derivada_de = derivada_de
        self.tf = tf
        self.reiniciar()

    def reiniciar(self) -> None:
        """Borra la memoria: integral, derivada y la señal anterior."""
        self.integral = 0.0
        self.derivada = 0.0
        self.anterior = None   # y (o e) del paso anterior

    def paso(self, referencia: float, medicion: float) -> float:
        """Calcula la salida del controlador para una muestra."""
        e = referencia - medicion

        # Derivada filtrada. En la primera muestra no hay pasado: D = 0.
        senal = -medicion if self.derivada_de == "medicion" else e
        if self.anterior is not None:
            a = self.tf / (self.tf + self.ts)
            self.derivada = (a * self.derivada
                             + self.kd / (self.tf + self.ts) * (senal - self.anterior))
        self.anterior = senal

        # Integral candidata (Euler hacia atrás) y salida sin saturar.
        integral_nueva = self.integral + self.ki * self.ts * e
        u = self.kp * e + integral_nueva + self.derivada

        # Saturación y anti-windup por integración condicional.
        if u > self.u_max:
            if not (self.anti_windup and e > 0):
                self.integral = integral_nueva
            u = self.u_max
        elif u < self.u_min:
            if not (self.anti_windup and e < 0):
                self.integral = integral_nueva
            u = self.u_min
        else:
            self.integral = integral_nueva
        return u


def ziegler_nichols(ku: float, tu: float) -> tuple[float, float, float]:
    """Ganancias PID por Ziegler-Nichols en lazo cerrado (tabla clásica).

    `ku`: ganancia proporcional con la que el lazo oscila sin decaer.
    `tu`: periodo de esa oscilación [s].
    Devuelve (kp, ki, kd) con kp = 0.6 ku, Ti = tu/2, Td = tu/8.
    """
    kp = 0.6 * ku
    ti, td = tu / 2, tu / 8
    return kp, kp / ti, kp * td


def pd_por_polos(J: float, b: float, K: float, wn: float,
                 zeta: float) -> tuple[float, float]:
    """Ganancias PD para la planta K / (s (J s + b)).

    Iguala J s² + (b + K kd) s + K kp  con  J (s² + 2 ζ ωn s + ωn²).
    Devuelve (kp, kd).
    """
    kp = J * wn**2 / K
    kd = (2 * zeta * wn * J - b) / K
    return kp, kd


def pid_por_polos(J: float, b: float, K: float, wn: float, zeta: float,
                  p: float) -> tuple[float, float, float]:
    """Ganancias PID para la planta K / (s (J s + b)).

    Iguala  J s³ + (b + K kd) s² + K kp s + K ki
    con     J (s² + 2 ζ ωn s + ωn²)(s + p).
    Devuelve (kp, ki, kd).
    """
    kd = (J * (2 * zeta * wn + p) - b) / K
    kp = J * (wn**2 + 2 * zeta * wn * p) / K
    ki = J * wn**2 * p / K
    return kp, ki, kd


def simular_lazo(f: Callable, controlador, referencia: Callable, x0,
                 t_final: float, subpasos: int = 10):
    """Simula una planta continua controlada por un controlador discreto.

    `f(x, u)`: devuelve dx/dt de la planta; la medición es x[0].
    `controlador`: objeto con `.ts` y `.paso(r, y)` (por ejemplo, `PID`).
    `referencia(t)`: la referencia en el instante t.
    Entre muestras, u se mantiene constante (retenedor de orden cero) y
    la planta se integra con RK4 (Bloque 05) en `subpasos` pasos.

    Devuelve (t, X, U): instantes de muestreo, estados (len(t), n) y
    la acción aplicada en cada muestra.
    """
    ts = controlador.ts
    n = int(round(t_final / ts))
    t = np.arange(n + 1) * ts
    x = np.atleast_1d(np.asarray(x0, dtype=float))
    X = np.zeros((n + 1, x.size))
    U = np.zeros(n + 1)
    X[0] = x
    tramo = np.linspace(0.0, ts, subpasos + 1)
    for k in range(n):
        u = controlador.paso(referencia(t[k]), X[k, 0])
        U[k] = u
        X[k + 1] = rk4(lambda _t, z: f(z, u), X[k], tramo)[-1]
    U[n] = U[n - 1]
    return t, X, U
