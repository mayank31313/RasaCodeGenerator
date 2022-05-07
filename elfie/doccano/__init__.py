from cndi.env import loadEnvFromFile, getContextEnvironment
from doccano_api_client import DoccanoClient


def transformToDoccanoIntentClassificationAndSlotFilling(record: dict):
    return dict(text=record['cleanText'],
                entities=list(map(lambda entity: [entity['start'],entity['end'],entity['entityType']], record['entities'])),
                cats=record['label'])

def downloadProjectData(project_id):
    EXAMPLES = dict()
    doccanoUrl = getContextEnvironment("rcn.doccano.url")
    doccanoUserName = getContextEnvironment("rcn.doccano.username")
    doccanoPassword = getContextEnvironment("rcn.doccano.password")

    doccano_client = DoccanoClient(doccanoUrl, doccanoUserName, doccanoPassword)
    url = f"/v1/projects/{project_id}/examples"
    while url is not None:
        data = doccano_client.get(url)
        url = data['next']
        for result in data['results']:
            EXAMPLES[result['id']] = dict(text=result['text'],
                                          is_confirmed=result['is_confirmed']
                                          )

    CATEGORIES = dict(map(lambda category: (category['id'], category['text']),doccano_client.get(f"v1/projects/{project_id}/category-types")))
    SPANS = dict(map(lambda span: (span['id'], span['text']), doccano_client.get(f"/v1/projects/{project_id}/span-types")))

    for example_id in EXAMPLES:
        url = f"v1/projects/{project_id}/examples/{example_id}/spans"
        spans = doccano_client.get(url)
        categories_linked = doccano_client.get(f"v1/projects/{project_id}/examples/{example_id}/categories")
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