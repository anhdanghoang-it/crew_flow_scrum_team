from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task,llm
from crewai import LLM
from crewai.tasks.task_output import TaskOutput
import os
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import re
from pathlib import Path
from pydantic import BaseModel, Field

@CrewBase
class BackEndHellFlames():
    """BackEndHellFlames crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @llm
    def gemini_creative(self):
        # Best config for complex code implementation:
        # - Temperature 0.1: Low creativity, high precision for following technical specs
        # - Top_p 0.95: Standard setting for reasoning and code generation
        return LLM(
            model="gemini/gemini-2.5-pro",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1, 
            top_p=0.95
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
    def backend_dev_hell_flames(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_dev_hell_flames'], # type: ignore[index]
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
    def implement_backend_module(self) -> Task:
        return Task(
            config=self.tasks_config['implement_backend_module'], # type: ignore[index]
        )
    
    @task
    def write_python_backend_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_python_backend_task'], # type: ignore[index]
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the BackEndHellFlames crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            memory=True,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
