import pytest
import markdown
from markdown_katex_rs import KatexRsExtension

def render(text):
    md = markdown.Markdown(extensions=[KatexRsExtension()])
    return md.convert(text)

BLOCK_MATH_CASES = [
    r"""```math
\begin{align*}
    f(x) &= a - \frac{ac}{x+c} =\\
         &= a\left(1 - \frac{c}{x+c}\right) =\\
         &= a\left(\frac{x+c}{x+c} - \frac{c}{x+c}\right) =\\
         &= \frac{ax}{x+c}
\end{align*}
```""",
    r"""```math
E = \sum_{i=1}^{N}{\left(y_i - f(x_i)\right)^2} = \sum_{i=1}^{N}{\left(y_i - \frac{x_i\left(e^c+1)\right)}{x_ie^c+1}\right)^2} 
```""",
    r"""```math
c_{n+1} \leftarrow c_n - \frac{\frac{\partial E}{\partial c}}{\frac{\partial^2 E}{\partial c^2}}
```""",
    r"""```math
\begin{align*}
\frac{d}{dx}K\left(x\right) &= \frac{d}{dx}\left(\frac{f''}{\left(1+f'^2\right)^\frac32}\right) = 0 \\
\frac{d}{dx}f''\cdot\left(1+f'^2\right)^{\frac32} &= f''\cdot\frac{d}{dx}\left(\left(1+f'^2\right)^{\frac32}\right) \\
f'''\left(1+f'^2\right)^{\frac32} &= f''\cdot\frac32\left(1+f'^2\right)^{\frac12}\cdot2f'f''\\
f'''\left(1+f'^2\right) &= 3f''^2f' \\
\end{align*}
```""",
    r"""```math
E\left[X\right] = -p\ln\left(p\right) - \left(1-p\right)\ln\left(1-p\right)
```""",
    r"""```math
\begin{align*}
f(x) &= \frac{x\left(e^c+1\right)}{xe^c+1} \\
f'(x) = \frac{d}{dx}f(x)&=\frac{e^c+1}{\left(xe^c+1\right)^2} \\
f''(x) = \frac{d}{dx}f'(x)&=-\frac{2e^c\left(e^c+1\right)}{\left(xe^c+1\right)^3} \\
f'''(x) = \frac{d}{dx}f''(x)&=\frac{6e^{2c}\left(e^c+1\right)}{\left(xe^c+1\right)^4} \\
\end{align*}
```""",
    r"""```math
\begin{align*}
1-x &= \frac{x\left(e^c+1\right)}{xe^c+1} \\
\left(1-x\right)\left(xe^c+1\right) &= x\left(e^c+1\right) \\
e^cx+1-e^cx^2-e^cx-x&=0 \\
e^cx^2+2x-1&=0 \\
\end{align*}
```""",
    r"""```math
\begin{align*}
\frac{d}{dx}f(x) &= 1 \\
\frac{d}{dx}\frac{x\left(e^c+1\right)}{xe^c+1} &= 1 \\
\frac{e^c+1}{\left(xe^c+1\right)^2} &= 1\\
\end{align*}
```""",
    r"""```math
f(x)=\frac{ex}{-\frac{7e^4}{180}x^4+\frac{e^3}{24}x^3-\frac{e^2}6x^2 + 1}
```""",
    r"""```math
f\left(x\right) = a+ \frac{b}{x+c}
```""",
]

INLINE_MATH_CASES = [
    r"""$`f(0)=0`$""",
    r"""$`\frac16`$""",
    r"""$`\lim_{c \rightarrow -\infty} = x`$""",
    r"""$`\frac{d}{dx}K\left(x\right) = 0`$""",
    r"""$`\textbf{x}`$""",
    r"""$`1-\frac1{x^2}`$""",
    r"""$`\frac1x`$""",
    r"""$`1=k-1-\text{(ddof)}`$""",
    r"""$`c \rightarrow \frac1{e^c}`$""",
    r"""$`y=1-x`$""",
]

@pytest.mark.parametrize("math_text", BLOCK_MATH_CASES)
def test_block_math_renders(math_text):
    html = render(math_text)
    assert 'class="katex-display"' in html
    assert '<math' in html

@pytest.mark.parametrize("math_text", INLINE_MATH_CASES)
def test_inline_math_renders(math_text):
    html = render(math_text)
    assert 'class="katex"' in html
    assert 'class="katex-display"' not in html
    assert '<math' in html
