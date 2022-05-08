
class IntentStep:
    def __init__(self, intentName, entities=None):
        self.intent = intentName
        self.entities = entities

    def __hash__(self):
        return hash(self.intent)

    def as_dict(self):
        responseObject = dict(
            intent=self.intent,
        )
        if self.entities is not None:
            responseObject['entities'] = self.entities
        return responseObject

class SlotWasSetStep:
    def __init__(self):
        self.slots = list()

    def addSlot(self, slotName, slotValue):
        self.slots.append({slotName: slotValue})
        return self

    def __hash__(self):
        hashs = tuple(map(lambda object: hash(zip(
                                                tuple(object.keys()),
                                                tuple(object.values())
                                            )), self.slots))
        return hash(hashs)

    def as_dict(self):
        return dict(
            slot_was_set=self.slots
        )

class ActionStep:
    def __init__(self, actionName):
        self.actionName = actionName

    def __hash__(self):
        return hash(self.actionName)

    def as_dict(self):
        return dict(action=self.actionName)

class ActiveLoopStep:
    def __init__(self, actionName):
        self.actionName = actionName
    def __hash__(self):
        return hash(self.actionName)
    def as_dict(self):
        return dict(active_loop=self.actionName)
