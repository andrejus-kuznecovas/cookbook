"""Generate the Cookbook PWA icons.

One-off development tool. It draws the brand pot mark (a white pot
silhouette on the orange background) and writes PNG icons into
``meals/static/meals/icons/``:

- ``icon-192.png`` and ``icon-512.png``: rounded orange square with
  transparent corners, referenced by the web app manifest.
- ``apple-touch-icon.png`` (180x180): full-bleed opaque square, because
  iOS applies its own corner mask and renders transparency as black.

The generated PNGs are committed, so this script only needs to run again
when the brand mark or palette changes.

Requires Pillow. Pillow is intentionally NOT in ``requirements.txt``
because this script is a one-off dev tool, not an app dependency:

    pip install pillow

Run from the repo root:

    python scripts/generate_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

ACCENT = (249, 115, 22, 255)  # --accent #f97316
WHITE = (255, 255, 255, 255)

OUT_DIR = (
    Path(__file__).resolve().parent.parent / "meals" / "static" / "meals" / "icons"
)

# Draw at 4x and downscale for smooth edges (Pillow has no anti-aliasing).
SUPERSAMPLE = 4


def draw_pot(draw: ImageDraw.ImageDraw, size: int) -> None:
    """Draw the white pot mark centered on a ``size`` x ``size`` canvas.

    The brand SVG lives in a 24-unit viewBox, drawn as 2-unit strokes: a
    pot body with a flat rim at y=11 and a rounded bottom reaching y=20,
    plus a handle arc of radius 4 centered on (12, 7). Two arcs
    approximate it here: one for the body bottom, one for the handle.
    """
    # Glyph bounding box with stroke is roughly x 3..21, y 2..21, so its
    # center sits near (12, 11.5). Scale it to ~55% of the canvas to stay
    # inside the maskable safe zone (a circle of 40% radius).
    scale = size * 0.55 / 19

    def xy(x: float, y: float) -> tuple[float, float]:
        return (size / 2 + (x - 12) * scale, size / 2 + (y - 11.5) * scale)

    stroke = round(2 * scale)

    def centered_arc(cx: float, cy: float, r: float, start: float, end: float):
        """Arc whose stroke is centered on radius ``r`` (Pillow's arc
        width grows inward from the bounding box, so pad it outward)."""
        half = 1  # one SVG unit = half the 2-unit stroke
        bbox = [*xy(cx - r - half, cy - r - half), *xy(cx + r + half, cy + r + half)]
        draw.arc(bbox, start=start, end=end, fill=WHITE, width=stroke)

    # Body: the original path's bottom (two radius-7 corner arcs joined by
    # a short flat) is close to one circular arc of radius 8.1 centered on
    # (12, 11.8); its chord at y=11 spans the rim from (4,11) to (20,11).
    centered_arc(12, 11.8, 8.1, 354.3, 185.7)
    draw.line([*xy(4, 11), *xy(20, 11)], fill=WHITE, width=stroke)
    # Round the rim's stroke caps like the SVG's stroke-linecap="round".
    for end_x in (4, 20):
        draw.ellipse([*xy(end_x - 1, 10), *xy(end_x + 1, 12)], fill=WHITE)

    # Handle: semicircular arc over the rim plus two vertical legs.
    centered_arc(12, 7, 4, 180, 360)
    draw.line([*xy(8, 7), *xy(8, 11)], fill=WHITE, width=stroke)
    draw.line([*xy(16, 7), *xy(16, 11)], fill=WHITE, width=stroke)


def make_icon(size: int, rounded: bool) -> Image.Image:
    """Render one icon. ``rounded`` gives the rounded-square background."""
    big = size * SUPERSAMPLE
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if rounded:
        draw.rounded_rectangle([0, 0, big - 1, big - 1], radius=big * 0.22, fill=ACCENT)
    else:
        draw.rectangle([0, 0, big, big], fill=ACCENT)
    draw_pot(draw, big)
    return image.resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_icon(512, rounded=True).save(OUT_DIR / "icon-512.png")
    make_icon(192, rounded=True).save(OUT_DIR / "icon-192.png")
    # Flatten to RGB: iOS shows transparency as black.
    make_icon(180, rounded=False).convert("RGB").save(
        OUT_DIR / "apple-touch-icon.png"
    )
    print(f"Wrote 3 icons to {OUT_DIR}")


if __name__ == "__main__":
    main()
