"""PixelEngine PixelArtist — procedural pixel art generation for characters, backgrounds, and effects."""
import math
import random
from PIL import Image, ImageDraw
from pixelengine.pobject import PObject
from pixelengine.sprite import Sprite
from pixelengine.background import GradientBackground, ParallaxLayer
from pixelengine.color import parse_color, PICO8, NES, GAMEBOY


# ═══════════════════════════════════════════════════════════
#  Curated Palettes for Procedural Art
# ═══════════════════════════════════════════════════════════

PALETTES = {
    "warm":    ["#FF004D", "#FFA300", "#FFEC27", "#FFF1E8", "#FFCCAA", "#AB5236"],
    "cool":    ["#1D2B53", "#29ADFF", "#00E436", "#83769C", "#C2C3C7", "#008751"],
    "sunset":  ["#FF004D", "#FFA300", "#FFEC27", "#7E2553", "#1D2B53", "#000000"],
    "night":   ["#0B0E2A", "#1D2B53", "#29ADFF", "#83769C", "#FFF1E8", "#5F574F"],
    "forest":  ["#008751", "#00E436", "#1D2B53", "#AB5236", "#5F574F", "#FFEC27"],
    "ocean":   ["#1D2B53", "#29ADFF", "#00E436", "#FFF1E8", "#83769C", "#0B0E2A"],
    "lava":    ["#FF004D", "#FFA300", "#FFEC27", "#5F574F", "#000000", "#AB5236"],
    "pastel":  ["#FF77A8", "#FFCCAA", "#FFEC27", "#00E436", "#29ADFF", "#83769C"],
    "cyber":   ["#29ADFF", "#00E436", "#FF004D", "#FFF1E8", "#7E2553", "#000000"],
    "earth":   ["#AB5236", "#5F574F", "#008751", "#FFCCAA", "#C2C3C7", "#1D2B53"],
}

SKIN_TONES = ["#FFCCAA", "#E8B796", "#C4956A", "#A67C52", "#8B5E3C", "#6B4226"]


# ═══════════════════════════════════════════════════════════
#  Character Generators
# ═══════════════════════════════════════════════════════════

