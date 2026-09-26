"""Verifica el URDF del proyecto (prototipo_4gdl) en PyBullet contra
robotica.dh.directa, cerrando el Entregable 4 (Bloque 24).

Correr con:
    python codigo/bloque_24/verificar_pybullet_proyecto.py
"""

import sys
from pathlib import Path

import numpy as np
import pybullet as p

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from modelo_proyecto import DH  # noqa: E402


def posicion_pybullet(cid, robot_id, q):
    n = p.getNumJoints(robot_id, physicsClientId=cid)
    idx_joints = [i for i in range(n)
                  if p.getJointInfo(robot_id, i, physicsClientId=cid)[2] == p.JOINT_REVOLUTE]
    for idx, qi in zip(idx_joints, q):
        p.resetJointState(robot_id, idx, qi, physicsClientId=cid)
    estado = p.getLinkState(robot_id, n - 1, physicsClientId=cid)
    return np.array(estado[0])


def main() -> None:
    cid = p.connect(p.DIRECT)
    urdf_path = str(Path(__file__).parent / "prototipo_4gdl.urdf")
    robot_id = p.loadURDF(urdf_path, physicsClientId=cid, useFixedBase=True)

    rng = np.random.default_rng(4)
    max_err = 0.0
    for _ in range(15):
        q = rng.uniform(-np.pi / 2, np.pi / 2, 4)
        p_propia = directa(DH, q)[:3, 3]
        p_pb = posicion_pybullet(cid, robot_id, q)
        err = np.linalg.norm(p_propia - p_pb)
        max_err = max(max_err, err)

    print(f"Error máximo propia vs. PyBullet (15 posturas aleatorias): {max_err:.2e} m")
    assert max_err < 1e-6
    print("OK: el URDF generado reproduce la cinemática de robotica.dh.")
    p.disconnect(cid)


if __name__ == "__main__":
    main()
