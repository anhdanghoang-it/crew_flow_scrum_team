#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from scrum_team.crews.pm_demon_king_crew.pm_demon_king_crew import PmDemonKingCrew
from scrum_team.crews.tech_lead_devil_crew.tech_lead_devil_crew import TechLeadDevilCrew


class ScrumState(BaseModel):
    requirements: str = ""
    user_stories_created: str = ""
    technical_design_created: str = ""





class ScrumFlow(Flow[ScrumState]):
    @start()
    def generate_user_stories(self, crewai_trigger_payload: dict = None):
        pm_icon = "👹👹👹👹👹👹👹👹"
        pm_agent_name = f"Demon King PM"
        print(f"{pm_icon} {pm_agent_name} Generating user stories{pm_icon}")
        with open(f"docs/requirements.md", "r", encoding="utf-8") as f:
            requirements = f.read()
        self.state.requirements = requirements
        result = (
            PmDemonKingCrew()
            .crew()
            .kickoff(inputs={"requirements": self.state.requirements})
        )

        print(f"{pm_icon} {pm_agent_name} User stories generated{pm_icon}", result.raw)
        self.state.user_stories_created = result.raw

    @listen(generate_user_stories)
    def create_technical_design(self):
        tl_icon = "😈😈😈😈😈😈😈😈"
        tl_agent_name = f"Tech Lead Devil"
        print(f"{tl_icon} {tl_agent_name} Creating technical design{tl_icon}")
        result = (
            TechLeadDevilCrew()
            .crew()
            .kickoff(inputs={
                "user_stories": self.state.user_stories_created,
                "requirements": self.state.requirements,
                })
        )

        print(f"{tl_icon} {tl_agent_name} Technical design created{tl_icon}", result.raw)
        self.state.technical_design_created = result.raw

    # @listen(create_technical_design)
    # def save_technical_design(self):
    #     print(f"{tl_icon} {tl_agent_name} Saving technical design to file")
    #     with open("docs/crew/technical_design.md", "w") as f:
    #         f.write(self.state.technical_design_created)

def kickoff():
    scrum_flow = ScrumFlow()
    scrum_flow.kickoff()


def plot():
    scrum_flow = ScrumFlow()
    scrum_flow.plot("scrum_flow.html")


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
