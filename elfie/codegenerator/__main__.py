from cndi.env import loadEnvFromFile, getContextEnvironment

from elfie.code_generator.consts import generateOutputIntentsString, generateOutputEntitiesString, \
    generateOutputActionsString
from elfie.code_generator.forms import Forms
from elfie.doccano import downloadProjectData
from elfie.yaml_generator.domain import RasaDomain
from elfie.yaml_generator.nlu import RasaNLU
from elfie.yaml_generator.tree import IntentTree
import argparse


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("generate-sources", type=bool, default=False, nargs='?')
    args_parser.add_argument("--config", default="resources/application.yml")

    args = args_parser.parse_args()

    # if args.help:
    #     args_parser.print_help()
    #     exit(0)

    generateSources = args.__getattribute__('generate-sources')

    loadEnvFromFile(args.config)

    projectId = int(getContextEnvironment("rcn.doccano.projectId"))
    doccanoExamples = downloadProjectData(projectId)
    doccanoRasaNlu = RasaNLU.readFromDoccanoData(doccanoExamples)

    intents = set(map(lambda intent: '.'.join(intent.label), doccanoRasaNlu.intents))
    entities = set()
    actions = {'action_listen', 'action_restart'}
    actions.update(map(lambda intent: "action_" + intent, intents))

    if generateSources:
        generateOutputIntentsString(intents)
        generateOutputEntitiesString(entities)
        generateOutputActionsString(actions)