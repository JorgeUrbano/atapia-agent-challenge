from agents.coordinator.planner import Planner


planner = Planner()


def test_greeting():

    plan = planner.create_plan("Hello")

    assert plan.run_emotional is False
    assert plan.run_safety is False
    assert plan.run_guidance is False


def test_loneliness():

    plan = planner.create_plan(
        "I feel very lonely lately"
    )

    assert plan.run_emotional is True
    assert plan.run_guidance is True
    assert plan.run_safety is True


def test_anxiety():

    plan = planner.create_plan(
        "I am feeling anxious"
    )

    assert plan.run_emotional is True
    assert plan.run_guidance is True


def test_guidance_request():

    plan = planner.create_plan(
        "What can I do to sleep better?"
    )

    assert plan.run_guidance is True


def test_moderate_risk():

    plan = planner.create_plan(
        "Sometimes I wish I could disappear"
    )

    assert plan.run_safety is True


def test_high_risk():

    plan = planner.create_plan(
        "I want to kill myself"
    )

    assert plan.run_safety is True