from core.classes.Task import Task

class TaskGroup:
    def __init__(self, task_group_id, name):
        self.id = task_group_id
        self.name = name
        self.tasks = []

    def add_task(self, name, urgency, importance, completion):
        self.tasks.append(Task(name, urgency, importance, completion))
