"""Control PID discreto (Bloque 18).

Original de este curso: robotica-manipuladores no tiene control.
"""

from __future__ import annotations

import numpy as np

__all__ = ["PID"]


class PID:
    """Controlador PID discreto, con anti-windup por integración
    condicional (Tema 18.4) y derivada sobre la medición, con filtro
    de paso bajo opcional (Tema 18.5).

    Parámetros
    ----------
    Kp, Ki, Kd : ganancias proporcional, integral y derivativa.
    Ts : periodo de muestreo (s), Bloque 18 Tema 18.6.
    u_min, u_max : límites de saturación del actuador (Tema 16.1).
    N_filtro : si se da, frecuencia de corte (rad/s) del filtro de
        paso bajo de primer orden aplicado a la derivada; si es None,
        la derivada no se filtra.
    """

    def __init__(self, Kp: float, Ki: float, Kd: float, Ts: float,
                 u_min: float = -np.inf, u_max: float = np.inf,
                 N_filtro: float | None = None):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.Ts = Ts
        self.u_min, self.u_max = u_min, u_max
        self.N_filtro = N_filtro
        self.reset()

    def reset(self) -> None:
        """Reinicia el estado interno (integral, derivada, memoria)."""
        self.integral = 0.0
        self.medicion_anterior: float | None = None
        self.derivada_filtrada = 0.0

    def actualizar(self, referencia: float, medicion: float) -> float:
        """Un paso de control: devuelve la acción u (por ejemplo, un par o un voltaje)."""
        error = referencia - medicion

        if self.medicion_anterior is None:
            d_medicion = 0.0
        else:
            d_medicion = (medicion - self.medicion_anterior) / self.Ts
        self.medicion_anterior = medicion

        if self.N_filtro is not None:
            alfa = self.Ts * self.N_filtro / (1 + self.Ts * self.N_filtro)
            self.derivada_filtrada += alfa * (d_medicion - self.derivada_filtrada)
            termino_d = -self.Kd * self.derivada_filtrada
        else:
            termino_d = -self.Kd * d_medicion

        u_sin_saturar = self.Kp * error + self.Ki * self.integral + termino_d
        u = float(np.clip(u_sin_saturar, self.u_min, self.u_max))

        # Anti-windup por integración condicional (Tema 18.4): no
        # acumular más integral si ya está saturado empujando en el
        # mismo sentido que seguiría empujando el error.
        saturado_arriba = u_sin_saturar > self.u_max and error > 0
        saturado_abajo = u_sin_saturar < self.u_min and error < 0
        if not (saturado_arriba or saturado_abajo):
            self.integral += error * self.Ts

        return u
