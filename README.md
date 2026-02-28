# qrcode-mcp

An MCP (Model Context Protocol) server that generates **awesome QR codes** — with custom colors, gradients, logos, artistic shapes, and more. Like *Save QR As…* for AI agents.

Give it any text or URL and it will generate a beautiful, scannable QR code image. Powered by [qrcode](https://github.com/lincolnloop/python-qrcode) and [Pillow](https://pillow.readthedocs.io/).

## ✨ Features

- **6 QR styles** — basic, styled, gradient, logo, background image, transparent
- **6 module shapes** — square, gapped, circle, rounded, vertical bars, horizontal bars
- **5 gradient styles** — solid, radial, square, horizontal, vertical
- **Logo overlay** — embed any image in the center with auto-padding
- **Image fill** — color QR modules from a background photo or texture
- **Transparent PNGs** — for overlaying on other designs
- **Custom colors** — any hex color for foreground, background, gradients
- **4 error correction levels** — L, M, Q, H
- **Seven MCP tools** — `generate_qr`, `generate_styled_qr`, `generate_gradient_qr`, `generate_logo_qr`, `generate_image_qr`, `generate_transparent_qr`, `list_qr_styles`
- **Cross-platform** — Windows, macOS, Linux
- **Zero config** — works out of the box

## 🚀 Quick Start

### Run directly from GitHub

```bash
uvx --from git+https://github.com/muldercw/qrcode_mcp.git qrcode-mcp
```

### Local development

```bash
git clone https://github.com/muldercw/qrcode_mcp.git
cd qrcode_mcp
uv pip install -e .
qrcode-mcp              # start the MCP server
qrcode-mcp --info       # print available styles & capabilities
qrcode-mcp --verbose    # debug logging
```

## 🔌 Integration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "qrcode-mcp": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/muldercw/qrcode_mcp.git",
        "qrcode-mcp"
      ]
    }
  }
}
```

### VS Code / Copilot

Add to your `.vscode/mcp.json`:

```json
{
  "servers": {
    "qrcode-mcp": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/muldercw/qrcode_mcp.git",
        "qrcode-mcp"
      ]
    }
  }
}
```

## 🎨 QR Code Styles

### Basic

Clean, classic QR code with solid colors.

```
"Generate a QR code for https://example.com with red modules on a white background"
```

### Styled (Custom Shapes)

Mix and match module shapes with optional gradients.

| Shape | Description |
|---|---|
| `square` | Classic square modules |
| `gapped` | Squares with gaps between them |
| `circle` | Circular dots — modern look |
| `rounded` | Squares with rounded corners |
| `vertical_bars` | Vertical bar pattern |
| `horizontal_bars` | Horizontal bar pattern |

### Gradient

Beautiful color transitions across the QR code.

| Gradient | Description |
|---|---|
| `radial` | Circular gradient from center outward |
| `square` | Square gradient from center outward |
| `horizontal` | Left-to-right gradient |
| `vertical` | Top-to-bottom gradient |

### Logo

Embed a company logo, icon, or image in the center. Error correction is automatically set to H for maximum resilience.

### Background Image

QR modules take colors from a provided image — great for photos, textures, or branded artwork.

### Transparent

PNG output with a transparent background, perfect for overlaying on other designs.

## 🛠 Tool Reference

### `generate_qr`

Generate a basic QR code with custom colors.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `string` | *(required)* | Text or URL to encode |
| `output_dir` | `string` | from config | Save directory |
| `filename` | `string` | auto | Custom filename (no extension) |
| `size` | `int` | `10` | Pixel size per module |
| `border` | `int` | `2` | Border modules around QR |
| `fg_color` | `string` | `"#000000"` | Foreground color (hex) |
| `bg_color` | `string` | `"#FFFFFF"` | Background color (hex) |
| `error_correction` | `string` | `"H"` | `"L"`, `"M"`, `"Q"`, or `"H"` |
| `output_format` | `string` | `"png"` | `"png"` or `"svg"` |

### `generate_styled_qr`

Generate a QR code with custom shapes and optional gradient fills.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `string` | *(required)* | Text or URL to encode |
| `module_shape` | `string` | `"circle"` | `"square"`, `"gapped"`, `"circle"`, `"rounded"`, `"vertical_bars"`, `"horizontal_bars"` |
| `gradient_style` | `string` | `"solid"` | `"solid"`, `"radial"`, `"square"`, `"horizontal"`, `"vertical"` |
| `gradient_center_color` | `string` | fg_color | Center color for gradients |
| `gradient_edge_color` | `string` | `"#000088"` | Edge color for gradients |

*Plus all common parameters: output_dir, filename, size, border, fg_color, bg_color, error_correction, output_format.*

### `generate_gradient_qr`

Generate a QR code with a beautiful gradient fill.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `string` | *(required)* | Text or URL to encode |
| `gradient_style` | `string` | `"radial"` | `"radial"`, `"square"`, `"horizontal"`, `"vertical"` |
| `center_color` | `string` | `"#FF0000"` | Inner/starting gradient color |
| `edge_color` | `string` | `"#0000FF"` | Outer/ending gradient color |
| `module_shape` | `string` | `"square"` | Module shape |

### `generate_logo_qr`

Generate a QR code with an embedded logo in the center.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `string` | *(required)* | Text or URL to encode |
| `logo_path` | `string` | *(required)* | Path to logo image file |
| `logo_size_ratio` | `float` | `0.3` | Logo coverage (0.1–0.4) |
| `module_shape` | `string` | `"square"` | Module shape |

### `generate_image_qr`

Generate a QR code with modules colored from a background image.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `string` | *(required)* | Text or URL to encode |
| `image_path` | `string` | *(required)* | Path to background image |
| `module_shape` | `string` | `"circle"` | Module shape |

### `generate_transparent_qr`

Generate a QR code with a transparent background (PNG).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | `string` | *(required)* | Text or URL to encode |
| `module_shape` | `string` | `"square"` | Module shape |
| `fg_color` | `string` | `"#000000"` | Module color (hex) |

### `list_qr_styles`

Returns a summary of all available styles, shapes, gradients, error correction levels, and default settings. No parameters.

## ⚙️ Configuration

All defaults are configurable in `pyproject.toml` under `[tool.qrcode-mcp]`:

```toml
[tool.qrcode-mcp]
output_dir = "qrcodes"              # relative to project root, or absolute path
default_size = 10                    # pixels per module
default_border = 2                   # border modules
default_format = "png"               # png or svg
```

If `output_dir` is a relative path, it is resolved relative to the directory containing `pyproject.toml`.

## 📋 Requirements

- **Python** ≥ 3.10
- **qrcode** ≥ 8.0 — QR code generation with styled image support
- **Pillow** ≥ 10.0 — image manipulation for logos, gradients, shapes
- **FastMCP** ≥ 2.0 — serves the MCP protocol

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Built for the MCP ecosystem. Contributions welcome!
