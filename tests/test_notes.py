from src.agent.notes import mark_unverified, split_claims

NOTES = """Here are the study notes:

PEAS is a framework used to design agents. It consists of four key components:

1. Performance measure: This is the goal of the agent.
* Sensors: These are the inputs the agent receives.
"""


def test_split_claims_skips_headings_and_chatter():
    assert split_claims(NOTES) == [
        "PEAS is a framework used to design agents.",
        "Performance measure: This is the goal of the agent.",
        "Sensors: These are the inputs the agent receives.",
    ]


def test_mark_unverified_tags_only_unsupported_claims():
    notes = "A thermostat is a basic agent. A self-driving car reaches its destination."

    def fake_check(claim, source):
        return "thermostat" in claim

    marked, stats = mark_unverified(notes, "lecture text", fake_check)
    assert "destination. [unverified]" in marked
    assert "agent. [unverified]" not in marked
    assert stats == {"checked": 2, "unverified": 1}


def test_checker_failure_is_not_marked_unverified():
    marked, stats = mark_unverified(
        "A thermostat is a basic agent.", "lecture text", lambda claim, source: None
    )
    assert "[unverified]" not in marked
    assert stats["unverified"] == 0