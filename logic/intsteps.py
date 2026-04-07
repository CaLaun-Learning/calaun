"""Step-by-step integration with HTML output."""
import sympy
from logic import stepprinter
from logic.stepprinter import replace_u_var

from sympy.integrals.manualintegrate import (
    integral_steps, manualintegrate, ConstantRule, ConstantTimesRule, 
    PowerRule, AddRule, URule, PartsRule, CyclicPartsRule, TrigRule, 
    ExpRule, ArctanRule, AlternativeRule, DontKnowRule, RewriteRule
)

# LogRule may not exist in newer SymPy versions
try:
    from sympy.integrals.manualintegrate import LogRule
except ImportError:
    LogRule = None


def _manualintegrate(rule):
    """Compatibility wrapper for evaluating integration rules."""
    return rule.eval() if hasattr(rule, 'eval') else manualintegrate(rule.integrand, rule.variable)


def contains_dont_know(rule):
    """Check if a rule contains any DontKnowRule."""
    if isinstance(rule, DontKnowRule):
        return True
    for val in rule._asdict().values():
        if isinstance(val, tuple) and contains_dont_know(val):
            return True
        if isinstance(val, list) and any(contains_dont_know(i) for i in val):
            return True
    return False


def filter_unknown_alternatives(rule):
    """Filter out alternatives that contain DontKnowRule."""
    if isinstance(rule, AlternativeRule):
        known = [r for r in rule.alternatives if not contains_dont_know(r)]
        return AlternativeRule(known or rule.alternatives, rule.context, rule.symbol)
    return rule


# Rule type to print method mapping
RULE_PRINTERS = {}

def prints_rule(rule_type):
    """Decorator to register a print method for a rule type."""
    def decorator(func):
        RULE_PRINTERS[rule_type] = func
        return func
    return decorator


