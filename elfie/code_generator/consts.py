
import os

from cndi.env import getContextEnvironment

from elfie.code_generator import writeToPythonFile

CONSTS_CREATION_STRING = '''
# GENERATED CODE
"""
created by default
@author mayank31313
"""


'''

def checkForConstsOutputDir(filename):
    constsdir = os.path.abspath(getContextEnvironment("rcn.autogenerate.consts.dir"))
    if not os.path.exists(constsdir):
        os.makedirs(constsdir)

    return os.path.join(constsdir, filename)

def generateOutputEntitiesString(entities):
    formatedString = ""
    for entity in entities:
        formatedString += f"ENTITY_{entity.replace('.','_').upper()} = '{entity.strip()}'{os.linesep}"

    absoluteFilePath = checkForConstsOutputDir("entities.py")
    writeToPythonFile(absoluteFilePath, CONSTS_CREATION_STRING + formatedString)
    return absoluteFilePath

def generateOutputIntentsString(intents):
    formatedString = ""
    for intent in intents:
        formatedString += f"INTENT_{intent.replace('.','_').upper()} = '{intent.strip()}'{os.linesep}"

    absoluteFilePath = checkForConstsOutputDir("intents.py")
    writeToPythonFile(absoluteFilePath, CONSTS_CREATION_STRING + formatedString)
    return absoluteFilePath

def generateOutputActionsString(actions):
    formatedString = ""
    for action in actions:
        formatedString += f"{action.replace('.','_').upper()} = '{action.strip()}'{os.linesep}"

    absoluteFilePath = checkForConstsOutputDir("actions.py")
    writeToPythonFile(absoluteFilePath, CONSTS_CREATION_STRING + formatedString)
    return absoluteFilePath


