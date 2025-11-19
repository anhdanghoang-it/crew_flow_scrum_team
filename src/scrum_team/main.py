#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from scrum_team.crews.poem_crew.poem_crew import PoemCrew
from scrum_team.crews.engineering_team.engineering_team import EngineeringTeam


class ScrumState(BaseModel):
    requirements: str = ""
    user_stories_created: str = ""

class ScrumFlow(Flow[ScrumState]):
    @start()
    def generate_user_stories(self, crewai_trigger_payload: dict = None):
        print("Generating user stories")
        with open(f"docs/requirements.md", "r", encoding="utf-8") as f:
            requirements = f.read()
        self.state.requirements = requirements
        result = (
            EngineeringTeam()
            .crew()
            .kickoff(inputs={"requirements": self.state.requirements})
        )

        print("User stories generated", result.raw)
        self.state.user_stories_created = result.raw

    @listen(generate_user_stories)
    def save_user_stories(self):
        print("Saving user stories to file")
        with open("docs/crew/user_stories/trading_simulation.md", "w") as f:
            f.write(self.state.user_stories_created)


def kickoff():
    scrum_flow = ScrumFlow()
    scrum_flow.kickoff()


def plot():
    scrum_flow = ScrumFlow()
    scrum_flow.plot()


def run_with_trigger():
    """
    Run the flow with trigger payload.
    """
    import json
    import sys

    # Get trigger payload from command line argument
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    # Create flow and kickoff with trigger payload
    # The @start() methods will automatically receive crewai_trigger_payload parameter
    poem_flow = ScrumFlow()

    try:
        result = poem_flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow with trigger: {e}")


if __name__ == "__main__":
    kickoff()
