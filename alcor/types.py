from typing import (Union,
                    Dict,
                    Callable,
                    Tuple)

import numpy as np

NumericType = Union[int, float]
GridParametersInfoType = Dict[str, Union[NumericType,
                                         Dict[str, NumericType]]]
CSVParametersInfoType = Dict[str, Dict[str, Union[str, int]]]
GeneratorType = Callable[[float, float, float], np.ndarray]
UnitRangeGeneratorType = Callable[[Tuple[int, ...]], np.ndarray]
