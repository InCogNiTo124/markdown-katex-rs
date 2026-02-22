import re
import json
import base64
import typing as typ
import hashlib
import logging

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor

from markdown_katex_rs.html import KATEX_STYLES
from markdown_katex_rs import _rust

logger = logging.getLogger(__name__)

SVG_ELEM_RE = re.compile(r"<svg.*?</svg>", flags=re.MULTILINE | re.DOTALL)
SVG_XMLNS = 'xmlns="http://www.w3.org/2000/svg" ' + 'xmlns:xlink="http://www.w3.org/1999/xlink" '
B64IMG_TMPL = '<img src="data:image/svg+xml;base64,{img_text}"/>'

FENCE_RE       = re.compile(r"^(\s*)(`{3,}|~{3,})")
BLOCK_START_RE = re.compile(r"^(\s*)(`{3,}|~{3,})math")
BLOCK_CLEAN_RE = re.compile(r"^(\s*)(`{3,}|~{3,})math(.*)(\2)$", flags=re.DOTALL)

def _clean_block_text(block_text: str) -> str:
    block_match = BLOCK_CLEAN_RE.match(block_text)
    if block_match:
        return block_match.group(3)
    else:
        return block_text

def make_marker_id(text: str) -> str:
    data = text.encode("utf-8")
    return hashlib.md5(data).hexdigest()

def svg2img(html: str) -> str:
    while True:
        match = SVG_ELEM_RE.search(html)
        if match:
            svg_text = match.group(0)
            if "xmlns" not in svg_text:
                svg_text = svg_text.replace("<svg ", "<svg " + SVG_XMLNS)
            svg_data = svg_text.encode("utf-8")
            img_b64_data: bytes = base64.standard_b64encode(svg_data)
            img_b64_text = img_b64_data.decode("utf-8")
            img_b64_tag  = B64IMG_TMPL.format(img_text=img_b64_text)
            start, end = match.span()
            html = html[:start] + img_b64_tag + html[end:]
        else:
            break
    return html

def tex2html(tex: str, options: typ.Optional[typ.Dict[str, typ.Any]] = None) -> str:
    options = options or {}
    no_inline_svg = options.get("no_inline_svg", False)
    display_mode = options.get("display-mode", False)

    result = _rust.render_math(tex, display_mode)
    if no_inline_svg:
        result = svg2img(result)
    return result

def md_block2html(block_text: str, default_options: typ.Optional[typ.Dict[str, typ.Any]] = None) -> str:
    options = {'display-mode': True}
    if default_options:
        options.update(default_options)

    block_text = _clean_block_text(block_text)
    header, rest = block_text.split("\n", 1) if "\n" in block_text else ("", block_text)
    if "{" in header and "}" in header:
        try:
            options.update(json.loads(header))
            block_text = rest
        except json.JSONDecodeError:
            pass

    return tex2html(block_text, options)

def _clean_inline_text(inline_text: str) -> str:
    for prefix in ("$``", "$`"):
        if inline_text.startswith(prefix):
            inline_text = inline_text[len(prefix):]
            break
    for suffix in ("``$", "`$"):
        if inline_text.endswith(suffix):
            inline_text = inline_text[:-len(suffix)]
            break
    return inline_text

def md_inline2html(inline_text: str, default_options: typ.Optional[typ.Dict[str, typ.Any]] = None) -> str:
    options = default_options.copy() if default_options else {}
    inline_text = _clean_inline_text(inline_text)
    return tex2html(inline_text, options)

INLINE_DELIM_RE = re.compile(r"`{1,2}")

class InlineCodeItem(typ.NamedTuple):
    inline_text: str
    start      : int
    end        : int

def iter_inline_katex(line: str) -> typ.Iterable[InlineCodeItem]:
    pos = 0
    while True:
        inline_match_start = INLINE_DELIM_RE.search(line, pos)
        if inline_match_start is None:
            break

        pos   = inline_match_start.end()
        start = inline_match_start.start()
        delim = inline_match_start.group()

        try:
            end = line.index(delim, start + len(delim)) + (len(delim) - 1)
        except ValueError:
            continue

        pos = end

        if start == 0 or end + 1 >= len(line):
            continue

        if line[start - 1] != "$":
            continue
        if line[end + 1] != "$":
            continue

        inline_text = line[start - 1 : end + 2]
        pos         = end + len(delim)

        yield InlineCodeItem(inline_text, start - 1, end + 2)

