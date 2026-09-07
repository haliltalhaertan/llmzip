"""Read persisted scale-result aggregates only; never import experiment runners."""
import collections
import csv
import gzip
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[4]


def ratio(native, raw, scaled):
    return (scaled - raw) / (native - raw)


def main():
    result = {"scope": "persisted metric records only; no raw corpus or retrieval rerun", "datasets": {}}
    # Negative control: averaging and division provably do not commute.
    assert statistics.fmean([ratio(1, 0, .5), ratio(1, .9, 1)]) != ratio(1, .45, .75)
    for ds in ["locomo", "longmemeval"]:
        path = ROOT / "research/v52" / (ds + "_scale_outputs")
        summary = json.loads((path / (ds + "_scale_summary.json")).read_text())
        with gzip.open(path / (ds + "_scale_per_question.csv.gz"), "rt") as stream:
            rows = list(csv.DictReader(stream))
        groups = collections.defaultdict(list)
        keys = set()
        for row in rows:
            key = (row["question_id"], row["rotation_seed"], row["arm"])
            assert key not in keys
            keys.add(key)
            score = float(row["fractional_R3"])
            assert 0 <= score <= 1
            groups[(row["rotation_seed"], row["arm"])].append(score)
        means = {key: statistics.fmean(values) for key, values in groups.items()}
        seeds = sorted({key[0] for key in means})
        assert seeds == list(map(str, range(59001, 59011)))
        dataset = {"rows": len(rows), "unique_keys": len(keys), "groups": len(groups), "arms": {}}
        for label, raw, scaled in [("full", "FULLHAAR_FRESH", "SCALED_FULLHAAR"), ("block", "BLOCK32_FRESH", "SCALED_BLOCK32")]:
            values = [ratio(means[t, "NATIVE"], means[t, raw], means[t, scaled]) for t in seeds]
            denoms = [means[t, "NATIVE"] - means[t, raw] for t in seeds]
            aggregate = ratio(*(statistics.fmean(means[t, arm] for t in seeds) for arm in ["NATIVE", raw, scaled]))
            delta = max(abs(a - b) for a, b in zip(values, summary["primary"]["frac_" + label + "_per_seed"]))
            assert delta < 1e-10
            assert abs(aggregate - summary["primary"]["frac_" + label]) < 1e-10
            dataset["arms"][label] = {"mean_seed_ratios": statistics.fmean(values), "ratio_of_seed_means": aggregate, "per_seed": values, "denominators": denoms, "nonpositive_denominators": sum(d <= 0 for d in denoms), "persisted_seed_ratio_max_abs_error": delta}
        dataset["mean_seed_I"] = dataset["arms"]["full"]["mean_seed_ratios"] - dataset["arms"]["block"]["mean_seed_ratios"]
        dataset["reported_I"] = summary["primary"]["I_frac_secondary"]
        dataset["summary_top_level_keys"] = list(summary)
        result["datasets"][ds] = dataset
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
