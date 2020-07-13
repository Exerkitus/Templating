from jsonschema import validate
from json import loads

def assert_valid_question(question, main_schemas_filepath):
    schemas = load_schemas(main_schemas_filepath)
    return validate_question(question, schemas)

def validate_question(question, schemas):
    if "mode" not in question or question["mode"] not in schemas:
        raise ValueError("\"mode\" must be one of the supported question types.")
    validate(question, schemas[question["mode"]])
    return question

def load_schemas(main_schemas_filepath):
    with open(main_schemas_filepath, 'r') as json_schemas:
        schemas = loads(json_schemas.read())

    return schemas

"""
MAIN
"""

if __name__ == "__main__":
    with open("./question_types.json", "r") as json_question_examples:
        question_examples = loads(json_question_examples.read())

    schemas = load_schemas("./question_schemas.json")

    try:
        for question in question_examples:
            validate_question(question, schemas)
    except Exception as error:
        print(error, "\n\nFail.")
    else:
        print("Success.")
