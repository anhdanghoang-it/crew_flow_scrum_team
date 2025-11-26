#!/usr/bin/env python
from random import randint
import os
from pydantic import BaseModel
import re
from crewai.flow import Flow, listen, start
import subprocess
import time
import requests

from scrum_team.crews.pm_demon_king_crew.pm_demon_king_crew import PmDemonKingCrew
from scrum_team.crews.tech_lead_devil_crew.tech_lead_devil_crew import TechLeadDevilCrew
from scrum_team.crews.back_end_hell_flames.back_end_hell_flames import BackEndHellFlames
from scrum_team.crews.front_end_skull_master.front_end_skull_master import FrontEndSkullMaster

class ScrumState(BaseModel):
    module_name: str = "trading_simulation"
    class_name: str = "TradingSimulation"
    requirements: str = ""
    user_stories_created: str = ""
    technical_design_created: str = ""
    backend_module_implemented: str = ""
    frontend_module_implemented: str = ""

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
    @start()
    def start_gradio_app(self):
        app_icon = "🚀🚀🚀🚀🚀🚀🚀🚀"
        print(f"{app_icon} Starting Gradio app server {app_icon}")
        
        app_path = "src/crew_generated/engineering/app.py"
        url = "http://127.0.0.1:7860"
        timeout = 120  # 2 minutes
        
        # Start the app in background
        process = subprocess.Popen(
            ["uv", "run", app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"  - Process started with PID: {process.pid}")
        print(f"  - Waiting for server to be ready at {url}...")
        
        # Wait for server to be ready
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    print(f"✅ Gradio app is running at {url}")
                    print(f"  - Server ready in {time.time() - start_time:.2f} seconds")
                    print(f"  - Press Ctrl+C to stop the server")
                    
                    # Keep the process running and stream output
                    try:
                        for line in process.stdout:
                            print(line, end='')
                    except KeyboardInterrupt:
                        print(f"\n{app_icon} Stopping Gradio app {app_icon}")
                        process.terminate()
                        process.wait(timeout=5)
                    return
            except (requests.RequestException, Exception):
                time.sleep(1)
        
        # Timeout reached
        print(f"❌ Server did not start within {timeout} seconds")
        process.terminate()
        stderr = process.stderr.read() if process.stderr else ""
        if stderr:
            print(f"Error output:\n{stderr}")
    
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

        # backend_module_path = "src/crew_generated/engineering/trading_simulation_backend.py"
        # if os.path.exists(backend_module_path):
        #     print(f"Loading backend module implementation from {backend_module_path}")
        #     with open(backend_module_path, "r", encoding="utf-8") as f:
        #         self.state.backend_module_implemented = f.read()
        # else:
        #     print(f"File not found: {backend_module_path}")

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
