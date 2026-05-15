import csv
import math


def calc_stats(scores):
    if not scores:
        return 0, 0
    mean = sum(scores) / len(scores)
    if len(scores) < 2:
        return mean, 0
    variance = sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)
    return mean, math.sqrt(variance)


rows = []
with open("/home/tottern/Projects/compas-analysis/compas-scores-two-years.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # ProPublica filters
        if row["days_b_screening_arrest"] == "":
            continue
        if abs(int(row["days_b_screening_arrest"])) > 30:
            continue
        if row["is_recid"] == "-1":
            continue
        if row["c_charge_degree"] == "O":
            continue
        if row["score_text"] == "N/A":
            continue

        race = row["race"]
        if race not in ("African-American", "Caucasian"):
            continue

        score = float(row["decile_score"])
        # Scale score to 0-100 to match our UI (decile_score is 1-10)
        score = score * 10

        recid = int(row["two_year_recid"])

        rows.append({"race": race, "score": score, "recid": recid})

stats = {}
for race in ("African-American", "Caucasian"):
    race_rows = [r for r in rows if r["race"] == race]
    pos_rows = [r for r in race_rows if r["recid"] == 1]
    neg_rows = [r for r in race_rows if r["recid"] == 0]

    prevalence = len(pos_rows) / len(race_rows) if len(race_rows) > 0 else 0

    mu_pos, sig_pos = calc_stats([r["score"] for r in pos_rows])
    mu_neg, sig_neg = calc_stats([r["score"] for r in neg_rows])

    stats[race] = {
        "prevalence": prevalence,
        "mu_pos": mu_pos,
        "sigma_pos": sig_pos,
        "mu_neg": mu_neg,
        "sigma_neg": sig_neg,
        "n": len(race_rows),
    }

for k, v in stats.items():
    print(k)
    for p, val in v.items():
        print(f"  {p}: {val:.2f}")
