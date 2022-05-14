from typing import List

from elfie.bot.utils import saveyaml, loadyaml
from elfie.story.step_definations import IntentStep, ActionStep, SlotWasSetStep, ActiveLoopStep


class RasaStory(object):
    def __init__(self, story, steps):
        self.story = story
        self.steps = steps

    def __hash__(self):
        hashs = tuple(map(hash, self.steps))
        return hash(hashs)

    def as_dict(self):
        steps = list(map(lambda step: step.as_dict(), self.steps.copy()))
        return dict(story=self.story,
                    steps=steps)
    @staticmethod
    def from_dict(obj):
        storyName = obj['story']
        steps = list()
        for step in obj['steps']:
            if 'intent' in step:
                stepObject = IntentStep(step['intent'],
                                        entities=step['entities'] if 'entities' in step else None)
            elif 'action' in step:
                stepObject = ActionStep(actionName=step['action'])
            elif 'slot_was_set' in step:
                stepObject = SlotWasSetStep()
                for slots in step['slot_was_set']:
                    for slot in slots:
                        stepObject.addSlot(slot, slots[slot])
            elif 'active_loop' in step:
                stepObject = ActiveLoopStep(actionName=step['active_loop'])
            else:
                stepObject = None

            steps.append(stepObject)

        return RasaStory(storyName, steps)

class RasaStories:
    def __init__(self, version='2.0'):
        self.stories: List[RasaStory] = list()
        self.version = version

    def addStory(self, story: RasaStory):
        self.stories.append(story)
        return self

    def interceptStoryToCreateBranch(self, intent_step_def:IntentStep, intents=[]):
        registeredStories = list()
        for story in self.stories:
            for index,step in enumerate(story.steps):
                if step.as_dict() == intent_step_def.as_dict():
                    for intent in intents:
                        copiedStory = RasaStory.from_dict(story.as_dict().copy())
                        copied_step_def = IntentStep(intent, intent_step_def.entities)
                        copiedStory.steps[index] = copied_step_def
                        registeredStories.append(copiedStory)

        self.stories.extend(registeredStories)


    @staticmethod
    def loadStoriesFromYaml(path):
        storiesData = loadyaml(path)
        rasaStories = RasaStories(version=storiesData['version'])
        stories = storiesData['stories']
        for story in stories:
            rasaStories.addStory(RasaStory.from_dict(story))
        return rasaStories

    def exportAsYaml(self, path):
        stories = list(dict(map(lambda story: (hash(story), story.as_dict()), self.stories.copy())).values())
        saveyaml(path, dict(
            version=self.version,
            stories=stories
        ))

class RasaStoryBuilder:
    def __init__(self, storyName):
        self.steps = list()
        self.story = storyName

    def addStep(self, step: object):
        self.steps.append(step)
        return self

    def build(self):
        rasaStory = RasaStory(steps=self.steps.copy(),
                              story=self.story)
        self.steps.clear()
        return rasaStory

