"""
qrcode-mcp MCP Server — generate awesome, stylish QR codes.

Tools exposed:
  • generate_qr             — basic QR code with custom colors
  • generate_styled_qr      — custom shapes + gradient fills
  • generate_gradient_qr    — beautiful gradient QR codes
  • generate_logo_qr        — QR code with embedded center logo
  • generate_image_qr       — QR colored from a background image
  • generate_transparent_qr — PNG with transparent background
  • list_qr_styles          — list all available styles and options
"""

from __future__ import annotations

import logging
import sys

from fastmcp import FastMCP

from qrcode_mcp.generator import (
    generate_basic,
    generate_styled,
    generate_gradient,
    generate_with_logo,
    generate_with_background_image,
    generate_transparent,
    get_capabilities,
    DEFAULT_SIZE,
    DEFAULT_BORDER,
    DEFAULT_FORMAT,
    DEFAULT_OUTPUT_DIR,
    MODULE_SHAPES,
    GRADIENT_STYLES,
    ERROR_CORRECTION_LEVELS,
)

logger = logging.getLogger("qrcode_mcp")

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="qrcode-mcp",
    instructions=(
        "An MCP server that generates awesome QR codes with custom styles. "
        "Create QR codes with custom colors, gradients, embedded logos, "
        "artistic shapes (circles, rounded, bars), background images, and "
        "transparent PNGs. Just provide the data to encode and pick a style."
    ),
)

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def generate_qr(
    data: str,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = 10,
    border: int = 2,
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    error_correction: str = "H",
    output_format: str = "png",
) -> dict:
    """Generate a basic QR code with custom foreground and background colors.

    Parameters
    ----------
    data : str
        The text, URL, or data to encode in the QR code.
    output_dir : str, optional
        Directory where the QR image will be saved.
        Defaults to ~/Downloads/qrcode_mcp (configurable in pyproject.toml).
    filename : str, optional
        Custom filename (without extension). Auto-generated if omitted.
    size : int, optional
        Pixel size of each QR module/dot (default: 10). Larger = bigger image.
    border : int, optional
        Number of blank modules around the QR (default: 2). Minimum 1.
    fg_color : str, optional
        Foreground (module) color in hex, e.g. "#000000" (black), "#FF0000" (red).
    bg_color : str, optional
        Background color in hex, e.g. "#FFFFFF" (white), "#F0F0F0" (light gray).
    error_correction : str, optional
        Error tolerance: "L" (~7%), "M" (~15%), "Q" (~25%), "H" (~30%, default).
        Higher = more data redundancy = survives more damage/obstruction.
    output_format : str, optional
        Output format — "png" (default) or "svg".

    Returns
    -------
    dict
        - saved_path: path to the generated QR image
        - data: the encoded content (truncated)
        - style, fg_color, bg_color, size, border, error_correction, format
    """
    return generate_basic(
        data,
        output_dir=output_dir,
        filename=filename,
        size=size,
        border=border,
        fg_color=fg_color,
        bg_color=bg_color,
        error_correction=error_correction,
        output_format=output_format,
    )


@mcp.tool()
def generate_styled_qr(
    data: str,
    module_shape: str = "circle",
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = 10,
    border: int = 2,
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    gradient_style: str = "solid",
    gradient_center_color: str | None = None,
    gradient_edge_color: str | None = None,
    error_correction: str = "H",
    output_format: str = "png",
) -> dict:
    """Generate a styled QR code with custom module shapes and optional gradients.

    Parameters
    ----------
    data : str
        The text, URL, or data to encode.
    module_shape : str, optional
        Shape of each QR module/dot:
        - "square" — classic square modules
        - "gapped" — squares with gaps between them
        - "circle" — circular dots (default, modern look)
        - "rounded" — squares with rounded corners
        - "vertical_bars" — vertical bar style
        - "horizontal_bars" — horizontal bar style
    gradient_style : str, optional
        Color fill style:
        - "solid" — single solid color (default)
        - "radial" — radial gradient from center
        - "square" — square gradient from center
        - "horizontal" — left-to-right gradient
        - "vertical" — top-to-bottom gradient
    gradient_center_color : str, optional
        Center/start color for gradients (hex). Uses fg_color if omitted.
    gradient_edge_color : str, optional
        Edge/end color for gradients (hex). Defaults to "#000088".

    Returns
    -------
    dict
        - saved_path, data, style, module_shape, gradient_style, colors, etc.
    """
    return generate_styled(
        data,
        output_dir=output_dir,
        filename=filename,
        size=size,
        border=border,
        module_shape=module_shape,
        fg_color=fg_color,
        bg_color=bg_color,
        gradient_style=gradient_style,
        gradient_center_color=gradient_center_color,
        gradient_edge_color=gradient_edge_color,
        error_correction=error_correction,
        output_format=output_format,
    )


