#!/usr/bin/env python
from random import randint
import os
from pydantic import BaseModel
import re
from crewai.flow import Flow, listen, start
import subprocess
import time
import requests
import json
from typing import List, Optional

from scrum_team.crews.pm_demon_king_crew.pm_demon_king_crew import PmDemonKingCrew
from scrum_team.crews.tech_lead_devil_crew.tech_lead_devil_crew import TechLeadDevilCrew
from scrum_team.crews.back_end_hell_flames.back_end_hell_flames import BackEndHellFlames
from scrum_team.crews.front_end_skull_master.front_end_skull_master import FrontEndSkullMaster
from scrum_team.crews.qa_lead_evil.qa_lead_evil import QaLeadEvil
from scrum_team.crews.playwright_qa_demon.playwright_qa_demon import PlaywrightQaDemon
from scrum_team.crews.qa_lead_evil.models import TestPlanStructured, TestScenario, TestStep

class ScrumState(BaseModel):
    module_name: str = "trading_simulation"
    class_name: str = "TradingSimulation"
    requirements: str = ""
    user_stories_created: str = ""
    technical_design_created: str = ""
    backend_module_implemented: str = ""
    frontend_module_implemented: str = ""
    test_plan_created: str = ""
    test_plan_structured: Optional[TestPlanStructured] = None
    playwright_tests_generated: List[str] = []
    application_url: str = "http://127.0.0.1:7860/"

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
    #         .kickoff(inputs={
    #             "requirements": self.state.requirements,
    #         })
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
    #             "module_name": self.state.module_name,
    #             "class_name": self.state.class_name,
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
    #             "module_name": self.state.module_name,
    #             "class_name": self.state.class_name,
    #             })
    #     )

    #     print(f"{be_icon} {be_agent_name} Backend module implemented {be_icon}", result.raw)
    #     self.state.backend_module_implemented = result.raw


    # @listen(implement_backend_module)
    # def save_backend_module(self):
    #     self._save_code_to_file(
    #         self.state.backend_module_implemented, 
    #         f"{self.state.module_name}.py", 
    #         "backend module"
    #     )

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
    #             "module_name": self.state.module_name,
    #             "class_name": self.state.class_name,
    #             })
    #     )

    #     print(f"{fe_icon} {fe_agent_name} Frontend module implemented {fe_icon}", result.raw)
    #     self.state.frontend_module_implemented = result.raw

    # @listen(implement_frontend_module)
    # def save_frontend_module(self):
    #     self._save_code_to_file(
    #         self.state.frontend_module_implemented, 
    #         "app.py", 
    #         "frontend module"
    #     )

    # @listen(save_frontend_module)
    # def start_gradio_app(self):
    #     app_icon = "🚀🚀🚀🚀🚀🚀🚀🚀"
    #     print(f"{app_icon} Starting Gradio app server {app_icon}")
        
    #     app_path = "src/crew_generated/engineering/app.py"
    #     url = self.state.application_url
    #     timeout = 15  # 15 seconds
        
    #     # Start the app in background
    #     process = subprocess.Popen(
    #         ["uv", "run", app_path],
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         text=True
    #     )
        
    #     print(f"  - Process started with PID: {process.pid}")
    #     print(f"  - Waiting for server to be ready at {url}...")
    #     # Wait for server to be ready
    #     start_time = time.time()
    #     while time.time() - start_time < timeout:
    #         try:
    #             response = requests.get(url, timeout=1)
    #             if response.status_code == 200:
    #                 print(f"✅ Gradio app is running at {url}")
    #                 print(f"  - Server ready in {time.time() - start_time:.2f} seconds")
    #                 print(f"  - Server will continue running in background")
    #                 print(f"  - Proceeding to next step...")
    #                 # Server is ready, proceed to next step without blocking
    #                 return
    #         except (requests.RequestException, Exception):
    #             time.sleep(1)
        
    #     # Timeout reached
    #     print(f"❌ Server did not start within {timeout} seconds")
    #     process.terminate()
    #     stderr = process.stderr.read() if process.stderr else ""
    #     if stderr:
    #         print(f"Error output:\n{stderr}")
    #     raise Exception(f"Failed to start Gradio server within {timeout} seconds")
    
    # @listen(start_gradio_app)
    # @start()
    # def run_qa_testing(self):
    #     self._load_context()
    #     qa_icon = "👺👺👺👺👺👺👺👺"
    #     qa_agent_name = "QA Lead - Evil Tester"
    #     print(f"{qa_icon} {qa_agent_name} Creating comprehensive test plan {qa_icon}")
        
    #     # Use relative path to seed file
    #     seed_file_path = "e2e/seed.spec.ts"
    #     print(f"  - Seed file path: {seed_file_path}")
        
    #     result = (
    #         QaLeadEvil()
    #         .crew()
    #         .kickoff(inputs={
    #             "application_url": self.state.application_url,
    #             "user_stories": self.state.user_stories_created,
    #             "seed_file_path": seed_file_path,
    #             "module_name": self.state.module_name,
    #             })
    #     )        
        
    #     # Store both structured and raw outputs
    #     self.state.test_plan_structured = result.pydantic
    #     self.state.test_plan_created = result.raw
        
    #     num_scenarios = len(self.state.test_plan_structured.scenarios) if self.state.test_plan_structured else 0
    #     print(f"{qa_icon} {qa_agent_name} Test plan created with {num_scenarios} scenarios {qa_icon}")

    # @listen(run_qa_testing)
    @start()
    def generate_playwright_tests(self):
        self._load_context()
        pw_icon = "🎃🎃🎃🎃🎃🎃🎃🎃"
        pw_agent_name = "Playwright QA Demon"
        print(f"\n{pw_icon} {pw_agent_name} Generating Playwright test scripts {pw_icon}")
        
        if not self.state.test_plan_structured or not self.state.test_plan_structured.scenarios:
            print("⚠️  No test scenarios found in structured test plan. Skipping test generation.")
            return
        
        seed_file_path = "e2e/seed.spec.ts"
        total_scenarios = len(self.state.test_plan_structured.scenarios)
        max_scenarios = min(2, total_scenarios)  # Limit to first 2 scenarios
        
        print(f"  - Application URL: {self.state.application_url}")
        print(f"  - Seed File: {seed_file_path}")
        print(f"  - Total Scenarios: {total_scenarios} (generating first {max_scenarios})\n")
        
        # Iterate through first 2 test scenarios only
        for idx, scenario in enumerate(self.state.test_plan_structured.scenarios[:max_scenarios], 1):
            print(f"  [{idx}/{total_scenarios}] Generating test for: {scenario.test_id} - {scenario.title}")
            
            # Convert scenario to JSON for agent
            scenario_json = json.dumps(scenario.model_dump(), indent=2)
            
            try:
                result = (
                    PlaywrightQaDemon()
                    .crew()
                    .kickoff(inputs={
                        "application_url": self.state.application_url,
                        "seed_file": seed_file_path,
                        "test_scenario": scenario_json,
                    })
                )
                
                self.state.playwright_tests_generated.append(scenario.test_id)
                print(f"      ✅ Generated: {scenario.test_id}\n")
                
            except Exception as e:
                print(f"      ❌ Failed to generate {scenario.test_id}: {str(e)}\n")
                continue
        
        print(f"\n{pw_icon} Completed: {len(self.state.playwright_tests_generated)}/{max_scenarios} tests generated (limited to first 2 scenarios) {pw_icon}")
    
    def _save_code_to_file(self, content, filename, log_description):
        print(f"💾 Saving {log_description} to file...")
        
        # 1. Remove "Thought:" blocks (common in ReAct agents)
        # Handles single line or multi-line thoughts if they are clearly marked
        content = re.sub(r'^Thought:.*$', '', content, flags=re.MULTILINE)
        
        # 2. Extract code from markdown fences if present
        # Matches ```python ... ``` or ``` ... ```
        code_block_pattern = r"```(?:python|py)?\s*(.*?)```"
        match = re.search(code_block_pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            print("  - Found markdown code block, extracting content...")
            content = match.group(1)
            
        # 3. Clean up common conversational fillers at the start
        content = content.strip()
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            
            # Skip lines starting with "Thought:" (in case regex missed it or it's inside the block)
            if stripped.startswith("Thought:"):
                continue
                
            # Skip filename outputs like "filename.py"
            if stripped.endswith(".py") and len(stripped.split()) == 1:
                continue

            # If line starts with import, from, class, def, @, or """, it's likely code
            if stripped.startswith(('import ', 'from ', 'class ', 'def ', '@', '"""', "'''", '#')):
                start_idx = i
                break
            
            # If line looks like conversation, keep skipping
            if stripped.lower().startswith(('here is', 'sure', 'the code', 'below is', 'i have', 'creating', 'implementing')):
                continue
            
            # If we hit something else, assume it's code (or we can't tell)
            start_idx = i
            break
            
        content = "\n".join(lines[start_idx:])
        
        # Create the output directory if it doesn't exist
        output_dir = "src/crew_generated/engineering"
        os.makedirs(output_dir, exist_ok=True)
        
        # Write to file
        output_path = f"{output_dir}/{filename}"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ {log_description} saved to {output_path}")

    def _load_context(self):
        requirements_path = "docs/requirements.md"
        if os.path.exists(requirements_path):
            print(f"Loading requirements from {requirements_path}")
            with open(requirements_path, "r", encoding="utf-8") as f:
                self.state.requirements = f.read()
        else:
            print(f"File not found: {requirements_path}")

        user_stories_path = "docs/crew/trading_simulation_user_stories.md"
        if os.path.exists(user_stories_path):
            print(f"Loading user stories from {user_stories_path}")
            with open(user_stories_path, "r", encoding="utf-8") as f:
                self.state.user_stories_created = f.read()
        else:
            print(f"File not found: {user_stories_path}")

        technical_design_path = "docs/crew/trading_simulation_technical_design.md"
        if os.path.exists(technical_design_path):
            print(f"Loading technical design from {technical_design_path}")
            with open(technical_design_path, "r", encoding="utf-8") as f:
                self.state.technical_design_created = f.read()
        else:
            print(f"File not found: {technical_design_path}")

        test_plan_path = "docs/crew/trading_simulation_test_plan.json"
        if os.path.exists(test_plan_path):
            print(f"Loading test plan from {test_plan_path}")
            with open(test_plan_path, "r", encoding="utf-8") as f:
                test_plan_data = json.load(f)
                self.state.test_plan_created = json.dumps(test_plan_data, indent=2)
                self.state.test_plan_structured = TestPlanStructured(**test_plan_data)
            print(f"  - Loaded {len(self.state.test_plan_structured.scenarios)} test scenarios")
        else:
            print(f"File not found: {test_plan_path}")


def kickoff():
    """Run the full development workflow"""
    scrum_flow = ScrumFlow()
    scrum_flow.kickoff()

def kickoff_qa():
    """Run only QA testing workflow"""
    scrum_flow = ScrumFlow()
    scrum_flow.run_qa_testing()

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