class KatexExtension(Extension):
    def __init__(self, **kwargs) -> None:
        self.config = {
            'no_inline_svg'   : ["", "Replace inline <svg> with <img> tags."],
            'insert_fonts_css': ["", "Insert font loading stylesheet."],
        }
        self.options = {}
        for name in self.config:
            val = kwargs.get(name, self.getConfig(name, ""))
            if val != "":
                self.options[name] = val
        self.math_html = {}
        super().__init__(**kwargs)

    def reset(self) -> None:
        self.math_html.clear()

    def extendMarkdown(self, md) -> None:
        preproc = KatexPreprocessor(md, self)
        md.preprocessors.register(preproc, name='katex_fenced_code_block', priority=50)

        postproc = KatexPostprocessor(md, self)
        md.postprocessors.register(postproc, name='katex_fenced_code_block', priority=0)
        md.registerExtension(self)


class KatexPreprocessor(Preprocessor):
    def __init__(self, md, ext: KatexExtension) -> None:
        super().__init__(md)
        self.ext = ext

    def _make_tag_for_block(self, block_lines: typ.List[str]) -> str:
        indent_len  = len(block_lines[0]) - len(block_lines[0].lstrip())
        indent_text = block_lines[0][:indent_len]

        block_text = "\n".join(line[indent_len:] for line in block_lines).rstrip()
        marker_id  = make_marker_id("block" + block_text)
        marker_tag = f"tmp_block_md_katex_{marker_id}"

        math_html = md_block2html(block_text, self.ext.options)
        self.ext.math_html[marker_tag] = f"<p>{math_html}</p>"
        return indent_text + marker_tag

    def _make_tag_for_inline(self, inline_text: str) -> str:
        marker_id  = make_marker_id("inline" + inline_text)
        marker_tag = f"tmp_inline_md_katex_{marker_id}"

        math_html = md_inline2html(inline_text, self.ext.options)
        self.ext.math_html[marker_tag] = math_html
        return marker_tag

    def _iter_out_lines(self, lines: typ.List[str]) -> typ.Iterable[str]:
        is_in_math_fence     = False
        is_in_fence          = False
        expected_close_fence = "```"
        block_lines = []

        for line in lines:
            if is_in_fence:
                yield line
                if line.rstrip() == expected_close_fence:
                    is_in_fence = False
            elif is_in_math_fence:
                block_lines.append(line)
                if line.rstrip() == expected_close_fence:
                    is_in_math_fence = False
                    marker_tag       = self._make_tag_for_block(block_lines)
                    block_lines.clear()
                    yield marker_tag
            else:
                math_fence_match = BLOCK_START_RE.match(line)
                fence_match      = FENCE_RE.match(line)
                if math_fence_match:
                    is_in_math_fence     = True
                    prefix               = math_fence_match.group(1)
                    expected_close_fence = prefix + math_fence_match.group(2)
                    block_lines.append(line)
                elif fence_match:
                    is_in_fence          = True
                    prefix               = fence_match.group(1)
                    expected_close_fence = prefix + fence_match.group(2)
                    yield line
                else:
                    inline_codes = list(iter_inline_katex(line))
                    for code in reversed(inline_codes):
                        marker_tag = self._make_tag_for_inline(code.inline_text)
                        line       = line[: code.start] + marker_tag + line[code.end :]
                    yield line

        if block_lines:
            for line in block_lines:
                yield line

    def run(self, lines: typ.List[str]) -> typ.List[str]:
        return list(self._iter_out_lines(lines))


class KatexPostprocessor(Postprocessor):
    def __init__(self, md, ext: KatexExtension) -> None:
        super().__init__(md)
        self.ext = ext

    def run(self, text: str) -> str:
        if any(marker in text for marker in self.ext.math_html):
            insert_fonts_css = self.ext.options.get("insert_fonts_css", True)

            if insert_fonts_css and KATEX_STYLES not in text:
                text = KATEX_STYLES + text

            for marker, html in self.ext.math_html.items():
                is_block  = marker.startswith("tmp_block_md_katex_")
                if marker in text:
                    wrapped_marker = f"<p>{marker}</p>" if is_block else marker
                    while marker in text:
                        if wrapped_marker in text:
                            text = text.replace(wrapped_marker, html)
                        else:
                            text = text.replace(marker, html)
                else:
                    logger.warning(f"KatexPostprocessor couldn't find: {marker}")

        return text
