# Copyright (c) OpenMMLab. All rights reserved.
import collections
import numpy as np
from mmcv.utils import build_from_cfg

from ..builder import PIPELINES


@PIPELINES.register_module()
class Compose:
    """Compose multiple transforms sequentially.

    Args:
        transforms (Sequence[dict | callable]): Sequence of transform object or
            config dict to be composed.
    """

    def __init__(self, transforms):
        assert isinstance(transforms, collections.abc.Sequence)
        self.transforms = []
        for transform in transforms:
            if isinstance(transform, dict):
                transform = build_from_cfg(transform, PIPELINES)
                self.transforms.append(transform)
            elif callable(transform):
                self.transforms.append(transform)
            else:
                raise TypeError('transform must be callable or a dict')

    def __call__(self, data):
        """Call function to apply transforms sequentially.

        Args:
            data (dict): A result dict contains the data to transform.

        Returns:
           dict: Transformed data.
        """

        for t in self.transforms:
            data = t(data)
            if data is None:
                return None
        # print(data['img_metas'],data['gt_bboxes'])
        gt_bboxes = []
        num_frames = 0
        for key in list(data.keys()):
            if 'gt_bboxes' in key:
                num_frames = num_frames + 1
        for i in range(num_frames):
            key = 'gt_bboxes_' + str(i+1)
            gt_bboxes.append(data[key])
            del data[key]
        if num_frames>0:
            data['gt_bboxes'] = np.concatenate(gt_bboxes, 0)


        return data

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        for t in self.transforms:
            str_ = t.__repr__()
            if 'Compose(' in str_:
                str_ = str_.replace('\n', '\n    ')
            format_string += '\n'
            format_string += f'    {str_}'
        format_string += '\n)'
        return format_string
