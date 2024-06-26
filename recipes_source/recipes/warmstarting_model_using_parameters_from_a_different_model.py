"""
PyTorch 使用不同模型的参数对模型进行热启动
=====================================================================
在转移学习或训练新的复杂模型时,加载部分模型是很常见的场景。
利用已经训练好的参数,即使只有少数可用,也将有助于加快训练过程的启动,
并有望使您的模型比从头开始训练收敛得更快。

简介
------------
无论您是加载缺少某些键的部分 ``state_dict`` ,还是加载比预期的模型更多键的 ``state_dict``,
您都可以通过 ``load_state_dict()`` 函数中将 strict 参数设置为 ``False`` 以忽略不匹配的键。
在本教程中,我们将尝试使用不同模型的参数对模型进行热启动。

环境设置
-----
在开始之前,如果尚未安装 ``torch``,我们需要先安装它。

.. code-block:: sh

   pip install torch
   
"""



######################################################################
# 具体步骤
# -----
# 
# 1. 导入加载数据所需的所有必要库
# 2. 定义并初始化神经网络 A 和 B
# 3. 保存模型 A
# 4. 加载到模型 B
# 
# 1. 导入加载数据所需的必要库
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# 对于本教程,我们将使用 ``torch`` 及其子模块 ``torch.nn`` 和 ``torch.optim``。
# 

import torch
import torch.nn as nn
import torch.optim as optim


######################################################################
# 2. 定义并初始化神经网络 A 和 B
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# 我们将创建一个用于训练图像的神经网络。要了解更多信息,请参阅定义神经网络的教程。
# 我们将创建两个神经网络,将类型 A 的一个参数加载到类型 B 中。
# 

class NetA(nn.Module):
    def __init__(self):
        super(NetA, self).__init__()
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

netA = NetA()

class NetB(nn.Module):
    def __init__(self):
        super(NetB, self).__init__()
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

netB = NetB()


######################################################################
# 3. 保存模型 A
# ~~~~~~~~~~~~~~~~~~~
# 

# 指定保存路径
PATH = "model.pt"

torch.save(netA.state_dict(), PATH)


######################################################################
# 4. 加载到模型 B
# ~~~~~~~~~~~~~~~~~~~~~~~~
# 
# 如果您想将一个层的参数加载到另一个层,但是某些键不匹配,
# 只需将要加载的 state_dict 中的参数键名称更改为与要加载到的模型中的键名称相匹配即可。
# 

netB.load_state_dict(torch.load(PATH), strict=False)


######################################################################
# 您可以看到所有键都匹配成功!
# 
# 祝贺您!您已成功使用不同模型的参数对模型进行了热启动。
# 
# 学习更多
# ----------
# 
# 查看这些其他教程,继续您的学习:
# 
# - `使用PyTorch在一个文件中保存和加载多个模型 <https://pytorch.org/tutorials/recipes/recipes/saving_multiple_models_in_one_file.html>`__
# - `在PyTorch中跨设备保存和加载模型 <https://pytorch.org/tutorials/recipes/recipes/save_load_across_devices.html>`__