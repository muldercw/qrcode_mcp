"""
QR code generation engine.

Supports:
  - Basic QR codes with custom colors
  - Gradient fills (radial, linear, square)
  - Embedded logos / center images
  - Custom module shapes (squares, circles, rounded, bars, etc.)
  - Custom eye/finder-pattern styles
  - Multiple output formats (PNG, SVG)
  - All four error-correction levels
"""

from __future__ import annotations

import io
import logging
import os
import sys
from pathlib import Path
from typing import Any

import qrcode
from qrcode.constants import (
    ERROR_CORRECT_H,
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
)
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    CircleModuleDrawer,
    GappedSquareModuleDrawer,
    HorizontalBarsDrawer,
    RoundedModuleDrawer,
    SquareModuleDrawer,
    VerticalBarsDrawer,
)
from qrcode.image.styles.colormasks import (
    HorizontalGradiantColorMask,
    ImageColorMask,
    RadialGradiantColorMask,
    SolidFillColorMask,
    SquareGradiantColorMask,
    VerticalGradiantColorMask,
)
from PIL import Image, ImageDraw

try:
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef]
except ImportError:
    tomllib = None  # type: ignore[assignment]

logger = logging.getLogger("qrcode_mcp")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPPORTED_FORMATS = ("png", "svg")

ERROR_CORRECTION_LEVELS = {
    "L": ERROR_CORRECT_L,  # ~7% recovery
    "M": ERROR_CORRECT_M,  # ~15% recovery
    "Q": ERROR_CORRECT_Q,  # ~25% recovery
    "H": ERROR_CORRECT_H,  # ~30% recovery
}

MODULE_SHAPES = {
    "square": SquareModuleDrawer,
    "gapped": GappedSquareModuleDrawer,
    "circle": CircleModuleDrawer,
    "rounded": RoundedModuleDrawer,
    "vertical_bars": VerticalBarsDrawer,
    "horizontal_bars": HorizontalBarsDrawer,
}

GRADIENT_STYLES = {
    "solid": SolidFillColorMask,
    "radial": RadialGradiantColorMask,
    "square": SquareGradiantColorMask,
    "horizontal": HorizontalGradiantColorMask,
    "vertical": VerticalGradiantColorMask,
}

# ---------------------------------------------------------------------------
# Config from pyproject.toml
# ---------------------------------------------------------------------------


def _load_pyproject_config() -> dict:
    """Load [tool.qrcode-mcp] settings from pyproject.toml if present."""
    if tomllib is None:
        return {}

    search_dir = Path(__file__).resolve().parent
    for _ in range(10):
        candidate = search_dir / "pyproject.toml"
        if candidate.is_file():
            try:
                with open(candidate, "rb") as f:
                    data = tomllib.load(f)
                return data.get("tool", {}).get("qrcode-mcp", {})
            except Exception:
                return {}
        parent = search_dir.parent
        if parent == search_dir:
            break
        search_dir = parent
    return {}


_CONFIG = _load_pyproject_config()

DEFAULT_SIZE: int = _CONFIG.get("default_size", 10)
DEFAULT_BORDER: int = _CONFIG.get("default_border", 2)
DEFAULT_FORMAT: str = _CONFIG.get("default_format", "png")

_raw_output_dir = _CONFIG.get("output_dir", None)
if _raw_output_dir:
    _out_path = Path(_raw_output_dir)
    if not _out_path.is_absolute():
        _project_root = Path(__file__).resolve().parent
        for _ in range(10):
            if (_project_root / "pyproject.toml").is_file():
                break
            _project_root = _project_root.parent
        _out_path = _project_root / _out_path
    DEFAULT_OUTPUT_DIR = str(_out_path.resolve())
else:
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "qrcode_mcp")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_color(color: str) -> tuple[int, int, int]:
    """Parse a hex color string (#RRGGBB or RRGGBB) into an (R, G, B) tuple."""
    color = color.strip().lstrip("#")
    if len(color) == 3:
        color = "".join(c * 2 for c in color)
    if len(color) != 6:
        raise ValueError(f"Invalid color: '#{color}'. Use hex format like #FF0000 or #F00.")
    return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))


