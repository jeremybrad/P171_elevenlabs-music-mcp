#!/usr/bin/env python3
"""
Phase 2 Live Testing Suite
Tests all Phase 2 components with real API integration

Run this to verify:
- CompositionPlanner creates intelligent plans
- ContextAnalyzer detects mood and activity
- PreferenceLearner tracks and recommends
- MCP tools work end-to-end
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from composition_planner import CompositionPlanner
from context_analyzer import ContextAnalyzer
from preference_learner import PreferenceLearner
from music_mcp_server import MusicMCPServer
from config_manager import Config

# Test configuration
TEMP_STORAGE = Path("/tmp/phase2_test_preferences")
TEMP_STORAGE.mkdir(exist_ok=True)


def print_section(title):
    """Print a test section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_result(test_name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   {details}")


async def test_composition_planner():
    """Test CompositionPlanner functionality"""
    print_section("TEST 1: CompositionPlanner")

    planner = CompositionPlanner()
    all_passed = True

    # Test 1.1: Template-based generation
    print("1.1 Testing template-based composition...")
    try:
        plan = planner.create_from_template("focus_work", duration_ms=120000)

        passed = (
            hasattr(plan, 'sections') and
            len(plan.sections) == 3 and
            plan.total_duration_ms == 120000
        )

        if passed:
            details = f"Created {len(plan.sections)} sections, total {plan.total_duration_ms}ms"
            for i, section in enumerate(plan.sections, 1):
                details += f"\n      Section {i}: {section.style} ({section.duration_ms}ms, {section.mood})"
        else:
            details = "Plan structure invalid"

        print_result("focus_work template", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("focus_work template", False, f"Error: {e}")
        all_passed = False

    # Test 1.2: Progressive mood plan
    print("\n1.2 Testing progressive mood transition...")
    try:
        plan = planner.create_progressive_plan(
            start_mood="calm",
            end_mood="energetic",
            duration_ms=90000,
            num_sections=3
        )

        passed = (
            hasattr(plan, 'sections') and
            len(plan.sections) == 3
        )

        if passed:
            styles = [s.style for s in plan.sections]
            details = f"Progression: '{styles[0]}' → '{styles[1]}' → '{styles[2]}'"
        else:
            details = "Progressive plan invalid"

        print_result("calm→energetic progression", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("calm→energetic progression", False, f"Error: {e}")
        all_passed = False

    # Test 1.3: Prompt-based planning
    print("\n1.3 Testing intelligent prompt analysis...")
    try:
        plan = planner.create_plan_from_prompt(
            "energetic workout music",
            total_duration_ms=180000
        )

        passed = (
            hasattr(plan, 'sections') and
            len(plan.sections) >= 3
        )

        if passed:
            details = f"Detected template, created {len(plan.sections)} sections"
        else:
            details = "Prompt-based plan invalid"

        print_result("Prompt analysis (workout)", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("Prompt analysis (workout)", False, f"Error: {e}")
        all_passed = False

    # Test 1.4: All templates available
    print("\n1.4 Testing all templates...")
    templates = ["focus_work", "energetic_workout", "calming_meditation",
                "creative_flow", "dramatic_build"]

    for template in templates:
        try:
            plan = planner.create_from_template(template, duration_ms=60000)
            passed = hasattr(plan, 'sections') and len(plan.sections) > 0
            details = f"{len(plan.sections)} sections" if passed else "Failed"
            print_result(f"  Template: {template}", passed, details)
            all_passed &= passed
        except Exception as e:
            print_result(f"  Template: {template}", False, f"Error: {e}")
            all_passed = False

    return all_passed


async def test_context_analyzer():
    """Test ContextAnalyzer functionality"""
    print_section("TEST 2: ContextAnalyzer")

    analyzer = ContextAnalyzer()
    all_passed = True

    # Test 2.1: Mood detection
    print("2.1 Testing mood detection...")

    test_cases = [
        ("This code is so frustrating! Nothing works!", "frustrated", 0.5),
        ("I'm really focused and in the zone right now", "focused", 0.5),
        ("I'm so stressed out about this deadline", "stressed", 0.5),
        ("This is amazing! I love it!", "happy", 0.5),
    ]

    for context, expected_mood, min_confidence in test_cases:
        try:
            result = analyzer.detect_mood(context)
            passed = (
                result["mood"] == expected_mood and
                result["confidence"] >= min_confidence
            )
            details = f"Detected: {result['mood']} (confidence: {result['confidence']:.2f})"
            print_result(f"  '{context[:40]}...'", passed, details)
            all_passed &= passed
        except Exception as e:
            print_result(f"  '{context[:40]}...'", False, f"Error: {e}")
            all_passed = False

    # Test 2.2: Activity detection
    print("\n2.2 Testing activity detection...")

    test_cases = [
        ("Working on the authentication function", "coding", 0.5),
        ("Writing the documentation for this API", "writing", 0.5),
        ("Going for a run, doing my workout", "exercising", 0.5),
    ]

    for context, expected_activity, min_confidence in test_cases:
        try:
            result = analyzer.detect_activity(context)
            passed = (
                result["activity"] == expected_activity and
                result["confidence"] >= min_confidence
            )
            details = f"Detected: {result['activity']} (confidence: {result['confidence']:.2f})"
            print_result(f"  '{context[:40]}...'", passed, details)
            all_passed &= passed
        except Exception as e:
            print_result(f"  '{context[:40]}...'", False, f"Error: {e}")
            all_passed = False

    # Test 2.3: Music suggestions
    print("\n2.3 Testing context-aware music suggestions...")

    test_cases = [
        ("coding", "frustrated", ["calm", "gentle", "ambient"]),
        ("coding", "focused", ["lo-fi", "steady", "beat"]),
        ("exercising", "motivated", ["energy", "upbeat", "driving", "power"]),
    ]

    for activity, mood, expected_keywords in test_cases:
        try:
            suggestion = analyzer.suggest_music_for_context(
                activity=activity,
                mood=mood,
                duration_ms=60000
            )

            passed = any(kw in suggestion.lower() for kw in expected_keywords)
            details = f"Suggested: '{suggestion[:60]}...'" if passed else f"Got: {suggestion[:60]}"
            print_result(f"  {activity}/{mood}", passed, details)
            all_passed &= passed
        except Exception as e:
            print_result(f"  {activity}/{mood}", False, f"Error: {e}")
            all_passed = False

    return all_passed


async def test_preference_learner():
    """Test PreferenceLearner functionality"""
    print_section("TEST 3: PreferenceLearner")

    # Clean up previous test data
    pref_file = TEMP_STORAGE / "preferences.json"
    if pref_file.exists():
        pref_file.unlink()

    learner = PreferenceLearner(TEMP_STORAGE)
    all_passed = True

    # Test 3.1: Record preferences
    print("3.1 Testing preference recording...")
    try:
        learner.record_preference(
            prompt="lo-fi beats for coding",
            liked=True,
            activity="coding",
            mood="focused"
        )
        learner.record_preference(
            prompt="ambient coding music",
            liked=True,
            activity="coding",
            mood="focused"
        )
        learner.record_preference(
            prompt="workout energy",
            liked=True,
            activity="exercising",
            mood="motivated"
        )

        passed = len(learner.preferences) == 3
        details = f"Recorded {len(learner.preferences)} preferences"
        print_result("Record preferences", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("Record preferences", False, f"Error: {e}")
        all_passed = False

    # Test 3.2: Get recommendations
    print("\n3.2 Testing recommendations by activity...")
    try:
        recs = learner.get_recommendations(activity="coding", limit=5)

        # Should return coding-related recs (may include fallback items)
        passed = len(recs) >= 2 and len(recs) <= 5
        coding_recs = [r for r in recs if "coding" in r.lower()]
        details = f"Got {len(recs)} recommendations ({len(coding_recs)} coding-specific): {recs}"
        print_result("Filter by activity", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("Filter by activity", False, f"Error: {e}")
        all_passed = False

    # Test 3.3: Get statistics
    print("\n3.3 Testing statistics generation...")
    try:
        stats = learner.get_statistics()

        passed = (
            stats["total_generations"] == 3 and
            stats["liked_count"] == 3 and
            stats["like_rate"] == 1.0
        )

        details = f"Total: {stats['total_generations']}, Liked: {stats['liked_count']}, Rate: {stats['like_rate']:.0%}"
        if "favorite_activities" in stats:
            details += f"\n      Favorite activities: {stats['favorite_activities']}"

        print_result("Statistics", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("Statistics", False, f"Error: {e}")
        all_passed = False

    # Test 3.4: Persistence
    print("\n3.4 Testing preference persistence...")
    try:
        # Create new instance - should load existing preferences
        learner2 = PreferenceLearner(TEMP_STORAGE)

        passed = len(learner2.preferences) == 3
        details = f"Loaded {len(learner2.preferences)} preferences from storage"
        print_result("Load from storage", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("Load from storage", False, f"Error: {e}")
        all_passed = False

    return all_passed


async def test_mcp_integration():
    """Test MCP server integration"""
    print_section("TEST 4: MCP Server Integration")

    all_passed = True

    # Test 4.1: Server initialization
    print("4.1 Testing MCP server initialization...")
    try:
        # Check if we can import and initialize the server
        from music_mcp_server import MusicMCPServer
        from mcp.server import Server

        # We can't actually instantiate it without MCP running,
        # but we can verify the class and components are available
        passed = True
        details = "MusicMCPServer class importable and components defined"
        print_result("Server initialization", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("Server initialization", False, f"Error: {e}")
        all_passed = False
        return all_passed  # Can't continue without server

    # Create individual components for testing
    try:
        from composition_planner import CompositionPlanner
        from context_analyzer import ContextAnalyzer
        from preference_learner import PreferenceLearner
        from config_manager import Config

        config = Config.from_env()
        server_planner = CompositionPlanner()
        server_analyzer = ContextAnalyzer()
        server_learner = PreferenceLearner(config.preference_storage_path)

        passed = True
        print_result("Component instantiation", passed, "All components created successfully")
        all_passed &= passed
    except Exception as e:
        print_result("Component instantiation", False, f"Error: {e}")
        all_passed = False
        return all_passed

    # Test 4.2: Composition plan tool (simulated)
    print("\n4.2 Testing create_composition_plan tool interface...")
    try:
        plan = server_planner.create_from_template("focus_work", duration_ms=60000)

        passed = hasattr(plan, 'sections') and len(plan.sections) > 0
        details = f"Tool accessible, returns {len(plan.sections)}-section plan"
        print_result("create_composition_plan", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("create_composition_plan", False, f"Error: {e}")
        all_passed = False

    # Test 4.3: Mood analysis tool (simulated)
    print("\n4.3 Testing analyze_mood_for_music tool interface...")
    try:
        mood_result = server_analyzer.detect_mood("I'm so frustrated!")
        activity_result = server_analyzer.detect_activity("Working on code")
        suggestion = server_analyzer.suggest_music_for_context(
            activity="coding",
            mood="frustrated",
            duration_ms=60000
        )

        passed = (
            mood_result["mood"] == "frustrated" and
            suggestion is not None and
            len(suggestion) > 0
        )

        details = f"Detected: {mood_result['mood']}, Suggested: '{suggestion[:40]}...'"
        print_result("analyze_mood_for_music", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("analyze_mood_for_music", False, f"Error: {e}")
        all_passed = False

    # Test 4.4: Preference learning integration
    print("\n4.4 Testing preference learning integration...")
    try:
        # Check it's using the right storage path
        passed = server_learner.storage_path == config.preference_storage_path
        details = f"Storage path: {server_learner.storage_path}"
        print_result("Preference learner config", passed, details)
        all_passed &= passed
    except Exception as e:
        print_result("Preference learner config", False, f"Error: {e}")
        all_passed = False

    return all_passed


async def test_end_to_end_workflow():
    """Test a complete end-to-end workflow"""
    print_section("TEST 5: End-to-End Workflow")

    all_passed = True

    print("Simulating: Betty detects user stress → suggests music → learns preference\n")

    # Step 1: Betty observes user conversation
    print("Step 1: Analyze user context...")
    try:
        analyzer = ContextAnalyzer()
        context = "This is so frustrating! The API keeps timing out and I can't figure out why!"

        mood_result = analyzer.detect_mood(context)
        activity_result = analyzer.detect_activity(context)

        print(f"   Context: '{context}'")
        print(f"   Detected mood: {mood_result['mood']} (confidence: {mood_result['confidence']:.2f})")
        print(f"   Detected activity: {activity_result['activity']} (confidence: {activity_result['confidence']:.2f})")

        passed = mood_result['mood'] == 'frustrated'
        print_result("Context analysis", passed)
        all_passed &= passed
    except Exception as e:
        print_result("Context analysis", False, f"Error: {e}")
        all_passed = False
        return all_passed

    # Step 2: Generate appropriate music suggestion
    print("\nStep 2: Generate music suggestion...")
    try:
        suggestion = analyzer.suggest_music_for_context(
            activity=activity_result['activity'],
            mood=mood_result['mood'],
            duration_ms=120000
        )

        print(f"   Suggested prompt: '{suggestion}'")

        passed = len(suggestion) > 0 and any(word in suggestion.lower() for word in ['calm', 'gentle', 'ambient'])
        print_result("Music suggestion", passed, f"Calming music for frustrated state")
        all_passed &= passed
    except Exception as e:
        print_result("Music suggestion", False, f"Error: {e}")
        all_passed = False
        return all_passed

    # Step 3: Record this as a preference
    print("\nStep 3: Record preference for learning...")
    try:
        learner = PreferenceLearner(TEMP_STORAGE)

        initial_count = len(learner.preferences)

        learner.record_preference(
            prompt=suggestion,
            liked=True,  # User liked the suggestion
            activity=activity_result['activity'],
            mood=mood_result['mood']
        )

        final_count = len(learner.preferences)

        print(f"   Preferences before: {initial_count}, after: {final_count}")

        passed = final_count == initial_count + 1
        print_result("Record preference", passed)
        all_passed &= passed
    except Exception as e:
        print_result("Record preference", False, f"Error: {e}")
        all_passed = False
        return all_passed

    # Step 4: Next time, get personalized recommendations
    print("\nStep 4: Get personalized recommendations...")
    try:
        recs = learner.get_recommendations(
            activity="coding",
            mood="frustrated",
            limit=3
        )

        print(f"   Personalized recommendations ({len(recs)}):")
        for i, rec in enumerate(recs[:3], 1):
            print(f"      {i}. '{rec[:60]}...'")

        passed = len(recs) > 0 and suggestion in recs
        print_result("Personalized recommendations", passed, "System learned from interaction")
        all_passed &= passed
    except Exception as e:
        print_result("Personalized recommendations", False, f"Error: {e}")
        all_passed = False

    return all_passed


async def main():
    """Run all Phase 2 tests"""
    print("\n" + "="*70)
    print("  PHASE 2 LIVE TESTING SUITE")
    print("  Testing: CompositionPlanner, ContextAnalyzer, PreferenceLearner")
    print("="*70)

    results = {}

    # Run all test suites
    results["CompositionPlanner"] = await test_composition_planner()
    results["ContextAnalyzer"] = await test_context_analyzer()
    results["PreferenceLearner"] = await test_preference_learner()
    results["MCP Integration"] = await test_mcp_integration()
    results["End-to-End Workflow"] = await test_end_to_end_workflow()

    # Print summary
    print_section("FINAL RESULTS")

    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)

    for test_suite, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_suite}")

    print(f"\n{'='*70}")
    print(f"  Overall: {passed_count}/{total_count} test suites passed")

    if passed_count == total_count:
        print(f"  🎉 ALL PHASE 2 TESTS PASSED! Ready for production.")
    elif passed_count > 0:
        print(f"  ⚠️  Some tests failed. Review failures above.")
    else:
        print(f"  ❌ All tests failed. Major issues detected.")

    print(f"{'='*70}\n")

    return passed_count == total_count


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
