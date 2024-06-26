"""
`简介 <introyt1_tutorial.html>`_ ||
`张量 <tensors_deeper_tutorial.html>`_ ||
`自动微分 <autogradyt_tutorial.html>`_ ||
`构建模型 <modelsyt_tutorial.html>`_ ||
**TensorBoard支持** ||
`训练模型 <trainingyt.html>`_ ||
`模型理解 <captumyt.html>`_

PyTorch TensorBoard 支持
===========================

跟随下面的视频或在 `youtube <https://www.youtube.com/watch?v=6CEld3hZgqc>`__ 上观看。

.. raw:: html

   <div style="margin-top:10px; margin-bottom:10px;">
     <iframe width="560" height="315" src="https://www.youtube.com/embed/6CEld3hZgqc" frameborder="0" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
   </div>

开始之前
----------------

要运行此教程，您需要安装PyTorch、TorchVision、Matplotlib和TensorBoard。

使用 ``conda``：

.. code-block:: sh

    conda install pytorch torchvision -c pytorch
    conda install matplotlib tensorboard

使用 ``pip``：

.. code-block:: sh

    pip install torch torchvision matplotlib tensorboard

安装完依赖项后，请在安装它们的Python环境中重新启动此笔记本。


介绍
------------
 
在本笔记本中，我们将训练LeNet-5的变体，针对Fashion-MNIST数据集。
Fashion-MNIST是一组描绘各种服装的图像瓦片，有十个类标签指示所描绘的服装类型。

"""

# PyTorch模型和训练必需品
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# 图像数据集和图像操作
import torchvision
import torchvision.transforms as transforms

# 图像显示
import matplotlib.pyplot as plt
import numpy as np

# PyTorch TensorBoard支持
from torch.utils.tensorboard import SummaryWriter

# 如果您使用的环境安装了TensorFlow（如Google Colab），请取消注释以下代码以避免将嵌入保存到TensorBoard目录时出现错误

# import tensorflow as tf
# import tensorboard as tb
# tf.io.gfile = tb.compat.tensorflow_stub.io.gfile

######################################################################
# 在TensorBoard中显示图像
# -----------------------------
# 
# 让我们从将数据集中的示例图像添加到TensorBoard开始：
# 

# 收集数据集并准备消费
transform = transforms.Compose(
    [transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))])

# 在./data中存储单独的训练和验证分割
training_set = torchvision.datasets.FashionMNIST('./data',
    download=True,
    train=True,
    transform=transform)
validation_set = torchvision.datasets.FashionMNIST('./data',
    download=True,
    train=False,
    transform=transform)

training_loader = torch.utils.data.DataLoader(training_set,
                                              batch_size=4,
                                              shuffle=True,
                                              num_workers=2)


validation_loader = torch.utils.data.DataLoader(validation_set,
                                                batch_size=4,
                                                shuffle=False,
                                                num_workers=2)

# 类标签
classes = ('T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
        'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle Boot')

# 内联图像显示的辅助函数
def matplotlib_imshow(img, one_channel=False):
    if one_channel:
        img = img.mean(dim=0)
    img = img / 2 + 0.5     # 反归一化
    npimg = img.numpy()
    if one_channel:
        plt.imshow(npimg, cmap="Greys")
    else:
        plt.imshow(np.transpose(npimg, (1, 2, 0)))

# 提取一批4张图像
dataiter = iter(training_loader)
images, labels = next(dataiter)

# 从图像创建网格并显示它们
img_grid = torchvision.utils.make_grid(images)
matplotlib_imshow(img_grid, one_channel=True)


########################################################################
# 上面，我们使用TorchVision和Matplotlib创建了一个输入数据小批量的可视网格。下面，我们在``SummaryWriter``上使用``add_image()``调用来记录图像，以供TensorBoard使用，我们还调用``flush()``以确保它立即写入磁盘。
# 

# 默认log_dir参数为"runs" - 但最好明确指定
# torch.utils.tensorboard.SummaryWriter在上面导入
writer = SummaryWriter('runs/fashion_mnist_experiment_1')

# 将图像数据写入TensorBoard日志目录
writer.add_image('Four Fashion-MNIST Images', img_grid)
writer.flush()

# 要查看，请在命令行上启动TensorBoard：
#   tensorboard --logdir=runs
# ...并在新的浏览器选项卡中打开http://localhost:6006/


