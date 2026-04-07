"""Step-by-step differentiation with HTML output."""
import sympy
import functools
from collections import namedtuple

from logic import stepprinter
from logic.stepprinter import functionnames, replace_u_var

from sympy.core.function import AppliedUndef
from sympy.functions.elementary.trigonometric import TrigonometricFunction
from sympy.strategies.core import switch


# Rule types for differentiation steps
def Rule(name, props=""):
    return namedtuple(name, props + " context symbol")

ConstantRule = Rule("ConstantRule", "number")
ConstantTimesRule = Rule("ConstantTimesRule", "constant other substep")
PowerRule = Rule("PowerRule", "base exp")
AddRule = Rule("AddRule", "substeps")
MulRule = Rule("MulRule", "terms substeps")
DivRule = Rule("DivRule", "numerator denominator numerstep denomstep")
ChainRule = Rule("ChainRule", "substep inner u_var innerstep")
TrigRule = Rule("TrigRule", "f")
ExpRule = Rule("ExpRule", "f base")
LogRule = Rule("LogRule", "arg base")
FunctionRule = Rule("FunctionRule")
AlternativeRule = Rule("AlternativeRule", "alternatives")
DontKnowRule = Rule("DontKnowRule")
RewriteRule = Rule("RewriteRule", "rewritten substep")

DerivativeInfo = namedtuple('DerivativeInfo', 'expr symbol')

# Evaluators for computing derivatives from rules
_evaluators = {}

def evaluates(rule):
    """Decorator to register an evaluator for a rule type."""
    def decorator(func):
        _evaluators[rule] = func
        return func
    return decorator


def diff(rule):
    """Evaluate a differentiation rule to get the result."""
    evaluator = _evaluators.get(rule.__class__)
    if not evaluator:
        raise ValueError("Cannot evaluate derivative")
    return evaluator(*rule)


# Rule evaluators
@evaluates(ConstantRule)
def eval_constant(*args):
    return 0

@evaluates(ConstantTimesRule)
def eval_constanttimes(constant, other, substep, expr, symbol):
    return constant * diff(substep)

@evaluates(AddRule)
def eval_add(substeps, expr, symbol):
    return sum(diff(step) for step in substeps)

@evaluates(DivRule)
def eval_div(numer, denom, numerstep, denomstep, expr, symbol):
    d_numer, d_denom = diff(numerstep), diff(denomstep)
    return (denom * d_numer - numer * d_denom) / (denom ** 2)

@evaluates(ChainRule)
def eval_chain(substep, inner, u_var, innerstep, expr, symbol):
    return diff(substep).subs(u_var, inner) * diff(innerstep)

@evaluates(MulRule)
def eval_mul(terms, substeps, expr, symbol):
    diffs = [diff(s) for s in substeps]
    return sum(diffs[i] * functools.reduce(lambda a, b: a * b, 
               [t for j, t in enumerate(terms) if j != i], 1) 
               for i in range(len(terms)))

@evaluates(TrigRule)
def eval_trig(*args):
    return sympy.trigsimp(eval_default(*args))

@evaluates(RewriteRule)
def eval_rewrite(rewritten, substep, expr, symbol):
    return diff(substep)

@evaluates(AlternativeRule)
def eval_alternative(alternatives, expr, symbol):
    return diff(alternatives[1])

@evaluates(PowerRule)
@evaluates(ExpRule)
@evaluates(LogRule)
@evaluates(DontKnowRule)
@evaluates(FunctionRule)
def eval_default(*args):
    func, symbol = args[-2], args[-1]
    if isinstance(func, sympy.Symbol):
        func = sympy.Pow(func, 1, evaluate=False)
    
    substitutions, mapping = [], {}
    constant_symbol = sympy.Dummy()
    for arg in func.args:
        if symbol in arg.free_symbols:
            mapping[symbol] = arg
            substitutions.append(symbol)
        else:
            mapping[constant_symbol] = arg
            substitutions.append(constant_symbol)
    
    rule = func.func(*substitutions).diff(symbol)
    return rule.subs(mapping)


