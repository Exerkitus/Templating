'''
TODO: Dynamic Sheet and question numbers
      Fix the weighting for questions
      Figure out media imports
'''

# Public packages
from jinja2 import Environment, FileSystemLoader
from uuid import uuid4
import json
import os
import sys
import shutil
from zipfile import ZipFile


# Custom packages
from datasource.validator import add_defaults_and_validate

##### GLOBALS #####
class consts:
    SCRIPTS_LOCATION = "/web/Pjohnso000/Public_Html/Scripts/QuestionJavaScript.txt"
    THEME_LOCATION = "/themes/cad8b55c-b186-4899-a406-b92966ee7766"
###################

##### FUNCTIONS #####
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
    workDir = sys.argv[1]
else:
    print("Please specify a path to the directory in which the questions are stored")
    quit()

# Fetch group information
try:
    with open(os.path.join(workDir, "SheetInfo.json"), 'r') as file:
        SheetInfo = json.load(file)
except FileNotFoundError:
    print("[ERROR] Folder specified does not contain the SheetInfo.json file")
    quit()

# If the group has not been given a uid yet, give it one
if "uid" not in SheetInfo:
    SheetInfo["uid"] = str(uuid4())

    # Save it, this is important for version control
    with open(os.path.join(workDir, "SheetInfo.json"), 'w') as file:
        json.dump(SheetInfo, file, indent=3)

# Fetch each question, storing them in a list
questions = []
for question_path in os.listdir(workDir):
    if question_path.endswith(".json") and question_path != "SheetInfo.json":
        questions += [importQuestion(os.path.join(workDir, question_path), SCHEMAS, DEFAULTS)]

####### SETUP TEMPLATING ENVIRONMENT #######
# Configure jinja environment
env = Environment(loader=FileSystemLoader("./templates"),
                  trim_blocks=True,
                  lstrip_blocks=True)

# Load globals into the Jinja2 environment
env.globals.update(consts=consts)

# Load master template from environment
master = env.get_template("master.xml")

####### RENDER, SORT OUT MEDIA AND EXPORT #######
# Render sheet data using master template
renderedXML = master.render(questions=questions, SheetInfo=SheetInfo)
print("XML Rendered Successfully")

# Create an output folder in the workdir if it doesn't already exist
if not os.path.exists(os.path.join(workDir, "renders")):
    os.mkdir(os.path.join(workDir, "renders"))

# Save rendered XML to that folder
with open(os.path.join(workDir, "renders", f"{SheetInfo['name']}.xml"), 'w') as file:
    file.write(renderedXML)

# If there is media to import, will need to zip .xml and web_folders together
media_path = os.path.join(workDir, "Media")
if os.path.isdir(media_path) and os.listdir(media_path):
    print("Detected Media folder - bundling media files and .xml")

    # Bundle all media files and xml in a zip
    with ZipFile(os.path.join(workDir, "renders", f"{SheetInfo['name']}.zip"), "w") as zip:
        # Write the xml file
        zip.write(os.path.join(workDir, "renders", f"{SheetInfo['name']}.xml"), arcname=f"{SheetInfo['name']}.xml")

        # Write media to web_folders inside of the zip file
        for media_file in os.listdir(media_path):
            zip.write(os.path.join(media_path, media_file), arcname=os.path.join("web_folders", f"{SheetInfo['name']}", media_file))
