# markdown-katex-rs

A fast, Rust-backed [KaTeX](https://katex.org/) extension for the [Python Markdown](https://python-markdown.github.io/) library.

This project aspires to be a drop-in replacement for `mbarkhau/markdown-katex`. The main difference is, instead of shipping node and katex binaries, it's using the `katex-rs` crate via PyO3 for significantly improved rendering performance and smaller distribution size.

## Requirements

- Python 3.10+ 

## Installation

Once the package is published to PyPI, you can install it using `uv` (recommended) or `pip`:

```bash
uv add markdown-katex-rs
```

## Usage

Use it just like any other Python Markdown extension. It supports both inline math (`$` or `$``) and block math (fenced `math` code blocks).

```python
import markdown
from markdown_katex_rs import KatexRsExtension

text = r"""
This is inline math: $`a^2 + b^2 = c^2`$

This is block math:
```math
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
```
"""

# Render with the KatexRsExtension
md = markdown.Markdown(extensions=[KatexRsExtension()])
html = md.convert(text)

print(html)
```

## Local Development & Building

The project requires `uv` for Python dependency management and `cargo` / Rust for compiling the PyO3 extension.

```bash
# Clone the repository
git clone <your-repo-url>

# Setup your env and build the development wheel automatically
uv sync

# Run tests
uv run pytest -v
```

## CI/CD and Publishing

This project is configured with GitHub Actions to:
1. Automatically run the PyTest suite on every pull request or push to `main`.
2. Build cross-platform binary wheels via `maturin-action` and push them to PyPI seamlessly whenever a new GitHub Release is created.

To trigger a release to PyPI:
1. Update your version bumps in `Cargo.toml` and `pyproject.toml`.
2. Create and publish a new Release in the GitHub UI (i.e., `v0.1.0`).
3. The Action will automatically execute and handle the heavy lifting of publishing.


*(Note: The wheel filename will vary depending on your OS, Python version, and system architecture.)*



