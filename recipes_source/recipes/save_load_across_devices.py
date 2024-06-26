"""
PyTorch 中跨设备保存和加载模型
===================================================

在某些情况下,您可能需要在不同的设备之间保存和加载神经网络模型。

简介
------------

使用PyTorch在不同设备之间保存和加载模型是相对直接的。在本教程中,我们将尝试在CPU和GPU之间保存和加载模型。

环境设置
-----

为了让本教程中的每个代码块都能正确运行,您必须先将运行环境切换到"GPU"或更高。
完成后,如果还没有安装`torch`,我们需要安装它。


.. code-block:: sh

   pip install torch

"""

######################################################################
# 具体步骤
# -----
#
# 1. 导入加载数据所需的所有必要库
# 2. 定义并初始化神经网络
# 3. 在GPU上保存,CPU上加载
# 4. 在GPU上保存,GPU上加载
# 5. 在CPU上保存,GPU上加载
# 6. 保存和加载`DataParallel`模型
#
# 1. 导入加载数据所需的必要库
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# 在本教程中,我们将使用`torch`及其子模块`torch.nn`和`torch.optim`。
#

import torch
import torch.nn as nn
import torch.optim as optim


######################################################################
# 2. 定义并初始化神经网络
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# 为了演示,我们将创建一个用于训练图像的神经网络。
# 要了解更多信息,请参阅定义神经网络的教程。
#

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

net = Net()
print(net)


######################################################################
# 3. 在GPU上保存,CPU上加载
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# 当在CPU上加载使用GPU训练的模型时,请将`torch.device('cpu')`传递给`torch.load()`函数的`map_location`参数。
#

# 指定保存路径
PATH = "model.pt"

# 保存
torch.save(net.state_dict(), PATH)

# 加载
device = torch.device('cpu')
model = Net()
model.load_state_dict(torch.load(PATH, map_location=device))


######################################################################
# 在这种情况下,张量底层的存储将使用`map_location`参数动态重新映射到CPU设备。
#
# 4. 在GPU上保存,GPU上加载
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# 当在GPU上加载使用GPU训练和保存的模型时,只需使用`model.to(torch.device('cuda'))`将初始化的模型转换为CUDA优化模型。
#
# 请确保对所有模型输入使用`.to(torch.device('cuda'))`函数,为模型准备数据。
#

# 保存
torch.save(net.state_dict(), PATH)

# 加载
device = torch.device("cuda")
model = Net()
model.load_state_dict(torch.load(PATH))
model.to(device)


######################################################################
# 注意,调用`my_tensor.to(device)`会返回`my_tensor`在GPU上的新副本。它不会覆盖`my_tensor`。
# 因此,请记住手动覆盖张量:
# `my_tensor = my_tensor.to(torch.device('cuda'))`。
#
# 5. 在CPU上保存,在GPU上加载
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# 当在GPU上加载使用CPU训练和保存的模型时,请在`torch.load()`函数中将`map_location`参数设置为`cuda:device_id`,
# 将模型加载到给定的GPU设备。
#
# 请确保调用`model.to(torch.device('cuda'))`将模型的参数张量转换为CUDA张量。
#
# 最后,还要确保对所有模型输入使用`.to(torch.device('cuda'))`函数,为CUDA优化的模型准备数据。
#

# 保存
torch.save(net.state_dict(), PATH)

# 加载
device = torch.device("cuda")
model = Net()
# 选择您想用的GPU设备编号
model.load_state_dict(torch.load(PATH, map_location="cuda:0"))
model.to(device)


######################################################################
# 6. Saving ``torch.nn.DataParallel`` Models
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# ``torch.nn.DataParallel`` is a model wrapper that enables parallel GPU
# utilization.
# 
# To save a ``DataParallel`` model generically, save the
# ``model.module.state_dict()``. This way, you have the flexibility to
# load the model any way you want to any device you want.
# 

# Save
# 6. 保存`torch.nn.DataParallel`模型
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# `torch.nn.DataParallel`是一个模型包装器,可以启用并行GPU利用。
#
# 要通用地保存`DataParallel`模型,请保存`model.module.state_dict()`。
# 这样,您就可以灵活地将模型加载到任何设备。
#

# 保存
torch.save(net.module.state_dict(), PATH)

# 加载到任何您想要的设备


######################################################################
# 祝贺您!您已成功在PyTorch中跨设备保存和加载模型。
#
