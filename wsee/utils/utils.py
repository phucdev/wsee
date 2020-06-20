import pickle
import json
import re

import pandas as pd
import numpy as np

from wsee import SD4M_RELATION_TYPES


def get_deep_copy(obj):
    return pickle.loads(pickle.dumps(obj))


def pretty_print_json(obj):
    print(json.dumps(json.loads(obj.to_json()), indent=2, ensure_ascii=False))


def parse_gaz_file(path):
    cause_consequence_mapping = {}
    with open(path, 'r') as gaz_reader:
        for line in gaz_reader.readlines():
            cols = line.split(' | ')
            cause_event = cols[0]
            consequence = re.findall('"([^"]*)"', cols[2])
            assert len(consequence) > 0
            cause_consequence_mapping[cause_event] = consequence[0]
    return cause_consequence_mapping


def let_most_probable_class_dominate(x: pd.Series) -> pd.Series:
    for event in x['event_triggers']:
        type_probs = np.asarray(event['event_type_probs'])
        max_idx = type_probs.argmax()
        type_probs *= 0.0
        type_probs[max_idx] = 1.0
        event['event_type_probs'] = list(type_probs)
    for role_pair in x['event_roles']:
        arg_probs = np.asarray(role_pair['event_argument_probs'])
        max_idx = arg_probs.argmax()
        arg_probs *= 0.0
        arg_probs[max_idx] = 1.0
        role_pair['event_argument_probs'] = list(arg_probs)
    return x


def zero_out_abstains(y: np.ndarray, L: np.ndarray) -> np.ndarray:
    """
    Finds all the rows, where all the LFs abstained and sets all the class probabilities to zero.
    The Snorkel model in eventx will ignore these during loss & metrics calculation.
    :param y: Matrix of probabilities output by label model's predict_proba method.
    :param L: Matrix of labels emitted by LFs.
    :return: Probabilities matrix where the probabilities for data points that were labeled by none of the LF in L
            are set to zero.
    """
    mask = (L == -1).all(axis=1)
    y[mask] *= 0.0
    return y


def has_events(doc, include_negatives=False):
    """
    :param doc: Document
    :param include_negatives: Count document as having events when at least one trigger is not an abstain

    :return: Whether the document contains any (positive) events
    """
    if 'events' in doc and doc['events']:
        return True
    elif 'event_triggers' in doc and doc['event_triggers']:
        trigger_probs = np.asarray(
            [trigger['event_type_probs'] for trigger in doc['event_triggers']]
        )
        if include_negatives:
            return trigger_probs.sum() > 0.0
        labeled_triggers = trigger_probs.sum(axis=1) > 0.0
        trigger_labels = trigger_probs[labeled_triggers].argmax(axis=1)
        if any(label < len(SD4M_RELATION_TYPES)-1 for label in trigger_labels):
            return True
    return False
