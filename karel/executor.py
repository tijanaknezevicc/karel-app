import ast
import builtins
from karel.commands import COMMAND_ATTR_NAMES, expand_aliases
from karel.exceptions import InfiniteLoopError, InvalidCommandError
from karel.levels import LEVELS


MAX_STEPS = 10000  # to prevent infinite loops

def validate_syntax(code, level):
    tree = ast.parse(code)
    allowed_nodes = LEVELS[level]["node_types"]
    allowed_commands = expand_aliases(LEVELS[level]["commands"])
    allowed_builtins = LEVELS[level]["builtins"]

    for node in ast.walk(tree):
        if type(node) not in allowed_nodes:
            raise InvalidCommandError(f"Neobradjena konstrukcija u kodu: {type(node).__name__}")

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in allowed_commands and name not in allowed_builtins:
                raise InvalidCommandError(f"Neobradjena komanda ili konstrukcija u kodu: {name}")

def _wrap_with_step_limit(method, step_counter):
    def wrapped(*args, **kwargs):
        step_counter["count"] += 1
        if step_counter["count"] > MAX_STEPS:
            raise InfiniteLoopError("Beskonačna petlja :c")
        return method(*args, **kwargs)
    return wrapped

def execute_program(code, robot, level):
    validate_syntax(code, level)

    step_counter = {"count": 0}
    namespace = {"__builtins__": {}}

    allowed_commands = expand_aliases(LEVELS[level]["commands"])

    for command_name in allowed_commands:
        attr_name = COMMAND_ATTR_NAMES[command_name]
        namespace[command_name] = _wrap_with_step_limit(getattr(robot, attr_name), step_counter)

    for builtin_name in LEVELS[level]["builtins"]:
        namespace[builtin_name] = getattr(builtins, builtin_name)

    exec(code, namespace)