import json

from elfie.doccano import transformToDoccanoIntentClassificationAndSlotFilling, downloadProjectData
from elfie.yaml_generator.domain import RasaDomain
from elfie.yaml_generator.nlu import RasaNLU
from elfie.yaml_generator.tree import IntentTree

if __name__ == '__main__':
    intentTree = IntentTree()
    intentTree.loadIntentTree("../resources/question_tree.yml")
    intentTree.loadIntentTree("../resources/greeting_tree.yml")
    intentTree.loadIntentTree("../resources/command_tree.yml")
    intentTree.loadIntentTree("../resources/copter_tree.yml")
    intentTree.loadIntentTree("../resources/no_parent_tree.yml")


    intentTree.computePriorityForIntentTree()
    examples = intentTree.parseExamples()
    doccanoExamples = downloadProjectData(2)
    doccanoRasaNlu = RasaNLU.readFromDoccanoData(doccanoExamples)

    examples = intentTree.mergeExamples(doccanoRasaNlu.examples, examples)
    rasaNlu = RasaNLU.readRasaNlu("D:\\Projects\\elfie\\controlnet_manager\\data\\nlu.yml")
    intentTreeRasaNlu = intentTree.parseToRasaNlu(examples)
    doccanoRasaNlu.mergeRasaNlu(intentTreeRasaNlu)
    doccanoRasaNlu.exportAsRasaNlu("text.yml")

    rasaDomain = RasaDomain()
    rasaDomain.addRasaNlu(doccanoRasaNlu)
    rasaDomain.exportToDomainYml("domain.yml")

    text_examples = list(map(lambda example: example['text'],doccanoExamples.values()))

    with open("output.json", "w") as stream:
        for example_text, labels in examples.items():
            if example_text in text_examples:
                continue
            data = transformToDoccanoIntentClassificationAndSlotFilling(dict(
                cleanText=example_text,
                entities=list(),
                label=labels
            ))
            stream.write(json.dumps(data) + "\n")