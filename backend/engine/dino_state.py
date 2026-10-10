"""
State representation and candidate action generation for Cyber-Dino AI models.
Computes obstacle timing projections, kinematic jump windows,
ducking requirements, and ASCII multi-lane telemetry.
"""

from typing import Dict, Any, List, Optional
from backend.engine.dino_engine import DinoGame, DinoObstacle


def build_dino_state(game: DinoGame) -> Dict[str, Any]:
    speed = game.speed
    dino_x = game.DINO_X
    dino_w = game.DUCK_WIDTH if game.is_ducking else game.STAND_WIDTH
    dino_right = dino_x + dino_w
    dino_y = game.y
    is_grounded = (dino_y == 0.0 and not game.is_jumping)

    # Sort upcoming obstacles by distance from dino's front
    upcoming = [obs for obs in game.obstacles if (obs.x + obs.width) > dino_x]
    upcoming.sort(key=lambda o: o.x)

    immediate: Optional[DinoObstacle] = upcoming[0] if upcoming else None
    trailing: Optional[DinoObstacle] = upcoming[1] if len(upcoming) > 1 else None

    # Kinematic jump calculations
    t_hang_ticks = (2.0 * game.JUMP_VELOCITY) / game.GRAVITY  # ~35.4 frames
    apex_height = (game.JUMP_VELOCITY ** 2) / (2.0 * game.GRAVITY)  # ~101.7 px
    jump_travel_px = speed * t_hang_ticks

    # Distance to immediate obstacle
    dist_to_imm = (immediate.x - dino_right) if immediate else 9999.0
    imm_time_ticks = max(0.0, dist_to_imm / speed) if speed > 0 else 999.0

    # Determine recommended / safe actions
    candidates = ["RUN", "JUMP", "DUCK"]
    criteria: Dict[str, str] = {}
    optimal_action = "RUN"

    # Evaluate threat
    if immediate:
        imm_type = immediate.type
        # Optimal takeoff window for ground cactus / low ptero:
        # Distance between 50px and 120px (approx 8 to 16 ticks before impact)
        takeoff_min = speed * 6.0
        takeoff_max = speed * 15.0

        if "cactus" in imm_type or imm_type == "ptero_low":
            if is_grounded and (takeoff_min <= dist_to_imm <= takeoff_max):
                optimal_action = "JUMP"
            elif dist_to_imm < takeoff_min and is_grounded:
                optimal_action = "JUMP"  # Emergency late jump
        elif imm_type == "ptero_mid":
            # Head-height flying drone: Must duck!
            if dist_to_imm <= (speed * 18.0) and (immediate.x + immediate.width) >= dino_x:
                optimal_action = "DUCK"
        elif imm_type == "ptero_high":
            # High altitude drone: Safe to run or duck, NEVER jump into it!
            optimal_action = "RUN"
    else:
        imm_type = "none"

    # Human-readable criteria descriptions
    if immediate:
        criteria["RUN"] = (
            f"Maintain running stride. Safe if no ground hazard. Current hazard: {immediate.type} at {int(dist_to_imm)}px."
        )
        criteria["JUMP"] = (
            f"Execute jump (apex {int(apex_height)}px, hangtime {int(t_hang_ticks)}f). "
            f"Takeoff window: [{int(speed*6)}px - {int(speed*15)}px]. Current dist: {int(dist_to_imm)}px."
        )
        criteria["DUCK"] = (
            f"Crouch profile (height 26px). Necessary for mid-air drones (y=42px). Fast-drops if airborne."
        )
    else:
        criteria["RUN"] = "Maintain running stride. No incoming obstacles detected within radar range."
        criteria["JUMP"] = "Jump into empty air. (Unnecessary hazard risk)."
        criteria["DUCK"] = "Crouch on clear ground. (Unnecessary deceleration risk)."

    # Build ASCII horizontal lane visualization
    # Lane width 50 characters, scale: 1 char = 12 pixels
    lane_len = 50
    lane_scale = 12.0
    sky_lane = [" "] * lane_len
    mid_lane = [" "] * lane_len
    ground_lane = ["_"] * lane_len

    # Place dino
    dino_char_pos = int(dino_x / lane_scale)
    if dino_char_pos < lane_len:
        if dino_y > 35:
            sky_lane[dino_char_pos] = "D"
        elif dino_y > 10:
            mid_lane[dino_char_pos] = "D"
        elif game.is_ducking:
            ground_lane[dino_char_pos] = "c"  # crouch
        else:
            ground_lane[dino_char_pos] = "D"  # standing/running dino

    # Place obstacles
    for obs in upcoming:
        char_pos = int(obs.x / lane_scale)
        if 0 <= char_pos < lane_len:
            if obs.type == "ptero_high":
                sky_lane[char_pos] = "P"
            elif obs.type == "ptero_mid":
                mid_lane[char_pos] = "M"
            elif obs.type == "ptero_low":
                mid_lane[char_pos] = "v"
            elif "cactus" in obs.type:
                ground_lane[char_pos] = "C"

    ascii_view = (
        "SKY:    [" + "".join(sky_lane) + "]\n"
        "MID:    [" + "".join(mid_lane) + "]\n"
        "GROUND: [" + "".join(ground_lane) + "]"
    )

    return {
        "speed": round(speed, 2),
        "distance": round(game.distance, 1),
        "score": int(game.distance),
        "obstacles_cleared": game.obstacles_cleared,
        "is_alive": game.is_alive,
        "dino": {
            "x": dino_x,
            "y": round(dino_y, 1),
            "vy": round(game.vy, 2),
            "state": game.state,
            "is_jumping": game.is_jumping,
            "is_ducking": game.is_ducking,
            "is_grounded": is_grounded,
        },
        "immediate_obstacle": immediate.to_dict() if immediate else None,
        "immediate_distance_px": round(dist_to_imm, 1) if immediate else None,
        "immediate_time_ticks": round(imm_time_ticks, 1) if immediate else None,
        "trailing_obstacle": trailing.to_dict() if trailing else None,
        "optimal_action": optimal_action,
        "candidates": candidates,
        "criteria": criteria,
        "ascii_grid": ascii_view,
        "kinematics": {
            "hang_time_frames": round(t_hang_ticks, 1),
            "apex_height_px": round(apex_height, 1),
            "jump_travel_px": round(jump_travel_px, 1),
            "takeoff_min_px": round(speed * 6.0, 1),
            "takeoff_max_px": round(speed * 15.0, 1),
        },
    }
