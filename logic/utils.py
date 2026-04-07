"""Utilities for evaluating and formatting mathematical expressions."""
import collections
import traceback
import sys
import ast
import re
from io import StringIO
import sympy

OTHER_SYMPY_FUNCTIONS = ('sqrt',)

Arguments = collections.namedtuple('Arguments', 'function args kwargs')


class Eval:
    """Evaluates Python/SymPy expressions in a namespace."""
    
    def __init__(self, namespace=None):
        self._namespace = namespace or {}

    def get(self, name):
        return self._namespace.get(name)

    def set(self, name, value):
        self._namespace[name] = value

    def eval_node(self, node):
        tree = ast.fix_missing_locations(ast.Expression(node))
        return eval(compile(tree, '<string>', 'eval'), self._namespace)

    def eval(self, x, use_none_for_exceptions=False, repr_expression=True):
        try:
            x = x.strip().replace("\r", "")
            lines = x.split('\n')
            if not lines:
                return ''
            
            # Split into exec part and final eval expression
            setup = '\n'.join(lines[:-1]) + '\n'
            final = lines[-1]
            
            try:
                final_code = compile(final + '\n', '', 'eval')
            except SyntaxError:
                setup += '\n' + final
                final_code = None

            old_stdout = sys.stdout
            try:
                sys.stdout = StringIO()
                exec(compile(setup, '', 'exec'), self._namespace)

                if final_code:
                    result = eval(final_code, self._namespace)
                    result = repr(result) if repr_expression else result
                else:
                    result = ''

                if repr_expression:
                    sys.stdout.seek(0)
                    result = sys.stdout.read() + (result or '')
            finally:
                sys.stdout = old_stdout
            return result
        except Exception:
            if use_none_for_exceptions:
                return None
            return "".join(traceback.format_exception(*sys.exc_info()))


class LatexVisitor(ast.NodeVisitor):
    """Converts AST nodes to LaTeX representation."""
    
    EXCEPTIONS = {'integrate': sympy.Integral, 'diff': sympy.Derivative}
    formatters = {}

    @staticmethod
    def formats_function(name):
        def decorator(func):
            LatexVisitor.formatters[name] = func
            return func
        return decorator

    def format(self, name, node):
        formatter = self.formatters.get(name)
        return formatter(node, self) if formatter else None

    def visit_Call(self, node):
        fname = node.func.id

        if fname in self.EXCEPTIONS:
            node.func.id = self.EXCEPTIONS[fname].__name__
            self.latex = sympy.latex(self.evaluator.eval_node(node))
        else:
            result = self.format(fname, node)
            if result:
                self.latex = result
            elif fname[0].islower() and fname not in OTHER_SYMPY_FUNCTIONS:
                args = []
                for arg in node.args:
                    if isinstance(arg, ast.Call) and getattr(arg.func, 'id', '')[0:1].islower():
                        args.append(self.visit_Call(arg))
                    else:
                        args.append(sympy.latex(self.evaluator.eval_node(arg)))
                self.latex = r"\mathrm{%s}(%s)" % (fname.replace('_', r'\_'), ', '.join(args))
            else:
                self.latex = sympy.latex(self.evaluator.eval_node(node))
        return self.latex


@LatexVisitor.formats_function('rsolve')
def format_rsolve(node, visitor):
    recurrence = sympy.latex(sympy.Eq(visitor.evaluator.eval_node(node.args[0]), 0))
    if len(node.args) == 3:
        conds = visitor.evaluator.eval_node(node.args[2])
        initconds = r'\\'.join('&' + sympy.latex(sympy.Eq(eq, val)) 
                                for eq, val in conds.items())
        return (r'\begin{align}&\mathrm{Solve~the~recurrence~}' + recurrence + 
                r'\\&\mathrm{with~initial~conditions}\\' + initconds + r'\end{align}')
    return r'\mathrm{Solve~the~recurrence~}' + recurrence


@LatexVisitor.formats_function('summation')
@LatexVisitor.formats_function('product')
def format_sum_product(node, visitor):
    klass = sympy.Sum if node.func.id == 'summation' else sympy.Product
    return sympy.latex(klass(*map(visitor.evaluator.eval_node, node.args)))


@LatexVisitor.formats_function('help')
def format_help(node, visitor):
    if node.args:
        func = visitor.evaluator.eval_node(node.args[0])
        return r'\mathrm{Show~documentation~for~}' + func.__name__
    return r'\mathrm{Show~documentation~(requires~1~argument)}'


class TopCallVisitor(ast.NodeVisitor):
    """Extracts the top-level function call from an AST."""
    
    def __init__(self):
        self.call = None

    def visit_Call(self, node):
        self.call = node

    def visit_Name(self, node):
        if not self.call:
            self.call = node


def ordinal(n):
    """Return ordinal suffix for a number (1st, 2nd, 3rd, etc.)."""
    if 10 <= n % 100 < 20:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')


def latexify(string, evaluator):
    """Convert a string expression to LaTeX."""
    visitor = LatexVisitor()
    visitor.evaluator = evaluator
    visitor.visit(ast.parse(string))
    return visitor.latex


def topcall(string):
    """Get the name of the top-level function call in a string."""
    visitor = TopCallVisitor()
    visitor.visit(ast.parse(string))
    return getattr(getattr(visitor.call, 'func', None), 'id', None) if visitor.call else None


def arguments(string_or_node, evaluator):
    """Extract function arguments from a string or AST node."""
    if not isinstance(string_or_node, ast.Call):
        visitor = TopCallVisitor()
        visitor.visit(ast.parse(string_or_node))
        node = visitor.call
    else:
        node = string_or_node

    if not node:
        return None
        
    if isinstance(node, ast.Call):
        name = getattr(node.func, 'id', None)
        args = list(map(evaluator.eval_node, node.args)) if node.args else None
        kwargs = {kw.arg: evaluator.eval_node(kw.value) for kw in node.keywords} if node.keywords else None
        return Arguments(name, args, kwargs)
    elif isinstance(node, ast.Name):
        return Arguments(node.id, [], {})
    return None


_RE_SYMPY_CALLS = re.compile(
    r'(Integer|Symbol|Float|Rational)\s*\([\'\"]?([a-zA-Z0-9\.]+)[\'\"]?\s*\)')


def removeSymPy(string):
    """Remove SymPy wrapper calls from a string representation."""
    return _RE_SYMPY_CALLS.sub(r'\2', string)