class PixelArtist:
    """Procedural pixel art generation engine.

    Generate characters, backgrounds, and animated effects entirely in code.

    Usage::

        from pixelengine.pixelart import PixelArtist

        # Generate a humanoid character
        hero = PixelArtist.humanoid(height=16, body_color="#FF004D", seed=42)
        scene.add(hero)

        # Generate a sky background
        sky = PixelArtist.sky(width=256, height=80, time="sunset")
        scene.add(sky)

        # Generate animated fire frames
        fire = PixelArtist.fire_sprite(width=8, height=12, frames=6)
        scene.add(fire)
    """

    # ── Character Generation ─────────────────────────────────

    @staticmethod
    def humanoid(
        height: int = 16,
        body_color: str = "#FF004D",
        skin_color: str = "#FFCCAA",
        hair_color: str = "#AB5236",
        eye_color: str = "#FFF1E8",
        has_hair: bool = True,
        has_hat: bool = False,
        hat_color: str = "#1D2B53",
        has_weapon: bool = False,
        weapon_type: str = "sword",
        x: int = 0, y: int = 0,
        seed: int = None,
    ) -> Sprite:
        """Procedurally generate a humanoid character sprite.

        Uses symmetric generation: builds the left half, mirrors to right.

        Args:
            height: Character height in pixels (width auto-calculated as ~height*0.75).
            body_color: Main clothing/body color.
            skin_color: Skin color for face and hands.
            hair_color: Hair color.
            eye_color: Eye color.
            has_hair: Whether to add hair on top.
            has_hat: Whether to add a hat (overrides hair).
            hat_color: Hat color.
            has_weapon: Whether to add a held weapon.
            weapon_type: "sword", "staff", or "shield".
            x, y: Position on canvas.
            seed: Random seed for reproducibility.
        """
        rng = random.Random(seed)
        width = max(8, int(height * 0.75))
        if width % 2 == 1:
            width += 1  # Ensure even width for symmetry

        img = Image.new("RGBA", (width + 4, height + 4), (0, 0, 0, 0))
        body_c = parse_color(body_color)
        skin_c = parse_color(skin_color)
        hair_c = parse_color(hair_color)
        eye_c = parse_color(eye_color)
        hat_c = parse_color(hat_color)
        outline_c = (0, 0, 0, 255)

        hw = width // 2  # half width
        cx = width // 2 + 2  # center x with padding

        # Proportions based on height
        head_h = max(3, height // 4)
        body_h = max(4, height // 3)
        leg_h = height - head_h - body_h
        head_w = max(3, hw - 1)
        body_w = max(2, hw)
        leg_w = max(1, hw // 2)

        y_off = 2  # padding offset

        # ── Head ──
        head_top = y_off
        for row in range(head_h):
            ry = head_top + row
            for col in range(-head_w, head_w + 1):
                px = cx + col
                if 0 <= px < img.width and 0 <= ry < img.height:
                    # Outline on edges
                    if abs(col) == head_w or row == 0 or row == head_h - 1:
                        img.putpixel((px, ry), outline_c)
                    else:
                        img.putpixel((px, ry), skin_c)

        # Eyes (2 pixels wide, centered, on row 1-2 of head)
        eye_row = head_top + max(1, head_h // 3)
        eye_offset = max(1, head_w // 2)
        for dx in [-eye_offset, eye_offset]:
            px = cx + dx
            if 0 <= px < img.width:
                img.putpixel((px, eye_row), eye_c)

        # Hair or Hat
        if has_hat:
            hat_top = max(0, head_top - 2)
            for row in range(hat_top, head_top + max(1, head_h // 3)):
                brim = head_w + (2 if row == head_top - 1 else 1)
                for col in range(-brim, brim + 1):
                    px = cx + col
                    if 0 <= px < img.width and 0 <= row < img.height:
                        img.putpixel((px, row), hat_c)
        elif has_hair:
            hair_row = head_top
            for col in range(-head_w, head_w + 1):
                px = cx + col
                if 0 <= px < img.width:
                    img.putpixel((px, hair_row), hair_c)
                    if rng.random() > 0.4 and hair_row > 0:
                        img.putpixel((px, hair_row - 1), hair_c)

        # ── Body / Torso ──
        body_top = head_top + head_h
        for row in range(body_h):
            ry = body_top + row
            # Slight taper: wider at shoulders, narrower at waist
            t = row / max(1, body_h - 1)
            row_w = int(body_w * (1.0 - 0.15 * t))
            for col in range(-row_w, row_w + 1):
                px = cx + col
                if 0 <= px < img.width and 0 <= ry < img.height:
                    if abs(col) == row_w or row == 0 or row == body_h - 1:
                        img.putpixel((px, ry), outline_c)
                    else:
                        img.putpixel((px, ry), body_c)

        # Arms (1-2px wide, hanging from shoulders)
        arm_len = max(2, body_h - 1)
        for side in [-1, 1]:
            arm_x = cx + side * (body_w + 1)
            for row in range(arm_len):
                ry = body_top + row
                if 0 <= arm_x < img.width and 0 <= ry < img.height:
                    if row < arm_len - 1:
                        img.putpixel((arm_x, ry), body_c)
                    else:
                        img.putpixel((arm_x, ry), skin_c)  # hand

        # ── Legs ──
        leg_top = body_top + body_h
        for row in range(max(1, leg_h)):
            ry = leg_top + row
            for side in [-1, 1]:
                leg_cx = cx + side * leg_w
                for col in range(-max(1, leg_w // 2), max(1, leg_w // 2) + 1):
                    px = leg_cx + col
                    if 0 <= px < img.width and 0 <= ry < img.height:
                        if row == leg_h - 1:
                            img.putpixel((px, ry), outline_c)  # shoes
                        else:
                            # Pants slightly darker than body
                            r, g, b, a = body_c
                            darker = (max(0, r - 30), max(0, g - 30), max(0, b - 30), a)
                            img.putpixel((px, ry), darker)

        # ── Weapon (optional) ──
        if has_weapon:
            weapon_c = parse_color("#C2C3C7")
            if weapon_type == "sword":
                sx = cx + body_w + 2
                for row in range(max(3, body_h)):
                    ry = body_top - 1 + row
                    if 0 <= sx < img.width and 0 <= ry < img.height:
                        img.putpixel((sx, ry), weapon_c)
                # crossguard
                ry = body_top + 1
                for dx in [-1, 0, 1]:
                    px = sx + dx
                    if 0 <= px < img.width and 0 <= ry < img.height:
                        img.putpixel((px, ry), parse_color("#FFEC27"))
            elif weapon_type == "staff":
                sx = cx + body_w + 2
                for row in range(height - 2):
                    ry = y_off + row
                    if 0 <= sx < img.width and 0 <= ry < img.height:
                        img.putpixel((sx, ry), parse_color("#AB5236"))
                # orb on top
                if 0 <= sx < img.width and y_off > 0:
                    img.putpixel((sx, y_off - 1), parse_color("#29ADFF"))

        # Crop to content
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        return Sprite(img, x=x, y=y)

    @staticmethod
    def creature(
        type: str = "slime",
        size: int = 12,
        color: str = "#00E436",
        eye_color: str = "#FFF1E8",
        x: int = 0, y: int = 0,
        seed: int = None,
    ) -> Sprite:
        """Generate a creature sprite (slime, bat, ghost, skull).

        Args:
            type: "slime", "bat", "ghost", or "skull".
            size: Base size in pixels.
            color: Primary creature color.
            x, y: Position on canvas.
            seed: Random seed for reproducibility.
        """
        rng = random.Random(seed)
        img = Image.new("RGBA", (size + 4, size + 4), (0, 0, 0, 0))
        c = parse_color(color)
        eye_c = parse_color(eye_color)
        outline = (0, 0, 0, 255)
        cx, cy = (size + 4) // 2, (size + 4) // 2

        if type == "slime":
            # Blob shape: elliptical bottom, rounded top
            for y_px in range(size):
                ry = cy - size // 3 + y_px
                t = y_px / max(1, size - 1)
                # Wider at bottom
                row_w = int((size // 2) * (0.6 + 0.4 * t))
                for col in range(-row_w, row_w + 1):
                    px = cx + col
                    if 0 <= px < img.width and 0 <= ry < img.height:
                        if abs(col) >= row_w - 1 or y_px == 0 or y_px == size - 1:
                            img.putpixel((px, ry), outline)
                        else:
                            # Slight highlight on top
                            if y_px < size // 3:
                                r, g, b, a = c
                                lighter = (min(255, r + 40), min(255, g + 40), min(255, b + 40), a)
                                img.putpixel((px, ry), lighter)
                            else:
                                img.putpixel((px, ry), c)
            # Eyes
            eye_y = cy - size // 6
            for dx in [-size // 5, size // 5]:
                px = cx + dx
                if 0 <= px < img.width and 0 <= eye_y < img.height:
                    img.putpixel((px, eye_y), eye_c)
                    if 0 <= eye_y + 1 < img.height:
                        img.putpixel((px, eye_y + 1), eye_c)

        elif type == "ghost":
            # Rounded top, wavy bottom
            for y_px in range(size):
                ry = cy - size // 3 + y_px
                t = y_px / max(1, size - 1)
                if y_px < size // 2:
                    # Top: circular
                    angle = math.acos(max(-1, min(1, 1 - 2 * y_px / (size // 2))))
                    row_w = int((size // 2) * math.sin(angle))
                else:
                    row_w = size // 2
                for col in range(-row_w, row_w + 1):
                    px = cx + col
                    # Wavy bottom edge
                    if y_px == size - 1:
                        if col % 3 == 0:
                            continue
                    if 0 <= px < img.width and 0 <= ry < img.height:
                        img.putpixel((px, ry), c)
            # Eyes + mouth
            eye_y = cy - size // 6
            for dx in [-size // 5, size // 5]:
                px = cx + dx
                if 0 <= px < img.width and 0 <= eye_y < img.height:
                    img.putpixel((px, eye_y), outline)
            # Mouth
            mouth_y = eye_y + 2
            if 0 <= cx < img.width and 0 <= mouth_y < img.height:
                img.putpixel((cx, mouth_y), outline)

        elif type == "bat":
            # Small body with wide wings
            body_w = max(2, size // 4)
            wing_span = size // 2
            body_h = max(3, size // 3)
            body_top = cy - body_h // 2
            # Body
            for row in range(body_h):
                ry = body_top + row
                for col in range(-body_w, body_w + 1):
                    px = cx + col
                    if 0 <= px < img.width and 0 <= ry < img.height:
                        img.putpixel((px, ry), c)
            # Wings
            for side in [-1, 1]:
                for row in range(body_h - 1):
                    ry = body_top + row
                    wing_w = wing_span - row
                    for col in range(wing_w):
                        px = cx + side * (body_w + col + 1)
                        if 0 <= px < img.width and 0 <= ry < img.height:
                            img.putpixel((px, ry), c)
            # Eyes
            for dx in [-1, 1]:
                px = cx + dx
                if 0 <= px < img.width and 0 <= body_top + 1 < img.height:
                    img.putpixel((px, body_top + 1), eye_c)

        elif type == "skull":
            radius = size // 3
            # Round head
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dx * dx + dy * dy <= radius * radius:
                        px, py = cx + dx, cy + dy - 1
                        if 0 <= px < img.width and 0 <= py < img.height:
                            dist = math.sqrt(dx * dx + dy * dy)
                            if dist > radius - 1.5:
                                img.putpixel((px, py), outline)
                            else:
                                img.putpixel((px, py), c)
            # Eye sockets
            for dx in [-radius // 2, radius // 2]:
                for dy2 in range(2):
                    for dx2 in range(2):
                        px = cx + dx + dx2
                        py = cy - 2 + dy2
                        if 0 <= px < img.width and 0 <= py < img.height:
                            img.putpixel((px, py), outline)
            # Jaw
            jaw_y = cy + radius - 1
            jaw_w = radius - 1
            for col in range(-jaw_w, jaw_w + 1):
                px = cx + col
                for row in range(2):
                    py = jaw_y + row
                    if 0 <= px < img.width and 0 <= py < img.height:
                        if col % 2 == 0 and row == 1:
                            continue  # teeth gaps
                        img.putpixel((px, py), c)

        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        return Sprite(img, x=x, y=y)

    @staticmethod
    def robot(
        size: int = 16,
        body_color: str = "#C2C3C7",
        accent_color: str = "#29ADFF",
        eye_color: str = "#FF004D",
        style: str = "cute",
        x: int = 0, y: int = 0,
        seed: int = None,
    ) -> Sprite:
        """Generate a robot character sprite.

        Args:
            size: Base size in pixels.
            body_color: Main body color.
            accent_color: Accent/detail color.
            eye_color: LED eye color.
            style: "cute" (rounded) or "angular" (boxy).
            x, y: Position on canvas.
            seed: Random seed for reproducibility.
        """
        rng = random.Random(seed)
        w = max(8, int(size * 0.8))
        h = size
        if w % 2 == 1:
            w += 1

        img = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
        body_c = parse_color(body_color)
        accent_c = parse_color(accent_color)
        eye_c = parse_color(eye_color)
        outline = (0, 0, 0, 255)
        dark_c = (max(0, body_c[0] - 50), max(0, body_c[1] - 50), max(0, body_c[2] - 50), 255)

        cx = (w + 4) // 2
        head_h = max(4, h // 3)
        body_h = max(3, h // 3)
        leg_h = h - head_h - body_h
        head_w = max(3, w // 2)
        body_w = max(3, w // 2 + 1)
        y_off = 2

        # Antenna
        img.putpixel((cx, y_off - 1), accent_c)
        img.putpixel((cx, y_off - 2), eye_c) if y_off >= 2 else None

        # Head (boxy)
        head_top = y_off
        for row in range(head_h):
            ry = head_top + row
            for col in range(-head_w, head_w + 1):
                px = cx + col
                if 0 <= px < img.width and 0 <= ry < img.height:
                    if abs(col) == head_w or row == 0 or row == head_h - 1:
                        img.putpixel((px, ry), outline)
                    elif style == "cute" and row == 1:
                        img.putpixel((px, ry), accent_c)
                    else:
                        img.putpixel((px, ry), body_c)

        # Eyes (LED style — 2 bright pixels)
        eye_row = head_top + head_h // 2
        for dx in [-head_w // 2, head_w // 2]:
            px = cx + dx
            if 0 <= px < img.width and 0 <= eye_row < img.height:
                img.putpixel((px, eye_row), eye_c)
                # Glow pixel below
                if 0 <= eye_row + 1 < img.height:
                    r, g, b, _ = eye_c
                    glow = (r, g, b, 128)
                    img.putpixel((px, eye_row + 1), glow)

        # Body (wider, with panel lines)
        body_top = head_top + head_h
        for row in range(body_h):
            ry = body_top + row
            for col in range(-body_w, body_w + 1):
                px = cx + col
                if 0 <= px < img.width and 0 <= ry < img.height:
                    if abs(col) == body_w or row == 0 or row == body_h - 1:
                        img.putpixel((px, ry), outline)
                    elif col == 0:
                        img.putpixel((px, ry), dark_c)  # center seam
                    elif row == body_h // 2:
                        img.putpixel((px, ry), accent_c)  # belt/stripe
                    else:
                        img.putpixel((px, ry), body_c)

        # Arms (mechanical)
        for side in [-1, 1]:
            arm_x = cx + side * (body_w + 1)
            for row in range(body_h):
                ry = body_top + row
                if 0 <= arm_x < img.width and 0 <= ry < img.height:
                    if row == body_h - 1:
                        img.putpixel((arm_x, ry), accent_c)  # claw
                    else:
                        img.putpixel((arm_x, ry), dark_c)

        # Legs (blocky)
        leg_top = body_top + body_h
        for side in [-1, 1]:
            leg_x = cx + side * max(1, body_w // 2)
            for row in range(max(1, leg_h)):
                ry = leg_top + row
                for dx in range(-1, 2):
                    px = leg_x + dx
                    if 0 <= px < img.width and 0 <= ry < img.height:
                        if row == leg_h - 1:
                            img.putpixel((px, ry), outline)  # feet
                        else:
                            img.putpixel((px, ry), dark_c)

        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        return Sprite(img, x=x, y=y)

    # ── Background Generation ────────────────────────────────

    @staticmethod
    def sky(
        width: int = 256,
        height: int = 80,
        time: str = "sunset",
        clouds: bool = True,
        cloud_count: int = 5,
        x: int = 0, y: int = 0,
        seed: int = None,
    ) -> Sprite:
        """Generate a pixel art sky with optional dithered clouds.

        Args:
            width, height: Dimensions.
            time: "day", "sunset", "night", "dawn".
            clouds: Whether to add procedural clouds.
            cloud_count: Number of clouds.
            x, y: Position.
            seed: Random seed.
        """
        rng = random.Random(seed)
        time_palettes = {
            "day":    [("#87CEEB", 0.0), ("#4A90D9", 0.5), ("#1D2B53", 1.0)],
            "sunset": [("#FFEC27", 0.0), ("#FFA300", 0.25), ("#FF004D", 0.5), ("#7E2553", 0.75), ("#1D2B53", 1.0)],
            "night":  [("#0B0E2A", 0.0), ("#1D2B53", 0.5), ("#000000", 1.0)],
            "dawn":   [("#FFCCAA", 0.0), ("#FF77A8", 0.3), ("#7E2553", 0.6), ("#1D2B53", 1.0)],
        }
        stops = time_palettes.get(time, time_palettes["sunset"])

        img = Image.new("RGBA", (width, height))

        # Multi-stop gradient
        for py in range(height):
            t = py / max(1, height - 1)
            # Find which two stops we're between
            c1_hex, t1 = stops[0]
            c2_hex, t2 = stops[-1]
            for i in range(len(stops) - 1):
                if stops[i][1] <= t <= stops[i + 1][1]:
                    c1_hex, t1 = stops[i]
                    c2_hex, t2 = stops[i + 1]
                    break
            local_t = (t - t1) / max(0.001, t2 - t1)
            c1 = parse_color(c1_hex)
            c2 = parse_color(c2_hex)
            color = tuple(int(c1[j] + (c2[j] - c1[j]) * local_t) for j in range(4))
            for px in range(width):
                img.putpixel((px, py), color)

        # Stars for night/dawn
        if time in ("night", "dawn"):
            star_count = rng.randint(20, 50)
            for _ in range(star_count):
                sx = rng.randint(0, width - 1)
                sy = rng.randint(0, int(height * 0.7))
                brightness = rng.choice([(255, 241, 232, 255), (194, 195, 199, 180)])
                img.putpixel((sx, sy), brightness)

        # Clouds (dithered blobs)
        if clouds:
            cloud_color = (255, 241, 232, 160) if time != "night" else (131, 118, 156, 100)
            for _ in range(cloud_count):
                cx_cloud = rng.randint(10, width - 10)
                cy_cloud = rng.randint(5, int(height * 0.5))
                cw = rng.randint(12, 30)
                ch = rng.randint(4, 8)
                for dy in range(-ch, ch + 1):
                    for dx in range(-cw, cw + 1):
                        # Elliptical shape with dithering
                        dist = (dx / cw) ** 2 + (dy / ch) ** 2
                        if dist < 1.0:
                            # Dither: skip some pixels near edge
                            if dist > 0.6 and rng.random() > 0.5:
                                continue
                            px = cx_cloud + dx
                            py_cloud = cy_cloud + dy
                            if 0 <= px < width and 0 <= py_cloud < height:
                                img.putpixel((px, py_cloud), cloud_color)

        sprite = Sprite(img, x=x, y=y)
        sprite.z_index = -100
        return sprite

    @staticmethod
    def mountains(
        width: int = 256,
        height: int = 60,
        layers: int = 3,
        palette: str = "cool",
        base_y: int = 84,
        x: int = 0,
        seed: int = None,
    ) -> list:
        """Generate layered mountain silhouettes using midpoint displacement.

        Returns a list of Sprite objects, one per layer (far to near).

        Args:
            width, height: Max dimensions of the mountain region.
            layers: Number of mountain layers (depth).
            palette: Color palette name from PALETTES.
            base_y: Y position of the bottom of the mountains on canvas.
            x: X position.
            seed: Random seed.
        """
        rng = random.Random(seed)
        colors = [parse_color(c) for c in PALETTES.get(palette, PALETTES["cool"])]
        result = []

        for layer_idx in range(layers):
            t = layer_idx / max(1, layers - 1)
            layer_height = int(height * (0.4 + 0.6 * t))
            roughness = 0.4 + 0.3 * t

            # Midpoint displacement for mountain ridge
            points = [rng.uniform(0.2, 0.6) for _ in range(9)]
            # Interpolate to full width
            ridge = []
            for px_idx in range(width):
                ft = px_idx / max(1, width - 1) * (len(points) - 1)
                idx = int(ft)
                frac = ft - idx
                idx = min(idx, len(points) - 2)
                val = points[idx] + (points[idx + 1] - points[idx]) * frac
                # Add per-pixel noise
                val += rng.uniform(-0.03, 0.03) * roughness
                ridge.append(max(0.1, min(0.9, val)))

            # Render to image
            img = Image.new("RGBA", (width, layer_height + 5), (0, 0, 0, 0))
            color_idx = min(layer_idx, len(colors) - 1)
            c = colors[color_idx]
            # Darken further layers
            darken = 1.0 - (1.0 - t) * 0.4
            c_dark = tuple(int(c[j] * darken) for j in range(3)) + (255,)

            for px_idx in range(width):
                peak = int((1.0 - ridge[px_idx]) * layer_height)
                for py_idx in range(peak, layer_height + 5):
                    if 0 <= py_idx < img.height:
                        # Subtle vertical gradient
                        grad_t = (py_idx - peak) / max(1, layer_height - peak)
                        r = int(c_dark[0] * (1.0 - grad_t * 0.2))
                        g = int(c_dark[1] * (1.0 - grad_t * 0.2))
                        b = int(c_dark[2] * (1.0 - grad_t * 0.2))
                        img.putpixel((px_idx, py_idx), (max(0, r), max(0, g), max(0, b), 255))

            sprite = Sprite(img, x=x, y=base_y - layer_height + int(t * height * 0.3))
            sprite.z_index = -90 + layer_idx
            result.append(sprite)

        return result

    @staticmethod
    def cityscape(
        width: int = 256,
        height: int = 144,
        building_count: int = 20,
        style: str = "retro",
        sky_color: str = "#0B0E2A",
        building_color: str = "#1D2B53",
        window_color: str = "#FFEC27",
        x: int = 0, y: int = 0,
        seed: int = None,
    ) -> Sprite:
        """Generate a city skyline with lit windows.

        Args:
            width, height: Canvas dimensions.
            building_count: Number of buildings.
            style: "retro" or "modern".
            sky_color: Background sky color.
            building_color: Base building color.
            window_color: Lit window color.
            x, y: Position.
            seed: Random seed.
        """
        rng = random.Random(seed)
        img = Image.new("RGBA", (width, height), parse_color(sky_color))
        bldg_c = parse_color(building_color)
        win_c = parse_color(window_color)
        win_off_c = parse_color("#1D2B53")
        dark_c = tuple(max(0, c - 20) for c in bldg_c[:3]) + (255,)

        # Stars in sky
        for _ in range(40):
            sx = rng.randint(0, width - 1)
            sy = rng.randint(0, height // 2)
            img.putpixel((sx, sy), (255, 241, 232, rng.randint(100, 255)))

        # Generate buildings left to right
        bx = 0
        buildings = []
        while bx < width:
            bw = rng.randint(8, 20)
            bh = rng.randint(height // 4, height - 10)
            buildings.append((bx, bw, bh))
            bx += bw + rng.randint(0, 3)

        # Draw far buildings (shorter, darker)
        for bx_pos, bw, bh in buildings:
            far_h = int(bh * 0.6)
            far_y = height - far_h
            for py_px in range(far_y, height):
                for px_px in range(bx_pos - 2, bx_pos + bw + 2):
                    if 0 <= px_px < width:
                        img.putpixel((px_px, py_px), dark_c)

        # Draw near buildings
        for bx_pos, bw, bh in buildings:
            by = height - bh
            # Building body
            for py_px in range(by, height):
                for px_px in range(bx_pos, min(bx_pos + bw, width)):
                    img.putpixel((px_px, py_px), bldg_c)

            # Rooftop line
            for px_px in range(bx_pos, min(bx_pos + bw, width)):
                if 0 <= by < height:
                    img.putpixel((px_px, by), dark_c)

            # Windows (2px with 2px gaps)
            for wy in range(by + 3, height - 3, 4):
                for wx in range(bx_pos + 2, bx_pos + bw - 2, 4):
                    is_lit = rng.random() > 0.35
                    wc = win_c if is_lit else win_off_c
                    for dy in range(2):
                        for dx in range(2):
                            px_px = wx + dx
                            py_px = wy + dy
                            if 0 <= px_px < width and 0 <= py_px < height:
                                img.putpixel((px_px, py_px), wc)

        sprite = Sprite(img, x=x, y=y)
        sprite.z_index = -100
        return sprite

    @staticmethod
    def forest(
        width: int = 256,
        height: int = 80,
        tree_count: int = 15,
        palette: str = "forest",
        x: int = 0, y: int = 64,
        seed: int = None,
    ) -> Sprite:
        """Generate a procedural forest with layered trees.

        Args:
            width, height: Dimensions.
            tree_count: Approximate number of trees.
            palette: Color palette name.
            x, y: Position.
            seed: Random seed.
        """
        rng = random.Random(seed)
        colors = [parse_color(c) for c in PALETTES.get(palette, PALETTES["forest"])]
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        # Ground
        ground_h = max(5, height // 5)
        ground_c = colors[4] if len(colors) > 4 else parse_color("#5F574F")
        for py_px in range(height - ground_h, height):
            for px_px in range(width):
                img.putpixel((px_px, py_px), ground_c)

        # Far grass overlay
        grass_c = colors[0] if colors else parse_color("#008751")
        for px_px in range(width):
            grass_h = rng.randint(1, 3)
            gy = height - ground_h - grass_h
            for dy in range(grass_h):
                if 0 <= gy + dy < height:
                    img.putpixel((px_px, gy + dy), grass_c)

        # Trees (back to front: 2 layers)
        for layer in range(2):
            count = tree_count // 2
            t = layer / max(1, 1)
            tree_color = colors[min(layer, len(colors) - 1)]
            trunk_c = colors[3] if len(colors) > 3 else parse_color("#AB5236")
            # Darken far layer
            if layer == 0:
                tree_color = tuple(max(0, c - 40) for c in tree_color[:3]) + (255,)

            for _ in range(count):
                tx = rng.randint(5, width - 5)
                tree_h = rng.randint(12, 25) + layer * 5
                tree_w = rng.randint(6, 12) + layer * 2
                tree_base = height - ground_h - 1

                # Trunk
                trunk_w = max(1, tree_w // 5)
                for dy in range(tree_h // 3):
                    ry = tree_base - dy
                    for dx in range(-trunk_w, trunk_w + 1):
                        px_px = tx + dx
                        if 0 <= px_px < width and 0 <= ry < height:
                            img.putpixel((px_px, ry), trunk_c)

                # Canopy (triangular/conical)
                canopy_h = tree_h - tree_h // 3
                canopy_top = tree_base - tree_h
                for row in range(canopy_h):
                    ry = canopy_top + row
                    row_w = int(tree_w * (row / max(1, canopy_h - 1)))
                    for dx in range(-row_w, row_w + 1):
                        px_px = tx + dx
                        if 0 <= px_px < width and 0 <= ry < height:
                            # Skip some edge pixels for organic look
                            if abs(dx) == row_w and rng.random() > 0.6:
                                continue
                            img.putpixel((px_px, ry), tree_color)

        sprite = Sprite(img, x=x, y=y)
        sprite.z_index = -50
        return sprite

    @staticmethod
    def ocean(
        width: int = 256,
        height: int = 40,
        color_deep: str = "#1D2B53",
        color_surface: str = "#29ADFF",
        foam_color: str = "#FFF1E8",
        frames: int = 6,
        x: int = 0, y: int = 104,
        seed: int = None,
    ) -> Sprite:
        """Generate animated ocean waves.

        Returns a Sprite with multiple animation frames.

        Args:
            width, height: Dimensions.
            color_deep, color_surface: Water gradient colors.
            foam_color: Wave foam/crest color.
            frames: Number of animation frames.
            x, y: Position.
            seed: Random seed.
        """
        rng = random.Random(seed)
        deep_c = parse_color(color_deep)
        surface_c = parse_color(color_surface)
        foam_c = parse_color(foam_color)
        frame_images = []

        for f in range(frames):
            img = Image.new("RGBA", (width, height))
            phase = (f / frames) * 2 * math.pi

            for py_px in range(height):
                t = py_px / max(1, height - 1)
                # Gradient from surface to deep
                color = tuple(int(surface_c[j] + (deep_c[j] - surface_c[j]) * t) for j in range(4))
                for px_px in range(width):
                    # Wave displacement
                    wave = math.sin(px_px * 0.1 + phase) * 2 + math.sin(px_px * 0.05 + phase * 0.7) * 1.5
                    effective_y = py_px + int(wave)
                    if effective_y < 2:
                        img.putpixel((px_px, py_px), foam_c)
                    else:
                        img.putpixel((px_px, py_px), color)

            # Foam highlights on wave crests
            for px_px in range(width):
                wave_top = int(math.sin(px_px * 0.1 + phase) * 2)
                fy = max(0, wave_top)
                if 0 <= fy < height and rng.random() > 0.4:
                    img.putpixel((px_px, fy), foam_c)

            frame_images.append(img)

        sprite = Sprite(frame_images[0], x=x, y=y)
        sprite._frames = frame_images
        sprite.auto_animate = True
        sprite.frame_duration = 0.15
        sprite.z_index = -40
        return sprite

    # ── Effect Sprite Generation ─────────────────────────────

    @staticmethod
    def fire_sprite(
        width: int = 8,
        height: int = 12,
        frames: int = 6,
        palette: list = None,
        x: int = 0, y: int = 0,
        seed: int = None,
    ) -> Sprite:
        """Generate animated fire using cellular automata.

        Args:
            width, height: Fire dimensions.
            frames: Number of animation frames.
            palette: Custom color list (hot to cool). Defaults to classic fire.
            x, y: Position.
            seed: Random seed.
        """
        rng = random.Random(seed)
        if palette is None:
            palette = ["#FFF1E8", "#FFEC27", "#FFA300", "#FF004D", "#AB5236", "#000000"]
        pal_colors = [parse_color(c) for c in palette]
        frame_images = []

        for f in range(frames):
            # Fire buffer (heat values 0.0–1.0)
            buf = [[0.0] * width for _ in range(height)]
            # Hot bottom row
            for px_idx in range(width):
                buf[height - 1][px_idx] = rng.uniform(0.7, 1.0)
                if height > 1:
                    buf[height - 2][px_idx] = rng.uniform(0.5, 0.9)

            # Propagate upward (cellular automata)
            for _ in range(3):
                new_buf = [[0.0] * width for _ in range(height)]
                for r in range(height):
                    for c in range(width):
                        if r >= height - 2:
                            new_buf[r][c] = buf[r][c]
                            continue
                        # Average of neighbors below + cooling
                        total = 0
                        count = 0
                        for dr in [0, 1, 2]:
                            for dc in [-1, 0, 1]:
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < height and 0 <= nc < width:
                                    total += buf[nr][nc]
                                    count += 1
                        avg = total / max(1, count)
                        cooling = rng.uniform(0.05, 0.15)
                        new_buf[r][c] = max(0, avg - cooling)
                buf = new_buf

            # Render to image
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            for r in range(height):
                for c in range(width):
                    heat = buf[r][c]
                    if heat < 0.05:
                        continue  # transparent
                    # Map heat to palette
                    idx = min(int((1.0 - heat) * (len(pal_colors) - 1)), len(pal_colors) - 1)
                    color = pal_colors[idx]
                    # Apply alpha based on heat
                    alpha = min(255, int(heat * 255 * 1.5))
                    img.putpixel((c, r), (color[0], color[1], color[2], alpha))

            frame_images.append(img)

        sprite = Sprite(frame_images[0], x=x, y=y)
        sprite._frames = frame_images
        sprite.auto_animate = True
        sprite.frame_duration = 0.1
        return sprite

    @staticmethod
    def explosion_sprite(
        radius: int = 12,
        frames: int = 8,
        palette: list = None,
        x: int = 0, y: int = 0,
        seed: int = None,
    ) -> Sprite:
        """Generate an explosion animation (radial burst).

        Args:
            radius: Maximum explosion radius.
            frames: Number of animation frames.
            palette: Custom color list. Defaults to fire colors.
            x, y: Position.
            seed: Random seed.
        """
        rng = random.Random(seed)
        if palette is None:
            palette = ["#FFF1E8", "#FFEC27", "#FFA300", "#FF004D", "#5F574F"]
        pal_colors = [parse_color(c) for c in palette]
        size = radius * 2 + 4
        frame_images = []

        for f in range(frames):
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            t = f / max(1, frames - 1)
            cx, cy = size // 2, size // 2
            current_r = int(radius * (0.3 + 0.7 * t))
            alpha_mult = 1.0 - t * 0.8  # Fade out

            for dy in range(-current_r, current_r + 1):
                for dx in range(-current_r, current_r + 1):
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > current_r:
                        continue
                    # Ring pattern: strongest at edge
                    ring_t = dist / max(1, current_r)
                    if t < 0.3:
                        # Early: filled circle
                        intensity = 1.0 - ring_t * 0.5
                    else:
                        # Later: expanding ring
                        ring_dist = abs(ring_t - 0.7)
                        intensity = max(0, 1.0 - ring_dist * 4)
                    if intensity < 0.1:
                        continue
                    # Add some randomness
                    intensity *= rng.uniform(0.7, 1.0)
                    # Map to palette
                    pal_idx = min(int((1.0 - intensity) * (len(pal_colors) - 1)), len(pal_colors) - 1)
                    color = pal_colors[pal_idx]
                    alpha = min(255, int(intensity * 255 * alpha_mult))
                    px, py = cx + dx, cy + dy
                    if 0 <= px < size and 0 <= py < size:
                        img.putpixel((px, py), (color[0], color[1], color[2], alpha))

            frame_images.append(img)

        sprite = Sprite(frame_images[0], x=x, y=y)
        sprite._frames = frame_images
        sprite.auto_animate = True
        sprite.frame_duration = 0.08
        sprite.loop = False
        sprite.anchor_x = 0.5
        sprite.anchor_y = 0.5
        return sprite

    @staticmethod
    def sparkle_sprite(
        size: int = 8,
        frames: int = 6,
        color: str = "#FFEC27",
        x: int = 0, y: int = 0,
        seed: int = None,
    ) -> Sprite:
        """Generate an animated sparkle/glitter effect.

        Args:
            size: Sparkle size in pixels.
            frames: Number of animation frames.
            color: Sparkle color.
            x, y: Position.
            seed: Random seed.
        """
        rng = random.Random(seed)
        c = parse_color(color)
        frame_images = []

        for f in range(frames):
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            cx, cy = size // 2, size // 2
            t = f / max(1, frames - 1)
            # Pulsing: grows then shrinks
            pulse = 1.0 - abs(t - 0.5) * 2
            arm_len = max(1, int(size // 2 * pulse))

            # 4-pointed star
            for d in range(arm_len):
                alpha = int(255 * (1.0 - d / arm_len) * pulse)
                pixel_c = (c[0], c[1], c[2], alpha)
                # Horizontal
                for dx in [-d, d]:
                    px = cx + dx
                    if 0 <= px < size:
                        img.putpixel((px, cy), pixel_c)
                # Vertical
                for dy in [-d, d]:
                    py = cy + dy
                    if 0 <= py < size:
                        img.putpixel((cx, py), pixel_c)

            # Center pixel always bright
            img.putpixel((cx, cy), (c[0], c[1], c[2], int(255 * max(0.3, pulse))))

            frame_images.append(img)

        sprite = Sprite(frame_images[0], x=x, y=y)
        sprite._frames = frame_images
        sprite.auto_animate = True
        sprite.frame_duration = 0.1
        sprite.anchor_x = 0.5
        sprite.anchor_y = 0.5
        return sprite

    # ── Palette Cycling ──────────────────────────────────────

    @staticmethod
    def palette_cycle(
        image: Image.Image,
        cycle_colors: list,
        frames: int = 8,
    ) -> list:
        """Generate animation frames by cycling specific colors in an image.

        This creates a classic retro "palette cycling" effect for water, lava, etc.

        Args:
            image: Base PIL Image.
            cycle_colors: List of hex color strings to cycle through.
            frames: Number of frames in the cycle.

        Returns:
            List of PIL Images, one per frame.
        """
        parsed = [parse_color(c) for c in cycle_colors]
        frame_images = []

        for f in range(frames):
            img = image.copy()
            shift = f % len(parsed)
            shifted = parsed[shift:] + parsed[:shift]

            # Replace each original palette color with its shifted version
            for py_px in range(img.height):
                for px_px in range(img.width):
                    pixel = img.getpixel((px_px, py_px))
                    for i, orig in enumerate(parsed):
                        if pixel[:3] == orig[:3]:
                            img.putpixel((px_px, py_px), shifted[i])
                            break
            frame_images.append(img)

        return frame_images

    # ── Utility: Scene Builder ───────────────────────────────

    @staticmethod
    def scene_pack(
        theme: str = "fantasy",
        width: int = 256,
        height: int = 144,
        seed: int = None,
    ) -> dict:
        """Generate a complete scene background pack for a theme.

        Returns a dict with keys: "sky", "terrain", "ground", all as Sprites.

        Args:
            theme: "fantasy", "sci_fi", "nature", "ocean_world".
            width, height: Canvas dimensions.
            seed: Random seed.

        Returns:
            dict with "background" (Sprite) and "layers" (list of Sprites).
        """
        rng = random.Random(seed)
        s = seed or 42

        if theme == "fantasy":
            sky = PixelArtist.sky(width, height // 2, time="sunset", seed=s)
            mountains = PixelArtist.mountains(width, 60, layers=3, palette="warm", base_y=height - 30, seed=s)
            return {"background": sky, "layers": mountains}

        elif theme == "sci_fi":
            city = PixelArtist.cityscape(width, height, seed=s,
                                          building_color="#1D2B53",
                                          window_color="#29ADFF",
                                          sky_color="#0B0E2A")
            return {"background": city, "layers": []}

        elif theme == "nature":
            sky = PixelArtist.sky(width, height // 2, time="day", seed=s)
            forest = PixelArtist.forest(width, 80, seed=s)
            return {"background": sky, "layers": [forest]}

        elif theme == "ocean_world":
            sky = PixelArtist.sky(width, height // 3, time="dawn", seed=s)
            ocean = PixelArtist.ocean(width, height // 2, y=height // 2, seed=s)
            return {"background": sky, "layers": [ocean]}

        else:
            sky = PixelArtist.sky(width, height, time="night", seed=s)
            return {"background": sky, "layers": []}
