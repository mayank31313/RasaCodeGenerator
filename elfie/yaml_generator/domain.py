from elfie.bot.utils import saveyaml


class RasaDomain:
    def __init__(self):
        self.intents = set()
        self.entities = set()
        self.forms = dict()
        self.slots = dict()
        self.actions = list()

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