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
    
    def evaluate_limit(self):
        """Main entry point for evaluating the limit step by step."""
        expr = self.expr
        var = self.var
        point = self.point
        direction = self.direction
        
        with self.new_step():
            self.append(f"Evaluate the limit:")
            self.append(self.format_math_display(self.format_limit(expr, var, point, direction)))
        
        # Try direct substitution first
        result = self.try_direct_substitution(expr, var, point, direction)
        
        if result is not None:
            return
        
        # Check for indeterminate forms and apply appropriate techniques
        self.handle_indeterminate_form(expr, var, point, direction)
    
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
        
        # Check if L'Hôpital's rule applies
        numer, denom = expr.as_numer_denom()
        if denom != 1:
            numer_limit = self._safe_limit(numer, var, point, direction)
            denom_limit = self._safe_limit(denom, var, point, direction)
            
            if (numer_limit == 0 and denom_limit == 0) or \
               (numer_limit in (oo, -oo) and denom_limit in (oo, -oo)):
                self.apply_lhopital(expr, var, point, direction, numer, denom)
                return
        
        # Try algebraic manipulation
        self.try_algebraic_simplification(expr, var, point, direction)
    
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
                
                self.append(self.format_math_display(sympy.Eq(expr, numer_factored / denom_factored)))
                
                # Try to cancel
                simplified = sympy.cancel(expr)
                
                if simplified != expr:
                    with self.new_step():
                        self.append("After canceling common factors:")
                        self.append(self.format_math_display(simplified))
                    
                    # Now try direct substitution on simplified form
                    result = self._safe_subs(simplified, var, point)
                    if result is not None and result.is_finite:
                        with self.new_step():
                            self.append(f"Substituting {self.format_math(var)} = {self.format_math(point)}:")
                            self.append(self.format_math_display(result))
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
