"""Step-by-step printing utilities for calculus operations."""
import sympy
from contextlib import contextmanager
from sympy import latex


def functionnames(numterms):
    """Generate function names (f, g, h, ...) for multi-term expressions."""
    if numterms <= 3:
        return ["f", "g", "h"][:numterms]
    return [f"f_{i}" for i in range(numterms)]


def replace_u_var(rule, old_u, new_u):
    """Replace a variable in a rule with a new variable."""
    d = rule._asdict()
    for field, val in d.items():
        if isinstance(val, sympy.Basic):
            d[field] = val.subs(old_u, new_u)
        elif isinstance(val, tuple):
            d[field] = replace_u_var(val, old_u, new_u)
        elif isinstance(val, list):
            d[field] = [replace_u_var(item, old_u, new_u) if isinstance(item, tuple) 
                        else item for item in val]
    return rule.__class__(**d)


class Printer:
    """Base class for step-by-step output printers."""
    
    def __init__(self):
        self.lines = []
        self.level = 0

    def append(self, text):
        self.lines.append(self.level * "\t" + text)

    def finalize(self):
        return "\n".join(self.lines)

    def format_math(self, math):
        return str(math)

    def format_math_display(self, math):
        return self.format_math(math)

    @contextmanager
    def new_level(self):
        self.level += 1
        yield self.level
        self.level -= 1

    @contextmanager
    def new_step(self):
        yield self.level
        self.lines.append('\n')


class LaTeXPrinter(Printer):
    """Printer that formats math as LaTeX."""
    
    def format_math(self, math):
        return latex(math)


class HTMLPrinter(LaTeXPrinter):
    """Printer that outputs HTML with embedded LaTeX for MathJax 3."""
    
    def __init__(self):
        super().__init__()
        self.lines = ['<ol id="changedisplaytonone">']
        self.u = self.du = None

    def format_math(self, math):
        return f'\\({latex(math)}\\)'

    def format_math_display(self, math):
        math_latex = math if isinstance(math, str) else latex(math)
        return f'\\[{math_latex}\\]'

    @contextmanager
    def new_level(self):
        indent = ' ' * 4 * self.level
        self.level += 1
        self.lines.append(f'{indent}<div class="collapsible"><h2>open</h2><ol class="content">')
        yield
        self.lines.append(f'{indent}</ol></div>')
        self.level -= 1

    @contextmanager
    def new_step(self):
        indent = ' ' * 4 * self.level
        self.lines.append(f'{indent}<li>')
        yield self.level
        self.lines.append(f'{indent}</li>')

    @contextmanager
    def new_collapsible(self):
        indent = ' ' * 4 * self.level
        self.lines.append(f'{indent}<div target="_blank" id="change_to_invisible">')
        yield self.level
        self.lines.append(f'{indent}</div>')

    @contextmanager
    def new_u_vars(self):
        self.u, self.du = sympy.Symbol('u'), sympy.Symbol('du')
        yield self.u, self.du

    def append(self, text):
        indent = ' ' * 4 * (self.level + 1)
        self.lines.append(f'{indent}<p>{text}</p>')

    def append_header(self, text):
        indent = ' ' * 4 * (self.level + 1)
        self.lines.append(f'{indent}<h2>{text}</h2>')
