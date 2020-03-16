import unittest

import pandas as pd
import numpy as np
from wsee.utils import utils
from wsee.data.pipeline import build_event_trigger_examples, build_event_role_examples, \
    merge_event_trigger_examples, merge_event_role_examples, build_training_data


class TestPipeline(unittest.TestCase):

    def setUp(self):
        dataframes_path = '/Users/phuc/develop/python/wsee/tests/fixtures/dataframes.jsonl'
        self.pd_df: pd.DataFrame = pd.read_json(dataframes_path, lines=True)

    def test_event_triggers(self):
        event_type_rows, event_type_rows_y = build_event_trigger_examples(self.pd_df)
        event_trigger_examples = utils.get_deep_copy(event_type_rows)
        self.assertTrue(len(event_trigger_examples) == 3)

        trigger_class_probs = np.random.rand(len(event_trigger_examples), 3)
        merged_trigger_examples = merge_event_trigger_examples(event_trigger_examples, trigger_class_probs)
        self.assertTrue(len(merged_trigger_examples) == 2)

    def test_event_roles(self):
        event_role_rows, event_role_rows_y = build_event_role_examples(self.pd_df)
        event_role_examples = utils.get_deep_copy(event_role_rows)
        self.assertTrue(len(event_role_examples) == 11)

        role_class_probs = np.random.rand(len(event_role_examples), 3)
        merged_role_examples = merge_event_role_examples(event_role_examples, role_class_probs)
        self.assertTrue(len(merged_role_examples) == 2)

    def test_build_training_data(self):
        event_type_rows, event_type_rows_y = build_event_trigger_examples(self.pd_df)
        event_trigger_examples = utils.get_deep_copy(event_type_rows)
        trigger_class_probs = np.random.rand(len(event_trigger_examples), 3)
        merged_trigger_examples = merge_event_trigger_examples(event_trigger_examples, trigger_class_probs)

        event_role_rows, event_role_rows_y = build_event_role_examples(self.pd_df)
        event_role_examples = utils.get_deep_copy(event_role_rows)
        role_class_probs = np.random.rand(len(event_role_examples), 3)
        merged_role_examples = merge_event_role_examples(event_role_examples, role_class_probs)

        merged_examples = build_training_data(self.pd_df, merged_trigger_examples, merged_role_examples)
        self.assertIsNotNone(merged_examples)


if __name__ == '__main__':
    unittest.main()