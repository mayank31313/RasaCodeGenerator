from cndi.env import loadEnvFromFile, getContextEnvironment
from doccano_api_client import DoccanoClient


def transformToDoccanoIntentClassificationAndSlotFilling(record: dict):
    return dict(text=record['cleanText'],
                entities=list(map(lambda entity: [entity['start'],entity['end'],entity['entityType']], record['entities'])),
                cats=record['label'])


class RasaDoccanoClient:
    def __init__(self):
        doccanoUrl = getContextEnvironment("rcn.doccano.url")
        doccanoUserName = getContextEnvironment("rcn.doccano.username")
        doccanoPassword = getContextEnvironment("rcn.doccano.password")

        self.doccanoClient = DoccanoClient(doccanoUrl, doccanoUserName, doccanoPassword)

    def getAllExamples(self, project_id):
        EXAMPLES = dict()
        url = f"/v1/projects/{project_id}/examples"
        while url is not None:
            data = self.doccanoClient.get(url)
            url = data['next']
            for result in data['results']:
                EXAMPLES[result['id']] = dict(text=result['text'],
                                              is_confirmed=result['is_confirmed']
                                              )

        return EXAMPLES

    def getForms(self, project_id):
        return list(filter(lambda x: x.endswith('form'), self.getCategories(project_id).values()))

    def getCategories(self,project_id):
        return dict(map(lambda category: (category['id'], category['text']),
                 self.doccanoClient.get(f"v1/projects/{project_id}/category-types")))

    def getSpans(self, project_id):
        return dict(map(lambda span: (span['id'], span['text']),
                        self.doccanoClient.get(f"/v1/projects/{project_id}/span-types")))

def downloadProjectData(project_id):
    rasaDoccanoClient = RasaDoccanoClient()
    EXAMPLES = rasaDoccanoClient.getAllExamples(project_id)

    CATEGORIES = rasaDoccanoClient.getCategories(project_id)

    SPANS = rasaDoccanoClient.getSpans(project_id)

    for example_id in EXAMPLES:
        url = f"v1/projects/{project_id}/examples/{example_id}/spans"
        spans = rasaDoccanoClient.doccanoClient.get(url)
        categories_linked = rasaDoccanoClient.doccanoClient.get(f"v1/projects/{project_id}/examples/{example_id}/categories")
        text = EXAMPLES[example_id]['text']

        entities = list(map(lambda span: dict(
                                        **span,
                                        entityType=SPANS[span['label']],
                                        entity=text[span['start_offset']-1:span['end_offset']-1]
                                    ), spans))
        uncleanedText = text
        for entity in entities:
            uncleanedText = uncleanedText.replace(entity['entity'], f"[{entity['entity']}]({entity['entityType']})")

        EXAMPLES[example_id] = dict(**EXAMPLES[example_id],
                                    uncleanedText = uncleanedText,
                                    entities=entities,
                                    categories=list(map(lambda category: CATEGORIES[category['label']], categories_linked))
                                )
    return EXAMPLES