def _ensure_output_dir(output_dir: str) -> Path:
    """Make sure the output directory exists and return it as a Path."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    return out


def _unique_filename(output_dir: Path, prefix: str, ext: str) -> Path:
    """Generate a unique filename in the output directory."""
    import hashlib
    import time

    stamp = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    return output_dir / f"{prefix}_{stamp}.{ext}"


# ---------------------------------------------------------------------------
# Core generation functions
# ---------------------------------------------------------------------------


def generate_basic(
    data: str,
    *,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = DEFAULT_SIZE,
    border: int = DEFAULT_BORDER,
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    error_correction: str = "H",
    output_format: str = DEFAULT_FORMAT,
) -> dict:
    """
    Generate a basic QR code with solid foreground and background colors.

    Parameters
    ----------
    data : the text or URL to encode
    output_dir : directory to save the QR image (default ~/Downloads/qrcode_mcp)
    filename : optional custom filename (without extension)
    size : box size in pixels per module (default 10)
    border : number of border modules (default 2)
    fg_color : foreground color in hex, e.g. "#000000"
    bg_color : background color in hex, e.g. "#FFFFFF"
    error_correction : "L", "M", "Q", or "H" (default "H")
    output_format : "png" or "svg"

    Returns
    -------
    dict with saved_path, data, settings
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    out_path = _ensure_output_dir(Path(output_dir))
    ec = ERROR_CORRECTION_LEVELS.get(error_correction.upper(), ERROR_CORRECT_H)
    fg = _parse_color(fg_color)
    bg = _parse_color(bg_color)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=SquareModuleDrawer(),
        color_mask=SolidFillColorMask(
            back_color=bg,
            front_color=fg,
        ),
    )

    if filename:
        save_path = out_path / f"{filename}.{output_format}"
    else:
        save_path = _unique_filename(out_path, "qr_basic", output_format)

    img.save(str(save_path))
    logger.info("Saved basic QR → %s", save_path)

    return {
        "saved_path": str(save_path),
        "data": data[:200],
        "style": "basic",
        "fg_color": fg_color,
        "bg_color": bg_color,
        "size": size,
        "border": border,
        "error_correction": error_correction.upper(),
        "format": output_format,
    }


