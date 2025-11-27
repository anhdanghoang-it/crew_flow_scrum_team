from pydantic import BaseModel, Field
from typing import List, Optional


class TestStep(BaseModel):
    """Represents a single test step with action and expected outcome"""
    step_number: int = Field(description="Sequential step number starting from 1")
    action: str = Field(description="The action to perform in this step")
    expected_outcome: str = Field(description="The expected result after performing this action")


class TestScenario(BaseModel):
    """Represents a single test scenario with all necessary details for test generation"""
    test_id: str = Field(
        description="Unique test scenario identifier (e.g., TS-1.1, TS-2.3)"
    )
    title: str = Field(
        description="Clear, descriptive title for the test scenario"
    )
    source_user_story_id: str = Field(
        description="Reference to the source user story ID (e.g., US-001, US-002)"
    )
    detailed_steps: List[TestStep] = Field(
        description="Ordered list of test steps with actions and expected outcomes, including setup steps at the beginning"
    )
    expected_result: str = Field(
        description="Overall expected result or acceptance criteria validation for this scenario"
    )
    user_story_detail: str = Field(
        description="Full text or relevant details from the associated user story for context"
    )


class TestPlanStructured(BaseModel):
    """Complete structured test plan containing all test scenarios"""
    module_name: str = Field(
        description="Name of the module being tested (e.g., trading_simulation, account_management)"
    )
    executive_summary: str = Field(
        description="High-level overview of the test plan scope and objectives"
    )
    scenarios: List[TestScenario] = Field(
        description="Complete list of all test scenarios in this test plan"
    )
