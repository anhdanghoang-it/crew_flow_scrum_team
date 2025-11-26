import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, llm
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter

@CrewBase
class QaLeadEvil():
    """QaLeadEvil crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # mcp_server_params = [
    #     # StdIO Server
    #     StdioServerParameters(
    #         command="npx",
    #         args=["@playwright/mcp@latest"],
    #     )
    # ]

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
    def qa_lead_evil_tester(self) -> Agent:
        return Agent(
            config=self.agents_config['qa_lead_evil_tester'], # type: ignore[index]
            llm=self.qa_plan_llm(),
            tools=self.get_mcp_tools(),
            verbose=True
        )

    @task
    def create_test_plan(self) -> Task:
        return Task(
            config=self.tasks_config['create_test_plan'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the QaLeadEvil crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
