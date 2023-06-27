from typing import List, Union
from collections import defaultdict
import pandas as pd
import numpy as np
import torch

from lightwood.encoder.base import BaseEncoder
from lightwood.helpers.constants import _UNCOMMON_WORD


class LabelEncoder(BaseEncoder):
    """
    Simple encoder that assigns a unique integer to every observed label.
    
    Allocates an `unknown` label by default to index 0.
    
    Labels must be exact matches between inference and training (e.g. no .lower() on strings is performed here).
    """  # noqa

    def __init__(self, is_target=False, normalize=True) -> None:
        super().__init__(is_target)
        self.label_map = defaultdict(int)  # UNK category maps to 0
        self.inv_label_map = {}  # invalid encoded values are mapped to None in `decode`
        self.output_size = 1
        self.n_labels = None
        self.normalize = normalize

    def prepare(self, priming_data: Union[list, pd.Series]) -> None:
        if not isinstance(priming_data, pd.Series):
            priming_data = pd.Series(priming_data)

        for i, v in enumerate(priming_data.unique()):
            if v is not None:
                self.label_map[v] = int(i + 1)  # leave 0 for UNK
        self.n_labels = len(self.label_map)
        for k, v in self.label_map.items():
            self.inv_label_map[v] = k
        self.is_prepared = True

    def encode(self, data: Union[tuple, np.ndarray, pd.Series]) -> torch.Tensor:
        # specific to the Gym class - remove once deprecated!
        if isinstance(data, tuple):
            data = pd.Series(data)
        if isinstance(data, np.ndarray):
            data = pd.Series(data)
        encoded = torch.Tensor(data.map(self.label_map))
        if self.normalize:
            encoded /= self.n_labels
        return encoded

    def decode(self, encoded_values: torch.Tensor) -> List[object]:
        if self.normalize:
            encoded_values *= self.n_labels
        values = encoded_values.long().tolist()
        values = [self.inv_label_map.get(v, _UNCOMMON_WORD) for v in values]
        return values
