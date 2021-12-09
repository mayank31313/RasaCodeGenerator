class Forms:
    def __init__(self, form_name, required_slots={}):
        self.name = form_name
        self.required_slots = required_slots
    def __dict__(self):

        slots = dict()
        for slot, type in self.required_slots.items():
            slots[slot] = [{
                "type": type
            }]
        return {
            'required_slots': slots
        }
