

def _snake_to_camel(name):
    parts = name.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])

def expand_aliases(names):
    expanded = set()
    for name in names:
        expanded.add(name)
        expanded.add(_snake_to_camel(name))
    return expanded

_BASE_COMMANDS = {
    "napred": "move_forward",
    "levo": "turn_left",
    "desno": "turn_right",
    "uzmi": "pick_beeper",
    "ostavi": "put_beeper",
    "moze_napred": "can_move_forward",
    "ima_loptica_na_polju": "beeper_present_on_field",
    "broj_loptica_na_polju": "beeper_count_on_field",
    "ima_loptica_kod_sebe": "beepers_present_in_bag",
    "broj_loptica_kod_sebe": "beeper_count_in_bag",
}

COMMAND_ATTR_NAMES = {}
for snake_name, attr_name in _BASE_COMMANDS.items():
    COMMAND_ATTR_NAMES[snake_name] = attr_name
    camel_name = _snake_to_camel(snake_name)
    if camel_name != snake_name:
        COMMAND_ATTR_NAMES[camel_name] = attr_name