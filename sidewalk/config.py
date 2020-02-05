# -*- coding: utf-8 -*-
def add_sidewalk_config(cfg, dataset_type):
    """
    Add config for sidewalk_polygon.
    """
    cfg.DATASETS.TRAIN = ("sidewalk_" + dataset_type + "_train",)
    cfg.DATASETS.TEST = ("sidewalk_" + dataset_type + "_val",)
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 29
