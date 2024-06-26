"""
`基础知识 <intro.html>`_ ||
`快速入门 <quickstart_tutorial.html>`_ ||
`张量 <tensorqs_tutorial.html>`_ ||
`数据集与数据加载器 <data_tutorial.html>`_ ||
**Transforms** ||
`构建神经网络 <buildmodel_tutorial.html>`_ ||
`自动微分 <autogradqs_tutorial.html>`_ ||
`优化模型参数 <optimization_tutorial.html>`_ ||
`保存和加载模型 <saveloadrun_tutorial.html>`_

Transforms
==========

数据并不总是以训练机器学习算法所需的最终处理形式呈现。我们使用**transforms**来对数据进行一些处理，使其适用于训练。

所有 TorchVision 数据集都有两个参数 - `transform` 用于修改特征，`target_transform` 用于修改标签 
- 它们接受包含转换逻辑的可调用对象。`torchvision.transforms <https://pytorch.org/vision/stable/transforms.html>`_ 模块提供了几种常用的转换。

FashionMNIST 的特征是以 PIL 图像格式呈现的，标签是整数。对于训练，我们需要将特征转换为归一化的张量，
将标签转换为编码的张量。为了进行这些转换，我们使用了 ``ToTensor`` 和 ``Lambda``。
"""

import torch
from torchvision import datasets
from torchvision.transforms import ToTensor, Lambda

ds = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor(),
    target_transform=Lambda(lambda y: torch.zeros(
        10, dtype=torch.float).scatter_(0, torch.tensor(y), value=1))
)

#################################################
# ToTensor()
# -------------------------------
#
# `ToTensor <https://pytorch.org/vision/stable/transforms.html#torchvision.transforms.ToTensor>`_
# 将 PIL 图像或 NumPy ``ndarray`` 转换为 ``FloatTensor``，并将图像的像素强度值缩放到范围 [0., 1.]。

##############################################
# Lambda Transforms
# -------------------------------
#
# Lambda transforms 应用任何用户定义的 lambda 函数。这里，我们定义一个函数将整数转换为独热编码的张量。
# 它首先创建一个大小为 10（我们数据集中标签的数量）的零张量，然后调用 `scatter_ <https://pytorch.org/docs/stable/generated/torch.Tensor.scatter_.html>`_，
# 在由标签 ``y`` 指定的索引上赋值为 ``1``。

target_transform = Lambda(lambda y: torch.zeros(
    10, dtype=torch.float).scatter_(dim=0, index=torch.tensor(y), value=1))

######################################################################
# --------------
#

#################################################################
# 延伸阅读
# ~~~~~~~~~~~~~~~~~
# - `torchvision.transforms API <https://pytorch.org/vision/stable/transforms.html>`_
