"""PixelEngine keyframe timeline — multi-property animation via keyframes.

Allows chaining complex multi-property animations on a single object,
with per-keyframe easing and automatic property interpolation.
"""
from pixelengine.animation import Animation, linear, get_easing
from pixelengine.pobject import PObject
from pixelengine.color import parse_color


class Keyframe:
    """A single keyframe with a time position and property values.

    Args:
        at: Normalized time position (0.0–1.0).
        easing: Easing function for interpolation TO this keyframe (keyword-only).
        **props: Property name=value pairs to set at this time.
    """

    def __init__(self, at: float = 0.0, *, easing=linear, **props):
        self.at = max(0.0, min(1.0, at))
        self.easing = get_easing(easing) if easing else linear
        self.props = props


class KeyframeTrack:
    """Build a multi-keyframe animation for a target object.

    Usage::

        track = KeyframeTrack(obj)
        track.add(at=0.0, x=50, y=200, opacity=0.0)
        track.add(at=0.3, x=240, y=135, opacity=1.0, easing="ease_out")
        track.add(at=0.7, x=240, y=135, scale_x=1.5)
        track.add(at=1.0, x=400, y=50, opacity=0.0, easing="ease_in")
        scene.play(track.build(), duration=3.0)

    Interpolates any numeric property (x, y, opacity, scale_x, scale_y,
    width, height, angle) and color properties.
    """

    COLOR_PROPS = {'color'}

    def __init__(self, target: PObject):
        self.target = target
        self._keyframes: list = []

    def add(self, at: float = 0.0, easing=linear, **props) -> "KeyframeTrack":
        """Add a keyframe at a specific time position.

        Args:
            at: Normalized time (0.0–1.0).
            easing: Easing for interpolation towards this keyframe.
            **props: Properties to animate (x, y, opacity, etc.).
        """
        # Parse any color values
        parsed_props = {}
        for k, v in props.items():
            if k in self.COLOR_PROPS and isinstance(v, str):
                parsed_props[k] = parse_color(v)
            else:
                parsed_props[k] = v
        self._keyframes.append(Keyframe(at=at, easing=easing, **parsed_props))
        self._keyframes.sort(key=lambda kf: kf.at)
        return self

    def build(self) -> "KeyframeAnimation":
        """Build and return an Animation object for scene.play()."""
        if len(self._keyframes) < 2:
            raise ValueError("KeyframeTrack requires at least 2 keyframes")
        return KeyframeAnimation(self.target, list(self._keyframes))


class KeyframeAnimation(Animation):
    """Animation driven by a sequence of keyframes.

    Created by KeyframeTrack.build(). Not typically instantiated directly.
    """

    def __init__(self, target: PObject, keyframes: list):
        super().__init__(target, easing=linear)  # We handle easing per-segment
        self._keyframes = keyframes
        self._all_props = set()
        for kf in keyframes:
            self._all_props.update(kf.props.keys())
        # Snapshot: props not in first keyframe use target's current value
        self._initial_values = {}

    def on_start(self):
        # Capture current values for any property that appears later
        for prop in self._all_props:
            self._initial_values[prop] = getattr(self.target, prop, 0)
        # Fill in missing property values in keyframes by forward/back-filling
        for kf in self._keyframes:
            for prop in self._all_props:
                if prop not in kf.props:
                    kf.props[prop] = None  # Mark as not specified

    def _get_value_at(self, prop: str, kf_list: list, kf_idx: int):
        """Walk keyframes to find the last specified value for a prop."""
        # Look backward for the most recent specified value
        for i in range(kf_idx, -1, -1):
            val = kf_list[i].props.get(prop)
            if val is not None:
                return val
        return self._initial_values.get(prop, 0)

    def _get_next_value(self, prop: str, kf_list: list, kf_idx: int):
        """Walk keyframes forward to find the next specified value."""
        for i in range(kf_idx, len(kf_list)):
            val = kf_list[i].props.get(prop)
            if val is not None:
                return val
        # If nothing found forward, use the last known value
        return self._get_value_at(prop, kf_list, len(kf_list) - 1)

    def update(self, alpha: float):
        kf_list = self._keyframes

        # Find the two bounding keyframes
        kf_before = kf_list[0]
        kf_after = kf_list[-1]
        for i in range(len(kf_list) - 1):
            if kf_list[i].at <= alpha <= kf_list[i + 1].at:
                kf_before = kf_list[i]
                kf_after = kf_list[i + 1]
                break
            elif alpha > kf_list[i + 1].at:
                kf_before = kf_list[i + 1]
                kf_after = kf_list[min(i + 2, len(kf_list) - 1)]

        # Compute local alpha within the segment
        segment_duration = kf_after.at - kf_before.at
        if segment_duration > 0:
            local_alpha = (alpha - kf_before.at) / segment_duration
        else:
            local_alpha = 1.0
        local_alpha = max(0.0, min(1.0, local_alpha))

        # Apply easing of the target keyframe
        eased = kf_after.easing(local_alpha)

        # Interpolate each property
        before_idx = kf_list.index(kf_before)
        after_idx = kf_list.index(kf_after)

        for prop in self._all_props:
            val_from = self._get_value_at(prop, kf_list, before_idx)
            val_to = self._get_next_value(prop, kf_list, after_idx)

            if val_from is None:
                val_from = self._initial_values.get(prop, 0)
            if val_to is None:
                val_to = val_from

            # Interpolate
            if prop in KeyframeTrack.COLOR_PROPS:
                # Color interpolation (RGBA tuple)
                if isinstance(val_from, tuple) and isinstance(val_to, tuple):
                    result = tuple(
                        int(val_from[c] + (val_to[c] - val_from[c]) * eased)
                        for c in range(min(len(val_from), len(val_to)))
                    )
                    setattr(self.target, prop, result)
            elif isinstance(val_from, (int, float)) and isinstance(val_to, (int, float)):
                # Numeric interpolation
                result = val_from + (val_to - val_from) * eased
                if isinstance(getattr(self.target, prop, None), int):
                    result = int(result)
                setattr(self.target, prop, result)
