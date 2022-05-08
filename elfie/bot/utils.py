from yaml import load, Loader, dump, Dumper

def loadyaml(path):
    with open(path, "r") as stream:
        data = load(stream, Loader)
    return data

def saveyaml(path, data: dict):
    with open(path, "w") as stream:
        dump(data,stream, Dumper)

