from elfie.bot.utils import saveyaml, loadyaml
from elfie.code_generator.forms import Forms


class RasaDomain:
    def __init__(self, intents=None,
                 entities=None, forms=None,
                 actions=None, slots=None):
        if slots is None:
            slots = dict()
        if actions is None:
            actions = set()
        if forms is None:
            forms = dict()
        if entities is None:
            entities = set()
        if intents is None:
            intents = set()
        self.intents = intents
        self.entities = entities
        self.forms = forms
        self.slots = slots
        self.actions = actions

    @staticmethod
    def readFromYamlFile(path):
        domainData = loadyaml(path)
        rasaDomain = RasaDomain(intents=set(domainData['intents']),
                                entities=set(domainData['entities']),
                                actions=set(domainData['actions']),
                                slots=domainData['slots'],
                                forms=domainData['forms'])

        return rasaDomain

    def addForms(self, form: Forms):
        self.forms[form.name] = form.__dict__()
    def mergeDomains(self, other):
        self.intents.update(other.intents)
        self.entities.update(other.entities)
        self.actions.update(other.actions)
        for form_key in other.forms:
            if form_key in self.forms:
                continue
            self.forms[form_key] = other.forms[form_key]

        for slot_key in other.slots:
            if slot_key in self.slots:
                continue
            self.slots[slot_key] = other.slots[slot_key]

    def addRasaNlu(self, rasaNlu):
        for intent in rasaNlu.intents:
            self.intents.update(intent.label)
            self.entities.update(map(lambda entity: entity['entityType'], intent.entities))

    def exportToDomainYml(self, path):
        domain = dict(
            version="2.0",
            intents=list(self.intents),
            entities=list(self.entities),
            actions=list(self.actions),
            forms=self.forms,
            slots=self.slots,
            session_config=dict(
                session_expiration_time=60,
                carry_over_slots_to_new_session=True
            )
        )

        saveyaml(path, domain)