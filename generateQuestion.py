from jinja2 import Environment, FileSystemLoader
import json
import os
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
workDir = os.path.dirname(question_path)

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
with open(os.path.join("datasource", "questions", "schemas.json"), 'r') as file:
    schemas = json.load(file)

# Load response area defaults
with open(os.path.join("datasource", "questions", "defaults.json"), 'r') as file:
    defaults = json.load(file)

# I don't know a better way to do this part, but we need to give each response area in a question its own unique number, as well as saving them to a list (this is how the manifest.xml question file is structured... with the <1> and <2> tags)
question["response_areas"] = []
identifier  = 1
for i in range(len(question["parts"])):
    if "response" in question["parts"][i]:
        question["response_areas"] += [add_defaults_and_validate(question["parts"][i]["response"], schemas, defaults)]
        question["parts"][i]["response"] = identifier
        identifier += 1

# If this question happens to be in a Tutorial sheet group, we need to retain the right links to any media it uses. To acheive this, we'll have to find out what sheet it is in...
sheet_info_path = os.path.join(workDir, "SheetInfo.json")
if os.path.exists(sheet_info_path):
    with open(sheet_info_path, "r") as file:
        sheetName = json.load(file)["name"]
else:
    sheetName = ''

####### SETUP TEMPLATING ENVIRONMENT #######
# Configure jinja environment
env = Environment(loader=FileSystemLoader("./templates"),
                  trim_blocks=True,
                  lstrip_blocks=True)

# Load globals into the Jinja2 environment
env.globals.update(consts=consts, sheetName=sheetName)

# Load master template from environment
master = env.get_template("master.xml")

####### RENDER AND EXPORT #######
# Render sheet data using master template
renderedXML = master.render(questions=[question])
print("XML Rendered Successfully")

# Create an output folder in the workdir if it doesn't already exist
if not os.path.exists(os.path.join(workDir, "renders")):
    os.mkdir(os.path.join(workDir, "renders"))

# Save rendered XML to that folder
with open(os.path.join(workDir, "renders", f"{question['number']}.xml"), 'w') as file:
    file.write(renderedXML)
