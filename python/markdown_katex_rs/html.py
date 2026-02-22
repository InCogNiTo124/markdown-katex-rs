_STYLESHEET_LINK = """
<link rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/katex@0.15.1/dist/katex.min.css"
  integrity="sha384-R4558gYOUz8mP9YWpZJjofhk+zx0AS11p36HnD2ZKj/6JR5z27gSSULCNHIRReVs"
  crossorigin="anonymous" />
"""

_KATEX_IMAGE_STYLES = """
<style type="text/css">
    .katex img {
      object-fit: fill;
      padding: unset;
      display: block;
      position: absolute;
      width: 100%;
      height: inherit;
    }
</style>
"""

KATEX_STYLES = _STYLESHEET_LINK + _KATEX_IMAGE_STYLES
