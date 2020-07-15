from jsonschema import validate
from json import load

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

    Returns the same instance that has the added defaults.
    """
    for key, value in defaults.items():
        if key not in instance:
            instance[key] = value
        elif type(instance[key]) != type(value):
            raise ValueError(f"{key} must have the same value as in the default.")
        elif type(value) == dict:
            instance[key] = recursively_add_defaults(instance[key], value)

    return instance

"""
MAIN
"""

if __name__ == "__main__":

    with open("./questions/examples_minimal.json", 'r') as examples_file:
        question_examples = load(examples_file)

    with open("./questions/schemas.json", 'r') as schemas_file:
        schemas = load(schemas_file)

    with open("./questions/defaults.json", 'r') as defaults_file:
        defaults = load(defaults_file)

    try:
        for minimal_question in question_examples:
            question = add_question_defaults(minimal_question, defaults)
            validate_question_data(question, schemas)

    except Exception as error:
        print(error, "\n\nFail.")
    
    else:
        print("Success.")