def generate_styled(
    data: str,
    *,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = DEFAULT_SIZE,
    border: int = DEFAULT_BORDER,
    module_shape: str = "square",
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    gradient_style: str = "solid",
    gradient_center_color: str | None = None,
    gradient_edge_color: str | None = None,
    error_correction: str = "H",
    output_format: str = DEFAULT_FORMAT,
) -> dict:
    """
    Generate a styled QR code with custom module shapes and color gradients.

    Parameters
    ----------
    data : the text or URL to encode
    module_shape : "square", "gapped", "circle", "rounded",
                   "vertical_bars", "horizontal_bars"
    gradient_style : "solid", "radial", "square", "horizontal", "vertical"
    gradient_center_color : center color for gradients (hex)
    gradient_edge_color : edge color for gradients (hex)
    fg_color : foreground color (used for solid style)
    bg_color : background color (hex)
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    out_path = _ensure_output_dir(Path(output_dir))
    ec = ERROR_CORRECTION_LEVELS.get(error_correction.upper(), ERROR_CORRECT_H)
    bg = _parse_color(bg_color)

    # Module drawer
    shape_key = module_shape.lower()
    if shape_key not in MODULE_SHAPES:
        raise ValueError(
            f"Unknown module_shape '{module_shape}'. "
            f"Choose from: {', '.join(MODULE_SHAPES)}"
        )
    drawer = MODULE_SHAPES[shape_key]()

    # Color mask
    grad_key = gradient_style.lower()
    if grad_key not in GRADIENT_STYLES:
        raise ValueError(
            f"Unknown gradient_style '{gradient_style}'. "
            f"Choose from: {', '.join(GRADIENT_STYLES)}"
        )

    if grad_key == "solid":
        fg = _parse_color(fg_color)
        color_mask = SolidFillColorMask(back_color=bg, front_color=fg)
    else:
        center = _parse_color(gradient_center_color or fg_color)
        edge = _parse_color(gradient_edge_color or "#000088")
        GradientClass = GRADIENT_STYLES[grad_key]
        if grad_key == "horizontal":
            color_mask = GradientClass(back_color=bg, left_color=center, right_color=edge)
        elif grad_key == "vertical":
            color_mask = GradientClass(back_color=bg, top_color=center, bottom_color=edge)
        else:
            color_mask = GradientClass(back_color=bg, center_color=center, edge_color=edge)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=color_mask,
    )

    if filename:
        save_path = out_path / f"{filename}.{output_format}"
    else:
        save_path = _unique_filename(out_path, f"qr_{shape_key}_{grad_key}", output_format)

    img.save(str(save_path))
    logger.info("Saved styled QR → %s", save_path)

    return {
        "saved_path": str(save_path),
        "data": data[:200],
        "style": "styled",
        "module_shape": shape_key,
        "gradient_style": grad_key,
        "fg_color": fg_color,
        "bg_color": bg_color,
        "size": size,
        "border": border,
        "error_correction": error_correction.upper(),
        "format": output_format,
    }


def generate_with_logo(
    data: str,
    logo_path: str,
    *,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = DEFAULT_SIZE,
    border: int = DEFAULT_BORDER,
    module_shape: str = "square",
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    logo_size_ratio: float = 0.3,
    error_correction: str = "H",
    output_format: str = DEFAULT_FORMAT,
) -> dict:
    """
    Generate a QR code with an embedded logo/image in the center.

    Parameters
    ----------
    data : the text or URL to encode
    logo_path : path to a logo image file (PNG, JPG, etc.)
    logo_size_ratio : how much of the QR the logo covers (0.1–0.4, default 0.3)
    error_correction : forced to "H" for best logo tolerance

    Note: Error correction is always set to H when using logos to ensure
    the QR remains scannable even with the logo covering part of it.
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    out_path = _ensure_output_dir(Path(output_dir))

    logo_file = Path(logo_path)
    if not logo_file.is_file():
        raise FileNotFoundError(f"Logo file not found: {logo_path}")

    # Force high error correction for logo overlay
    ec = ERROR_CORRECT_H
    fg = _parse_color(fg_color)
    bg = _parse_color(bg_color)

    shape_key = module_shape.lower()
    if shape_key not in MODULE_SHAPES:
        raise ValueError(
            f"Unknown module_shape '{module_shape}'. "
            f"Choose from: {', '.join(MODULE_SHAPES)}"
        )
    drawer = MODULE_SHAPES[shape_key]()

    logo_size_ratio = max(0.1, min(0.4, logo_size_ratio))

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=SolidFillColorMask(back_color=bg, front_color=fg),
    ).convert("RGBA")

    # Overlay logo
    logo = Image.open(logo_file).convert("RGBA")
    qr_width, qr_height = img.size
    logo_max = int(qr_width * logo_size_ratio)
    logo.thumbnail((logo_max, logo_max), Image.LANCZOS)

    # Center the logo with a white padding circle/rectangle behind it
    logo_w, logo_h = logo.size
    pad = int(logo_w * 0.1)

    # Draw a white rounded-rectangle background behind the logo
    bg_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(bg_layer)
    cx, cy = qr_width // 2, qr_height // 2
    rect = (
        cx - logo_w // 2 - pad,
        cy - logo_h // 2 - pad,
        cx + logo_w // 2 + pad,
        cy + logo_h // 2 + pad,
    )
    draw.rounded_rectangle(rect, radius=pad, fill=(255, 255, 255, 255))
    img = Image.alpha_composite(img, bg_layer)

    # Paste the logo
    logo_pos = (cx - logo_w // 2, cy - logo_h // 2)
    img.paste(logo, logo_pos, logo)

    # Convert to RGB for saving as PNG/JPEG
    final = img.convert("RGB")

    if filename:
        save_path = out_path / f"{filename}.{output_format}"
    else:
        save_path = _unique_filename(out_path, "qr_logo", output_format)

    final.save(str(save_path))
    logger.info("Saved logo QR → %s", save_path)

    return {
        "saved_path": str(save_path),
        "data": data[:200],
        "style": "logo",
        "logo_path": str(logo_file),
        "logo_size_ratio": logo_size_ratio,
        "module_shape": shape_key,
        "fg_color": fg_color,
        "bg_color": bg_color,
        "size": size,
        "border": border,
        "error_correction": "H",
        "format": output_format,
    }


def generate_with_background_image(
    data: str,
    image_path: str,
    *,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = DEFAULT_SIZE,
    border: int = DEFAULT_BORDER,
    module_shape: str = "circle",
    brightness: float = 1.5,
    error_correction: str = "H",
    output_format: str = DEFAULT_FORMAT,
) -> dict:
    """
    Generate a QR code with colors sampled from a background image.

    The modules of the QR code take on colors from the provided image,
    creating a beautiful blended effect. Great for branded QR codes.

    Parameters
    ----------
    data : the text or URL to encode
    image_path : path to the background image (PNG, JPG, etc.)
    brightness : contrast boost for readability (1.0–2.0, default 1.5)
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    out_path = _ensure_output_dir(Path(output_dir))

    img_file = Path(image_path)
    if not img_file.is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    ec = ERROR_CORRECTION_LEVELS.get(error_correction.upper(), ERROR_CORRECT_H)

    shape_key = module_shape.lower()
    if shape_key not in MODULE_SHAPES:
        raise ValueError(
            f"Unknown module_shape '{module_shape}'. "
            f"Choose from: {', '.join(MODULE_SHAPES)}"
        )
    drawer = MODULE_SHAPES[shape_key]()

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    color_mask = ImageColorMask(
        back_color=(255, 255, 255),
        color_mask_path=str(img_file),
    )

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=color_mask,
    )

    if filename:
        save_path = out_path / f"{filename}.{output_format}"
    else:
        save_path = _unique_filename(out_path, "qr_image", output_format)

    img.save(str(save_path))
    logger.info("Saved image-styled QR → %s", save_path)

    return {
        "saved_path": str(save_path),
        "data": data[:200],
        "style": "background_image",
        "image_path": str(img_file),
        "module_shape": shape_key,
        "size": size,
        "border": border,
        "error_correction": error_correction.upper(),
        "format": output_format,
    }


def generate_transparent(
    data: str,
    *,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = DEFAULT_SIZE,
    border: int = DEFAULT_BORDER,
    module_shape: str = "square",
    fg_color: str = "#000000",
    error_correction: str = "H",
) -> dict:
    """
    Generate a QR code with a transparent background (PNG with alpha).

    Perfect for overlaying on top of other designs or documents.

    Parameters
    ----------
    data : the text or URL to encode
    fg_color : foreground/module color (hex)
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    out_path = _ensure_output_dir(Path(output_dir))
    ec = ERROR_CORRECTION_LEVELS.get(error_correction.upper(), ERROR_CORRECT_H)
    fg = _parse_color(fg_color)

    shape_key = module_shape.lower()
    if shape_key not in MODULE_SHAPES:
        raise ValueError(
            f"Unknown module_shape '{module_shape}'. "
            f"Choose from: {', '.join(MODULE_SHAPES)}"
        )
    drawer = MODULE_SHAPES[shape_key]()

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Generate with white background first
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=SolidFillColorMask(
            back_color=(255, 255, 255),
            front_color=fg,
        ),
    ).convert("RGBA")

    # Make white pixels transparent
    pixels = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if r > 240 and g > 240 and b > 240:
                pixels[x, y] = (r, g, b, 0)

    if filename:
        save_path = out_path / f"{filename}.png"
    else:
        save_path = _unique_filename(out_path, "qr_transparent", "png")

    img.save(str(save_path), "PNG")
    logger.info("Saved transparent QR → %s", save_path)

    return {
        "saved_path": str(save_path),
        "data": data[:200],
        "style": "transparent",
        "fg_color": fg_color,
        "module_shape": shape_key,
        "size": size,
        "border": border,
        "error_correction": error_correction.upper(),
        "format": "png",
    }