# Rule generators
def diff_steps(expr, symbol):
    """Generate differentiation steps for an expression."""
    deriv = DerivativeInfo(expr, symbol)

    def key(d):
        e = d.expr
        if isinstance(e, TrigonometricFunction):
            return TrigonometricFunction
        if isinstance(e, AppliedUndef):
            return AppliedUndef
        if not e.has(symbol):
            return 'constant'
        return e.func

    return switch(key, {
        sympy.Pow: power_rule,
        sympy.Symbol: power_rule,
        sympy.Dummy: power_rule,
        sympy.Add: add_rule,
        sympy.Mul: mul_rule,
        TrigonometricFunction: trig_rule,
        sympy.exp: exp_rule,
        sympy.log: log_rule,
        AppliedUndef: function_rule,
        'constant': constant_rule
    })(deriv)


def power_rule(derivative):
    expr, symbol = derivative.expr, derivative.symbol
    base, exp = expr.as_base_exp()

    if not base.has(symbol):
        if isinstance(exp, sympy.Symbol):
            return ExpRule(expr, base, expr, symbol)
        u = sympy.Dummy()
        f = base ** u
        return ChainRule(ExpRule(f, base, f, u), exp, u, diff_steps(exp, symbol), expr, symbol)
    elif not exp.has(symbol):
        if isinstance(base, sympy.Symbol):
            return PowerRule(base, exp, expr, symbol)
        u = sympy.Dummy()
        f = u ** exp
        return ChainRule(PowerRule(u, exp, f, u), base, u, diff_steps(base, symbol), expr, symbol)
    return DontKnowRule(expr, symbol)


def add_rule(derivative):
    expr, symbol = derivative.expr, derivative.symbol
    return AddRule([diff_steps(arg, symbol) for arg in expr.args], expr, symbol)


def constant_rule(derivative):
    return ConstantRule(derivative.expr, derivative.expr, derivative.symbol)


def mul_rule(derivative):
    expr, symbol = derivative.expr, derivative.symbol
    coeff, f = expr.as_independent(symbol)
    
    if coeff != 1:
        return ConstantTimesRule(coeff, f, diff_steps(f, symbol), expr, symbol)
    
    numer, denom = expr.as_numer_denom()
    if denom != 1:
        return DivRule(numer, denom, diff_steps(numer, symbol), diff_steps(denom, symbol), expr, symbol)
    
    return MulRule(expr.args, [diff_steps(g, symbol) for g in expr.args], expr, symbol)


def trig_rule(derivative):
    expr, symbol = derivative.expr, derivative.symbol
    arg = expr.args[0]
    
    default = TrigRule(expr, expr, symbol)
    if not isinstance(arg, sympy.Symbol):
        u = sympy.Dummy()
        default = ChainRule(TrigRule(expr.func(u), expr.func(u), u), arg, u, diff_steps(arg, symbol), expr, symbol)

    if isinstance(expr, (sympy.sin, sympy.cos)):
        return default
    
    # Rewrite rules for other trig functions
    rewrites = {
        sympy.tan: [sympy.sin(arg) / sympy.cos(arg)],
        sympy.csc: [1 / sympy.sin(arg)],
        sympy.sec: [1 / sympy.cos(arg)],
        sympy.cot: [1 / sympy.tan(arg), sympy.cos(arg) / sympy.sin(arg)],
    }
    
    if expr.func in rewrites:
        alts = [default] + [RewriteRule(r, diff_steps(r, symbol), expr, symbol) for r in rewrites[expr.func]]
        return AlternativeRule(alts, expr, symbol)
    
    return DontKnowRule(expr, symbol)


def exp_rule(derivative):
    expr, symbol = derivative.expr, derivative.symbol
    exp_arg = expr.args[0]
    
    if isinstance(exp_arg, sympy.Symbol):
        return ExpRule(expr, sympy.E, expr, symbol)
    
    u = sympy.Dummy()
    f = sympy.exp(u)
    return ChainRule(ExpRule(f, sympy.E, f, u), exp_arg, u, diff_steps(exp_arg, symbol), expr, symbol)


