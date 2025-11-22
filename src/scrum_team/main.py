#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from scrum_team.crews.pm_demon_king_crew.pm_demon_king_crew import PmDemonKingCrew
from scrum_team.crews.tech_lead_devil_crew.tech_lead_devil_crew import TechLeadDevilCrew
from scrum_team.crews.back_end_hell_flames.back_end_hell_flames import BackEndHellFlames
from scrum_team.crews.front_end_skull_master.front_end_skull_master import FrontEndSkullMaster

class ScrumState(BaseModel):
    module_name: str = f"trading_simulation"
    class_name: str = f"TradingSimulation"
    requirements: str = ""
    user_stories_created: str = ""
    technical_design_created: str = ""
    backend_module_implemented: str = ""

class ScrumFlow(Flow[ScrumState]):
    # @start()
    # def generate_user_stories(self, crewai_trigger_payload: dict = None):
    #     pm_icon = "👹👹👹👹👹👹👹👹"
    #     pm_agent_name = f"Demon King PM"
    #     print(f"{pm_icon} {pm_agent_name} Generating user stories {pm_icon}")
    #     with open(f"docs/requirements.md", "r", encoding="utf-8") as f:
    #         requirements = f.read()
    #     self.state.requirements = requirements
    #     result = (
    #         PmDemonKingCrew()
    #         .crew()
    #         .kickoff(inputs={"requirements": self.state.requirements})
    #     )

    #     print(f"{pm_icon} {pm_agent_name} User stories generated{pm_icon}", result.raw)
    #     self.state.user_stories_created = result.raw

    # @listen(generate_user_stories)
    # def create_technical_design(self):
    #     tl_icon = "😈😈😈😈😈😈😈😈"
    #     tl_agent_name = f"Tech Lead Devil"
    #     print(f"{tl_icon} {tl_agent_name} Creating technical design {tl_icon}")
    #     result = (
    #         TechLeadDevilCrew()
    #         .crew()
    #         .kickoff(inputs={
    #             "user_stories": self.state.user_stories_created,
    #             "requirements": self.state.requirements,
    #             })
    #     )

    #     print(f"{tl_icon} {tl_agent_name} Technical design created {tl_icon}", result.raw)
    #     self.state.technical_design_created = result.raw

    # @listen(create_technical_design)
    # def implement_backend_module(self):
    #     be_icon = "🔥🔥🔥🔥🔥🔥🔥🔥"
    #     be_agent_name = f"Backend Dev Hell Flames"
    #     print(f"{be_icon} {be_agent_name} Implementing backend module {be_icon}")
    #     result = (
    #         BackEndHellFlames()
    #         .crew()
    #         .kickoff(inputs={
    #             "technical_design": self.state.technical_design_created,
    #             "user_stories": self.state.user_stories_created,
    #             })
    #     )

    #     print(f"{be_icon} {be_agent_name} Backend module implemented {be_icon}", result.raw)
    #     self.state.backend_module_implemented = result.raw

    # @listen(implement_backend_module)
    # def implement_frontend_module(self):
    #     fe_icon = "💀💀💀💀💀💀💀💀"
    #     fe_agent_name = f"Frontend Dev Skull Master"
    #     print(f"{fe_icon} {fe_agent_name} Implementing frontend module {fe_icon}")
    #     result = (
    #         FrontEndSkullMaster()
    #         .crew()
    #         .kickoff(inputs={
    #             "backend_module": self.state.backend_module_implemented,
    #             "technical_design": self.state.technical_design_created,
    #             "user_stories": self.state.user_stories_created,
    #             })
    #     )

    #     print(f"{fe_icon} {fe_agent_name} Frontend module implemented {fe_icon}", result.raw)

    @start()
    def implement_frontend_module(self):
        fe_icon = "💀💀💀💀💀💀💀💀"
        fe_agent_name = f"Frontend Dev Skull Master"
        self.load_context()
        print(f"{fe_icon} {fe_agent_name} Implementing frontend module {fe_icon}")
        result = (
            FrontEndSkullMaster()
            .crew()
            .kickoff(inputs={
                "backend_module": self.state.backend_module_implemented,
                "technical_design": self.state.technical_design_created,
                "user_stories": self.state.user_stories_created,
                })
        )

        print(f"{fe_icon} {fe_agent_name} Frontend module implemented {fe_icon}", result.raw)        

    def load_context(self):
        print(f"Loading requirements from docs/requirements.md")
        with open(f"docs/requirements.md", "r", encoding="utf-8") as f:
            self.state.requirements = f.read()

        print(f"Loading user stories from docs/crew/trading_simulation_user_stories.md")
        with open(f"docs/crew/trading_simulation_user_stories.md", "r", encoding="utf-8") as f:
            self.state.user_stories_created = f.read()

        print(f"Loading technical design from docs/crew/trading_simulation_technical_design.md")
        with open(f"docs/crew/trading_simulation_technical_design.md", "r", encoding="utf-8") as f:
            self.state.technical_design_created = f.read()

        print(f"Loading backend module implementation from src/crew_generated/engineering/trading_simulation_backend.py")
        with open(f"src/crew_generated/engineering/trading_simulation_backend.py", "r", encoding="utf-8") as f:
            self.state.backend_module_implemented = f.read()

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
