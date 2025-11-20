# 😈 THE DEMON TEAM Crew

Welcome to the 😈 THE DEMON TEAM Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Dual Agent Architecture

This project intentionally supports two parallel concepts of AI agent collaboration, serving similar product goals through different execution models:

1. **GitHub Copilot Custom Agents** (`.github/agents/`)
	- Lightweight, repo-native automation primitives you can evolve into GitHub workflows or external triggers.
	- Ideal for on-demand generation and iterative refinement directly alongside code (user stories, designs, backend models, UI scaffolding).
	- Recommended when you want rapid, developer-centric generation without running a full CrewAI flow.

2. **CrewAI Flow (Automated End-to-End)** (`crewai run`)
	- Orchestrated, stateful multi-agent execution across defined tasks and roles.
	- Ideal for larger, repeatable flows producing comprehensive artifacts (reports, full technical design packs, multi-file implementations).
	- Uses the configuration in `src/scrum_team/config/` plus any custom tools.

### Shared Role Model
Both agent sets target the same collaborative lifecycle, with each role specializing in a stage of delivery:

- **PM Agent**: Generates and refines user stories (scope, acceptance criteria).
- **Technical Lead Agent**: Produces architectural & technical design documentation.
- **Backend Developer Agent**: Implements Python backend models & service logic.
- **Frontend (Gradio) Developer Agent**: Builds the interactive UI (`app.py`) for account management & trading.

### When to Use Which
| Scenario | Choose Copilot Custom Agents | Choose CrewAI Flow |
|----------|------------------------------|--------------------|
| Quick, ad-hoc generation (single artifact) | ✅ | |
| Full multi-stage delivery (stories → design → code → UI) | | ✅ |
| Tight iteration inside PRs | ✅ | |
| Repeatable scheduled workflow | | ✅ |
| Minimal setup / fast feedback | ✅ | |
| Rich orchestration & chaining | | ✅ |

If the `.github/agents/` directory is not yet present, create it to begin defining JSON/YAML/Markdown specs for Copilot custom agents (e.g., prompts, expected outputs, invocation guidance). These agents do not require the CrewAI runtime; they complement it.

### Typical Hybrid Workflow
1. Draft initial user stories with a Copilot PM agent.
2. Convert to a formal technical design via Copilot Technical Lead agent.
3. Decide: quick prototype (stay in Copilot agents) or full orchestrated generation (switch to CrewAI flow).
4. Run `crewai run` to have CrewAI agents elaborate, cross-verify, and produce integrated outputs.
5. Use Copilot agents again for incremental adjustments inside feature branches.

---

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/scrum_team/config/agents.yaml` to define your agents
- Modify `src/scrum_team/config/tasks.yaml` to define your tasks
- Modify `src/scrum_team/crew.py` to add your own logic, tools and specific args
- Modify `src/scrum_team/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your flow and begin execution, run this from the root folder of your project:

```bash
crewai run
```

This command initializes the scrum_team Flow as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Running Copilot Custom Agents

While CrewAI handles orchestrated flows, Copilot custom agents (in `.github/agents/`) can be invoked manually or integrated into GitHub Actions. Suggested structure:

```
.github/agents/
	pm_user_stories.md
	tech_design.md
	backend_generation.md
	frontend_ui_scaffold.md
```

Each file should describe:
- Objective
- Input expectations (e.g., existing specs, domain constraints)
- Output format (Markdown sections, code blocks, files to create)
- Validation checklist

You can then reference these artifacts when prompting Copilot Chat or embedding them in automation.

## Trading Simulation UI

The `src/scrum_team/engineering/app.py` file exposes a Gradio interface that covers all account-management user stories (account creation, deposits, withdrawals, trading, portfolio analytics, snapshots, and transaction history). Launch it after installing the project dependencies:

```bash
pip install -e .
python src/scrum_team/engineering/app.py
```

Once running, open the provided local URL to create an account, manage funds, place trades, and inspect historical activity from the dedicated tabs.

## Understanding Your Crew

The scrum_team Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the 😈 THE DEMON TEAM Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
