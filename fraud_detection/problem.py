import os
import numpy as np
import pandas as pd
import rampwf as rw
from sklearn.model_selection import StratifiedShuffleSplit
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


problem_title = 'Fraud detection'
_target_column_name = 'isFraud'
_prediction_label_names = [0, 1]
# A type (class) which will be used to create wrapper objects for y_pred
Predictions = rw.prediction_types.make_multiclass(
    label_names=_prediction_label_names)
# An object implementing the workflow
workflow = rw.workflows.FeatureExtractorClassifier()


from rampwf.score_types.classifier_base import ClassifierBaseScoreType
from sklearn.metrics import cohen_kappa_score
class Kappa(ClassifierBaseScoreType):
    is_lower_the_better = False
    minimum = -1.0
    maximum = 1.0

    def __init__(self, name='Kappa', precision=2):
        self.name = name
        self.precision = precision

    def __call__(self, y_true_label_index, y_pred_label_index):
        score = cohen_kappa_score(y_true_label_index, y_pred_label_index)
        return score

from sklearn.metrics import matthews_corrcoef
class Matthews_corrcoef(ClassifierBaseScoreType):
    is_lower_the_better = False
    minimum = -1.0
    maximum = 1.0

    def __init__(self, name='Matthews', precision=2):
        self.name = name
        self.precision = precision

    def __call__(self, y_true_label_index, y_pred_label_index):
        score = matthews_corrcoef(y_true_label_index, y_pred_label_index)
        return score

score_types = [
    Kappa(name='kappa', precision=3),
    Matthews_corrcoef(name='matthews', precision=3),
    rw.score_types.ROCAUC(name='roc_auc', precision=3),
    rw.score_types.Accuracy(name='acc', precision=3),
]


def get_cv(X, y):
    cv = StratifiedShuffleSplit(n_splits=8, test_size=0.5, random_state=57)
    return cv.split(X, y)


def _read_data(path, f_name):
    test = os.getenv('RAMP_TEST_MODE', 0)
    if test:
        data = pd.read_csv(os.path.join(path, 'data', 'train.csv'))
    else:
        data = pd.read_csv(os.path.join(path, 'kaggle_data', 'train.csv'))
    y_array = data[_target_column_name].values
    X_df = data.drop(_target_column_name, axis=1)
    return X_df, y_array


def get_train_data(path='.'):
    f_name = 'train.csv'
    return _read_data(path, f_name)


def get_test_data(path='.'):
    f_name = 'test.csv'
    return _read_data(path, f_name)


def AAAget_test_data(path='.'):
    test = os.getenv('RAMP_TEST_MODE', 0)
    if test:
        X_df = pd.read_csv(os.path.join(path, 'data', 'test.csv'))
    else:
        X_df = pd.read_csv(os.path.join(path, 'kaggle_data', 'test.csv'))
    y_array = np.zeros(len(X_df))  # dummy labels for syntax
    y_array[0] = 1  # to make AUC work
    return X_df, y_array


def save_submission(y_pred, data_path='.', output_path='.', suffix='test'):
    if 'test' not in suffix:
        return  # we don't care about saving the training predictions
    test = os.getenv('RAMP_TEST_MODE', 0)
    if test:
        sample_df = pd.read_csv(os.path.join(
            data_path, 'data', 'sample_submission.csv'))
    else:
        sample_df = pd.read_csv(os.path.join(
            data_path, 'kaggle_data', 'sample_submission.csv'))
    df = pd.DataFrame()
    df['id'] = sample_df['id']
    df['isFraud'] = y_pred[:, 1]
    output_f_name = os.path.join(
        output_path, 'submission_{}.csv'.format(suffix))
    df.to_csv(output_f_name, index=False)
