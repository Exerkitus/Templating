from jsonschema import validate
from json import load


def add_defaults_and_validate(question, schemas, defaults):
    """
    Method to validate and set defaults on a question instance.
    ---
    This is done by initially adding any defaults that are not in the instance, followed
    by schema check (specified in questions/).

    Returns a dictionary.
    """
    question_with_defaults = add_question_defaults(question.copy(), defaults)
    validate_question_data(question_with_defaults, schemas)

    return question_with_defaults


def validate_question_data(question, schemas):
    if "mode" not in question or question["mode"] not in schemas:
        raise ValueError("\"mode\" must be one of the supported question types.")

    validate(question, schemas[question["mode"]])

def add_question_defaults(question, defaults):
    if "mode" not in question or question["mode"] not in defaults:
        raise ValueError("\"mode\" must be one of the supported question types.")

    return recursively_add_defaults(question, defaults[question["mode"]])

def recursively_add_defaults(instance, defaults):
    """
    Method to recursively add defaults into an instance.
    ---
    This is done by looping through the keys in the default dictionary, adding values
    into the instance if they do not exist already.

    If a key is in the instance, but has a different value type, then a ValueError is
    thrown. Else if a key exists but its value is also a dict, the method is called again
    within that dict (hence recursive).

    Returns the same instance which has the added defaults.
    """
    for key, value in defaults.items():
        if key not in instance:
            instance[key] = value
        elif type(instance[key]) != type(value):
            raise ValueError(f"{key} must have the same value as in the default.")
        elif type(value) == dict:
            instance[key] = recursively_add_defaults(instance[key], value)

    return instance
