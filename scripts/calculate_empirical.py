import csv
import json


def get_empirical_data(filepath, score_col, recid_col):
    rows = []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["is_recid"] == "-1":
                continue
            if row["c_charge_degree"] == "O":
                continue
            if row.get("score_text", "") == "N/A" or row.get("v_score_text", "") == "N/A":
                continue

            race = row["race"]
            if race not in ("African-American", "Caucasian"):
                continue

            try:
                score = float(row[score_col])
                recid = int(row[recid_col])
                rows.append({"race": race, "score": score, "recid": recid})
            except ValueError:
                pass

    stats = {}
    for race in ("African-American", "Caucasian"):
        race_rows = [r for r in rows if r["race"] == race]
        pos_rows = [r for r in race_rows if r["recid"] == 1]
        neg_rows = [r for r in race_rows if r["recid"] == 0]

        prevalence = len(pos_rows) / len(race_rows) if len(race_rows) > 0 else 0

        def get_histogram(data_rows):
            counts = dict.fromkeys(range(1, 11), 0)
            for r in data_rows:
                decile = int(r["score"])
                if 1 <= decile <= 10:
                    counts[decile] += 1
            total = sum(counts.values())
            # Convert to PDF-like values (area under curve = 1)
            # Each bin has width 10 (when scaled to 0-100)
            pdf = {}
            for k, v in counts.items():
                pdf[k] = (v / total) / 10 if total > 0 else 0
            return pdf

        stats[race] = {
            "prevalence": prevalence,
            "pos_hist": get_histogram(pos_rows),
            "neg_hist": get_histogram(neg_rows),
        }
    return stats


general = get_empirical_data(
    "/home/tottern/Projects/compas-analysis/compas-scores-two-years.csv",
    "decile_score",
    "two_year_recid",
)
violent = get_empirical_data(
    "/home/tottern/Projects/compas-analysis/compas-scores-two-years-violent.csv",
    "v_decile_score",
    "two_year_recid",
)

with open("/home/tottern/Projects/FairnessMetrics/compas_empirical.json", "w") as f:
    json.dump({"general": general, "violent": violent}, f, indent=2)
print("Done")
