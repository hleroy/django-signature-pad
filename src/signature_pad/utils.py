import base64
import math
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
    pressure: float = 0
    time: int = 0

    def distance_to(self, start: "Point") -> float:
        return math.sqrt(math.pow(self.x - start.x, 2) + math.pow(self.y - start.y, 2))

    def velocity_from(self, start: "Point") -> float:
        return self.distance_to(start) / (self.time - start.time) if self.time != start.time else 0


class Bezier:
    def __init__(
        self,
        start_point: Point,
        control2: Point,
        control1: Point,
        end_point: Point,
        start_width: float,
        end_width: float,
    ):
        self.start_point = start_point
        self.control2 = control2
        self.control1 = control1
        self.end_point = end_point
        self.start_width = start_width
        self.end_width = end_width

    @staticmethod
    def calculate_control_points(s1: Point, s2: Point, s3: Point) -> tuple[Point, Point]:
        dx1 = s1.x - s2.x
        dy1 = s1.y - s2.y
        dx2 = s2.x - s3.x
        dy2 = s2.y - s3.y

        m1 = Point((s1.x + s2.x) / 2.0, (s1.y + s2.y) / 2.0)
        m2 = Point((s2.x + s3.x) / 2.0, (s2.y + s3.y) / 2.0)

        l1 = math.sqrt(dx1 * dx1 + dy1 * dy1)
        l2 = math.sqrt(dx2 * dx2 + dy2 * dy2)

        dxm = m1.x - m2.x
        dym = m1.y - m2.y

        k = l2 / (l1 + l2) if (l1 + l2) != 0 else 0
        cm = Point(m2.x + dxm * k, m2.y + dym * k)

        tx = s2.x - cm.x
        ty = s2.y - cm.y

        return (Point(m1.x + tx, m1.y + ty), Point(m2.x + tx, m2.y + ty))

    @classmethod
    def from_points(cls, points: list[Point], widths: dict[str, float]) -> "Bezier":
        c2, c3 = (
            cls.calculate_control_points(points[0], points[1], points[2])[1],
            cls.calculate_control_points(points[1], points[2], points[3])[0],
        )
        return cls(points[1], c2, c3, points[2], widths["start"], widths["end"])


class SignatureConverter:
    def __init__(self):
        self._last_points: list[Point] = []
        self._last_velocity: float = 0
        self._last_width: float = 0

    def _get_point_group_options(self, group: dict) -> dict:
        return {
            "pen_color": group.get("penColor", "black"),
            "dot_size": group.get("dotSize", 0),
            "min_width": group.get("minWidth", 0.5),
            "max_width": group.get("maxWidth", 2.5),
            "velocity_filter_weight": group.get("velocityFilterWeight", 0.7),
            "composite_operation": group.get("compositeOperation", "source-over"),
        }

    def _reset(self, options: dict) -> None:
        self._last_points = []
        self._last_velocity = 0
        self._last_width = (options["min_width"] + options["max_width"]) / 2

    def _stroke_width(self, velocity: float, options: dict) -> float:
        return max(options["max_width"] / (velocity + 1), options["min_width"])

    def _calculate_curve_widths(self, start_point: Point, end_point: Point, options: dict) -> dict:
        velocity = (
            options["velocity_filter_weight"] * end_point.velocity_from(start_point)
            + (1 - options["velocity_filter_weight"]) * self._last_velocity
        )

        new_width = self._stroke_width(velocity, options)
        widths = {"end": new_width, "start": self._last_width}

        self._last_velocity = velocity
        self._last_width = new_width

        return widths

    def _add_point(self, point: Point, options: dict) -> Bezier | None:
        self._last_points.append(point)

        if len(self._last_points) > 2:
            if len(self._last_points) == 3:
                self._last_points.insert(0, self._last_points[0])

            widths = self._calculate_curve_widths(self._last_points[1], self._last_points[2], options)

            curve = Bezier.from_points(self._last_points, widths)
            self._last_points.pop(0)
            return curve

        return None

    def points_to_svg(self, signature_data: list[dict], width: int = 400, height: int = 200) -> str:
        svg_paths = []

        for group in signature_data:
            points = group["points"]
            options = self._get_point_group_options(group)

            if len(points) > 1:
                for j, point_data in enumerate(points):
                    point = Point(
                        point_data["x"],
                        point_data["y"],
                        point_data.get("pressure", 0.5),
                        point_data["time"],
                    )

                    # Reset at the start of each stroke
                    if j == 0:
                        self._reset(options)

                    curve = self._add_point(point, options)

                    if curve:
                        path = (
                            f'<path d="M {curve.start_point.x:.3f},{curve.start_point.y:.3f} '
                            f"C {curve.control1.x:.3f},{curve.control1.y:.3f} "
                            f"{curve.control2.x:.3f},{curve.control2.y:.3f} "
                            f'{curve.end_point.x:.3f},{curve.end_point.y:.3f}" '
                            f'stroke-width="{(curve.end_width * 2.25):.3f}" '
                            f'stroke="black" fill="none" stroke-linecap="round"></path>'
                        )
                        svg_paths.append(path)
            else:
                # Handle single point (dot)
                self._reset(options)
                if points:
                    point = points[0]
                    dot_size = options.get("dot_size", 0)
                    size = dot_size or ((options["min_width"] + options["max_width"]) / 2)
                    path = f'<circle r="{size}" cx="{point["x"]}" cy="{point["y"]}" fill="black"></circle>'
                    svg_paths.append(path)

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">'
        )
        svg += "".join(svg_paths)
        svg += "</svg>"

        return svg


def signature_to_data_url(signature_data: list[dict], width: int = 400, height: int = 200) -> str:
    converter = SignatureConverter()
    svg_string = converter.points_to_svg(signature_data, width, height)

    svg_bytes = svg_string.encode("utf-8")
    base64_svg = base64.b64encode(svg_bytes).decode("utf-8")

    return f"data:image/svg+xml;base64,{base64_svg}"
