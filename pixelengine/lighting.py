"""PixelEngine lighting — point lights, directional lights, shadows, and shading."""
import math
from PIL import Image, ImageDraw, ImageFilter
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


# ═══════════════════════════════════════════════════════════
#  Light Sources
# ═══════════════════════════════════════════════════════════

class AmbientLight:
    """Global base illumination applied uniformly to the entire scene.

    Usage::

        ambient = AmbientLight(intensity=0.3, color="#FFFFFF")
        scene.add_light(ambient)

    Args:
        intensity: Light level from 0.0 (pitch black) to 1.0 (full bright).
        color: Tint color for the ambient light.
    """

    def __init__(self, intensity: float = 0.3, color: str = "#FFFFFF"):
        self.intensity = max(0.0, min(1.0, intensity))
        self.color = parse_color(color)
        self.enabled: bool = True


class PointLight(PObject):
    """Radial light source at a world position with falloff.

    Inherits PObject so it can be animated with MoveTo, FadeIn, etc.

    Usage::

        light = PointLight(x=128, y=72, radius=60, color="#FFA300",
                           intensity=1.0, falloff="quadratic")
        scene.add_light(light)
        scene.play(MoveTo(light, 200, 72), duration=2.0)

    Args:
        x, y: World position of the light.
        radius: Maximum reach of the light in pixels.
        color: Light color (tints illuminated objects).
        intensity: Brightness multiplier (0.0–2.0).
        falloff: "linear" or "quadratic" distance attenuation.
    """

    def __init__(self, x: int = 0, y: int = 0, radius: int = 60,
                 color: str = "#FFA300", intensity: float = 1.0,
                 falloff: str = "quadratic"):
        super().__init__(x=x, y=y, color=color)
        self.radius = max(1, radius)
        self.intensity = max(0.0, intensity)
        self.falloff = falloff  # "linear" or "quadratic"
        self.visible = False  # Don't render the light source itself by default

    def get_attenuation(self, dist: float) -> float:
        """Calculate light attenuation at a given distance."""
        if dist >= self.radius:
            return 0.0
        t = dist / self.radius
        if self.falloff == "linear":
            return (1.0 - t) * self.intensity
        else:  # quadratic
            return (1.0 - t * t) * self.intensity

    def render(self, canvas):
        """Optionally render a visible glow dot at the light position."""
        if not self.visible:
            return
        color = self.get_render_color()
        canvas.set_pixel(int(self.x), int(self.y), color)
        # Small cross for visibility
        for d in range(1, 3):
            canvas.set_pixel(int(self.x) + d, int(self.y), color)
            canvas.set_pixel(int(self.x) - d, int(self.y), color)
            canvas.set_pixel(int(self.x), int(self.y) + d, color)
            canvas.set_pixel(int(self.x), int(self.y) - d, color)


class DirectionalLight:
    """Infinite parallel rays from a direction, simulating sun/moon.

    Usage::

        sun = DirectionalLight(angle=225, intensity=0.6, color="#FFEC27")
        scene.add_light(sun)

    Args:
        angle: Direction the light comes FROM in degrees (0=right, 90=down,
               180=left, 270=up). 225 = light from top-left.
        intensity: Brightness (0.0–1.0).
        color: Light color tint.
    """

    def __init__(self, angle: float = 225, intensity: float = 0.6,
                 color: str = "#FFEC27"):
        self.angle = angle
        self.intensity = max(0.0, min(1.0, intensity))
        self.color = parse_color(color)
        self.enabled: bool = True

    @property
    def direction(self) -> tuple:
        """Unit vector pointing in the light direction."""
        rad = math.radians(self.angle)
        return (math.cos(rad), math.sin(rad))


# ═══════════════════════════════════════════════════════════
#  Shadow Renderer
# ═══════════════════════════════════════════════════════════

