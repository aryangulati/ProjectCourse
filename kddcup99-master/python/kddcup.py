# (c) Michael Alderson-Bythell
# KDD cup 1999 dataset helper for scikit-learn

import pandas as pd
import numpy as np
import sklearn.datasets
import json
from sklearn.datasets.base import Bunch
from sklearn.preprocessing import LabelEncoder

# see here for tips on preparing data
# https://districtdatalabs.silvrback.com/building-a-classifier-from-census-data

# see here for data wrangling
# http://fastml.com/converting-categorical-data-into-numbers-with-pandas-and-scikit-learn/

meta_file = "../data/meta.json"
readme_file = "../data/KDD-CUP-99 Task Description.htm"

# TODO read in the names data from disk and parse/convert to a clean list
csv_column_names = [
    "duration",
    "protocol_type",
    "service",
    "flag",
    "src_bytes",
    "dst_bytes",
    "land",
    "wrong_fragment",
    "urgent",
    "hot",
    "num_failed_logins",
    "logged_in",
    "num_compromised",
    "root_shell",
    "su_attempted",
    "num_root",
    "num_file_creations",
    "num_shells",
    "num_access_files",
    "num_outbound_cmds",
    "is_host_login",
    "is_guest_login",
    "count",
    "srv_count",
    "serror_rate",
    "srv_serror_rate",
    "rerror_rate",
    "srv_rerror_rate",
    "same_srv_rate",
    "diff_srv_rate",
    "srv_diff_host_rate",
    "dst_host_count",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate",
    "dst_host_srv_serror_rate",
    "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate",
    "category"
]

target_name = "category"

# analyse csv & create json metadata file
def analyse(data_file):
    csv = pd.read_csv(data_file, names=csv_column_names)

    xnames = list(csv.columns)
    feature_names = list(csv.columns)
    feature_names.remove(target_name)

    meta = {
        'target_names': list(csv.category.unique()),
        'names': xnames,
        'feature_names': feature_names,
        'categorical_data': {
            column: list(csv[column].unique())
            for column in csv.columns
            if csv[column].dtype == 'object'
        },
    }

    with open(meta_file, 'w') as f:
        json.dump(meta, f, indent=2)

def encode_dataset(dataset):

    encoders = dict()
    raw_data = dict()

    for x in dataset.categorical_data:
        #print "encoding column: %s" % x
        if x == target_name:
            encoder = LabelEncoder()
            encoder.fit(dataset.target)
            encoders[x] = encoder
            transformed_data = encoder.transform(dataset.target)
            raw_data[x] = dataset.target
            dataset.target = transformed_data
        else:
            encoder = LabelEncoder()
            encoder.fit(dataset.data[x])
            encoders[x] = encoder
            transformed_data = encoder.transform(dataset.data[x])
            raw_data[x] = dataset.data[x]
            dataset.data = dataset.data.drop(x, 1)
            dataset.data[x] = transformed_data

    dataset['encoders'] = encoders
    dataset['raw_data'] = raw_data

def load_data_10_percent():
    return load_data("../data/kddcup.data_10_percent_corrected")

def load_data_100_percent():
    return load_data("../data/kddcup.data.corrected")

def load_data(data_file):

    analyse(data_file)

    # Load the meta data from the file
    with open(meta_file, 'r') as f:
        meta = json.load(f)

    # Load the readme information
    with open(readme_file, 'r') as f:
        readme = f.read()

    # Load the data
    csv = pd.read_csv(data_file, names=csv_column_names)

    # Return the bunch with the appropriate data chunked apart
    dataset = Bunch(
        data = csv[csv_column_names[:-1]],
        target = csv[csv_column_names[-1]],
        target_names = meta['target_names'],
        feature_names = meta['feature_names'],
        categorical_data = meta['categorical_data'],
        target_name = target_name,
        DESCR = readme)

    encode_dataset(dataset)

    return dataset

if __name__ == "__main__":
    dataset = load_data_10_percent()
