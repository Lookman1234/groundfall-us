#!/usr/bin/env python3
"""Step 4: apply the failure-mode and trigger rules to surface M/NM narratives.

Plain-language note: this script reads config/coding_rules.yaml (your rules) and
labels every surface metal/nonmetal ground-failure accident with one failure mode
and any triggers. It also records which phrase fired each label, so every label can
be traced back to a rule. You do not need to open this file; edit the rules file.

Output: data/processed/groundfall_failure_modes.csv
"""

import re

import pandas as pd
import yaml

from common import CONFIG, PROC, load_config, write_stats


def compile_rules(spec):
    return {
        "patterns": [re.compile(p, re.I) for p in spec.get("patterns", [])],
        "exclude": [re.compile(p, re.I) for p in spec.get("exclude", [])],
        "use_activity_field": spec.get("use_activity_field", False),
    }


def first_hit(text, rule):
    for x in rule["exclude"]:
        text = x.sub(" ", text)
    for p in rule["patterns"]:
        mt = p.search(text)
        if mt:
            return mt.group(0)
    return None


def code_row(narr, activity, modes, order, triggers):
    narr = narr if isinstance(narr, str) else ""
    mode, mode_hit = "unspecified", ""
    for mode_name in order:
        h = first_hit(narr, modes[mode_name])
        if h:
            mode, mode_hit = mode_name, h
            break
    out = {"failure_mode": mode, "failure_mode_evidence": mode_hit}
    for name, rule in triggers.items():
        h = first_hit(narr, rule)
        if not h and rule["use_activity_field"] and isinstance(activity, str) \
                and re.search(r"scal", activity, re.I):
            h = f"ACTIVITY: {activity}"
        out[f"trigger_{name}"] = bool(h)
        out[f"trigger_{name}_evidence"] = h or ""
    return out


def main():
    cfg = load_config()
    rules = yaml.safe_load((CONFIG / "coding_rules.yaml").read_text())
    modes = {k: compile_rules(v) for k, v in rules["modes"].items()}
    triggers = {k: compile_rules(v) for k, v in rules["triggers"].items()}
    order = rules["mode_precedence"]
    assert set(order) == set(modes), "mode_precedence must list every mode exactly once"

    inc = pd.read_csv(PROC / "groundfall_incidents.csv",
                      dtype={"mine_id": str, "subunit_cd": str, "degree_injury_cd": str})
    sc = cfg["coding_scope"]
    scope = inc[(inc["sector"] == "metal_nonmetal") &
                (inc["subunit_cd"].isin(sc["subunit_codes"]))].copy()

    coded = pd.DataFrame([code_row(n, a, modes, order, triggers)
                          for n, a in zip(scope["narrative"], scope["activity"])], index=scope.index)
    keep = ["document_no", "mine_id", "state", "year", "commodity", "subunit", "degree_injury",
            "is_fatal", "msha_classification", "activity", "narrative"]
    out = pd.concat([scope[keep], coded], axis=1)
    out["any_trigger"] = out[[f"trigger_{t}" for t in triggers]].any(axis=1)
    out["rules_version"] = rules["version"]
    out.to_csv(PROC / "groundfall_failure_modes.csv", index=False)

    dist = out["failure_mode"].value_counts().to_dict()
    tr = {t: int(out[f"trigger_{t}"].sum()) for t in triggers}
    write_stats({"coding_n": len(out), "coding_mode_counts": dist, "coding_trigger_counts": tr,
                 "coding_rules_version": rules["version"],
                 "coding_unspecified_pct": round(100 * dist.get("unspecified", 0) / max(len(out), 1), 1)})
    print(f"Coded {len(out):,} surface M/NM narratives (rules {rules['version']})")
    print("Failure modes:", dist)
    print("Triggers:", tr)


if __name__ == "__main__":
    main()
