from argparse import Action
from typing import List

from rasa_sdk import Action, FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from yaml import dump,load, Loader, Dumper
from elfie.code_generator import *
import os

from manager.consts.slots import REQUIRED_SLOTS

OUTPUT_DOMAIN_FILE = None

importStatements = [
    ImportStatement(Action.__name__, Action.__module__),
    ImportStatement(Tracker.__name__, Tracker.__module__),
    ImportStatement(CollectingDispatcher.__name__, CollectingDispatcher.__module__),
    ImportStatement(DomainDict.__name__, DomainDict.__module__),
    ImportStatement(List.__name__, List.__module__),
    ImportStatement(FormValidationAction.__name__, FormValidationAction.__module__)
]

class RasaDomainGenerator:
    def __init__(self, output_file,importStatement=[], forms=[]):
        global OUTPUT_DOMAIN_FILE
        self.domain = {
            "version": "2.0",
            'intents': set(),
            'entities': set(),
            'actions': set(),
            'slots': dict(),
            'forms': dict([(form.name, form.__dict__()) for form in forms]),
            "responses": dict()
        }
        OUTPUT_DOMAIN_FILE = output_file
        self.importStatements = importStatements + importStatement

        if os.path.exists(OUTPUT_DOMAIN_FILE):
            with open(OUTPUT_DOMAIN_FILE, "r") as stream:
                data = load(stream, Loader)
                for key, value in data.items():
                    if key in ["slots", "forms"]:
                        self.domain[key] = dict(value)
                        continue
                    if key in ["responses", "version", "session_config"]:
                        continue
                    self.domain[key] = set(value)

    def processResponses(self, responses):
        for utter_name in filter(lambda x: x.lower().startswith('utter'), dir(responses)):
            utter_text = getattr(responses, utter_name)
            self.domain["responses"][utter_name.lower()] = [{"text": utter_text}]

    def processIntents(self,intents):
        for intent_name in filter(lambda x: x.lower().startswith('intent'), dir(intents)):
            intent = getattr(intents, intent_name)
            self.domain['intents'].add(intent)
            if intent_name.lower().startswith('intent_action'):
                self.domain['actions'].add(f"action_{intent}")

    def processActions(self, actions):
        for action_name in filter(lambda x: x.lower().startswith('action') or x.lower().startswith("validate"),
                                  dir(actions)):
            action = getattr(actions, action_name)
            self.domain['actions'].add(action)

    def processEntities(self, slots):
        for slot_name in filter(lambda x: x.lower().startswith('entity'),dir(slots)):
            slot_value = getattr(slots, slot_name)
            if slot_name.lower().startswith('entity'):
                self.domain['entities'].add(slot_value)

    def processSlots(self, slots):
        for slot_name in filter(lambda x: x.lower().startswith('slot'),dir(slots)):
            _, slot_type = slot_name.split("___")
            slot_value = getattr(slots, slot_name)

            if isinstance(slot_value, str):
                self.domain['slots'][slot_value] = {
                    "type": slot_type.lower()
                }
                if slot_name.lower().startswith('slot_entity'):
                    self.domain['entities'].add(slot_value)

            elif isinstance(slot_value, dict):
                self.domain['slots'][slot_value['name']] = {
                    "type": slot_type.lower(),
                    **slot_value
                }

            self.processEntities(slots)

    def processDomain(self):
        for key in self.domain:
            if isinstance(self.domain[key], set):
                self.domain[key] = list(self.domain[key])

        with open(OUTPUT_DOMAIN_FILE, "w") as stream:
            dump(self.domain, stream, Dumper )


    def generateRasaActionClasses(self, outputPythonFile="generated.py"):
        TEMP_DICT = dict()
        class_generators = list()
        for action_name___slot, action_dict in FUNCTIONAL_ACTIONS.items():
            action_func = action_dict['func']
            action_name, _ = action_name___slot.split("___")
            action_slot = action_dict['slot']
            isForm = action_dict['isForm']
            action_name = "action_" + action_name if not isForm and not action_name.startswith(
                "action") else action_name
            superclass = Action.__name__
            tempfuncs = dict()
            if action_name in TEMP_DICT:
                tempfuncs = TEMP_DICT[action_name]['funcs']

            tempfuncs[action_slot] = action_func
            TEMP_DICT[action_name] = {
                'isForm': isForm,
                'funcs': tempfuncs
            }

            importStatements.append(ImportStatement(action_func.__name__, action_func.__module__))


        available_actions = set()
        for action_name, action_dict in TEMP_DICT.items():
            available_actions.add(action_name)
            function_generators = list()
            isForm = action_dict['isForm']

            for slotName, action_func in action_dict['funcs'].items():
                function_generator = None
                if slotName is not None and slotName != REQUIRED_SLOTS:
                    function_generator = FunctionGenerator(f'validate_{slotName}',
                                                           params=["slot_value","dispatcher: CollectingDispatcher", "tracker: Tracker",
                                                                   "domain: DomainDict", '**kwargs'],
                                                           content=f"{action_func.__name__}(slot_value=slot_value, dispatcher=dispatcher, tracker=tracker, domain=domain, **kwargs)",
                                                           isAsync=False, hasReturn=True)
                elif slotName is None:
                    function_generator = FunctionGenerator(action_func.build_name if action_func.build_name is not None else 'run',
                                                            params=["dispatcher: CollectingDispatcher", "tracker: Tracker", "domain: DomainDict", '**kwargs'],
                                                            content=f"{action_func.__name__}(dispatcher=dispatcher, tracker=tracker, domain=domain, **kwargs)",
                                                           isAsync=True, hasReturn=True)
                elif slotName == REQUIRED_SLOTS and isForm == True:
                    function_generator = FunctionGenerator(REQUIRED_SLOTS,
                                                           params=['slots_mapped_in_domain: List','dispatcher: CollectingDispatcher','tracker: Tracker','domain: DomainDict', '**kwargs'],
                                                            content=f"{action_func.__name__}(slots_mapped_in_domain=slots_mapped_in_domain,dispatcher=dispatcher, tracker=tracker, domain=domain, **kwargs)", isAsync=True, hasReturn=True)
                if function_generator is not None:
                    function_generators.append(function_generator)

            name_generator = FunctionGenerator('name',content=f"""
                                return "{action_name}"
                            """.strip())
            function_generators.append(name_generator)

            class_generator = ClassGenerator(action_name, functions=function_generators, superClass=[FormValidationAction.__name__ if isForm else Action.__name__])

            class_generators.append(class_generator)

        module_generator = ModuleGenerator(contents=class_generators,
                                           importStatements=importStatements)


        generated_str = module_generator.__str__() + ("\n" * 5)

        with open(outputPythonFile, "w") as stream:
            stream.write("""\n\n"AUTO GENERATED CODE DO NOT EDIT DIRECTLY"\n\n\n""")
            stream.write(generated_str)

        for actions_name in set(self.domain['actions']).difference(available_actions):
            print(f"Action not Implemented: {actions_name}")

