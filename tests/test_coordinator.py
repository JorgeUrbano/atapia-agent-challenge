from agents.coordinator.coordinator import Coordinator

coordinator = Coordinator()

response = coordinator.handle_message(
    "Me siento bastante solo últimamente"
)

print(response)