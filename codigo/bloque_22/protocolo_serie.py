"""Protocolo serie simple: encabezado + datos + checksum
(Bloque 22, Tema 22.2).

Trama: [255, id_servo, comando, dato, checksum], con
checksum = complemento (mod 256) de la suma de [id_servo, comando, dato].
"""

from __future__ import annotations

ENCABEZADO = 255


def _checksum(cuerpo: bytes) -> int:
    return (~sum(cuerpo)) & 0xFF


def codificar(id_servo: int, comando: int, dato: int) -> bytes:
    """Arma una trama [255, id, comando, dato, checksum]."""
    cuerpo = bytes([id_servo, comando, dato])
    return bytes([ENCABEZADO]) + cuerpo + bytes([_checksum(cuerpo)])


def decodificar(trama: bytes) -> tuple[dict | None, str | None]:
    """Decodifica una trama; devuelve (mensaje, None) o (None, error)."""
    if len(trama) != 5:
        return None, "longitud inválida"
    if trama[0] != ENCABEZADO:
        return None, "encabezado inválido"
    cuerpo = trama[1:4]
    if _checksum(cuerpo) != trama[4]:
        return None, "checksum inválido"
    return {"id": trama[1], "comando": trama[2], "dato": trama[3]}, None


if __name__ == "__main__":
    trama = codificar(id_servo=2, comando=240, dato=90)
    print(f"Trama codificada: {list(trama)}")
    mensaje, error = decodificar(trama)
    print(f"Decodificada: {mensaje}, error={error}")
    assert mensaje == {"id": 2, "comando": 240, "dato": 90}

    # Ejercicio B1: checksum a mano de [2, 240, 90]
    esperado = (~(2 + 240 + 90)) & 0xFF
    print(f"Checksum esperado (Ejercicio B1): {esperado}, obtenido: {trama[4]}")
    assert esperado == trama[4]

    print("\n=== Romper a propósito: corromper un bit de cada byte de datos ===")
    for i in range(1, 4):
        trama_corrupta = bytearray(trama)
        trama_corrupta[i] ^= 0x01   # invierte el bit menos significativo
        _, error = decodificar(bytes(trama_corrupta))
        print(f"  byte {i} corrompido -> {error!r} (se rechaza, no se ejecuta)")
        assert error is not None

    print("\nOK: la trama válida se acepta y toda trama corrompida se rechaza.")