def generate_gradient(
    data: str,
    *,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = DEFAULT_SIZE,
    border: int = DEFAULT_BORDER,
    module_shape: str = "square",
    gradient_style: str = "radial",
    center_color: str = "#FF0000",
    edge_color: str = "#0000FF",
    bg_color: str = "#FFFFFF",
    error_correction: str = "H",
    output_format: str = DEFAULT_FORMAT,
) -> dict:
    """
    Generate a QR code with a beautiful gradient fill.

    Parameters
    ----------
    data : the text or URL to encode
    gradient_style : "radial", "square", "horizontal", "vertical"
    center_color : the inner/starting gradient color (hex)
    edge_color : the outer/ending gradient color (hex)
    bg_color : background color (hex)
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    out_path = _ensure_output_dir(Path(output_dir))
    ec = ERROR_CORRECTION_LEVELS.get(error_correction.upper(), ERROR_CORRECT_H)
    bg = _parse_color(bg_color)
    center = _parse_color(center_color)
    edge = _parse_color(edge_color)

    shape_key = module_shape.lower()
    if shape_key not in MODULE_SHAPES:
        raise ValueError(
            f"Unknown module_shape '{module_shape}'. "
            f"Choose from: {', '.join(MODULE_SHAPES)}"
        )
    drawer = MODULE_SHAPES[shape_key]()

    grad_key = gradient_style.lower()
    valid_gradients = {"radial", "square", "horizontal", "vertical"}
    if grad_key not in valid_gradients:
        raise ValueError(
            f"Unknown gradient_style '{gradient_style}'. "
            f"Choose from: {', '.join(valid_gradients)}"
        )

    GradientClass = GRADIENT_STYLES[grad_key]
    if grad_key == "horizontal":
        color_mask = GradientClass(back_color=bg, left_color=center, right_color=edge)
    elif grad_key == "vertical":
        color_mask = GradientClass(back_color=bg, top_color=center, bottom_color=edge)
    else:
        color_mask = GradientClass(back_color=bg, center_color=center, edge_color=edge)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=color_mask,
    )

    if filename:
        save_path = out_path / f"{filename}.{output_format}"
    else:
        save_path = _unique_filename(out_path, f"qr_gradient_{grad_key}", output_format)

    img.save(str(save_path))
    logger.info("Saved gradient QR → %s", save_path)

    return {
        "saved_path": str(save_path),
        "data": data[:200],
        "style": "gradient",
        "gradient_style": grad_key,
        "center_color": center_color,
        "edge_color": edge_color,
        "bg_color": bg_color,
        "module_shape": shape_key,
        "size": size,
        "border": border,
        "error_correction": error_correction.upper(),
        "format": output_format,
    }


def get_capabilities() -> dict:
    """Return a summary of available QR styles, shapes, and options."""
    return {
        "module_shapes": list(MODULE_SHAPES.keys()),
        "gradient_styles": list(GRADIENT_STYLES.keys()),
        "error_correction_levels": {
            "L": "~7% recovery — smallest QR",
            "M": "~15% recovery — balanced",
            "Q": "~25% recovery — good for styling",
            "H": "~30% recovery — best for logos",
        },
        "output_formats": list(SUPPORTED_FORMATS),
        "qr_styles": [
            "basic — solid colors, clean look",
            "styled — custom shapes + optional gradients",
            "gradient — beautiful color gradient fills",
            "logo — embedded center image/logo",
            "background_image — modules colored from an image",
            "transparent — PNG with transparent background",
        ],
        "defaults": {
            "size": DEFAULT_SIZE,
            "border": DEFAULT_BORDER,
            "format": DEFAULT_FORMAT,
            "output_dir": DEFAULT_OUTPUT_DIR,
            "error_correction": "H",
        },
    }