class _ShadowRenderer:
    """Computes and renders 2D shadows cast by objects from light sources.

    Shadow algorithm:
    - For PointLights: Each corner of the object's bounding box is projected
      away from the light source individually. The shadow polygon is formed
      by the two silhouette corners (the outermost corners as seen from the
      light) and their projections.
    - For DirectionalLights: All corners are projected along the light's
      direction vector. The shadow is the convex hull of projected edges.
    """

    @staticmethod
    def _get_object_corners(obj: PObject) -> list:
        """Get the 4 bounding-box corners of an object."""
        ox = int(obj.x)
        oy = int(obj.y)
        # For circles, use the bounding box of the circle
        radius = getattr(obj, 'radius', None)
        if radius is not None:
            return [
                (ox, oy),
                (ox + radius * 2, oy),
                (ox + radius * 2, oy + radius * 2),
                (ox, oy + radius * 2),
            ]
        ow = getattr(obj, 'width', 10) or 10
        oh = getattr(obj, 'height', 10) or 10
        return [
            (ox, oy),
            (ox + ow, oy),
            (ox + ow, oy + oh),
            (ox, oy + oh),
        ]

    @staticmethod
    def compute_shadow(obj: PObject, light, canvas_w: int, canvas_h: int) -> list:
        """Compute shadow polygon vertices for an object.

        Returns a list of (x, y) tuples forming the shadow polygon.
        """
        if not getattr(obj, 'casts_shadow', False):
            return []

        corners = _ShadowRenderer._get_object_corners(obj)

        if isinstance(light, PointLight):
            lx, ly = float(light.x), float(light.y)

            # Project each corner individually away from the light
            projected = []
            for cx, cy in corners:
                dx = cx - lx
                dy = cy - ly
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 0.5:
                    continue  # Corner is at the light position

                # Shadow length: closer to light = longer shadow
                # Ranges from shadow_max (close) to shadow_min (far)
                t = min(1.0, dist / light.radius)
                shadow_len = int(8 + (1.0 - t) * 25)  # 8–33 pixels

                ndx = dx / dist
                ndy = dy / dist
                projected.append((
                    int(cx + ndx * shadow_len),
                    int(cy + ndy * shadow_len),
                ))

            if len(projected) != 4:
                return []

            # Build shadow polygon: connect far corners to their projections
            # Find the two silhouette edges by computing cross products from the
            # light to determine which corners are on the "left" and "right"
            # outline as seen from the light source.
            #
            # Simple approach: sort corners by angle from light, take the two
            # extremes (widest angular spread) as the silhouette boundary.
            angles = []
            for i, (cx, cy) in enumerate(corners):
                angle = math.atan2(cy - ly, cx - lx)
                angles.append((angle, i))
            angles.sort(key=lambda a: a[0])

            # The silhouette is formed by the corners with the widest gap
            # between consecutive sorted angles
            n = len(angles)
            max_gap = -1
            gap_idx = 0
            for i in range(n):
                a1 = angles[i][0]
                a2 = angles[(i + 1) % n][0]
                gap = (a2 - a1) % (2 * math.pi)
                if gap < 0:
                    gap += 2 * math.pi
                if gap > max_gap:
                    max_gap = gap
                    gap_idx = i

            # Corners in angular order, starting after the biggest gap
            ordered_indices = []
            for i in range(n):
                idx = (gap_idx + 1 + i) % n
                ordered_indices.append(angles[idx][1])

            # Shadow polygon: first corner → last corner → last projected →
            # first projected (traversing the silhouette)
            first_idx = ordered_indices[0]
            last_idx = ordered_indices[-1]

            shadow_poly = [
                corners[first_idx],
                corners[last_idx],
                projected[last_idx],
                projected[first_idx],
            ]
            return shadow_poly

        elif isinstance(light, DirectionalLight):
            dx, dy = light.direction
            shadow_len = 15

            # Project all 4 corners along the light direction
            projected = [
                (int(cx + dx * shadow_len), int(cy + dy * shadow_len))
                for cx, cy in corners
            ]

            # The shadow polygon is formed by the two edges of the object
            # that face away from the light and their projections.
            # For simplicity, use the two corners where the light hits last
            # (farthest along the light direction) and project them.
            dot_products = [
                (cx * dx + cy * dy, i)
                for i, (cx, cy) in enumerate(corners)
            ]
            dot_products.sort(key=lambda x: x[0], reverse=True)

            # Take the two farthest corners along light direction
            i1 = dot_products[0][1]
            i2 = dot_products[1][1]

            shadow_poly = [
                corners[i1],
                corners[i2],
                projected[i2],
                projected[i1],
            ]
            return shadow_poly

        return []

    @staticmethod
    def render_shadows(shadow_img: Image.Image, objects: list, lights: list,
                       canvas_w: int, canvas_h: int, shadow_opacity: float = 0.4):
        """Render all shadows onto a shadow image layer."""
        draw = ImageDraw.Draw(shadow_img)

        for light in lights:
            if isinstance(light, AmbientLight):
                continue
            if isinstance(light, PointLight) and light.intensity <= 0:
                continue
            if isinstance(light, DirectionalLight) and not light.enabled:
                continue

            for obj in objects:
                if not getattr(obj, 'casts_shadow', False):
                    continue

                shadow_poly = _ShadowRenderer.compute_shadow(
                    obj, light, canvas_w, canvas_h
                )
                if len(shadow_poly) >= 3:
                    opacity = int(255 * getattr(obj, 'shadow_opacity', shadow_opacity))
                    shadow_color = (0, 0, 0, opacity)
                    draw.polygon(shadow_poly, fill=shadow_color)


# ═══════════════════════════════════════════════════════════
#  Lighting Engine
# ═══════════════════════════════════════════════════════════

