from jinja2 import Environment, FileSystemLoader
import json
from os.path import join
import sys
from uuid import uuid4
from datasource.validator import add_defaults_and_validate

##### GLOBALS #####
class consts:
    SCRIPTS_LOCATION = "/web/Pjohnso000/Public_Html/Scripts/QuestionJavaScript.txt"
    THEME_LOCATION = "/themes/cad8b55c-b186-4899-a406-b92966ee7766"
###################

####### LOAD AND SETUP DATA FOR SHEET #######
# Parse optional commandline arguments
question_path = "AllResAreas.json" if len(sys.argv) == 1 else str(sys.argv[1])

# Load question data from file
with open(question_path, 'r') as file:
    question = json.load(file)

# If the question has not been given a uid yet, give it one
if "uid" not in question:
    question["uid"] = str(uuid4())

    # Save it, this is important for version control
    with open(question_path, 'w') as file:
        json.dump(question, file, indent=3)

# Load response area schemas
with open(join("datasource", "questions", "schemas.json"), 'r') as file:
    schemas = json.load(file)

# Load response area defaults
with open(join("datasource", "questions", "defaults.json"), 'r') as file:
    defaults = json.load(file)

# I don't know a better way to do this part, but we need to give each response area in a question its own unique number, as well as saving them to a list (this is how the manifest.xml question file is structured... with the <1> and <2> tags)
question["response_areas"] = []
identifier  = 1
for i in range(len(question["parts"])):
    if "response" in question["parts"][i]:
        question["response_areas"] += [add_defaults_and_validate(question["parts"][i]["response"], schemas, defaults)]
        question["parts"][i]["response"] = identifier
        identifier += 1

####### SETUP TEMPLATING ENVIRONMENT #######
# Configure jinja environment
env = Environment(loader=FileSystemLoader("./templates"),
                  trim_blocks=True,
                  lstrip_blocks=True)

# Load globals into the Jinja2 environment
env.globals.update(consts=consts)

# Load master template from environment
master = env.get_template("master.xml")

####### RENDER AND EXPORT #######
# Render sheet data using master template
renderedHTML = master.render(questions=[question])

# For debugging
print(renderedHTML)

# Save rendered HTML to File
with open(join("renders", f"{question['number']}.xml"), 'w') as file:
    file.write(renderedHTML)
