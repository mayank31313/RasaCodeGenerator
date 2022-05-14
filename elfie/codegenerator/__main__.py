from cndi.env import loadEnvFromFile, getContextEnvironment

from elfie.code_generator.consts import generateOutputIntentsString, generateOutputEntitiesString, \
    generateOutputActionsString
from elfie.doccano import downloadProjectData, RasaDoccanoClient
from elfie.yaml_generator.domain import RasaDomain
from elfie.yaml_generator.nlu import RasaNLU
import argparse


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("generate-sources", type=bool, default=False, nargs='?')
    args_parser.add_argument("generate-data", type=bool, default=False, nargs='?')
    args_parser.add_argument("--config", default="resources/application.yml", help="External Configuration for generator default path points to 'resources/application.yml'")

    args = args_parser.parse_args()
    generateSources = args.__getattribute__('generate-sources')
    generateData = args.__getattribute__('generate-data')

    loadEnvFromFile(args.config)

    rasaDoccanoClient = RasaDoccanoClient()
    projectId = int(getContextEnvironment("rcn.doccano.projectId"))

    doccanoExamples = downloadProjectData(projectId)
    doccanoRasaNlu = RasaNLU.readFromDoccanoData(doccanoExamples)

    intents = set(map(lambda intent: '.'.join(intent.label), doccanoRasaNlu.intents))
    entities = set()
    for intent in doccanoRasaNlu.intents:
        for entity in intent.entities:
            entities.add(entity['entityType'])

    actions = {'action_listen', 'action_restart'}
    actions.update(map(lambda intent: "action_" + intent, intents))
    actions.update(rasaDoccanoClient.getForms(projectId))

    rasaDomain = RasaDomain(intents=intents,
                            entities=entities,
                            actions=actions)



    if generateSources:
        generateOutputIntentsString(rasaDomain.intents)
        generateOutputEntitiesString(rasaDomain.entities)
        generateOutputActionsString(rasaDomain.actions)

    if generateData:
        doccanoRasaNlu.exportAsRasaNlu("data/nlu.yml")