def log_rule(derivative):
    expr, symbol = derivative.expr, derivative.symbol
    arg = expr.args[0]
    base = expr.args[1] if len(expr.args) == 2 else sympy.E
    
    if isinstance(arg, sympy.Symbol):
        return LogRule(arg, base, expr, symbol)
    
    u = sympy.Dummy()
    return ChainRule(LogRule(u, base, sympy.log(u, base), u), arg, u, diff_steps(arg, symbol), expr, symbol)


def function_rule(derivative):
    return FunctionRule(derivative.expr, derivative.symbol)


# Printer class for HTML output
class DiffPrinter(stepprinter.HTMLPrinter):
    """Generates HTML step-by-step differentiation output."""
    
    def __init__(self, rule):
        super().__init__()
        self.rule = rule
        self.alternative_functions_printed = set()
        self.print_rule(rule)

    def print_rule(self, rule):
        """Dispatch to appropriate print method."""
        method = getattr(self, f'print_{rule.__class__.__name__}', None)
        if method:
            method(rule)
        else:
            self.append(repr(rule))

    def print_ConstantRule(self, rule):
        with self.new_step():
            self.append(f"The derivative of the constant {self.format_math(rule.number)} is zero.")

    def print_PowerRule(self, rule):
        with self.new_step():
            self.append(f"Apply the power rule: {self.format_math(rule.context)} goes to {self.format_math(diff(rule))}")

    def print_ConstantTimesRule(self, rule):
        with self.new_step():
            self.append("The derivative of a constant times a function is the constant times the derivative of the function.")
            with self.new_level():
                self.print_rule(rule.substep)
            self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">So, the result is: ')
            self.append(self.format_math(diff(rule)) + '</ol></div>')

    def print_AddRule(self, rule):
        with self.new_step():
            self.append(f"Differentiate {self.format_math(rule.context)} term by term:")
            with self.new_level():
                for substep in rule.substeps:
                    self.print_rule(substep)
            self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">The result is: ')
            self.append(self.format_math(diff(rule)) + '</ol></div>')

    def print_MulRule(self, rule):
        with self.new_step():
            self.append("Apply the product rule:")
            fnames = [sympy.Function(n)(rule.symbol) for n in functionnames(len(rule.terms))]
            derivatives = [sympy.Derivative(f, rule.symbol) for f in fnames]
            
            ruleform = []
            for i in range(len(rule.terms)):
                parts = [derivatives[i] if j == i else fnames[j] for j in range(len(rule.terms))]
                ruleform.append(functools.reduce(lambda a, b: a * b, parts))
            
            self.append(self.format_math_display(sympy.Eq(
                sympy.Derivative(functools.reduce(lambda a, b: a * b, fnames), rule.symbol),
                sum(ruleform))))

            for fname, deriv, term, substep in zip(fnames, derivatives, rule.terms, rule.substeps):
                self.append(f"{self.format_math(sympy.Eq(fname, term))}; Now find {self.format_math(deriv)}:")
                with self.new_level():
                    self.print_rule(substep)
            
            self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">The result is:')
            self.append(self.format_math(diff(rule)) + '</ol></div>')

    def print_DivRule(self, rule):
        with self.new_step():
            x = rule.symbol
            ff, gg = sympy.Function("f")(x), sympy.Function("g")(x)
            qrule = sympy.Eq(sympy.Derivative(ff / gg, x), sympy.ratsimp(sympy.diff(ff / gg)))
            
            self.append("Apply the quotient rule:")
            self.append(self.format_math_display(qrule))
            self.append(f"{self.format_math(sympy.Eq(ff, rule.numerator))} and {self.format_math(sympy.Eq(gg, rule.denominator))}.")
            self.append(f"Find {self.format_math(ff.diff(x))}:")
            with self.new_level():
                self.print_rule(rule.numerstep)
            self.append(f"Find {self.format_math(gg.diff(x))}:")
            with self.new_level():
                self.print_rule(rule.denomstep)
            self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">Now plug in to get:')
            self.append(self.format_math(diff(rule)) + '</ol></div>')

    def print_ChainRule(self, rule):
        with self.new_step(), self.new_u_vars() as (u, _):
            self.append(f"Let {self.format_math(sympy.Eq(u, rule.inner))}.")
            self.print_rule(replace_u_var(rule.substep, rule.u_var, u))
        with self.new_step():
            if isinstance(rule.innerstep, FunctionRule):
                self.append(f"Now, before we apply the chain rule.<br><br> First find {self.format_math(sympy.Derivative(rule.inner, rule.symbol))}:")
                self.append(self.format_math_display(diff(rule)))
            else:
                self.append(f"Now, before we apply the chain rule. <br><br> First find {self.format_math(sympy.Derivative(rule.inner, rule.symbol))}:")
                with self.new_level():
                    self.print_rule(rule.innerstep)
                self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">The result of the chain rule is:')
                self.append(self.format_math(diff(rule)) + '</ol></div>')

    def print_TrigRule(self, rule):
        with self.new_step():
            messages = {
                sympy.sin: "The derivative of sine is cosine:",
                sympy.cos: "The derivative of cosine is negative sine:",
                sympy.sec: "The derivative of secant is secant times tangent:",
                sympy.csc: "The derivative of cosecant is negative cosecant times cotangent:",
            }
            if type(rule.f) in messages:
                self.append(messages[type(rule.f)])
            self.append(self.format_math_display(sympy.Eq(sympy.Derivative(rule.f, rule.symbol), diff(rule))))

    def print_ExpRule(self, rule):
        with self.new_step():
            if rule.base == sympy.E:
                self.append(f"The derivative of {self.format_math(sympy.exp(rule.symbol))} is itself.")
            else:
                self.append(self.format_math(sympy.Eq(sympy.Derivative(rule.f, rule.symbol), diff(rule))))

    def print_LogRule(self, rule):
        with self.new_step():
            self.append(f"The derivative of {self.format_math(rule.context)} is {self.format_math(diff(rule))}.")

    def print_AlternativeRule(self, rule):
        if rule.context.func in self.alternative_functions_printed:
            self.print_rule(rule.alternatives[0])
        elif len(rule.alternatives) == 2:
            self.alternative_functions_printed.add(rule.context.func)
            self.print_rule(rule.alternatives[1])
        else:
            self.alternative_functions_printed.add(rule.context.func)
            with self.new_step():
                self.append("There are multiple ways to do this derivative.")
                for i, r in enumerate(rule.alternatives[1:]):
                    with self.new_collapsible():
                        self.append_header(f"Method {i + 1}")
                        with self.new_level():
                            self.print_rule(r)

    def print_RewriteRule(self, rule):
        with self.new_step():
            self.append("Rewrite the function to be differentiated:")
            self.append(self.format_math_display(sympy.Eq(rule.context, rule.rewritten)))
            self.print_rule(rule.substep)

    def print_FunctionRule(self, rule):
        with self.new_step():
            self.append("Trivial:")
            self.append(self.format_math_display(sympy.Eq(sympy.Derivative(rule.context, rule.symbol), diff(rule))))

    def print_DontKnowRule(self, rule):
        with self.new_step():
            self.append("Don't know the steps in finding this derivative.")
            self.append("But the derivative is")
            self.append(self.format_math_display(diff(rule)))

    def finalize(self):
        answer = diff(self.rule)
        if answer:
            simp = sympy.simplify(answer)
            if simp != answer:
                with self.new_step():
                    self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">Now simplify to get:')
                    self.append(self.format_math_display(simp) + '</ol></div>')
        self.lines.append('</ol>')
        return '\n'.join(self.lines)


def print_html_steps(function, symbol):
    """Generate HTML steps for differentiating a function."""
    return DiffPrinter(diff_steps(function, symbol)).finalize()
