from functools import wraps
from itertools import groupby

FUNCTIONAL_ACTIONS=dict()

def functionalaction(action_name, slot=None, hasReturn=True, ignore=False, func_name=None):
    def innerFunction(func):
        func.build_name = func_name
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        if ignore == False:
            FUNCTIONAL_ACTIONS[f'{action_name}___{slot}'] = {
                'func': wrapper,
                'slot': slot,
                'hasReturn': hasReturn,
                'isForm': action_name.lower().endswith('form'),
            }

        return wrapper

    return innerFunction

class FunctionGenerator:
    def __init__(self, name, params=[],content="", isAsync=False, hasReturn=False):
        self.content = content
        self.name = name
        self.params=params
        self.hasReturn = hasReturn
        self.isAsync = isAsync

    def __str__(self, declareIndent = 4, prependParams=[]):
        contents = []
        contents.append(("async " if self.isAsync else "") + f"def {self.name}({','.join(prependParams + self.params)}):\n")
        for content in self.content.split("\n"):
            contents.append(" " * declareIndent + ("return " if self.hasReturn else "" ) + str(content) + "\n")
        return ''.join(contents)

class ClassGenerator:
    def __init__(self, className:str,superClass=["object"], functions=[]):
        self.className = className.title()
        self.attributes = functions
        self.superClass = superClass

    def __str__(self, declareIndent=4):
        contents = list()
        contents.append(f"class {self.className.replace('.', '__')}({','.join(self.superClass)}):\n")
        for function in self.attributes:
            contents.append(" " * declareIndent + function.__str__(declareIndent=declareIndent+4, prependParams=["self"]) + "\n")

        return "".join(contents)

class ImportStatement:
    def __init__(self, module_name, module_package):
        self.module_name = module_name
        self.module_package = module_package

class ModuleGenerator:
    def __init__(self, contents=[], importStatements=[]):
        self.contents = contents
        self.importStatements = importStatements

    def __str__(self, declareIndent=4):
        contents = list()
        for module, group in groupby(self.importStatements, lambda x: x.module_package):
            contents.append(f"from {module} import {', '.join(map(lambda x: x.module_name,group))}\n")
        contents.append("\n"*3)
        for content in self.contents:
            contents.append(content.__str__(declareIndent))

        return ''.join(contents)

def writeToPythonFile(path, content):
    with open(path, "w") as file:
        file.write(content)
