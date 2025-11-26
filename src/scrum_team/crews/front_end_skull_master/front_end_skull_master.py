from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, llm
from crewai import LLM
import os
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class FrontEndSkullMaster():
    """FrontEndSkullMaster crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @llm
    def gemini_creative(self):
        # Best config for frontend implementation:
        # - Temperature 0.2: Slightly higher than backend to allow for creative UI layout solutions, 
        #   but still low enough to ensure correct API usage and code structure.
        # - Top_p 0.9: Standard setting for balanced generation.
        return LLM(
            model="gemini/gemini-2.5-flash-preview-09-2025",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2, 
            top_p=0.9
        )

    @llm
    def gemini_flash_lite(self):
        # Best config for code cleanup:
        # - Temperature 0.0: Ensures deterministic output (no creativity/hallucinations)
        # - Top_p 0.1: Restricts to only the most probable tokens (exact code reproduction)
        return LLM(
            model="gemini/gemini-2.5-flash-lite",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.0, 
            top_p=0.1
        )

    @agent
    def frontend_dev_skull_master(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_dev_skull_master'], # type: ignore[index]
            allow_code_execution=True,
            code_execution_mode="safe",
            llm=self.gemini_creative(),
            verbose=True
        )
    
    @agent
    def code_writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['code_writer_agent'], # type: ignore[index]
            llm=self.gemini_flash_lite(),
            verbose=True
        ) 

    @task
    def implement_gradio_frontend(self) -> Task:
        return Task(
            config=self.tasks_config['implement_gradio_frontend'], # type: ignore[index]
        )

    @task
    def write_python_frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_python_frontend_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FrontEndSkullMaster crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            memory=True,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
