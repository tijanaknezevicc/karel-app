import ast

_BASE_NODE_TYPES = {ast.Module, ast.Expr, ast.Call, ast.Name, ast.Load}

_BASIC_COMMANDS = {"napred", "levo", "desno", "uzmi", "ostavi"}
_SENSOR_COMMANDS = {"moze_napred", "ima_loptica_na_polju", "broj_loptica_na_polju",
                     "ima_loptica_kod_sebe", "broj_loptica_kod_sebe"}

LEVELS = {}

LEVELS["linijski"] = {
    "commands": _BASIC_COMMANDS,
    "node_types": set(_BASE_NODE_TYPES),
    "builtins": set(),
}

LEVELS["brojacka_petlja"] = {
    "commands": LEVELS["linijski"]["commands"],
    "node_types": LEVELS["linijski"]["node_types"] | {ast.For, ast.Store, ast.Constant},
    "builtins": LEVELS["linijski"]["builtins"] | {"range"},
    "required_node_types": {ast.For},
}

LEVELS["uslovna_petlja"] = {
    "commands": LEVELS["brojacka_petlja"]["commands"] | _SENSOR_COMMANDS,
    "node_types": LEVELS["brojacka_petlja"]["node_types"] | {ast.While, ast.Compare},
    "builtins": LEVELS["brojacka_petlja"]["builtins"],
}

LEVELS["grananje"] = LEVELS["napredni"] = {
    "commands": LEVELS["uslovna_petlja"]["commands"],
    "node_types": LEVELS["uslovna_petlja"]["node_types"] | {ast.If},
    "builtins": LEVELS["uslovna_petlja"]["builtins"],
}