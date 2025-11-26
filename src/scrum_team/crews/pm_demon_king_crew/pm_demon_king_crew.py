from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, llm
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class PmDemonKingCrew():
    """PmDemonKingCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @llm
    def pm_llm(self):
        return LLM(
            model="gemini/gemini-2.5-flash-preview-09-2025",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.6, 
            top_p=0.9
        )

    @agent
    def product_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['product_manager'], # type: ignore[index]
            llm=self.pm_llm(),
            verbose=True
        )

    @task
    def create_userstories_task(self) -> Task:
        return Task(
            config=self.tasks_config['create_userstories_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PmDemonKingCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            memory=True,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
