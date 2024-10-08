# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
"""
PointRend Training Script.
This script is a simplified version of the training script in detectron2/tools.
"""

import os

import detectron2.utils.comm as comm
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.data.datasets import register_coco_instances
from detectron2.engine import (DefaultTrainer, default_argument_parser,
                               default_setup, launch)
from detectron2.evaluation import COCOEvaluator, verify_results
from sidewalk import sidewalk_class_names


class Trainer(DefaultTrainer):
    """
    We use the "DefaultTrainer" which contains a number pre-defined logic for
    standard training workflow. They may not work for you, especially if you
    are working on a new research project. In that case you can use the cleaner
    "SimpleTrainer", or write your own training loop.
    """

    @classmethod
    def build_evaluator(cls, cfg, dataset_name, output_folder=None):
        if output_folder is None:
            output_folder = os.path.join(cfg.OUTPUT_DIR, "inference")
        return COCOEvaluator(dataset_name, cfg, True, output_folder)


def _register_datasets(dataset_type='polygon', data_root='./data'):
    _dtype = 'sidewalk_' + dataset_type
    img_location = os.path.join(data_root, _dtype)
    anno_location = os.path.join(data_root, 'annotations')

    for d in ['train', 'val', 'test']:
        # ex: sidewalk_polygon_train
        dataset_name = '{}_{}'.format(_dtype, d)
        register_coco_instances(
            dataset_name, {},
            os.path.join(anno_location, dataset_name + '.json'), img_location)
        MetadataCatalog.get(dataset_name).thing_classes = list(
            sidewalk_class_names())


def setup(args):
    """
    Create configs and perform basic setups.
    """
    _register_datasets(dataset_type='polygon')
    _register_datasets(dataset_type='bbox')

    cfg = get_cfg()
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    cfg.freeze()
    default_setup(cfg, args)
    return cfg


def main(args):
    cfg = setup(args)

    if args.eval_only:
        model = Trainer.build_model(cfg)
        DetectionCheckpointer(
            model, save_dir=cfg.OUTPUT_DIR).resume_or_load(
                cfg.MODEL.WEIGHTS, resume=args.resume)
        res = Trainer.test(cfg, model)
        if comm.is_main_process():
            verify_results(cfg, res)
        return res

    trainer = Trainer(cfg)
    trainer.resume_or_load(resume=args.resume)
    return trainer.train()


if __name__ == "__main__":
    args = default_argument_parser().parse_args()
    print("Command Line Args:", args)
    launch(
        main,
        args.num_gpus,
        num_machines=args.num_machines,
        machine_rank=args.machine_rank,
        dist_url=args.dist_url,
        args=(args, ),
    )
