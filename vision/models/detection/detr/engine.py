import torch
from torch.cuda import amp
from vision.models import model_utils
from tqdm import tqdm
import time
from collections import OrderedDict

__all__ = ["train_step", "val_step", "fit", "train_sanity_fit",
           "val_sanity_fit", "sanity_fit", ]


def train_step(model, train_loader, criterion, device, optimizer, scheduler=None,
               num_batches: int = None, log_interval: int = 100, scaler=None,):
    model.train()
    criterion.train()

    total_loss = model_utils.AverageMeter()
    bbox_loss = model_utils.AverageMeter()
    giou_loss = model_utils.AverageMeter()
    labels_loss = model_utils.AverageMeter()

    for batch_idx, (inputs, targets) in enumerate(train_loader):
        images = list(image.to(device) for image in inputs)
        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

        outputs = model(images)
        loss_dict = criterion(outputs, targets)
        weight_dict = criterion.weight_dict
        losses = sum(loss_dict[k] * weight_dict[k] for k in loss_dict.keys() if k in weight_dict)

        optimizer.zero_grad()
        losses.backward()
        optimizer.step()

        if scheduler is not None:
            scheduler.step()

        total_loss.update(losses.item(), inputs.size(0))
        bbox_loss.update(loss_dict["loss_bbox"].item())
        giou_loss.update(loss_dict["loss_giou"].item())
        labels_loss.update(loss_dict["loss_ce"].item())

    print("Training: ")
    print(f"Total_loss = {total_loss.avg}, BBox_Loss = {bbox_loss.avg}, GIOU_Loss = {giou_loss.avg}"
          ", Labels_Loss = {labels_loss.avg}")
    return total_loss


def val_step(model, val_dataloader, criterion, device,
             num_batches: int = None, log_interval: int = 100):

    model.eval()
    criterion.eval()
    total_loss = model_utils.AverageMeter()
    bbox_loss = model_utils.AverageMeter()
    giou_loss = model_utils.AverageMeter()
    labels_loss = model_utils.AverageMeter()
    with torch.no_grad():
        for inputs, targets in tqdm(val_dataloader):
            # print("Here I was")
            images = list(image.to(device) for image in inputs)
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
            outputs = model(images)
            loss_dict = criterion(outputs, targets)
            weight_dict = criterion.weight_dict
            losses = sum(loss_dict[k] * weight_dict[k] for k in loss_dict.keys() if k in weight_dict)

            total_loss.update(losses.item(), inputs.size(0))
            bbox_loss.update(loss_dict["loss_bbox"].item())
            giou_loss.update(loss_dict["loss_giou"].item())
            labels_loss.update(loss_dict["loss_ce"].item())

    print("Validation: ")
    print(f"Total_loss = {total_loss.avg}, BBox_Loss = {bbox_loss.avg}, GIOU_Loss = {giou_loss.avg}"
          ", Labels_Loss = {labels_loss.avg}")

    return total_loss


def fit():
    pass


def train_sanity_fit():
    pass


def val_sanity_fit():
    pass


def sanity_fit():
    pass