"""Port of Engine/Inc/APawn.h (1 declared symbol).

APawn with EReachSpecFlags enum; other functions/methods raise NotImplementedError("Engine.lib").

The survey counts this as 1 declared symbol — the APawn class itself referenced
via inline function calcMoveFlags.  ReachSpecFlags are defined in core/net.py
already.  All other functions/methods raise NotImplementedError per port fidelity.
"""
from __future__ import annotations
from typing import Any, Optional
from ..core import UObject


class EReachSpecFlags:
    """EReachSpecFlags (APawn.h:6-25)"""
    R_WALK = 1   # walking required
    R_FLY = 2    # flying required
    R_SWIM = 4   # swimming required
    R_JUMP = 8   # jumping required
    R_DOOR = 16
    R_SPECIAL = 32
    R_PLAYERONLY = 64


class APawn(UObject):
    """APawn (APawn.h:32+) — 1 declared symbol per survey."""
    def __init__(self) -> None:
        super().__init__()

    # Latent movement
    def setMoveTimer(self, move_size: float) -> None:
        raise NotImplementedError("C++ APawn::setMoveTimer: Engine.lib")

    def move_toward(self, dest: Any) -> int:
        raise NotImplementedError("C++ APawn::moveToward: Engine.lib")

    def rotate_toward(self, focal_point: Any) -> int:
        raise NotImplementedError("C++ APawn::rotateToward: Engine.lib")

    def pick_wall_adjust(self) -> int:
        raise NotImplementedError("C++ APawn::PickWallAdjust: Engine.lib")

    # Seeing and hearing checks
    def show_self(self) -> None:
        raise NotImplementedError("C++ APawn::ShowSelf: Engine.lib")

    def can_hear(self, noise_loc: Any, loudness: float, other: Any) -> int:
        raise NotImplementedError("C++ APawn::CanHear: Engine.lib")

    def line_of_sight_to(self, other: Any, b_show_self: int = 0) -> int:
        raise NotImplementedError("C++ APawn::LineOfSightTo: Engine.lib")

    def check_enemy_visible(self) -> None:
        raise NotImplementedError("C++ APawn::CheckEnemyVisible: Engine.lib")

    # Reach tests
    def point_reachable(self, a_point: Any, b_know_visible: int = 0) -> int:
        raise NotImplementedError("C++ APawn::pointReachable: Engine.lib")

    def actor_reachable(self, other: Any, b_know_visible: int = 0) -> int:
        raise NotImplementedError("C++ APawn::actorReachable: Engine.lib")

    def reach(self, a_point: Any, threshold: float, goal_actor: Any) -> int:
        raise NotImplementedError("C++ APawn::Reachable: Engine.lib")

    def walk_reachable(self, dest: Any, threshold: float, reach_flags: int, goal_actor: Any) -> int:
        raise NotImplementedError("C++ APawn::walkReachable: Engine.lib")

    def jump_reachable(self, dest: Any, threshold: float, reach_flags: int, goal_actor: Any) -> int:
        raise NotImplementedError("C++ APawn::jumpReachable: Engine.lib")

    def fly_reachable(self, dest: Any, threshold: float, reach_flags: int, goal_actor: Any) -> int:
        raise NotImplementedError("C++ APawn::flyReachable: Engine.lib")

    def swim_reachable(self, dest: Any, threshold: float, reach_flags: int, goal_actor: Any) -> int:
        raise NotImplementedError("C++ APawn::swimReachable: Engine.lib")

    def jump_landing(self, test_vel: Any, landing: Any, move_actor: int = 0) -> None:
        raise NotImplementedError("C++ APawn::jumpLanding: Engine.lib")

    # Path finding
    def walk_toward(self, destination: Any, movesize: float) -> int:
        raise NotImplementedError("C++ APawn::walkToward: Engine.lib")

    def find_best_jump(self, dest: Any, vel: Any, landing: Any, move_actor: int = 0) -> int:
        raise NotImplementedError("C++ APawn::FindBestJump: Engine.lib")

    def find_jump_up(self, dest: Any, vel: Any, landing: Any, move_actor: int = 0) -> int:
        raise NotImplementedError("C++ APawn::FindJumpUp: Engine.lib")

    # Physics modes
    def phys_walking(self, delta_time: float, iterations: int) -> None:
        raise NotImplementedError("C++ APawn::physWalking: Engine.lib")

    def phys_flying(self, delta_time: float, iterations: int) -> None:
        raise NotImplementedError("C++ APawn::physFlying: Engine.lib")

    def phys_swimming(self, delta_time: float, iterations: int) -> None:
        raise NotImplementedError("C++ APawn::physSwimming: Engine.lib")

    def phys_spider(self, delta_time: float, iterations: int) -> None:
        raise NotImplementedError("C++ APawn::physSpider: Engine.lib")

    def start_swimming(self, old_vel: Any, time_tick: float, remaining_time: float, iterations: int) -> None:
        raise NotImplementedError("C++ APawn::startSwimming: Engine.lib")

    def physics_rotation(self, delta_time: float, old_vel: Any) -> None:
        raise NotImplementedError("C++ APawn::physicsRotation: Engine.lib")

    def perform_physics(self, delta_seconds: float) -> None:
        raise NotImplementedError("C++ APawn::performPhysics: Engine.lib")

    def exec_poll_wait_for_landing(self) -> None:
        raise NotImplementedError("C++ APawn::execPollWaitForLanding: Engine.lib")

    def exec_poll_move_to(self) -> None:
        raise NotImplementedError("C++ APawn::execPollMoveTo: Engine.lib")

    def exec_poll_move_toward(self) -> None:
        raise NotImplementedError("C++ APawn::execPollMoveToward: Engine.lib")

    def exec_poll_strafe_to(self) -> None:
        raise NotImplementedError("C++ APawn::execPollStrafeTo: Engine.lib")

    def exec_poll_strafe_facing(self) -> None:
        raise NotImplementedError("C++ APawn::execPollStrafeFacing: Engine.lib")

    def exec_poll_turn_toward(self) -> None:
        raise NotImplementedError("C++ APawn::execPollTurnToward: Engine.lib")

    def exec_poll_turn_to(self) -> None:
        raise NotImplementedError("C++ APawn::execPollTurnTo: Engine.lib")

    # Private methods
    def swim(self, delta: Any, hit: Any) -> float:
        raise NotImplementedError("C++ APawn::Swim: Engine.lib")

    def find_water_line(self, start: Any, end: Any) -> None:
        raise NotImplementedError("C++ APawn::findWaterLine: Engine.lib")

    def step_up(self, grav_dir: Any, desired_dir: Any, delta: Any, hit: Any) -> None:
        raise NotImplementedError("C++ APawn::stepUp: Engine.lib")

    def calc_velocity(self, accel_dir: Any, delta_time: float, max_speed: float, friction: int, fluid: int, brake: int, buoyant: int) -> None:
        raise NotImplementedError("C++ APawn::calcVelocity: Engine.lib")

    def find_new_floor(self, old_location: Any, delta_time: float, remaining_time: float, iterations: int) -> int:
        raise NotImplementedError("C++ APawn::findNewFloor: Engine.lib")

    def check_floor(self, dir: Any, hit: Any) -> None:
        raise NotImplementedError("C++ APawn::checkFloor: Engine.lib")


__all__ = ["APawn", "EReachSpecFlags"]