class IntegralPrinter(stepprinter.HTMLPrinter):
    """Generates HTML step-by-step integration output."""
    
    def __init__(self, rule):
        super().__init__()
        self.rule = rule
        self.alternative_functions_printed = set()
        self.print_rule(rule)

    def print_rule(self, rule):
        """Dispatch to appropriate print method based on rule type."""
        for rule_type, printer in RULE_PRINTERS.items():
            if isinstance(rule, rule_type):
                printer(self, rule)
                return
        self.append(repr(rule))

    @prints_rule(ConstantRule)
    def print_Constant(self, rule):
        with self.new_step():
            self.append("The integral of a constant is the constant times the variable of integration:")
            self.append(self.format_math_display(
                sympy.Eq(sympy.Integral(rule.constant, rule.symbol), _manualintegrate(rule))))

    @prints_rule(ConstantTimesRule)
    def print_ConstantTimes(self, rule):
        with self.new_step():
            self.append("The integral of a constant times a function is the constant times the integral:")
            self.append(self.format_math_display(sympy.Eq(
                sympy.Integral(rule.context, rule.symbol),
                rule.constant * sympy.Integral(rule.other, rule.symbol))))
            with self.new_level():
                self.print_rule(rule.substep)
            self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">So, the result is: ')
            self.append(self.format_math(_manualintegrate(rule)) + '</ol></div>')

    @prints_rule(PowerRule)
    def print_Power(self, rule):
        with self.new_step():
            n = sympy.Symbol('n')
            self.append(f"The integral of {self.format_math(rule.symbol ** n)} is "
                       f"{self.format_math((rule.symbol ** (1 + n)) / (1 + n))} when "
                       f"{self.format_math(sympy.Ne(n, -1))}:")
            self.append(self.format_math_display(
                sympy.Eq(sympy.Integral(rule.context, rule.symbol), _manualintegrate(rule))))

    @prints_rule(AddRule)
    def print_Add(self, rule):
        with self.new_step():
            self.append("Integrate term-by-term:")
            for substep in rule.substeps:
                with self.new_level():
                    self.print_rule(substep)
            self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">The result is: ')
            self.append(self.format_math(_manualintegrate(rule)) + '</ol></div>')

    @prints_rule(URule)
    def print_U(self, rule):
        with self.new_step(), self.new_u_vars() as (u, du):
            dx = sympy.Symbol('d' + rule.symbol.name, commutative=0)
            self.append(f"Let {self.format_math(sympy.Eq(u, rule.u_func))}.")
            self.append(f"Then let {self.format_math(sympy.Eq(du, rule.u_func.diff(rule.symbol) * dx))} "
                       f"and substitute {self.format_math(rule.constant * du)}:")
            integrand = rule.constant * rule.substep.context.subs(rule.u_var, u)
            self.append(self.format_math_display(sympy.Integral(integrand, u)))
            with self.new_level():
                self.print_rule(replace_u_var(rule.substep, rule.symbol.name, u))
            self.append(f'<div class="collapsible"><h2>open answer</h2><ol class="content">Now replace {self.format_math(u)} to get:')
            self.append(self.format_math_display(_manualintegrate(rule)) + '</ol></div>')

    @prints_rule(PartsRule)
    def print_Parts(self, rule):
        with self.new_step():
            self.append("Use integration by parts:")
            u, v, du, dv = [sympy.Function(f)(rule.symbol) for f in ['u', 'v', 'du', 'dv']]
            self.append(self.format_math_display(
                r"\int \operatorname{u} \operatorname{dv} = \operatorname{u}\operatorname{v} - \int \operatorname{v} \operatorname{du}"))
            self.append(f"Let {self.format_math(sympy.Eq(u, rule.u))} and let {self.format_math(sympy.Eq(dv, rule.dv))}.")
            self.append(f"Then {self.format_math(sympy.Eq(du, rule.u.diff(rule.symbol)))}.")
            self.append(f"To find {self.format_math(v)}:")
            with self.new_level():
                self.print_rule(rule.v_step)
            self.append("Now evaluate the sub-integral.")
            self.print_rule(rule.second_step)

    @prints_rule(CyclicPartsRule)
    def print_CyclicParts(self, rule):
        with self.new_step():
            self.append("Use integration by parts, noting that the integrand eventually repeats itself.")
            u, dv = sympy.Function('u')(rule.symbol), sympy.Function('dv')(rule.symbol)
            current_integrand = rule.context
            total_result = sympy.S.Zero
            sign = 1
            with self.new_level():
                for rl in rule.parts_rules:
                    with self.new_step():
                        self.append(f"For the integrand {self.format_math(current_integrand)}:")
                        self.append(f"Let {self.format_math(sympy.Eq(u, rl.u))} and {self.format_math(sympy.Eq(dv, rl.dv))}.")
                        v_f = _manualintegrate(rl.v_step)
                        du_f = rl.u.diff(rule.symbol)
                        total_result += sign * rl.u * v_f
                        current_integrand = v_f * du_f
                        self.append(f"Then {self.format_math(sympy.Eq(sympy.Integral(rule.context, rule.symbol), total_result - sign * sympy.Integral(current_integrand, rule.symbol)))}.")
                        sign *= -1
                with self.new_step():
                    self.append("Notice that the integrand has repeated itself, so move it to one side:")
                    self.append(self.format_math_display(sympy.Eq(
                        (1 - rule.coefficient) * sympy.Integral(rule.context, rule.symbol), total_result)))
                    self.append("Therefore,")
                    self.append(self.format_math_display(sympy.Eq(
                        sympy.Integral(rule.context, rule.symbol), _manualintegrate(rule))))

    @prints_rule(TrigRule)
    def print_Trig(self, rule):
        with self.new_step():
            messages = {
                'sin': "The integral of sine is negative cosine:",
                'cos': "The integral of cosine is sine:",
                'sec*tan': "The integral of secant times tangent is secant:",
                'csc*cot': "The integral of cosecant times cotangent is cosecant:",
            }
            if rule.func in messages:
                self.append(messages[rule.func])
            self.append(self.format_math_display(
                sympy.Eq(sympy.Integral(rule.context, rule.symbol), _manualintegrate(rule))))

    @prints_rule(ExpRule)
    def print_Exp(self, rule):
        with self.new_step():
            if rule.base == sympy.E:
                self.append("The integral of the exponential function is itself.")
            else:
                self.append("The integral of an exponential function is itself divided by the natural logarithm of the base.")
            self.append(self.format_math_display(
                sympy.Eq(sympy.Integral(rule.context, rule.symbol), _manualintegrate(rule))))

    @prints_rule(ArctanRule)
    def print_Arctan(self, rule):
        with self.new_step():
            self.append(f"The integral of {self.format_math(1 / (1 + rule.symbol ** 2))} is "
                       f"{self.format_math(_manualintegrate(rule))}.")

    @prints_rule(RewriteRule)
    def print_Rewrite(self, rule):
        with self.new_step():
            self.append("Rewrite the integrand:")
            self.append(self.format_math_display(sympy.Eq(rule.context, rule.rewritten)))
            self.print_rule(rule.substep)

    @prints_rule(DontKnowRule)
    def print_DontKnow(self, rule):
        with self.new_step():
            self.append("Don't know the steps in finding this integral.")
            self.append("But the integral is")
            self.append(self.format_math_display(sympy.integrate(rule.context, rule.symbol)))

    @prints_rule(AlternativeRule)
    def print_Alternative(self, rule):
        rule = filter_unknown_alternatives(rule)
        if len(rule.alternatives) == 1:
            self.print_rule(rule.alternatives[0])
            return
        if rule.context.func in self.alternative_functions_printed:
            self.print_rule(rule.alternatives[0])
        else:
            self.alternative_functions_printed.add(rule.context.func)
            with self.new_step():
                self.append("There are multiple ways to do this integral.")
                for i, r in enumerate(rule.alternatives):
                    with self.new_collapsible():
                        self.append_header(f"Method {i + 1}")
                        with self.new_level():
                            self.print_rule(r)

    def format_math_constant(self, math):
        return f'\\[{sympy.latex(math)}+ \\mathrm{{C}}\\]'

    def finalize(self):
        rule = filter_unknown_alternatives(self.rule)
        answer = _manualintegrate(rule)
        if answer:
            simp = sympy.simplify(sympy.trigsimp(answer))
            if simp != answer:
                answer = simp
                with self.new_step():
                    self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">Now simplify:')
                    self.append(self.format_math_display(simp) + '</ol></div>')
            with self.new_step():
                self.append('<div class="collapsible"><h2>open answer</h2><ol class="content">Add the constant of integration to get:')
                self.append(self.format_math_constant(answer) + '</ol></div>')
        self.lines.append('</ol>')
        return '\n'.join(self.lines)


# Register LogRule printer if available
if LogRule is not None:
    @prints_rule(LogRule)
    def print_Log(self, rule):
        with self.new_step():
            self.append(f"The integral of {self.format_math(1 / rule.func)} is "
                       f"{self.format_math(_manualintegrate(rule))}.")


def print_html_steps(function, symbol):
    """Generate HTML steps for integrating a function."""
    rule = integral_steps(function, symbol)
    if isinstance(rule, DontKnowRule):
        raise ValueError("Cannot evaluate integral")
    return IntegralPrinter(rule).finalize()
