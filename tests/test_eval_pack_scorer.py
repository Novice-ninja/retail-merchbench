from __future__ import annotations

import unittest
from pathlib import Path

from merchbench.eval_packs import (
    always_buy_chase_response,
    baseline_response,
    keyword_guardrail_response,
    load_packs,
    score_item,
    source_echo_response,
)


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "eval_packs"


def pack_by_segment(segment: str) -> dict:
    for pack in load_packs(PACK_ROOT):
        if pack["task_segment"] == segment:
            return pack
    raise AssertionError(f"missing pack for segment {segment}")


class EvalPackScorerHardeningTests(unittest.TestCase):
    def test_source_echo_is_capped_below_competent_reasoning(self) -> None:
        pack = pack_by_segment("ambiguous_planning_judgment")
        item = pack["items"][0]
        source_score = score_item(pack, item, source_echo_response(pack, item))
        reasoned_response = dict(item["expected_output"])
        reasoned_response["rationale"] = (
            "Reject full 20,000 unit chase because the 18 percent return rate versus 9 percent, "
            "pink 82 percent and navy 39 percent split, and social-view contamination make the full buy unsafe. "
            "Condition only a smaller fit-corrected test before committing OTB."
        )
        reasoned_score = score_item(pack, item, reasoned_response)

        self.assertLessEqual(source_score["total"], 4.5)
        self.assertGreater(reasoned_score["total"], source_score["total"])
        self.assertTrue(source_score["signals"]["anti_echo"]["penalties"])

    def test_keyword_guardrail_is_capped_when_it_lacks_causal_reasoning(self) -> None:
        pack = pack_by_segment("pricing_promotion")
        item = pack["items"][0]
        score = score_item(pack, item, keyword_guardrail_response(pack, item))

        self.assertLessEqual(score["total"], 5.5)
        self.assertEqual(score["signals"]["anti_echo"]["baseline_id"], "baseline/keyword_guardrail")
        self.assertTrue(score["signals"]["anti_echo"]["penalties"])

    def test_missing_escalation_caps_aggressive_answer(self) -> None:
        pack = pack_by_segment("portfolio_tradeoff")
        item = pack["items"][0]
        response = always_buy_chase_response(pack, item)
        score = score_item(pack, item, response)

        self.assertLessEqual(score["total"], 4.5)
        reasons = [penalty["reason"] for penalty in score["signals"]["anti_echo"]["penalties"]]
        self.assertIn("always-buy/chase policy ignores downside and constraints", reasons)
        self.assertIn("missing required escalation on high-downside item", reasons)

    def test_all_adversarial_baselines_are_scoreable(self) -> None:
        pack = pack_by_segment("constraint_checking")
        item = pack["items"][0]
        baseline_ids = (
            "baseline/source_echo",
            "baseline/keyword_guardrail",
            "baseline/generic_consultant",
            "baseline/always_escalate",
            "baseline/always_buy_chase",
            "baseline/always_conservative",
            "baseline/arithmetic_only",
        )
        for baseline_id in baseline_ids:
            with self.subTest(baseline_id=baseline_id):
                response = baseline_response(pack, item, baseline_id)
                score = score_item(pack, item, response)
                self.assertGreaterEqual(score["total"], 0)
                self.assertLessEqual(score["total"], 10)


if __name__ == "__main__":
    unittest.main()
