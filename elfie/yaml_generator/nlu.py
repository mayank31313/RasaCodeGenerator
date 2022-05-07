import json

import requests

from elfie.bot.utils import loadyaml, saveyaml
import re

from elfie.doccano import downloadProjectData


class RasaNLURequest:
    def __init__(self, url):
        self.url = url

    def parseText(self, text):
        response = requests.post(f"{self.url}/model/parse", data=json.dumps({
            "text": text
        }))

        return response.json()

class Intent(object):
    def __init__(self, intents, text):
        self.label = intents
        if isinstance(self.label, str):
            self.label = [self.label]
        self.text = text
        self.cleanText = self.clearText()
        self.entities = self.parseEntities()

    def clearText(self):
        matches = re.search("\[(?P<entity_text>[a-zA-Z ]+)\]\((?P<entity_type>[a-zA-Z_]+)\)", self.text)
        if matches is None:
            return self.text
        cleanedText = self.text

        for group in matches.groupdict():
            start, end = matches.span(group)
            replacement = matches.group(group) if group != "entity_type" else ""
            cleanedText = cleanedText.replace(self.text[start-1:end+1], replacement)

        return cleanedText

    def parseEntities(self):
        matches = re.search("\[(?P<entity_text>[a-zA-Z0-9 ]+)\]\((?P<entity_type>[a-zA-Z_]+)\)", self.text)
        entities = list()
        if matches  is not None:
            start,end = matches.span('entity_text')
            entityType = matches.group('entity_type')
            entityText = matches.group('entity_text')
            entity = dict(start=start,end=end,entityType=entityType, entity=entityText)
            entities.append(entity)
        return entities



def dumpRasaNluFileFromDoccano(path: str, projectId):
    examples = downloadProjectData(projectId)
    nlu = dict()
    for example_id, example in examples.items():
        intent = example['categories'][0]
        if intent not in nlu:
            nlu[intent] = list()

        text = example['text']
        entities = example['entities']
        for entity in entities:
            text = text.replace(entity['entity'], f"[{entity['entity']}]({entity['entityType']})")

        nlu[intent].append(text)

    nlu = dict(version="2.0",
               nlu= list(
                   map(lambda intent: dict(
                       intent=intent,
                       examples="".join(map(lambda text: f"- {text}", nlu[intent]))
                   ), nlu)
               )
          )
    saveyaml(path, nlu)

class RasaNLU:
    def __init__(self, intents: list):
        self.intents = intents
        self.examples = dict()
        self.loadExamples(self.intents)

    def loadExamples(self, intents):
        self.examples.clear()
        for intent in intents:
            if intent.cleanText not in self.examples:
                self.examples[intent.cleanText] = list()

            self.examples[intent.cleanText].extend(intent.label)

    def flatMapIntents(self):
        intents = list()
        for intent in self.intents:
            for label in intent.label:
                intents.append(Intent(label, intent.text))
        return RasaNLU(intents)

    def filterIntents(self, intents: list):
        flatRasaNlu = self.flatMapIntents()
        filteredIntents = list(filter(lambda x: x.label[0] in intents, flatRasaNlu.intents))
        return RasaNLU(filteredIntents)

    def exportAsRasaNlu(self, path):
        nlu = dict()

        for intent in self.intents:
            for category in intent.label:
                if category not in nlu:
                    nlu[category] = list()
                nlu[category].append(intent.text)

        nlu = dict(version="2.0",
                   nlu=list(
                       map(lambda intent: dict(
                           intent=intent,
                           examples="".join(map(lambda text: f"- {text}", nlu[intent]))
                       ), nlu)
                   )
                )
        saveyaml(path, nlu)

    def mergeRasaNlu(self, other):
        self.intents.extend(other.intents)
        self.loadExamples(self.intents)

    @staticmethod
    def readFromDoccanoData(doccanoExamples):
        intents_list = list()
        for example_id, example in doccanoExamples.items():
            intents = example['categories']
            text = example['uncleanedText']
            intents_list.append(Intent(intents, text))

        return RasaNLU(intents_list)

    @staticmethod
    def readRasaNlu(path):
        nluFileData = loadyaml(path)
        intents = nluFileData['nlu']

        nluIntents = list()
        for intent in intents:
            for example in intent['examples'].split("-"):
                nluIntents.append(Intent(intent['intent'], example.replace('-', '').replace('\n', '').strip()))

        return RasaNLU(nluIntents)