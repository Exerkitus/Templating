from urllib.parse import quote
from json import load

from .schema_validator import validate_question_data, add_question_defaults

def validate_and_parse_question_data(question, schemas, defaults):
    """
    Method to validate and parse a question instance.
    ---
    This is done by initially adding any defaults that are not in the instance, followed
    by schema check (specified in questions/).

    If the validation doesn't throw an error, the variables will be converted to a url
    encoded string, allowing mobius to read it.

    Returns a string.
    """
    question_with_defaults = add_question_defaults(question.copy(), defaults)
    validate_question_data(question_with_defaults, schemas)
    
    return parse_datasource(question_with_defaults)

def parse_datasource(question_dictionary):
    """
    Method to convert a question in json form into a string that is readable by Mobius.
    ---
    This is done by taking every property in the json file and combining it into a string
    where the variables are defined by key=val and are separated by an @ symbol.

    The string is then url encoded and returned.

    datasource is able to take extra unnecessary variables without crashing, however it
    is better to avoid this. Therefore the question schema should be used before parsing
    the question json here.
    """
    variables = unnest_dictionary(question_dictionary)
    variables_string = "@".join(variables) + "@"
    
    return quote(variables_string)

def unnest_dictionary(dictionary, prefixes=[]):
    """
    Method to unnest dictionary structures.
    ---
    If a variable is nested, it will inherit prefixes from its parent properties, which
    is the same syntax as accessing properties in javascript and python.

    If there is a list, variables will be named after their parent property, prefixed by
    their position in the list (starting from 1).

    Prefixes are a list of strings that are joined together by a period (.) to produce
    key-value pairs.
    """
    variables = []
    for key, value in dictionary.items():
        variables.extend(sort_data_types(key, value, prefixes))

    return variables

def unnest_list(li, prefixes=[]):
    """
    Method to flatten a list structure.
    ---
    Variables inherit the name of their parent property, followed by their number in the
    list starting from 1.
    """
    variables = []
    for i, value in enumerate(li):
        # Use the items position in list as its key
        variables.extend(sort_data_types(str(i+1), value, prefixes))
    
    return variables

def sort_data_types(key, value, prefixes=[]):
    """
    Method to sort different data types used in JSON so that it can be handled correctly.
    ---
    If a dictionary or list, continue unnesting. If its a single value such as a string
    or boolean, create a key-value pair.
    """
    # add key name to list of prefixes
    p = prefixes.copy() + [key]
    value_type = type(value)
    # if another dictionary, unnest recursively
    if value_type == dict:
        # add name of parent property to prefixes list
        return unnest_dictionary(value, p)
    # if a list, flatten using name.1, name.2, ...
    elif value_type == list:
        return unnest_list(value, p)
    # if a boolean, correct format and make the key-value pair
    elif value_type == bool:
        return [combine_key_val(p, "true" if value else "false")]
    # if a number or string, make the key-value pair
    elif value_type in [int, float, str]:
        return [combine_key_val(p, value)]
    # if anything else found, throw an error
    else:
        raise TypeError("Value can only be a number, string, boolean, list or object.")

def combine_key_val(prefixes, value):
    """
    Method to convert a key value pair into a single string.
    ---
    Prefixes are used to keep track of the nesting of each element.
    These are joined together by a period (.) to produce key-value pairs.

    However in Mobius, some variables are named with a prefix which is the same name as
    some other variable.
    
    E.g. display=menu and display.permute=true

    To overcome this, if a variable has the same name as its oparent property, the same
    name is not copied twice. Therefore to get the variables:
    display=menu
    ---
    display.permute=true
    ----
    
    the json should look like:
    
    "display": {
        "display": "menu",
        "permute": true
    }
    """
    prefixes_no_duplicates = []
    
    for i in range(len(prefixes)):
        # if variable doesn't have the same name as its parent property
        if i == 0 or prefixes[i] != prefixes[i-1]:
            # add it to the full list of prefixes
            prefixes_no_duplicates.append(prefixes[i])

    # format string to prefixes_no_duplicates=value, where affixes are joined together by a period (.)
    return f"{'.'.join(prefixes_no_duplicates)}={value}"

"""
MAIN
"""

if __name__ == "__main__":
    with open("./questions/examples.json", "r") as json_question_examples:
        question_examples = load(json_question_examples)

    with open("./questions/random.json", "r") as random_json:
        random_data = load(random_json)

    try:
        for question in question_examples:
            print(parse_datasource(question), "\n")

        print(parse_datasource(random_data), "\n")

    except Exception as error:
        print(error, "\n\nFail.")
    
    else:
        print("Success.")