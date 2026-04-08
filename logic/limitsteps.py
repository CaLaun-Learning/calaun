"""Step-by-step limit evaluation with HTML output."""
import sympy
from sympy import oo, zoo, nan, Symbol, limit, Limit
from sympy.core.function import AppliedUndef

from logic import stepprinter


def print_html_steps(expr, var, point, direction='+'):
    """Generate HTML step-by-step solution for a limit.
    
    Args:
        expr: The expression to take the limit of
        var: The variable approaching the limit point
        point: The point the variable approaches
        direction: '+' for right-hand, '-' for left-hand, '+-' for both
        
    Returns:
        HTML string with step-by-step solution
    """
    printer = LimitPrinter(expr, var, point, direction)
    return printer.finalize()


class LimitPrinter(stepprinter.HTMLPrinter):
    """Generates HTML step-by-step limit evaluation output."""
    
    def __init__(self, expr, var, point, direction='+'):
        super().__init__()
        self.expr = expr
        self.var = var
        self.point = point
        self.direction = direction
        self.evaluate_limit()
    
    def format_limit(self, expr, var, point, direction='+'):
        """Format a limit expression for display."""
        if direction == '+-':
            return sympy.Limit(expr, var, point)
        return sympy.Limit(expr, var, point, direction)
    
    def _safe_limit(self, expr, var, point, direction='+'):
        """Safely compute a limit, returning None on failure."""
        try:
            result = limit(expr, var, point, direction)
            if result.has(nan, zoo) or isinstance(result, type(sympy.S.ComplexInfinity)):
                return None
            return result
        except Exception:
            return None
    
    def evaluate_limit(self):
        """Main entry point for evaluating the limit step by step."""
        expr = self.expr
        var = self.var
        point = self.point
        direction = self.direction
        
        with self.new_step():
            self.append(f"Evaluate the limit:")
            self.append(self.format_math_display(self.format_limit(expr, var, point, direction)))
        
        # Check for special known limits first (like sin(x)/x)
        special_result = self.check_special_limits(expr, var, point, direction)
        if special_result is not None:
            return
        
        # Check for exponential indeterminate forms (1^∞, 0^0, ∞^0)
        if expr.is_Pow:
            exp_result = self.handle_exponential_form(expr, var, point, direction)
            if exp_result is not None:
                return
        
        # Try direct substitution first
        result = self.try_direct_substitution(expr, var, point, direction)
        
        if result is not None:
            return
        
        # Check for indeterminate forms and apply appropriate techniques
        self.handle_indeterminate_form(expr, var, point, direction)
    
    def check_special_limits(self, expr, var, point, direction):
        """Check for special known limits that have standard results."""
        # Only check when point is 0
        if point != 0:
            return None
        
        numer, denom = expr.as_numer_denom()
        
        # sin(x)/x -> 1 as x -> 0
        if numer == sympy.sin(var) and denom == var:
            with self.new_step():
                self.append("This is a fundamental trigonometric limit:")
                self.append(self.format_math_display(sympy.Eq(
                    Limit(sympy.sin(var)/var, var, 0), 1)))
                self.append("This limit can be proven using the squeeze theorem or geometric arguments.")
            with self.new_step():
                self.append("Therefore, the limit is:")
                self.append(self.format_math_display(1))
            return 1
        
        # (1 - cos(x))/x -> 0 as x -> 0
        if numer == 1 - sympy.cos(var) and denom == var:
            with self.new_step():
                self.append("This is a standard trigonometric limit:")
                self.append(self.format_math_display(sympy.Eq(
                    Limit((1 - sympy.cos(var))/var, var, 0), 0)))
            with self.new_step():
                self.append("Therefore, the limit is:")
                self.append(self.format_math_display(0))
            return 0
        
        # (1 - cos(x))/x^2 -> 1/2 as x -> 0
        if numer == 1 - sympy.cos(var) and denom == var**2:
            with self.new_step():
                self.append("This is a standard trigonometric limit:")
                self.append(self.format_math_display(sympy.Eq(
                    Limit((1 - sympy.cos(var))/var**2, var, 0), sympy.Rational(1, 2))))
                self.append("This can be derived using the identity "
                           f"{self.format_math(1 - sympy.cos(var))} = {self.format_math(2*sympy.sin(var/2)**2)}")
            with self.new_step():
                self.append("Therefore, the limit is:")
                self.append(self.format_math_display(sympy.Rational(1, 2)))
            return sympy.Rational(1, 2)
        
        # tan(x)/x -> 1 as x -> 0
        if numer == sympy.tan(var) and denom == var:
            with self.new_step():
                self.append("Rewrite using tan(x) = sin(x)/cos(x):")
                self.append(self.format_math_display(sympy.Eq(
                    sympy.tan(var)/var, sympy.sin(var)/(var*sympy.cos(var)))))
            with self.new_step():
                self.append("As x → 0, cos(x) → 1, and sin(x)/x → 1:")
                self.append(self.format_math_display(sympy.Eq(
                    Limit(sympy.tan(var)/var, var, 0), 1)))
            with self.new_step():
                self.append("Therefore, the limit is:")
                self.append(self.format_math_display(1))
            return 1
        
        # (e^x - 1)/x -> 1 as x -> 0
        if numer == sympy.exp(var) - 1 and denom == var:
            with self.new_step():
                self.append("This is a fundamental exponential limit:")
                self.append(self.format_math_display(sympy.Eq(
                    Limit((sympy.exp(var) - 1)/var, var, 0), 1)))
                self.append("This is the definition of the derivative of e^x at x=0.")
            with self.new_step():
                self.append("Therefore, the limit is:")
                self.append(self.format_math_display(1))
            return 1
        
        # ln(1+x)/x -> 1 as x -> 0
        if numer == sympy.log(1 + var) and denom == var:
            with self.new_step():
                self.append("This is a fundamental logarithmic limit:")
                self.append(self.format_math_display(sympy.Eq(
                    Limit(sympy.log(1 + var)/var, var, 0), 1)))
            with self.new_step():
                self.append("Therefore, the limit is:")
                self.append(self.format_math_display(1))
            return 1
        
        return None
    
    def handle_exponential_form(self, expr, var, point, direction):
        """Handle exponential indeterminate forms like 1^∞, 0^0, ∞^0."""
        if not expr.is_Pow:
            return None
        
        base = expr.base
        exponent = expr.exp
        
        # Try to evaluate base and exponent at the limit point
        base_limit = self._safe_limit(base, var, point, direction)
        exp_limit = self._safe_limit(exponent, var, point, direction)
        
        if base_limit is None or exp_limit is None:
            return None
        
        # Check for 1^∞ form
        is_one_inf = (base_limit == 1 and exp_limit in (oo, -oo))
        # Check for 0^0 form
        is_zero_zero = (base_limit == 0 and exp_limit == 0)
        # Check for ∞^0 form
        is_inf_zero = (base_limit in (oo, -oo) and exp_limit == 0)
        
        if not (is_one_inf or is_zero_zero or is_inf_zero):
            return None
        
        with self.new_step():
            if is_one_inf:
                self.append(f"This is an indeterminate form of type {self.format_math(sympy.Symbol('1^{\\infty}'))}.")
            elif is_zero_zero:
                self.append(f"This is an indeterminate form of type {self.format_math(sympy.Symbol('0^0'))}.")
            else:
                self.append(f"This is an indeterminate form of type {self.format_math(sympy.Symbol('\\infty^0'))}.")
            
            self.append("To evaluate, use the logarithm technique:")
            self.append(f"Let {self.format_math(sympy.Symbol('L'))} = {self.format_math(Limit(expr, var, point))}")
        
        log_expr = exponent * sympy.log(base)
        
        with self.new_step():
            self.append("Take the natural log of both sides:")
            self.append(self.format_math_display(sympy.Eq(
                sympy.log(sympy.Symbol('L')), 
                Limit(log_expr, var, point))))
            self.append(f"Since {self.format_math(sympy.log(base**exponent))} = {self.format_math(exponent * sympy.log(base))}")
        
        with self.new_step():
            self.append("Now evaluate the limit of the logarithm:")
            self.append(self.format_math_display(Limit(log_expr, var, point)))
        
        # Simplify the log expression
        log_expr_simplified = sympy.simplify(log_expr)
        if log_expr_simplified != log_expr:
            with self.new_step():
                self.append("Simplify:")
                self.append(self.format_math_display(sympy.Eq(log_expr, log_expr_simplified)))
                log_expr = log_expr_simplified
        
        # For 1^∞ form with exponent = var, apply L'Hopital's technique
        if is_one_inf and exponent == var:
            with self.new_step():
                # Rewrite x*ln(f(x)) as ln(f(x))/(1/x) for L'Hopital
                self.append("Rewrite as a fraction to apply L'Hôpital's Rule:")
                inner = sympy.log(base) / (1/var)
                inner_simplified = sympy.simplify(inner)
                self.append(f"{self.format_math(log_expr)} = {self.format_math(inner_simplified)}")
            
            with self.new_step():
                self.append(f"As {self.format_math(var)} → {self.format_math(point)}, this has the form 0/0.")
                self.append("Apply L'Hôpital's Rule:")
                
                numer = sympy.log(base)
                denom = 1/var
                numer_deriv = sympy.diff(numer, var)
                denom_deriv = sympy.diff(denom, var)
                
                self.append(f"Derivative of numerator: {self.format_math(numer_deriv)}")
                self.append(f"Derivative of denominator: {self.format_math(denom_deriv)}")
                
                new_ratio = numer_deriv / denom_deriv
                new_ratio_simplified = sympy.simplify(new_ratio)
                
                self.append(self.format_math_display(sympy.Eq(
                    Limit(numer/denom, var, point),
                    Limit(new_ratio_simplified, var, point))))
            
            with self.new_step():
                log_limit = self._safe_limit(new_ratio_simplified, var, point, direction)
                self.append(f"Evaluating the limit:")
                self.append(self.format_math_display(sympy.Eq(
                    Limit(new_ratio_simplified, var, point), log_limit)))
                self.append(f"So {self.format_math(sympy.log(sympy.Symbol('L')))} = {self.format_math(log_limit)}")
        else:
            # Try to evaluate the log limit directly
            log_limit = self._safe_limit(log_expr, var, point, direction)
            
            if log_limit is not None:
                with self.new_step():
                    self.append(f"The limit of the logarithm is:")
                    self.append(self.format_math_display(log_limit))
            else:
                # Fall back to sympy computation
                with self.new_step():
                    result = limit(expr, var, point, direction)
                    self.append("Evaluating this limit:")
                    self.append(self.format_math_display(result))
                    return result
        
        # Now exponentiate to get the final result
        with self.new_step():
            self.append(f"Since ln(L) = {self.format_math(log_limit)}, we have:")
            final_result = sympy.exp(log_limit)
            final_simplified = sympy.simplify(final_result)
            self.append(self.format_math_display(sympy.Eq(
                sympy.Symbol('L'), final_simplified)))
        
        with self.new_step():
            self.append("Therefore, the limit is:")
            self.append(self.format_math_display(final_simplified))
        
        return final_simplified
    
    def try_direct_substitution(self, expr, var, point, direction):
        """Try direct substitution to evaluate the limit."""
        with self.new_step():
            self.append(f"First, try direct substitution by plugging in "
                       f"{self.format_math(var)} = {self.format_math(point)}:")
            
            try:
                if point in (oo, -oo):
                    self.append(f"Since we're taking the limit as {self.format_math(var)} approaches "
                               f"{self.format_math(point)}, we analyze the behavior.")
                    return None
                
                substituted = expr.subs(var, point)
                
                # Check if result is defined
                if substituted.is_finite and not substituted.has(nan, zoo):
                    # Show the substitution process
                    self.append(self.format_math_display(
                        sympy.Eq(expr, substituted, evaluate=False)))
                    
                    with self.new_step():
                        self.append("Direct substitution works! The limit is:")
                        self.append(self.format_math_display(substituted))
                    
                    return substituted
                else:
                    self.append(f"Substituting gives an undefined or indeterminate form.")
                    return None
                    
            except Exception:
                self.append("Direct substitution doesn't work here.")
                return None
    
    def handle_indeterminate_form(self, expr, var, point, direction):
        """Handle indeterminate forms like 0/0, ∞/∞, etc."""
        
        # Identify the type of expression
        if expr.is_Mul or expr.is_Pow:
            # Check for 0 * ∞ or 0^0 or ∞^0 forms
            pass
        
        if expr.is_Rational or (hasattr(expr, 'is_rational_function') and expr.is_rational_function(var)):
            self.handle_rational_function(expr, var, point, direction)
            return
        
        # Check if expression involves square roots - try rationalization
        numer, denom = expr.as_numer_denom()
        if self._has_sqrt(numer) or self._has_sqrt(denom):
            result = self.try_rationalization(expr, var, point, direction, numer, denom)
            if result is not None:
                return
        
        # Check if L'Hôpital's rule applies
        if denom != 1:
            numer_limit = self._safe_limit(numer, var, point, direction)
            denom_limit = self._safe_limit(denom, var, point, direction)
            
            if (numer_limit == 0 and denom_limit == 0) or \
               (numer_limit in (oo, -oo) and denom_limit in (oo, -oo)):
                self.apply_lhopital(expr, var, point, direction, numer, denom)
                return
        
        # Try algebraic manipulation
        self.try_algebraic_simplification(expr, var, point, direction)
    
    def _has_sqrt(self, expr):
        """Check if expression contains a square root."""
        return expr.has(sympy.sqrt) or any(
            isinstance(arg, sympy.Pow) and arg.exp == sympy.Rational(1, 2)
            for arg in sympy.preorder_traversal(expr)
        )
    
    def _get_conjugate(self, expr):
        """Get the conjugate of an expression with square roots (a + b -> a - b)."""
        if not expr.is_Add:
            return None
        terms = expr.as_ordered_terms()
        if len(terms) != 2:
            return None
        # Return sum with opposite sign on second term
        return terms[0] - terms[1]
    
    def try_rationalization(self, expr, var, point, direction, numer, denom):
        """Try to rationalize expressions with square roots."""
        # Check for sqrt in numerator or denominator
        sqrt_in_numer = self._has_sqrt(numer)
        sqrt_in_denom = self._has_sqrt(denom)
        
        if not (sqrt_in_numer or sqrt_in_denom):
            return None
        
        with self.new_step():
            self.append("This expression contains a square root. Try rationalizing:")
            
            try:
                # Try to find conjugate and multiply
                if sqrt_in_numer and numer.is_Add:
                    conjugate = self._get_conjugate(numer)
                    if conjugate is not None:
                        self.append(f"Multiply numerator and denominator by the conjugate {self.format_math(conjugate)}:")
                        
                        new_numer = sympy.expand(numer * conjugate)
                        new_denom = sympy.expand(denom * conjugate)
                        new_expr = new_numer / new_denom
                        
                        self.append(self.format_math_display(sympy.Eq(
                            expr, (numer * conjugate) / (denom * conjugate), evaluate=False)))
                        
                        with self.new_step():
                            self.append("Using the difference of squares formula, the numerator simplifies:")
                            self.append(f"{self.format_math(numer)} × {self.format_math(conjugate)} = {self.format_math(new_numer)}")
                            self.append(self.format_math_display(new_expr))
                        
                        # Try to simplify/cancel
                        simplified = sympy.cancel(new_expr)
                        if simplified != new_expr:
                            with self.new_step():
                                self.append("After canceling common factors:")
                                self.append(self.format_math_display(simplified))
                        else:
                            simplified = new_expr
                        
                        # Try substitution
                        result = self._safe_subs(simplified, var, point)
                        if result is not None and result.is_finite and not result.has(nan, zoo):
                            with self.new_step():
                                self.append(f"Substitute {self.format_math(var)} = {self.format_math(point)}:")
                                self.append(self.format_math_display(result))
                                self.append("Therefore, the limit is:")
                                self.append(self.format_math_display(result))
                            return result
                
                # Fall back to sympy's rationalization
                rationalized = sympy.simplify(sympy.radsimp(expr))
                
                if rationalized != expr:
                    self.append("After rationalizing:")
                    self.append(self.format_math_display(rationalized))
                    
                    # Try substitution
                    result = self._safe_subs(rationalized, var, point)
                    if result is not None and result.is_finite and not result.has(nan, zoo):
                        with self.new_step():
                            self.append(f"Substitute {self.format_math(var)} = {self.format_math(point)}:")
                            self.append(self.format_math_display(result))
                            self.append("Therefore, the limit is:")
                            self.append(self.format_math_display(result))
                        return result
                    else:
                        # Try computing the limit directly
                        actual = self._safe_limit(rationalized, var, point, direction)
                        if actual is not None:
                            with self.new_step():
                                self.append(f"Evaluating the limit:")
                                self.append(self.format_math_display(actual))
                            return actual
                else:
                    self.append("Rationalization did not simplify the expression.")
                    
            except Exception:
                self.append("Unable to rationalize this expression.")
        
        return None

    def handle_rational_function(self, expr, var, point, direction):
        """Handle limits of rational functions."""
        numer, denom = expr.as_numer_denom()
        
        # Special handling for limits at infinity
        if point in (oo, -oo):
            self.handle_rational_at_infinity(expr, var, point, direction, numer, denom)
            return
        
        with self.new_step():
            self.append("This is a rational function. Analyze numerator and denominator separately:")
            self.append(self.format_math_display(sympy.Eq(
                Limit(expr, var, point), 
                Limit(numer, var, point) / Limit(denom, var, point), evaluate=False)))
        
        numer_at_point = self._safe_subs(numer, var, point)
        denom_at_point = self._safe_subs(denom, var, point)
        
        with self.new_step():
            self.append(f"Evaluate numerator at {self.format_math(var)} = {self.format_math(point)}:")
            self.append(self.format_math_display(sympy.Eq(numer, numer_at_point, evaluate=False)))
            
        with self.new_step():
            self.append(f"Evaluate denominator at {self.format_math(var)} = {self.format_math(point)}:")
            self.append(self.format_math_display(sympy.Eq(denom, denom_at_point, evaluate=False)))
        
        if denom_at_point == 0 and numer_at_point == 0:
            # 0/0 indeterminate form
            with self.new_step():
                self.append(f"This gives the indeterminate form {self.format_math(sympy.S(0)/sympy.S(0))}.")
                self.append("Try factoring or applying L'Hôpital's rule.")
            
            # Try factoring
            factored = self.try_factoring(expr, var, point, direction, numer, denom)
            if factored is not None:
                return
            
            # Apply L'Hôpital's rule
            self.apply_lhopital(expr, var, point, direction, numer, denom)
            
        elif denom_at_point == 0 and numer_at_point != 0:
            # Non-zero over zero - infinite limit or DNE
            with self.new_step():
                self.append(f"The denominator approaches 0 while the numerator approaches "
                           f"{self.format_math(numer_at_point)}.")
                
                result = limit(expr, var, point, direction)
                if result in (oo, -oo):
                    self.append(f"The limit is {self.format_math(result)}.")
                else:
                    self.append(f"The limit is: {self.format_math(result)}")
                self.append(self.format_math_display(result))
        else:
            # Regular case
            with self.new_step():
                result = numer_at_point / denom_at_point
                self.append(f"The limit is:")
                self.append(self.format_math_display(result))
    
    def handle_rational_at_infinity(self, expr, var, point, direction, numer, denom):
        """Handle limits of rational functions as x approaches infinity."""
        # Get the degrees of numerator and denominator
        numer_poly = sympy.Poly(numer, var) if numer.is_polynomial(var) else None
        denom_poly = sympy.Poly(denom, var) if denom.is_polynomial(var) else None
        
        if numer_poly and denom_poly:
            numer_degree = numer_poly.degree()
            denom_degree = denom_poly.degree()
            numer_leading = numer_poly.LC()
            denom_leading = denom_poly.LC()
            
            with self.new_step():
                self.append(f"For limits at {self.format_math(point)}, compare the degrees of numerator and denominator:")
                self.append(f"Degree of numerator: {numer_degree}")
                self.append(f"Degree of denominator: {denom_degree}")
            
            if numer_degree < denom_degree:
                with self.new_step():
                    self.append("Since the degree of the numerator is less than the degree of the denominator, the limit is 0.")
                    self.append(self.format_math_display(0))
            elif numer_degree > denom_degree:
                with self.new_step():
                    result = limit(expr, var, point, direction)
                    self.append("Since the degree of the numerator is greater than the degree of the denominator, the limit is infinite.")
                    self.append(self.format_math_display(result))
            else:
                # Degrees are equal - limit is ratio of leading coefficients
                result = numer_leading / denom_leading
                with self.new_step():
                    self.append("Since the degrees are equal, the limit is the ratio of the leading coefficients:")
                    self.append(self.format_math_display(sympy.Eq(
                        Limit(expr, var, point),
                        sympy.Rational(numer_leading, denom_leading) if denom_leading != 0 else result,
                        evaluate=False)))
                with self.new_step():
                    self.append(f"The limit is:")
                    self.append(self.format_math_display(sympy.simplify(result)))
        else:
            # Fall back to direct computation
            with self.new_step():
                result = limit(expr, var, point, direction)
                self.append(f"Computing the limit at {self.format_math(point)}:")
                self.append(self.format_math_display(result))
    
    def try_factoring(self, expr, var, point, direction, numer, denom):
        """Try to factor and cancel common terms."""
        with self.new_step():
            self.append("Try factoring to cancel common terms:")
            
            try:
                numer_factored = sympy.factor(numer)
                denom_factored = sympy.factor(denom)
                
                # Show factoring of numerator if it changed
                if numer_factored != numer:
                    self.append(f"Factor the numerator: {self.format_math(numer)} = {self.format_math(numer_factored)}")
                
                # Show factoring of denominator if it changed
                if denom_factored != denom:
                    self.append(f"Factor the denominator: {self.format_math(denom)} = {self.format_math(denom_factored)}")
                
                self.append(self.format_math_display(sympy.Eq(expr, numer_factored / denom_factored)))
                
                # Try to cancel
                simplified = sympy.cancel(expr)
                
                if simplified != expr:
                    # Find what was cancelled
                    common_factor = sympy.gcd(numer, denom)
                    if common_factor != 1:
                        with self.new_step():
                            self.append(f"Notice that {self.format_math(common_factor)} is a common factor.")
                            self.append(f"Cancel the common factor (valid when {self.format_math(sympy.Ne(common_factor, 0))}):")
                    else:
                        with self.new_step():
                            self.append("Cancel the common factors:")
                    
                    self.append(self.format_math_display(sympy.Eq(
                        numer_factored / denom_factored, simplified)))
                    
                    # Now try direct substitution on simplified form
                    with self.new_step():
                        self.append(f"Now substitute {self.format_math(var)} = {self.format_math(point)} into the simplified expression:")
                        
                        result = self._safe_subs(simplified, var, point)
                        if result is not None and result.is_finite:
                            # Show the substitution step by step
                            self.append(self.format_math_display(
                                sympy.Eq(simplified.subs(var, var), simplified, evaluate=False)))
                            self.append(f"Let {self.format_math(var)} = {self.format_math(point)}:")
                            self.append(self.format_math_display(
                                sympy.Eq(simplified, result, evaluate=False)))
                            
                            with self.new_step():
                                self.append("Therefore, the limit is:")
                                self.append(self.format_math_display(result))
                            return result
                else:
                    self.append("Factoring doesn't reveal cancellable terms.")
                    return None
                    
            except Exception:
                self.append("Unable to factor this expression.")
                return None
        
        return None
    
    def apply_lhopital(self, expr, var, point, direction, numer=None, denom=None):
        """Apply L'Hôpital's rule for 0/0 or ∞/∞ forms."""
        if numer is None or denom is None:
            numer, denom = expr.as_numer_denom()
        
        with self.new_step():
            self.append("Apply L'Hôpital's Rule: take the derivative of numerator and denominator:")
            self.append(self.format_math_display(
                sympy.Eq(Limit(numer/denom, var, point),
                        Limit(sympy.Derivative(numer, var)/sympy.Derivative(denom, var), var, point))))
        
        numer_deriv = sympy.diff(numer, var)
        denom_deriv = sympy.diff(denom, var)
        
        with self.new_step():
            self.append(f"Derivative of numerator: {self.format_math(sympy.Derivative(numer, var))} = {self.format_math(numer_deriv)}")
            self.append(f"Derivative of denominator: {self.format_math(sympy.Derivative(denom, var))} = {self.format_math(denom_deriv)}")
        
        new_expr = numer_deriv / denom_deriv
        
        with self.new_step():
            self.append("The new limit becomes:")
            self.append(self.format_math_display(Limit(new_expr, var, point)))
        
        # Try to evaluate the new limit
        result = self._safe_subs(new_expr, var, point)
        
        if result is not None and result.is_finite and not result.has(nan, zoo):
            with self.new_step():
                self.append(f"Substituting {self.format_math(var)} = {self.format_math(point)}:")
                self.append(self.format_math_display(result))
                self.append("Therefore, the limit is:")
                self.append(self.format_math_display(result))
        else:
            # May need to apply L'Hôpital's rule again or use other methods
            with self.new_step():
                actual_result = limit(expr, var, point, direction)
                self.append(f"Evaluating this limit gives:")
                self.append(self.format_math_display(actual_result))
    
    def try_algebraic_simplification(self, expr, var, point, direction):
        """Try algebraic simplification techniques."""
        with self.new_step():
            self.append("Apply algebraic simplification:")
            
            simplified = sympy.simplify(expr)
            if simplified != expr:
                self.append(self.format_math_display(sympy.Eq(expr, simplified)))
                
                result = self._safe_limit(simplified, var, point, direction)
                with self.new_step():
                    self.append("The limit evaluates to:")
                    self.append(self.format_math_display(result))
            else:
                # Fall back to direct computation
                result = limit(expr, var, point, direction)
                self.append("Computing the limit directly:")
                self.append(self.format_math_display(result))
    
    def _safe_subs(self, expr, var, point):
        """Safely substitute a value, returning None on error."""
        try:
            result = expr.subs(var, point)
            return result
        except Exception:
            return None
    
    def _safe_limit(self, expr, var, point, direction='+'):
        """Safely compute a limit, returning None on error."""
        try:
            return limit(expr, var, point, direction)
        except Exception:
            return None
    
    def finalize(self):
        """Finalize the HTML output."""
        self.lines.append('</ol>')
        return '\n'.join(self.lines)