##########################################################################
# 如果您在命令行启动TensorBoard并在新的浏览器选项卡中打开它（通常在`localhost:6006 <localhost:6006>`__），您应该在IMAGES选项卡下看到图像网格。
# 
# 绘制标量以可视化训练
# --------------------------------------
# 
# TensorBoard对于跟踪训练的进度和效果很有用。下面，我们将运行一个训练循环，跟踪一些指标，并保存数据以供TensorBoard使用。
# 
# 让我们定义一个模型来对我们的图像瓦片进行分类，以及用于训练的优化器和损失函数：
# 

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 4 * 4, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    

net = Net()
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)


##########################################################################
# 现在让我们训练一个epoch，并每1000批次评估一次训练与验证集的损失：
# 

print(len(validation_loader))
for epoch in range(1):  # 在数据集上循环多次
    running_loss = 0.0

    for i, data in enumerate(training_loader, 0):
        # 基本训练循环
        inputs, labels = data
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        if i % 1000 == 999:    # 每1000个小批量...
            print('Batch {}'.format(i + 1))
            # 对照验证集
            running_vloss = 0.0
            
            # 在评估模式下，可以省略一些特定于模型的操作，例如dropout层
            net.train(False) # 切换到评估模式，例如关闭正则化
            for j, vdata in enumerate(validation_loader, 0):
                vinputs, vlabels = vdata
                voutputs = net(vinputs)
                vloss = criterion(voutputs, vlabels)
                running_vloss += vloss.item()
            net.train(True) # 切换回训练模式，例如打开正则化
            
            avg_loss = running_loss / 1000
            avg_vloss = running_vloss / len(validation_loader)
            
            # 记录每批次平均的运行损失
            writer.add_scalars('Training vs. Validation Loss',
                            { 'Training' : avg_loss, 'Validation' : avg_vloss },
                            epoch * len(training_loader) + i)

            running_loss = 0.0
print('Finished Training')

writer.flush()


#########################################################################
# 切换到您打开的TensorBoard，查看SCALARS选项卡。
# 
# 可视化您的模型
# ----------------------
# 
# TensorBoard还可用于检查模型内的数据流。为此，请使用模型和示例输入调用``add_graph()``方法：
# 

# 再次获取一个小批量的图像
dataiter = iter(training_loader)
images, labels = next(dataiter)

# add_graph()将通过您的模型跟踪示例输入，
# 并将其渲染为图形。
writer.add_graph(net, images)
writer.flush()


#########################################################################
# 当您切换到TensorBoard时，您应该会看到一个GRAPHS选项卡。双击"NET"节点可查看模型内的层和数据流。
# 
# 使用嵌入可视化您的数据集
# ----------------------------------------
# 
# 我们使用的28x28图像瓦片可以建模为784维向量（28 * 28 = 784）。将其投影到较低维度的表示形式可能会很有启发性。``add_embedding()``方法将一组数据投影到具有最高方差的三个维度上，并将它们显示为交互式3D图表。``add_embedding()``方法通过投影到具有最高方差的三个维度来自动执行此操作。
# 
# 下面，我们将采样数据，并生成这样一个嵌入：
# 

# 选择随机子集的数据和相应的标签
def select_n_random(data, labels, n=100):
    assert len(data) == len(labels)

    perm = torch.randperm(len(data))
    return data[perm][:n], labels[perm][:n]

# 提取随机子集的数据
images, labels = select_n_random(training_set.data, training_set.targets)

# 获取每个图像的类标签
class_labels = [classes[label] for label in labels]

# 记录嵌入
features = images.view(-1, 28 * 28)
writer.add_embedding(features,
                    metadata=class_labels,
                    label_img=images.unsqueeze(1))
writer.flush()
writer.close()


#######################################################################
# 现在，如果您切换到TensorBoard并选择PROJECTOR选项卡，您应该会看到投影的3D表示。您可以旋转和缩放模型。在大小不同的尺度上检查它，看看您是否可以发现投影数据和标签聚类中的模式。
# 
# 为了更好的可见性，建议：
# 
# - 从左侧的"Color by"下拉菜单中选择"label"。
# - 切换顶部的Night Mode图标，将浅色图像置于深色背景上。
# 
# 其他资源
# ---------------
# 
# 有关更多信息，请查看：
# 
# - PyTorch关于`torch.utils.tensorboard.SummaryWriter <https://pytorch.org/docs/stable/tensorboard.html?highlight=summarywriter>`__的文档
# - `PyTorch.org教程 <https://pytorch.org/tutorials/>`__ 中的TensorBoard教程内容
# - 有关TensorBoard的更多信息，请参阅`TensorBoard文档 <https://www.tensorflow.org/tensorboard>`__
