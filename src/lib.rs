use pyo3::prelude::*;
use katex::{KatexContext, Settings};

/// Formats a block of LaTeX math using KaTeX.
#[pyfunction]
#[pyo3(signature = (math, display_mode=false))]
fn render_math(math: &str, display_mode: bool) -> PyResult<String> {
    let ctx = KatexContext::default();
    let mut settings = Settings::default();
    settings.display_mode = display_mode;
    
    match katex::render_to_string(&ctx, math, &settings) {
        Ok(html) => Ok(html),
        Err(e) => Err(pyo3::exceptions::PyValueError::new_err(format!("KaTeX error: {:?}", e))),
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render_math, m)?)?;
    Ok(())
}