@mcp.tool()
def generate_gradient_qr(
    data: str,
    gradient_style: str = "radial",
    center_color: str = "#FF0000",
    edge_color: str = "#0000FF",
    module_shape: str = "square",
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = 10,
    border: int = 2,
    bg_color: str = "#FFFFFF",
    error_correction: str = "H",
    output_format: str = "png",
) -> dict:
    """Generate a QR code with a beautiful gradient color fill.

    Parameters
    ----------
    data : str
        The text, URL, or data to encode.
    gradient_style : str, optional
        Gradient type:
        - "radial" — circular gradient from center outward (default)
        - "square" — square gradient from center outward
        - "horizontal" — left-to-right gradient
        - "vertical" — top-to-bottom gradient
    center_color : str, optional
        The inner/starting color of the gradient (hex, default "#FF0000" red).
    edge_color : str, optional
        The outer/ending color of the gradient (hex, default "#0000FF" blue).
    module_shape : str, optional
        Module shape — "square", "circle", "rounded", "gapped",
        "vertical_bars", "horizontal_bars".

    Returns
    -------
    dict
        - saved_path, data, style, gradient details, colors, etc.
    """
    return generate_gradient(
        data,
        output_dir=output_dir,
        filename=filename,
        size=size,
        border=border,
        module_shape=module_shape,
        gradient_style=gradient_style,
        center_color=center_color,
        edge_color=edge_color,
        bg_color=bg_color,
        error_correction=error_correction,
        output_format=output_format,
    )


@mcp.tool()
def generate_logo_qr(
    data: str,
    logo_path: str,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = 10,
    border: int = 2,
    module_shape: str = "square",
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    logo_size_ratio: float = 0.3,
    output_format: str = "png",
) -> dict:
    """Generate a QR code with an embedded logo/image in the center.

    The logo is placed in the center of the QR code with a clean white
    padding behind it. Error correction is automatically set to H (highest)
    to ensure the QR remains scannable despite the logo overlay.

    Parameters
    ----------
    data : str
        The text, URL, or data to encode.
    logo_path : str
        Absolute path to the logo image file (PNG, JPG, WEBP, etc.).
    module_shape : str, optional
        Module shape — "square" (default), "circle", "rounded", etc.
    fg_color : str, optional
        Module color (hex, default "#000000" black).
    bg_color : str, optional
        Background color (hex, default "#FFFFFF" white).
    logo_size_ratio : float, optional
        How much of the QR the logo covers (0.1–0.4, default 0.3).
        Larger logos look bolder but reduce scan reliability.

    Returns
    -------
    dict
        - saved_path, data, style, logo_path, logo_size_ratio, etc.
    """
    return generate_with_logo(
        data,
        logo_path,
        output_dir=output_dir,
        filename=filename,
        size=size,
        border=border,
        module_shape=module_shape,
        fg_color=fg_color,
        bg_color=bg_color,
        logo_size_ratio=logo_size_ratio,
        output_format=output_format,
    )


@mcp.tool()
def generate_image_qr(
    data: str,
    image_path: str,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = 10,
    border: int = 2,
    module_shape: str = "circle",
    error_correction: str = "H",
    output_format: str = "png",
) -> dict:
    """Generate a QR code with modules colored from a background image.

    Each QR module takes its color from the corresponding pixel in the
    provided image, creating a beautiful blended/branded effect.
    Great for using photos, textures, or brand artwork as the QR fill.

    Parameters
    ----------
    data : str
        The text, URL, or data to encode.
    image_path : str
        Absolute path to the background image (PNG, JPG, WEBP, etc.).
        The image is stretched to fill the QR area.
    module_shape : str, optional
        Module shape — "circle" (default), "square", "rounded", etc.

    Returns
    -------
    dict
        - saved_path, data, style, image_path, module_shape, etc.
    """
    return generate_with_background_image(
        data,
        image_path,
        output_dir=output_dir,
        filename=filename,
        size=size,
        border=border,
        module_shape=module_shape,
        error_correction=error_correction,
        output_format=output_format,
    )


@mcp.tool()
def generate_transparent_qr(
    data: str,
    output_dir: str | None = None,
    filename: str | None = None,
    size: int = 10,
    border: int = 2,
    module_shape: str = "square",
    fg_color: str = "#000000",
    error_correction: str = "H",
) -> dict:
    """Generate a QR code with a transparent background (PNG with alpha channel).

    Perfect for overlaying on top of other designs, documents, or images.
    Always outputs as PNG (the only format supporting transparency).

    Parameters
    ----------
    data : str
        The text, URL, or data to encode.
    module_shape : str, optional
        Module shape — "square" (default), "circle", "rounded", etc.
    fg_color : str, optional
        Module color (hex, default "#000000" black).

    Returns
    -------
    dict
        - saved_path, data, style, fg_color, module_shape, format ("png"), etc.
    """
    return generate_transparent(
        data,
        output_dir=output_dir,
        filename=filename,
        size=size,
        border=border,
        module_shape=module_shape,
        fg_color=fg_color,
        error_correction=error_correction,
    )


@mcp.tool()
def list_qr_styles() -> dict:
    """List all available QR code styles, shapes, gradients, and options.

    Returns a comprehensive reference of everything this server can do:
    - Available module shapes (square, circle, rounded, bars, etc.)
    - Gradient style options (radial, square, horizontal, vertical)
    - Error correction levels and their recovery rates
    - Output formats
    - Default settings
    """
    return get_capabilities()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run(verbose: bool = False) -> None:
    """Start the MCP server."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger.info("Starting qrcode-mcp MCP server v0.1.0")
    mcp.run()
