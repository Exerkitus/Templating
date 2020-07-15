from jinja2 import Environment, FileSystemLoader
import json
from os.path import join
from datasource_parser import validate_and_parse_question_data

##### GLOBALS #####
class consts:
    SCRIPTS_LOCATION = "/web/Pjohnso000/Public_Html/Scripts/QuestionJavaScript.txt"
    THEME_LOCATION = "/themes/cad8b55c-b186-4899-a406-b92966ee7766"
###################

# Load question data from file
with open("question.json", 'r') as file:
    question = json.load(file)

# Load response area schemas
with open(join("datasource_parser", "questions", "schemas.json"), 'r') as file:
    schemas = json.load(file)

# Load response area defaults
with open(join("datasource_parser", "questions", "defaults.json"), 'r') as file:
    defaults = json.load(file)

# Configure jinja environment
env = Environment(loader=FileSystemLoader("./templates"),
                  trim_blocks=True,
                  lstrip_blocks=True)

# Load custom validate_and_parse_question_data filter
env.globals.update(validate_and_parse_question_data=validate_and_parse_question_data)

# Load master template from environment
master = env.get_template("master.html")

# Render sheet data using master template
renderedHTML = master.render(question=question, schemas=schemas, defaults=defaults, consts=consts)

# For debugging
print(renderedHTML)

# Save rendered HTML to File
with open(join("renders", "index.html"), 'w') as file:
    file.write(renderedHTML)
