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


class BackendModuleOutput(BaseModel):
    """Structured output for backend module implementation."""
    code: str = Field(
        description="Complete Python code for the backend module, ready to be saved as a .py file"
    )
    module_name: str = Field(
        description="Name of the module (e.g., 'trading_simulation', 'account_management')"
    )

@CrewBase
class BackEndHellFlames():
    """BackEndHellFlames crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @llm
    def gemini_creative(self):
        return LLM(
            model="gemini/gemini-2.5-pro",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3, 
            top_p=0.85
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
            verbose=True
        )
    
    @task
    def implement_backend_module(self) -> Task:
        return Task(
            config=self.tasks_config['implement_backend_module'], # type: ignore[index]
            output_pydantic=BackendModuleOutput,
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
