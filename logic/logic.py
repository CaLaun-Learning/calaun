"""Main logic for processing user mathematical input."""
import traceback
import sympy
from sympy import latex
from sympy.core.function import FunctionClass
from sympy.parsing.sympy_parser import (
    stringify_expr, parse_expr, standard_transformations, convert_xor,
    TokenError, implicit_multiplication, split_symbols,
    implicit_multiplication_application, function_exponentiation, implicit_application
)

from logic.utils import Eval, latexify, arguments, removeSymPy, OTHER_SYMPY_FUNCTIONS
from logic.resultsets import find_result_set, get_card, format_by_type, is_function_handled

PREEXEC = "from sympy import *"

TRANSFORMATIONS = (
    standard_transformations + 
    (implicit_multiplication, convert_xor, function_exponentiation,
     split_symbols, implicit_application, implicit_multiplication_application)
)


def make_latex_readable(*args):
    """Convert SymPy objects to readable LaTeX wrapped for MathJax 3."""
    latex_parts = [obj.as_latex() if hasattr(obj, 'as_latex') else latex(obj) 
                   for obj in args]
    
    latex_content = ''.join(latex_parts)
    
    if len(args) == 1:
        obj = args[0]
        if (isinstance(obj, sympy.Basic) and not obj.free_symbols and
            not obj.is_Integer and not obj.is_Float and
            obj.is_finite is not False and hasattr(obj, 'evalf')):
            return (f'<span data-numeric="true" data-output-repr="{repr(obj)}" '
                    f'data-approximation="{latex(obj.evalf(15))}">\\[{latex_content}\\]</span>')
    
    return f'\\[{latex_content}\\]'


class UserInput:
    """Processes user mathematical input and generates result cards."""

    def change_to_cards(self, s):
        """Convert user input string to a list of result cards."""
        try:
            result = self.evaluate_user_input(s)
        except TokenError:
            return [{"title": "Input", "input": s},
                    {"title": "Error", "input": s, "error": "Invalid input"}]
        except Exception as e:
            return self._handle_error(s, e)

        if not result:
            return []
            
        parsed, args, evaluator, evaluated = result
        try:
            return self._prepare_cards(parsed, args, evaluator, evaluated)
        except ValueError as e:
            return self._handle_error(s, e)

    def _handle_error(self, s, e):
        """Create error cards for different exception types."""
        if isinstance(e, SyntaxError):
            error = {"msg": e.msg, "offset": e.offset}
            if e.text:
                error["input_start"] = e.text[:e.offset]
                error["input_end"] = e.text[e.offset:]
            return [{"title": "Input", "input": s},
                    {"title": "Error", "input": s, "exception_info": error}]
        elif isinstance(e, ValueError):
            return [{"title": "Input", "input": s},
                    {"title": "Error", "input": s, "error": str(e)}]
        else:
            trace = f"There was an error.\nStack trace:\n\n{traceback.format_exc()}"
            return [{"title": "Input", "input": s},
                    {"title": "Error", "input": s, "error": trace}]

    def evaluate_user_input(self, s):
        """Parse and evaluate user input string."""
        if not s:
            return None

        namespace = {}
        exec(PREEXEC, namespace)
        evaluator = Eval(namespace)

        parsed = stringify_expr(s, {}, namespace, TRANSFORMATIONS)
        try:
            evaluated = parse_expr(parsed, evaluate=True)
        except SyntaxError:
            raise
        except Exception as e:
            raise ValueError(str(e))

        return parsed, arguments(parsed, evaluator), evaluator, evaluated

    def _get_cards_and_components(self, args, evaluator, evaluated):
        """Determine which cards to show and extract components."""
        func_name = args[0]
        first_func = evaluator.get(func_name)
        is_applied = args.args or args.kwargs
        
        is_function = (
            first_func and
            not isinstance(first_func, FunctionClass) and
            not isinstance(first_func, sympy.Atom) and
            func_name and func_name[0].islower() and
            func_name not in OTHER_SYMPY_FUNCTIONS
        )

        convert_input, cards = find_result_set(
            args[0] if is_applied else None, evaluated
        )
        
        components = convert_input(args, evaluated)
        if 'input_evaluated' in components:
            evaluated = components['input_evaluated']
        evaluator.set('input_evaluated', evaluated)

        return components, cards, evaluated, (is_function and is_applied)

    def _prepare_cards(self, parsed, args, evaluator, evaluated):
        """Generate the list of result cards."""
        components, cards, evaluated, is_function = self._get_cards_and_components(
            args, evaluator, evaluated
        )

        # Format input display
        if is_function:
            latex_input = f'\\[{latexify(parsed, evaluator)}\\]'
        else:
            latex_input = make_latex_readable(evaluated)

        result = [{
            "title": "Input",
            "input": removeSymPy(parsed),
            "output": latex_input
        }]

        var = components['variable']

        # Add result card if needed
        if not cards and not var and is_function:
            result.append({
                'title': 'Result',
                'input': removeSymPy(parsed),
                'output': format_by_type(evaluated, args, make_latex_readable)
            })
        else:
            if is_function and not is_function_handled(args[0]):
                result.append({
                    "title": "Result",
                    "input": "",
                    "output": format_by_type(evaluated, args, make_latex_readable)
                })

            for card_name in cards:
                card = get_card(card_name)
                if not card:
                    continue
                try:
                    result.append({
                        'card': card_name,
                        'var': repr(var),
                        'title': card.format_title(evaluated),
                        'input': card.format_input(repr(evaluated), components),
                        'pre_output': latex(card.pre_output_function(evaluated, var)),
                        'parameters': card.card_info.get('parameters', [])
                    })
                except Exception:
                    pass

        return result

    def evaluate_card(self, card_name, expression, variable, parameters):
        """Evaluate a specific card with given parameters."""
        card = get_card(card_name)
        if not card:
            raise KeyError(f"Card '{card_name}' not found")

        _, args, evaluator, evaluated = self.evaluate_user_input(expression)
        variable = sympy.Symbol(variable)
        components, _, evaluated, _ = self._get_cards_and_components(args, evaluator, evaluated)
        components['variable'] = variable
        evaluator.set(str(variable), variable)
        result = card.eval(evaluator, components, parameters)

        return {
            'value': repr(result),
            'output': card.format_output(result, make_latex_readable)
        }
