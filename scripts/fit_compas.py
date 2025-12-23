import numpy as np
from scipy import stats
from scipy.optimize import minimize


def get_rates(mu_pos, sigma_pos, mu_neg, sigma_neg, threshold):
    tpr = 1 - stats.norm.cdf(threshold, loc=mu_pos, scale=sigma_pos)
    fpr = 1 - stats.norm.cdf(threshold, loc=mu_neg, scale=sigma_neg)
    return tpr, fpr


def objective(params, target_fpr, target_fnr):
    # params: [mu_pos, sigma_pos, mu_neg, sigma_neg, threshold]
    # Fixed constraints: sigma > 0
    # To simplify, we can fix sigma=15 for one and vary others, or vary all.
    # Let's fix sigmas to 15 to make it look nice (bell curves) and just vary mu and threshold?
    # No, to get specific FPR/FNR combinations, we might need to vary overlap (mu distance) and threshold.
    # Let's fix sigma=15 for all to keep visuals consistent/pretty, and only Find mu_pos, mu_neg, and threshold.
    # Actually, we need to shift them.

    mu_pos, mu_neg, threshold = params
    sigma = 15

    tpr, fpr = get_rates(mu_pos, sigma, mu_neg, sigma, threshold)
    fnr = 1 - tpr

    loss = (fpr - target_fpr) ** 2 + (fnr - target_fnr) ** 2
    return loss


def fit_population(target_fpr, target_fnr):
    # Initial guess
    # mu_pos > mu_neg usually
    x0 = [60, 40, 50]

    res = minimize(
        objective,
        x0,
        args=(target_fpr, target_fnr),
        bounds=[(0, 100), (0, 100), (0, 100)],
        method="L-BFGS-B",
    )

    return res.x


print("fitting General Recidivism...")
# General - Black: FPR 0.45, FNR 0.28
params_black = fit_population(0.45, 0.28)
print(
    f"Black: mu_pos={params_black[0]:.1f}, mu_neg={params_black[1]:.1f}, thresh={params_black[2]:.1f}"
)

# General - White: FPR 0.23, FNR 0.48
params_white = fit_population(0.23, 0.48)
print(
    f"White: mu_pos={params_white[0]:.1f}, mu_neg={params_white[1]:.1f}, thresh={params_white[2]:.1f}"
)


# For Violent, we need to satisfy the ratios and Probabilities.
# This implies we need prevalence too.
# Let's assume prevalence is accurate in the article.
# "Overall recidivism rate... 60%?" No.
# General Recidivism Prevalence is roughly 50% usually. I'll calculate it using PPV.
# PPV = TPR*Prev / (TPR*Prev + FPR*(1-Prev))
# 0.63 = (1-0.28)*P / ((1-0.28)*P + 0.45*(1-P)) -> Solve for P.
# 0.63 * (0.72P + 0.45 - 0.45P) = 0.72P
# 0.63 * (0.27P + 0.45) = 0.72P
# 0.1701P + 0.2835 = 0.72P
# 0.2835 = 0.5499P => P ~= 0.515. So Prevalence ~52% for Black.

# White: PPV 0.59
# 0.59 = (1-0.48)*P / ((1-0.48)*P + 0.23*(1-P))
# 0.59 * (0.52P + 0.23 - 0.23P) = 0.52P
# 0.59 * (0.29P + 0.23) = 0.52P
# 0.1711P + 0.1357 = 0.52P
# 0.1357 = 0.3489P => P ~= 0.39. So Prevalence ~39% for White.

print(f"Calculated Prevalences (General): Black={0.52}, White={0.39}")


def fit_violent(prev_black, prev_white):
    # We need to find Params A (Black) and Params B (White)
    # x = [mu_pos_a, mu_neg_a, t_a, mu_pos_b, mu_neg_b, t_b]
    sigma = 15

    def obj_violent(x):
        mu_pos_a, mu_neg_a, t_a, mu_pos_b, mu_neg_b, t_b = x

        tpr_a, fpr_a = get_rates(mu_pos_a, sigma, mu_neg_a, sigma, t_a)
        tpr_b, fpr_b = get_rates(mu_pos_b, sigma, mu_neg_b, sigma, t_b)

        fnr_a = 1 - tpr_a
        fnr_b = 1 - tpr_b

        # Calculate PPVs
        # PPV = TPR*P / (TPR*P + FPR*(1-P))
        def get_ppv(tpr, fpr, p):
            denom = tpr * p + fpr * (1 - p)
            return (tpr * p) / denom if denom > 0 else 0

        ppv_a = get_ppv(tpr_a, fpr_a, prev_black)
        ppv_b = get_ppv(tpr_b, fpr_b, prev_white)

        # Constraints errors
        # 1. FPR_Black ~= 2 * FPR_White
        err1 = (fpr_a - 2 * fpr_b) ** 2

        # 2. FNR_White ~= 1.632 * FNR_Black
        err2 = (fnr_b - 1.632 * fnr_a) ** 2

        # 3. PPVs
        err3 = (ppv_a - 0.21) ** 2
        err4 = (ppv_b - 0.17) ** 2

        # Regularization to keep params reasonable
        # err_reg = ((t_a - 50)/100)**2 + ((t_b-50)/100)**2

        return err1 + err2 + err3 + err4

    x0 = [60, 40, 50, 60, 40, 50]
    res = minimize(obj_violent, x0, bounds=[(0, 100)] * 6, method="L-BFGS-B")
    return res.x, res.fun


# Violent Prevalence Assumption
# General prev was ~50% / 39%. Violent is much lower.
# Let's assume ~15% for black and ~10% for white?
# Or just try to fit with these fixed prevalences.
prev_v_black = 0.20
prev_v_white = 0.10
v_params, v_err = fit_violent(prev_v_black, prev_v_white)

print(f"\nFitting Violent (P_black={prev_v_black}, P_white={prev_v_white})... Error: {v_err:.5f}")
print(f"Black: mu_pos={v_params[0]:.1f}, mu_neg={v_params[1]:.1f}, thresh={v_params[2]:.1f}")
print(f"White: mu_pos={v_params[3]:.1f}, mu_neg={v_params[4]:.1f}, thresh={v_params[5]:.1f}")
