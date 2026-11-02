import pyray as pr
import math


class Drone:
    def __init__(self, name: str, x: int, y: int, index: int) -> None:
        self.name = name
        self.index = index
        self.visual_pos = pr.Vector2(x, y)
        self.propeller_blades = 4
        self.propeller_angle = 180.0
        self.propeller_speed = 5.0
        self.propeller_radius = 8.0

    def update(self) -> None:
        self.propeller_angle = (self.propeller_angle + self.propeller_speed) % 360.0

    def draw_drones(self, cam: pr.Vector2) -> None:
        bob = math.sin(pr.get_time() * 3.0 + self.index) * 3.0
        center = pr.Vector2(self.visual_pos.x + cam.x, self.visual_pos.y + cam.y + bob)
        scale = 1.5
        arm_length = 16.0 * scale
        body_radius = 12.0 * scale

        motor_positions: list[pr.Vector2] = []
        for arm_deg in [45.0, 135.0, 225.0, 315.0]:
            rad = math.radians(arm_deg)
            motor_pos = pr.Vector2(
                center.x + math.cos(rad) * arm_length,
                center.y + math.sin(rad) * arm_length,
            )
            motor_positions.append(motor_pos)
            pr.draw_line_ex(center, motor_pos, 3.0, pr.Color(255, 255, 255, 170))

        blade_color = pr.BEIGE
        prop_r = self.propeller_radius * scale
        angle_step = 360.0 / self.propeller_blades
        for motor_pos in motor_positions:
            pr.draw_circle_v(motor_pos, prop_r, pr.fade(pr.BROWN, 0.1))
            pr.draw_circle_v(motor_pos, 3.5 * scale, pr.Color(170, 220, 255, 255))
            for blade_idx in range(self.propeller_blades):
                blade_rad = math.radians(self.propeller_angle + blade_idx * angle_step)
                blade_end = pr.Vector2(
                    motor_pos.x + math.cos(blade_rad) * prop_r,
                    motor_pos.y + math.sin(blade_rad) * prop_r,
                )
                pr.draw_line_ex(motor_pos, blade_end, 1.8, blade_color)

        pr.draw_circle_v(center, body_radius, pr.Color(170, 220, 255, 255))
        pr.draw_ring(center, body_radius - 2.0, body_radius, 0, 360, 24, pr.WHITE)

        for side in (-1, 1):
            eye = pr.Vector2(center.x + side * 4.5 * scale, center.y - 1.5 * scale)
            pr.draw_circle_v(eye, 2.4 * scale, pr.Color(60, 40, 80, 255))
            pr.draw_circle_v(
                pr.Vector2(eye.x + scale, eye.y - scale), 0.9 * scale, pr.WHITE
            )
        pr.draw_ring(
            pr.Vector2(center.x, center.y + 1.5 * scale),
            2.2 * scale,
            3.4 * scale,
            20,
            160,
            12,
            pr.Color(60, 40, 80, 255),
        )

        label = f"{self.index}"
        pr.draw_text(str(label), int(center.x) - 5, int(center.y) - 40, 15, pr.WHITE)
