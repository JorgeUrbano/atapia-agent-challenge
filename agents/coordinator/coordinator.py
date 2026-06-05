from agents.coordinator.planner import Planner


class Coordinator:

    def __init__(self):
        self.planner = Planner()

    def handle_message(self, user_message: str):

        plan = self.planner.create_plan(user_message)

        print("Execution Plan:")
        print(plan)

        return "Coordinator response placeholder"