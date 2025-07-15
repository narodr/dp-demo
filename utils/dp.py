import pandas as pd
import snsql
from snsql import Privacy, Stat, Mechanism


def get_unnoised_result(data):
    return data["binned_age"].value_counts().to_dict()

def get_noised_result(epsilon, data, query, meta_path):
    privacy = Privacy(epsilon=epsilon)
    privacy.mechanisms.map[Stat.count] = Mechanism.laplace
    reader = snsql.from_connection(data, privacy=privacy, metadata=meta_path)
    result = reader.execute(query)

    group_to_result = {}
    for (k, v) in result:
        group_to_result[k] = v
    group_to_result.pop('binned_age')
    return group_to_result

def get_relative_error_per_group(unnoised_result, noised_result):
  unscaled_error = {}
  scaled_error = {}
  for (k, v) in unnoised_result:
    unscaled_error[k] = v - noised_result[k]
    scaled_error[k] = unscaled_error[k] / v
  return unscaled_error, scaled_error

def get_scaled_error_per_group(err, result): 
  group_to_scaled_err = {}
  for (k, v) in result.items():
    group_to_scaled_err[k] = err / v
  return group_to_scaled_err

def get_abs_error(data, query, epsilon, alpha, meta_path):
  privacy = Privacy(epsilon=epsilon)
  privacy.mechanisms.map[Stat.count] = Mechanism.laplace
  reader = snsql.from_connection(data, privacy=privacy, metadata=meta_path)
  return reader.get_simple_accuracy(query, alpha=alpha)[1]

def alpha_to_percent_conf(alpha):
  return f"{int((1-alpha) * 100)}%"

def compute_all_stats(epsilon, alpha, groupby_keys, data, query, meta_path):
  percent_conf = alpha_to_percent_conf(alpha)
  unnoised_result = get_unnoised_result(data)
  noised_result = get_noised_result(epsilon, data, query, meta_path)
  df = pd.DataFrame(groupby_keys, columns=["Age bin"])
  df.set_index('Age bin')
  key_col = df["Age bin"]
  df["Exact result"] = key_col.apply(lambda age_bin: unnoised_result.get(age_bin, 0))
  df["Noised result"] = key_col.apply(lambda age_bin: noised_result.get(age_bin, 0))
  df[percent_conf + " error"] = get_abs_error(data, query, epsilon, alpha, meta_path)
  df[percent_conf + " min"] = (df["Noised result"] - df[percent_conf + " error"]).astype('int')
  df[percent_conf + " max"] = (df["Noised result"] + df[percent_conf + " error"]).astype('int')
  df["True error"] = abs(df["Noised result"] - df["Exact result"])
  df["True error %"] = abs(100.0 * (df["Noised result"] - df["Exact result"]) / df["Exact result"])
  df[percent_conf + " error %"] = 100.0 * df[percent_conf + " error"] / df["Noised result"]

  # Do math: expectation of abs(laplace(1/epsi))
  df[f"Expected error"] = 1.0 / epsilon
  df[f"Expected error %"] = 100.0 * df[f"Expected error"] / df["Noised result"]
  return df