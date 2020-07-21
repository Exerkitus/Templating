# Public packages
from jinja2 import Environment, FileSystemLoader
import json
import os
import sys
from uuid import uuid4

# Custom packages
from datasource.validator import add_defaults_and_validate

##### GLOBALS #####
class consts:
    SCRIPTS_LOCATION = "/web/Pjohnso000/Public_Html/Scripts/QuestionJavaScript.txt"
    THEME_LOCATION = "/themes/cad8b55c-b186-4899-a406-b92966ee7766"
###################

# Function imports and sets up the question dict for injecting into the template
def importQuestion(question_path, SCHEMAS, DEFAULTS):
    # Load question data from file
    with open(question_path, 'r') as file:
        question = json.load(file)

    # If the question has not been given a uid yet, give it one
    if "uid" not in question:
        question["uid"] = str(uuid4())

        # Save it, this is important for version control
        with open(question_path, 'w') as file:
            json.dump(question, file, indent=3)

    # I don't know a better way to do this part, but we need to give each response area in a question its own unique number, as well as saving them to a list (this is how the manifest.xml question file is structured... with the <1> and <2> tags)
    question["response_areas"] = []
    identifier  = 1
    for i in range(len(question["parts"])):
        if "response" in question["parts"][i]:
            question["response_areas"] += [add_defaults_and_validate(question["parts"][i]["response"], SCHEMAS, DEFAULTS)]
            question["parts"][i]["response"] = identifier
            identifier += 1

    return question

####### LOAD AND SETUP DATA FOR SHEET #######
# Load response area schemas
with open(os.path.join("datasource", "questions", "schemas.json"), 'r') as file:
    SCHEMAS = json.load(file)

# Load response area defaults
with open(os.path.join("datasource", "questions", "defaults.json"), 'r') as file:
    DEFAULTS = json.load(file)

# Parse optional commandline arguments
if len(sys.argv) == 2:
    folder = sys.argv[1]
else:
    print("Please specify a path to the folder in which the questions are stored")
    quit()

# Fetch group information
with open(os.path.join(folder, "groupInfo.json"), 'r') as file:
    groupInfo = json.load(file)

# If the group has not been given a uid yet, give it one
if "uid" not in groupInfo:
    groupInfo["uid"] = str(uuid4())

    # Save it, this is important for version control
    with open(os.path.join(folder, "groupInfo.json"), 'w') as file:
        json.dump(groupInfo, file, indent=3)

# Fetch each question, storing them in a list
questions = []
for question_path in os.listdir(folder):
    if question_path.endswith(".json") and question_path != "groupInfo.json":
        questions += [importQuestion(os.path.join(folder, question_path), SCHEMAS, DEFAULTS)]

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
renderedHTML = master.render(questions=questions, groupInfo=groupInfo)

# For debugging
print(renderedHTML)

# Save rendered HTML to File
with open(os.path.join("renders", f"{groupInfo['name']}.xml"), 'w') as file:
    file.write(renderedHTML)
