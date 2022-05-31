import pandas as pd
from sklearn.model_selection import StratifiedKFold
from pipeline.ngrams_classif import NgramsExtractor
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score
import numpy as np
import warnings

warnings.filterwarnings('ignore')


def average(arr: list):
    return sum(arr) / len(arr)


def classify_ndss(train, test):
    # print(test)
    combinedFeatures = FeatureUnion([
        # ('tsfresh', TSFreshBasicExtractor()),
        ('ngrams', NgramsExtractor(max_ngram_len=1)),
    ])

    pipeline = Pipeline([
        ('features', combinedFeatures),
        ('clf', RandomForestClassifier(n_estimators=100, max_depth=30, min_samples_leaf=5)),
        # ('clf', RandomForestClassifier(n_estimators=100)),
    ])
    pipeline.fit(train, list(train.class_label))
    # Prediction
    pred_ret = pipeline.predict(test)

    return pred_ret


def classify_ndss_key(train, test):
    # print(test)
    combinedFeatures = FeatureUnion([
        # ('tsfresh', TSFreshBasicExtractor()),
        ('ngrams', NgramsExtractor(max_ngram_len=1)),
    ])

    pipeline = Pipeline([
        ('features', combinedFeatures),
        ('clf', RandomForestClassifier(n_estimators=100, max_depth=30, min_samples_leaf=5)),
        # ('clf', RandomForestClassifier(n_estimators=100)),
    ])
    pipeline.fit(train, list(train.class_label))
    # Prediction
    pred_ret = pipeline.predict(test)

    return pred_ret


def classify_rf(train, test):
    rf = RandomForestClassifier()
    X = []
    Y = []
    for index, row in train.iterrows():
        lengths = list(row['lengths'])
        if len(lengths) > 100:
            lengths = lengths[:100]
        elif len(lengths) < 100:
            while len(lengths) < 100:
                lengths.append(0)
        X.append(lengths)
        label = int(row['class_label'])
        Y.append(label)
    rf.fit(X, Y)
    # return
    test_X = []
    for index, row in test.iterrows():
        lengths = list(row['lengths'])
        if len(lengths) > 100:
            lengths = lengths[:100]
        elif len(lengths) < 100:
            while len(lengths) < 100:
                lengths.append(0)
        test_X.append(lengths)
    pred_ret = rf.predict(test_X)
    return pred_ret


def trans_csv_to_df(csv_filename):
    src_df = pd.read_csv(csv_filename)
    dst_df = pd.DataFrame()
    for i in range(len(src_df)):
        features = np.array(eval(src_df.loc[i, 'lengths']))
        label = src_df.loc[i, 'class_label']
        # print(label,type(label))
        if label >= 100:
            continue
        # dst_df.
        dst_df = dst_df.append({
            "lengths": features,
            "class_label": label
        }, ignore_index=True)
    return dst_df


def exp(classifier, feature_model, data_model, ops_mode="win10"):
    if classifier == "rf":
        classify = classify_rf
    elif classifier == "ndss":
        if feature_model == "norm":
            classify = classify_ndss
        elif feature_model == "key":
            classify = classify_ndss_key
        else:
            print("feature_model", feature_model)
            return
    else:
        print("未知classifier", classifier)
        return
    if feature_model in ["key", "norm"]:
        df = trans_csv_to_df(f"./data/{feature_model}_feature_{data_model}_{ops_mode}.csv")
    else:
        print("未知特征类别！")
        return
    kf = StratifiedKFold(n_splits=10, shuffle=True)
    precisions = []
    recalls = []
    f1s = []
    accs = []
    for k, (train, test) in enumerate(kf.split(df, list(df.class_label))):
        if classifier == "ndss":
            predict_results = classify(df.iloc[train], df.iloc[test])
        elif classifier == "rf":
            predict_results = classify(df.iloc[train], df.iloc[test])
        else:
            print("未知分类方法")
            return
        gt_Y = df.iloc[test].class_label
        precision = precision_score(gt_Y, predict_results, average='weighted')
        recall = recall_score(gt_Y, predict_results, average='weighted')
        f1 = f1_score(gt_Y, predict_results, average='weighted')
        acc = accuracy_score(gt_Y, predict_results)
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
        accs.append(acc)
        break
    print("平均准确率: ", average(precisions), end="\t")
    print("平均召回率: ", average(recalls), end="\t")
    print("平均f1值: ", average(f1s), end="\t")
    print("平均acc: ", average(accs))


def cross_validation(classifier, feature_model):
    if classifier == "rf":
        classify = classify_rf
    elif classifier == "ndss":
        if feature_model == "norm":
            classify = classify_ndss
        elif feature_model == "key":
            classify = classify_ndss_key
        else:
            print("feature_model", feature_model)
            return
    else:
        print("未知classifier", classifier)
        return
    # train = "firefox"
    # test = "chrome"
    print("classifier:", classifier)
    print("feature_model", feature_model)
    # for train, test in [("chrome", "edge"), ("chrome", "firefox"), ("firefox", "chrome"), ("firefox", "edge"),
    #                     ("edge", "chrome"), ("edge", "firefox")]:
    #     print("train:", train, "test:", test)
    #     df_train = trans_csv_to_df(f"./data/{feature_model}_feature_{train}_win10.csv")
    #     df_test = trans_csv_to_df(f"./data/{feature_model}_feature_{test}_win10.csv")
    #     predict_results = classify(df_train, df_test)
    #     gt_Y = df_test.class_label
    #     precision = precision_score(gt_Y, predict_results, average='weighted')
    #     recall = recall_score(gt_Y, predict_results, average='weighted')
    #     f1 = f1_score(gt_Y, predict_results, average='weighted')
    #     acc = accuracy_score(gt_Y, predict_results)
    #     print("准确率: ", precision, end="\t")
    #     print("召回率: ", recall, end="\t")
    #     print("f1值: ", f1, end="\t")
    #     print("acc: ", acc)

    for train, test in [("win10", "ubuntu"), ("ubuntu", "win10")]:
        print("train:", train, "test:", test)
        df_train = trans_csv_to_df(f"./data/{feature_model}_feature_chrome_{train}.csv")
        df_test = trans_csv_to_df(f"./data/{feature_model}_feature_chrome_{test}.csv")
        predict_results = classify(df_train, df_test)
        gt_Y = df_test.class_label
        precision = precision_score(gt_Y, predict_results, average='weighted')
        recall = recall_score(gt_Y, predict_results, average='weighted')
        f1 = f1_score(gt_Y, predict_results, average='weighted')
        acc = accuracy_score(gt_Y, predict_results)
        print("准确率: ", precision, end="\t")
        print("召回率: ", recall, end="\t")
        print("f1值: ", f1, end="\t")
        print("acc: ", acc)


if __name__ == '__main__':
    exp("ndss", "norm", "firefox")
    exp("ndss", "key", "firefox")
    #
    exp("ndss", "norm", "chrome")
    exp("ndss", "key", "chrome")

    exp("ndss", "norm", "chrome", "ubuntu")
    exp("ndss", "key", "chrome", "ubuntu")

    cross_validation("ndss", "norm")
    cross_validation("ndss", "key")
