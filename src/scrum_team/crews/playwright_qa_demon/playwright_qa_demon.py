from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, llm
import os
from crewai import LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from mcp import StdioServerParameters
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class PlaywrightQaDemon():
    """PlaywrightQaDemon crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    mcp_server_params = [
        # Playwright MCP Server with headless mode
        StdioServerParameters(
            command="npx",
            args=["playwright", "run-test-mcp-server", "--headless"],
        )
    ]

    @llm
    def qa_plan_llm(self):
        return LLM(
            model="gemini/gemini-2.5-flash-preview-09-2025",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.6, 
            top_p=0.9
        ) 

    @agent
    def playwright_test_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['playwright_test_generator'], # type: ignore[index]
            llm=self.qa_plan_llm(),
            tools=self.get_mcp_tools(),
            verbose=True
        )

    @task
    def generate_playwright_tests_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_playwright_tests_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PlaywrightQaDemon crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            memory=True,
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
