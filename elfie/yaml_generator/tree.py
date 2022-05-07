from elfie.bot.utils import loadyaml
from elfie.yaml_generator.nlu import RasaNLURequest, Intent, RasaNLU

class IntentAssociatedEntities:
    def __init__(self, intent, entities):
        self.intent = intent
        self.entities = entities

class IntentTree:
    def __init__(self):
        self.intentTree = dict()
        self.entities = dict()

        self.rasaRequest = RasaNLURequest("http://localhost:5005")

    def parseToRasaNlu(self, examples: dict):
        intents_list = list()
        examples = self.mergeExamples(examples, {})
        for text, intents in examples.items():
            # responseData = self.rasaRequest.parseText(text)
            # entities = responseData['entities']
            # for entity in entities:
            #     text = text.replace(entity['value'], f"[{entity['value']}]({entity['entity']})")

            intents_list.append(Intent('.'.join(intents), text))

        return RasaNLU(intents_list)

    def mergeExamples(self, example1, example2):
        examples = dict()
        for text, intent_list in example1.items():
            if text not in examples:
                examples[text] = list()
            examples[text].extend(intent_list)

        for text, intent_list in example2.items():
            if text not in examples:
                examples[text] = list()
            examples[text].extend(intent_list)

        for example_text in examples:
            intents = set(examples[example_text])
            for intent in filter(lambda intent: intent not in self.intentTree, intents):
                self.intentTree[intent] = dict(intent=intent, parentIntent=None, priority=1000)

            intents = sorted(intents, key=lambda intent: self.intentTree[intent]['priority'], reverse=True)
            print(intents)
            removing_intents = set()
            for intent in intents:
                removing_intents.update(self.getParentIntentHierarchy(intent))
            for intent in removing_intents.intersection(intents):
                intents.remove(intent)
            examples[example_text] = sorted(intents)
        return examples

    def computePriorityForIntentTree(self):
        for intent in self.intentTree:
            currentIntent = intent
            while currentIntent is not None:
                self.intentTree[intent]['priority'] += 1
                currentIntent = self.intentTree[currentIntent]['parentIntent']

    def getParentIntentHierarchy(self, intent):
        intent = intent.strip()
        currentIntent = intent
        intents = list()
        while currentIntent is not None:
            intents.append(currentIntent)
            currentIntent = self.intentTree[currentIntent]['parentIntent']
        intents.remove(intent)
        return intents

    def parseExamples(self):
        examples = dict()
        for intentName, intent in self.intentTree.items():
            if 'examples' in intent:
                for example in intent['examples']:
                    example = example.strip()
                    if example not in examples:
                        examples[example] = list()
                    examples[example].extend(self.getParentIntentHierarchy(intent['intent']))
                    examples[example].append(intent['intent'])
        return examples

    def loadIntentTree(self, path):
        data = loadyaml(path)

        for intent in data:
            if 'entities' in intent:
                entityTypes = intent['entities']
                del intent['entities']
            else:
                entityTypes = list()

            self.intentTree[intent['intent']] = dict(**intent, priority=0)
            self.entities[intent['intent']] = IntentAssociatedEntities(intent['intent'], entityTypes)