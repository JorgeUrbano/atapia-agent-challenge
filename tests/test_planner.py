from agents.coordinator.planner import Planner


planner = Planner()

plan = planner.create_plan(
    "Me siento solo"
)

print(plan)