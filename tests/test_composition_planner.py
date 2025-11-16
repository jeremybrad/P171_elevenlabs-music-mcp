"""
Tests for composition planning functionality
"""

import pytest
from pathlib import Path
from src.composition_planner import CompositionPlanner


def test_create_from_template():
    """Test creating composition from template"""
    planner = CompositionPlanner()

    # Test focus_work template
    plan = planner.create_from_template("focus_work", duration_ms=60000)

    assert hasattr(plan, 'sections')
    assert len(plan.sections) == 3
    assert plan.total_duration_ms == 60000
    assert "focus" in plan.overall_mood.lower() or "concentration" in plan.overall_mood.lower()

    # Verify section structure
    for section in plan.sections:
        assert hasattr(section, 'style')
        assert hasattr(section, 'duration_ms')
        assert isinstance(section.duration_ms, int)


def test_create_progressive_plan():
    """Test creating plan with mood progression"""
    planner = CompositionPlanner()

    plan = planner.create_progressive_plan(
        start_mood="calm",
        end_mood="energetic",
        duration_ms=90000,
        num_sections=3
    )

    assert hasattr(plan, 'sections')
    assert len(plan.sections) == 3
    assert plan.total_duration_ms == 90000

    # Check that styles progress
    sections = plan.sections
    first_style = sections[0].style.lower()
    last_style = sections[-1].style.lower()

    # First should be calmer, last should be more energetic
    assert any(word in first_style for word in ["calm", "gentle", "soft"])
    assert any(word in last_style for word in ["energetic", "upbeat", "driving"])


def test_create_plan_from_prompt_with_template():
    """Test creating plan from prompt that matches template"""
    planner = CompositionPlanner()

    # Prompt that should trigger focus_work template
    plan = planner.create_plan_from_prompt(
        prompt="music for coding and focus work",
        total_duration_ms=60000
    )

    assert hasattr(plan, 'sections')
    assert len(plan.sections) > 0
    assert plan.total_duration_ms == 60000


def test_create_plan_from_prompt_with_mood_progression():
    """Test creating plan from prompt with mood progression keywords"""
    planner = CompositionPlanner()

    plan = planner.create_plan_from_prompt(
        prompt="start calm and build to energetic",
        total_duration_ms=90000
    )

    assert hasattr(plan, 'sections')
    assert len(plan.sections) >= 3  # Progressive plans have at least 3 sections


def test_create_plan_from_generic_prompt():
    """Test creating plan from generic prompt without templates"""
    planner = CompositionPlanner()

    plan = planner.create_plan_from_prompt(
        prompt="ambient electronic soundscape",
        total_duration_ms=60000,
        num_sections=2
    )

    assert hasattr(plan, 'sections')
    assert len(plan.sections) == 2
    assert plan.total_duration_ms == 60000


def test_all_templates_available():
    """Test that all expected templates exist"""
    planner = CompositionPlanner()

    templates = ["focus_work", "energetic_workout", "calming_meditation",
                "creative_flow", "dramatic_build"]

    for template_name in templates:
        plan = planner.create_from_template(template_name, duration_ms=60000)
        assert hasattr(plan, 'sections')
        assert len(plan.sections) > 0


def test_section_durations_sum_correctly():
    """Test that section durations sum to total duration"""
    planner = CompositionPlanner()

    total_duration = 120000
    plan = planner.create_from_template("focus_work", duration_ms=total_duration)

    sections = plan.sections
    actual_total = sum(s.duration_ms for s in sections)

    # Allow small rounding difference
    assert abs(actual_total - total_duration) < 1000


def test_energetic_workout_template():
    """Test energetic workout template specifically"""
    planner = CompositionPlanner()

    plan = planner.create_from_template("energetic_workout", duration_ms=180000)

    assert len(plan.sections) == 4

    # Verify progression: warmup -> main -> peak -> cooldown
    styles = [s.style.lower() for s in plan.sections]
    assert any("warmup" in p or "building" in p for p in styles)
    assert any("peak" in p or "intense" in p for p in styles)


def test_calming_meditation_template():
    """Test calming meditation template specifically"""
    planner = CompositionPlanner()

    plan = planner.create_from_template("calming_meditation", duration_ms=300000)

    assert len(plan.sections) == 3

    # All sections should be calming/gentle
    for section in plan.sections:
        style = section.style.lower()
        assert any(word in style for word in ["calm", "gentle", "soft", "ambient"])
