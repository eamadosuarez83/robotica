"""Clase Brazo: guarda la tabla DH de un robot (Bloque 11).

Version minima del catalogo `robots.py` de robotica-manipuladores,
para robots de ejemplo propios de este curso.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .dh import directa, marcos

__all__ = ["Brazo"]


@dataclass(frozen=True)
class Brazo:
    """Un manipulador descrito por su tabla DH.

    `dh`: array (n, 5), filas [theta, d, a, alpha, tipo] (Bloque 11).
    `limites_grados`: array (n, 2) opcional, [mínimo, máximo] por articulación.
    """

    nombre: str
    dh: np.ndarray
    limites_grados: np.ndarray | None = None

    @property
    def gdl(self) -> int:
        """Grados de libertad (filas de la tabla DH)."""
        return self.dh.shape[0]

    def directa(self, q) -> np.ndarray:
        """Cinemática directa (Bloque 11): T = A01 @ ... @ A(n-1)n, q en radianes."""
        return directa(self.dh, q)

    def marcos(self, q) -> list[np.ndarray]:
        """Lista de marcos [A00, ..., A0n] para dibujar el brazo completo."""
        return marcos(self.dh, q)

    def dentro_de_limites(self, q_grados) -> bool:
        """True si q_grados respeta los límites articulares (si los hay)."""
        if self.limites_grados is None:
            return True
        q = np.asarray(q_grados, dtype=float)
        return bool(np.all(q >= self.limites_grados[:, 0] - 1e-9) and
                    np.all(q <= self.limites_grados[:, 1] + 1e-9))