class LightingEngine:
    """Composites all lights into a light map and applies it to the canvas.

    The engine works in three passes:
    1. **Shadow pass**: Render shadow shapes from shadow-casting objects
    2. **Light map pass**: Accumulate light contributions into a brightness map
    3. **Composite pass**: Multiply the light map over the canvas

    Usage (internal — called by Scene._capture_frame)::

        engine = LightingEngine()
        engine.apply(canvas, lights, objects)
    """

    def __init__(self):
        self._light_map = None

    def apply(self, canvas, lights: list, objects: list):
        """Apply lighting to the canvas.

        Args:
            canvas: The Canvas to modify.
            lights: List of AmbientLight, PointLight, DirectionalLight.
            objects: List of PObjects in the scene.
        """
        if not lights:
            return

        w, h = canvas.width, canvas.height

        # ── 1. Compute base ambient level ──
        ambient_r, ambient_g, ambient_b = 0.0, 0.0, 0.0
        for light in lights:
            if isinstance(light, AmbientLight) and light.enabled:
                lr, lg, lb = light.color[0] / 255.0, light.color[1] / 255.0, light.color[2] / 255.0
                ambient_r = max(ambient_r, light.intensity * lr)
                ambient_g = max(ambient_g, light.intensity * lg)
                ambient_b = max(ambient_b, light.intensity * lb)

        # ── 2. Build light map ──
        # Start with ambient level
        light_map = Image.new("RGBA", (w, h), (
            int(ambient_r * 255),
            int(ambient_g * 255),
            int(ambient_b * 255),
            255,
        ))
        light_draw = ImageDraw.Draw(light_map)

        # Add point lights as radial gradients
        for light in lights:
            if isinstance(light, PointLight) and light.intensity > 0:
                self._add_point_light(light_map, light, w, h)

            elif isinstance(light, DirectionalLight) and light.enabled:
                self._add_directional_light(light_map, light, w, h)

        # ── 3. Render shadows ──
        shadow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        _ShadowRenderer.render_shadows(shadow_img, objects, lights, w, h)

        # ── 4. Composite ──
        # Apply light map as a multiply blend over the canvas
        self._multiply_blend(canvas, light_map)

        # Apply shadows on top
        canvas.blit(shadow_img, 0, 0)

    def _add_point_light(self, light_map: Image.Image, light: PointLight,
                         w: int, h: int):
        """Add a point light's contribution to the light map."""
        lx, ly = int(light.x), int(light.y)
        lr = light.color[0] / 255.0
        lg = light.color[1] / 255.0
        lb = light.color[2] / 255.0
        r = light.radius

        # Only process pixels within the light's bounding box
        min_x = max(0, lx - r)
        max_x = min(w, lx + r + 1)
        min_y = max(0, ly - r)
        max_y = min(h, ly + r + 1)

        pixels = light_map.load()
        for py in range(min_y, max_y):
            for px in range(min_x, max_x):
                dist = math.sqrt((px - lx) ** 2 + (py - ly) ** 2)
                atten = light.get_attenuation(dist)
                if atten <= 0:
                    continue

                # Additive blend with light color
                existing = pixels[px, py]
                new_r = min(255, int(existing[0] + atten * lr * 255))
                new_g = min(255, int(existing[1] + atten * lg * 255))
                new_b = min(255, int(existing[2] + atten * lb * 255))
                pixels[px, py] = (new_r, new_g, new_b, 255)

    def _add_directional_light(self, light_map: Image.Image,
                                light: DirectionalLight, w: int, h: int):
        """Add directional light as a uniform brightening."""
        lr = int(light.color[0] * light.intensity)
        lg = int(light.color[1] * light.intensity)
        lb = int(light.color[2] * light.intensity)

        overlay = Image.new("RGBA", (w, h), (lr, lg, lb, 255))
        # Additive-style blend: max of each channel
        pixels_map = light_map.load()
        pixels_ov = overlay.load()
        for py in range(h):
            for px in range(w):
                m = pixels_map[px, py]
                o = pixels_ov[px, py]
                pixels_map[px, py] = (
                    min(255, m[0] + o[0]),
                    min(255, m[1] + o[1]),
                    min(255, m[2] + o[2]),
                    255,
                )

    def _multiply_blend(self, canvas, light_map: Image.Image):
        """Multiply-blend the light map over the canvas image.

        Each pixel: result = canvas_pixel * (light_map_pixel / 255)
        This darkens unlit areas and preserves lit areas.
        """
        w, h = canvas.width, canvas.height
        canvas_pixels = canvas._image.load()
        light_pixels = light_map.load()

        for py in range(h):
            for px in range(w):
                cp = canvas_pixels[px, py]
                lp = light_pixels[px, py]

                r = int(cp[0] * lp[0] / 255)
                g = int(cp[1] * lp[1] / 255)
                b = int(cp[2] * lp[2] / 255)
                a = cp[3] if len(cp) >= 4 else 255

                canvas_pixels[px, py] = (r, g, b, a)
