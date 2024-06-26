"""
`简介 <introyt1_tutorial.html>`_ ||
`张量 <tensors_deeper_tutorial.html>`_ ||
**自动微分** ||
`构建模型 <modelsyt_tutorial.html>`_ ||
`TensorBoard支持 <tensorboardyt_tutorial.html>`_ ||
`训练模型 <trainingyt.html>`_ ||
`模型理解 <captumyt.html>`_

自动微分基础
============================
跟随下面的视频或在 `youtube <https://www.youtube.com/watch?v=M0fX15_-xrY>`__ 上观看。

.. raw:: html

   <div style="margin-top:10px; margin-bottom:10px;">
     <iframe width="560" height="315" src="https://www.youtube.com/embed/M0fX15_-xrY" frameborder="0" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
   </div>

PyTorch 的 *Autograd* 功能是使 PyTorch 在构建机器学习项目时灵活且快速的部分原因。
它允许对复杂计算快速轻松地计算多个偏导数(也称为 *梯度* )。这个操作是基于反向传播的神经网络学习的核心。

Autograd 的强大之处在于它在运行时动态地 *跟踪你的计算* ,这意味着如果你的模型有决策分支或长度在运行时才知道的循环,
计算仍然会被正确跟踪,你会得到正确的梯度来驱动学习。结合你的模型是用 Python 构建的事实,
这比依赖于对更加严格结构化的模型进行静态分析来计算梯度的框架提供了更大的灵活性。

我们为什么需要 Autograd?
-----------------------------

"""

###########################################################################
# 机器学习模型是一个 *函数* ,有输入和输出。在本讨论中,我们将把输入视为一个 *i* 维向量
# :math:`\vec{x}`，其元素为 :math:`x_{i}`。然后我们可以将模型 *M* 表示为输入的向量值函数:
# :math:`\vec{y} = \vec{M}(\vec{x})`。(我们将模型 M 的输出值视为向量,因为一般来说,
# 一个模型可能有任意数量的输出。)
#
# 由于我们主要在训练的背景下讨论自动微分,我们感兴趣的输出将是模型的损失。*损失函数*
# L(:math:`\vec{y}`) = L(:math:`\vec{M}`\ (:math:`\vec{x}`))是模型输出的单值标量函数。
# 该函数表示我们模型对特定输入的 *理想* 输出的预测偏差有多大。 *注意:从这一点开始,
# 我们通常会省略向量符号,例如使用* :math:`y` 而不是 :math:`\vec y`。
#
# 在训练模型时,我们希望最小化损失。在理想情况下,即完美模型的情况下,这意味着调整其学习权重 - 
# 也就是该函数的可调参数 - 使得对于所有输入,损失为零。在现实世界中,这意味着一个迭代过程,
# 不断微调学习权重,直到我们看到对于广泛的输入,得到可接受的损失。
#
# 我们如何决定权重应该朝哪个方向微调多远呢?我们希望 *最小化* 损失,这意味着使其关于输入的一阶导数等于0:
# :math:`\frac{\partial L}{\partial x} = 0`。
#
# 但是请记住,损失不是 *直接* 由输入导出的,而是由模型输出的函数导出的(而模型输出又是输入的直接函数),
# :math:`\frac{\partial L}{\partial x}` = :math:`\frac{\partial {L({\vec y})}}{\partial x}`。
# 根据微积分的链式法则,我们有 :math:`\frac{\partial {L({\vec y})}}{\partial x}` =
# :math:`\frac{\partial L}{\partial y}\frac{\partial y}{\partial x}` =
# :math:`\frac{\partial L}{\partial y}\frac{\partial M(x)}{\partial x}`。
#
# :math:`\frac{\partial M(x)}{\partial x}` 是复杂的地方。如果我们再次使用链式法则展开模型输出关于输入的偏导数的表达式,
# 它将涉及每个乘以的学习权重、每个激活函数以及模型中的每个其他数学变换的许多局部偏导数。
# 我们试图测量其梯度的每个变量的完整表达式,都是通过计算图中所有可能路径的局部梯度之和的乘积。
#
# 特别感兴趣的是学习权重上的梯度 - 它们告诉我们 *应该朝哪个方向改变每个权重* ,以使损失函数更接近于零。
#
# 由于这些局部导数的数量(每个对应于计算图中的单独路径)往往会随着神经网络的深度呈指数增长,
# 因此计算它们的复杂度也会增加。这就是自动微分发挥作用的地方:它跟踪每一步计算的历史。
# 你在PyTorch模型中计算的每个张量都保留了其输入张量和创建它的函数的历史记录。
# 结合PyTorch中用于对张量进行操作的每个函数都内置了计算自身导数的实现这一事实,
# 这极大地加快了学习所需的局部导数的计算速度。
#
# 一个简单的例子
# ----------------
#
# 这是很多理论 - 但在实践中使用自动微分是什么样的呢?
#
# 让我们从一个简单的例子开始。首先,我们将导入一些内容,以便可以绘制结果:
#

# %matplotlib inline

import torch

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math


#########################################################################
# 接下来,我们将创建一个输入张量,其值均匀分布在区间 [0, 2π] 上,并指定 ``requires_grad=True``。
# (与大多数创建张量的函数一样,``torch.linspace()`` 接受一个可选的 ``requires_grad`` 选项。)
# 设置此标志意味着在随后的每个计算中,autograd 都会在该计算的输出张量中累积计算历史。

a = torch.linspace(0., 2. * math.pi, steps=25, requires_grad=True)
print(a)


########################################################################
# 接下来,我们将执行一个计算,并绘制其输出与输入的关系图:
#

b = torch.sin(a)
plt.plot(a.detach(), b.detach())


########################################################################
# 让我们仔细看看张量 ``b``。当我们打印它时,我们看到一个指示它正在跟踪其计算历史的指示符:
#

print(b)


#######################################################################
# 这个 ``grad_fn`` 给了我们一个提示,当我们执行反向传播步骤并计算梯度时,
# 我们需要计算所有这个张量输入的 sin(x) 的导数。
#
# 让我们执行更多计算:

c = 2 * b
print(c)

d = c + 1
print(d)


##########################################################################
# 最后,让我们计算一个单元素输出。当你在不带参数的情况下对一个张量调用 ``.backward()`` 时,
# 它期望调用张量只包含一个元素,就像在计算损失函数时一样。
#

out = d.sum()
print(out)


##########################################################################
# 每个存储在我们张量中的 ``grad_fn`` 允许你使用其 ``next_functions`` 属性
# 沿着计算路径一直回溯到其输入。我们可以看到,在 ``d`` 上深入钻研这个属性会显示我们之前所有张量的梯度函数。
# 注意,``a.grad_fn`` 被报告为 ``None``,表示这是一个没有自身历史的函数输入。

print('d:')
print(d.grad_fn)
print(d.grad_fn.next_functions)
print(d.grad_fn.next_functions[0][0].next_functions)
print(d.grad_fn.next_functions[0][0].next_functions[0][0].next_functions)
print(d.grad_fn.next_functions[0][0].next_functions[0][0].next_functions[0][0].next_functions)
print('\nc:')
print(c.grad_fn)
print('\nb:')
print(b.grad_fn)
print('\na:')
print(a.grad_fn)


######################################################################
# 有了这些机制,我们如何获取导数呢?您在输出上调用 `backward()` 方法,并检查输入的
# `grad` 属性来检查梯度:
#


out.backward()
print(a.grad)
plt.plot(a.detach(), a.grad.detach())


#########################################################################
# 回顾一下我们为了达到这一步所采取的计算步骤:
#
# .. code-block:: python
#
#    a = torch.linspace(0., 2. * math.pi, steps=25, requires_grad=True)
#    b = torch.sin(a)
#    c = 2 * b
#    d = c + 1
#    out = d.sum()
#
# 添加一个常数,就像我们计算 `d` 时所做的那样,不会改变导数。剩下的就是 :math:`c = 2 * b = 2 * \sin(a)`,
# 它的导数应该是 :math:`2 * \cos(a)`。从上面的图中可以看出,这正是我们所看到的。
#
# 请注意,只有计算图的 *叶子节点* 才会计算它们的梯度。如果你尝试,例如, `print(c.grad)` 你会得到
# `None`。在这个简单的例子中,只有输入是叶子节点,所以只有它有计算梯度。
#
# 自动求导在训练中
# --------------------
#
# 我们已经简单地看了一下自动求导是如何工作的,但是当它在实际应用中,看起来会是什么样子呢?
# 让我们定义一个小模型并检查它在单个训练批次后是如何变化的。首先,定义一些常量、我们的模型,
# 以及一些输入和输出:

BATCH_SIZE = 16
DIM_IN = 1000
HIDDEN_SIZE = 100
DIM_OUT = 10

class TinyModel(torch.nn.Module):

    def __init__(self):
        super(TinyModel, self).__init__()
        
        self.layer1 = torch.nn.Linear(DIM_IN, HIDDEN_SIZE)
        self.relu = torch.nn.ReLU()
        self.layer2 = torch.nn.Linear(HIDDEN_SIZE, DIM_OUT)
    
    def forward(self, x):
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        return x
    
some_input = torch.randn(BATCH_SIZE, DIM_IN, requires_grad=False)
ideal_output = torch.randn(BATCH_SIZE, DIM_OUT, requires_grad=False)

model = TinyModel()


##########################################################################
# 你可能会注意到,我们从未为模型的层设置
# ``requires_grad=True``。在 ``torch.nn.Module`` 的子类中,
# 假定我们希望跟踪层权重的梯度以进行学习。
#
# 如果我们查看模型的层,我们可以检查权重的值,
# 并验证尚未计算任何梯度:
#

print(model.layer2.weight[0][0:10]) # 只打印一小部分
print(model.layer2.weight.grad)


##########################################################################
# 让我们看看当我们运行一个训练批次时会发生什么变化。作为损失函数,我们将使用 ``prediction`` 
# 和 ``ideal_output`` 之间的欧几里得距离的平方,并使用基本的随机梯度下降优化器。
#

optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

prediction = model(some_input)

loss = (ideal_output - prediction).pow(2).sum()
print(loss)


######################################################################
# 现在,让我们调用 ``loss.backward()`` 并看看会发生什么:
#

loss.backward()
print(model.layer2.weight[0][0:10])
print(model.layer2.weight.grad[0][0:10])


########################################################################
# 我们可以看到,每个学习权重的梯度都已经计算出来了,但权重保持不变,因为我们还没有运行优化器。
# 优化器负责根据计算出的梯度更新模型权重。
#

optimizer.step()
print(model.layer2.weight[0][0:10])
print(model.layer2.weight.grad[0][0:10])


######################################################################
# 你应该看到 ``layer2`` 的权重已经改变。
#
# 关于这个过程的一个重要事项:在调用 ``optimizer.step()`` 之后,
# 你需要调用 ``optimizer.zero_grad()``,否则每次你运行 ``loss.backward()``,
# 学习权重上的梯度将会累积:
#

print(model.layer2.weight.grad[0][0:10])

for i in range(0, 5):
    prediction = model(some_input)
    loss = (ideal_output - prediction).pow(2).sum()
    loss.backward()
    
print(model.layer2.weight.grad[0][0:10])

optimizer.zero_grad(set_to_none=False)

print(model.layer2.weight.grad[0][0:10])


#########################################################################
# 在运行上面的单元格后,你应该会看到在多次运行 ``loss.backward()`` 之后,
# 大多数梯度的幅度会变得更大。如果在运行下一个训练批次之前
# 没有将梯度清零,梯度就会以这种方式膨胀,从而导致不正确和
# 不可预测的学习结果。
#
# 关闭和打开自动求导
# ---------------------------
#
# 在某些情况下,你需要对是否启用自动求导进行细粒度控制。
# 有多种方法可以做到这一点,具体取决于情况。
#
# 最简单的方法是直接更改张量上的 ``requires_grad`` 标志:
#

a = torch.ones(2, 3, requires_grad=True)
print(a)

b1 = 2 * a
print(b1)

a.requires_grad = False
b2 = 2 * a
print(b2)


##########################################################################
# 在上面的单元格中,我们可以看到 ``b1`` 有一个 ``grad_fn``(即,一个
# 计算历史的跟踪记录),这是我们所期望的,因为它是从一个启用了
# autograd 的张量 ``a`` 派生出来的。当我们使用 ``a.requires_grad = False``
# 显式地关闭 autograd 时,计算历史就不再被跟踪了,正如我们在计算 ``b2`` 时
# 所看到的那样。
#
# 如果你只需要临时关闭 autograd,一个更好的方法是使用 ``torch.no_grad()``:
#

a = torch.ones(2, 3, requires_grad=True) * 2
b = torch.ones(2, 3, requires_grad=True) * 3

c1 = a + b
print(c1)

with torch.no_grad():
    c2 = a + b

print(c2)

c3 = a * b
print(c3)


##########################################################################
# ``torch.no_grad()`` 也可以用作函数或方法装饰器:
# 

def add_tensors1(x, y):
    return x + y

@torch.no_grad()
def add_tensors2(x, y):
    return x + y


a = torch.ones(2, 3, requires_grad=True) * 2
b = torch.ones(2, 3, requires_grad=True) * 3

c1 = add_tensors1(a, b)
print(c1)

c2 = add_tensors2(a, b)
print(c2)


##########################################################################
# 有一个对应的上下文管理器 ``torch.enable_grad()`` 用于在尚未启用时
# 打开 autograd。它也可以用作装饰器。
#
# 最后,你可能有一个需要梯度跟踪的张量,但你想要一个不需要的副本。
# 为此,我们有张量对象的 ``detach()`` 方法 - 它创建一个与计算历史
# *分离*的张量副本:
#

x = torch.rand(5, requires_grad=True)
y = x.detach()

print(x)
print(y)


#########################################################################
# 我们之前这样做是因为我们想要绘制一些张量的图像。这是因为 ``matplotlib``
# 期望输入是一个 NumPy 数组,而从具有 requires_grad=True 的 PyTorch 张量
# 到 NumPy 数组的隐式转换是不允许的。制作一个分离的副本让我们可以继续前进。
#
# Autograd 和原位操作
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# 在本练习中到目前为止的每个示例中,我们都使用了变量来捕获计算的中间值。
# Autograd 需要这些中间值来执行梯度计算。 *因此,在使用 autograd 时,你必须
# 小心使用原位操作。* 这样做可能会破坏计算导数所需的信息,在 ``backward()``
# 调用时需要这些信息。如果你尝试对需要 autograd 的叶变量进行原位操作,
# PyTorch 甚至会阻止你,如下所示。
#
# .. 注意::
#     下面的代码单元会抛出一个运行时错误。这是预期的行为。
#
#    .. code-block:: python
#
#       a = torch.linspace(0., 2. * math.pi, steps=25, requires_grad=True)
#       torch.sin_(a)
#

#########################################################################
# Autograd 分析器
# -----------------
#
# Autograd 会详细跟踪你的每一步计算。这种计算历史,结合时间信息,
# 将构成一个方便的分析器 - 而 autograd 就内置了这个功能。
# 这里有一个快速使用示例:
#

device = torch.device('cpu')
run_on_gpu = False
if torch.cuda.is_available():
    device = torch.device('cuda')
    run_on_gpu = True
    
x = torch.randn(2, 3, requires_grad=True)
y = torch.rand(2, 3, requires_grad=True)
z = torch.ones(2, 3, requires_grad=True)

with torch.autograd.profiler.profile(use_cuda=run_on_gpu) as prf:
    for _ in range(1000):
        z = (z / x) * y
        
print(prf.key_averages().table(sort_by='self_cpu_time_total'))


##########################################################################
# 分析器可以标记代码的单个子块,按输入张量形状分解数据,并将数据导出为
# Chrome 跟踪工具文件。有关 API 的完整详细信息,请参阅
# `文档 <https://pytorch.org/docs/stable/autograd.html#profiler>`__。
#
# 高级主题:更多 Autograd 细节和高级 API
# -----------------------------------------------------------
#
# 如果你有一个具有 n 维输入和 m 维输出的函数,
# :math:`\vec{y}=f(\vec{x})`,,完整的梯度是每个输出相对于每个输入的
# 导数的矩阵,称为 *Jacobian:*
#
# .. math::
#
#      J
#      =
#      \left(\begin{array}{ccc}
#      \frac{\partial y_{1}}{\partial x_{1}} & \cdots & \frac{\partial y_{1}}{\partial x_{n}}\\
#      \vdots & \ddots & \vdots\\
#      \frac{\partial y_{m}}{\partial x_{1}} & \cdots & \frac{\partial y_{m}}{\partial x_{n}}
#      \end{array}\right)
#
# 如果你有第二个函数 :math:`l=g\left(\vec{y}\right)`,它
# 接受 m 维输入(也就是与上面的输出具有相同的维度),并返回一个
# 标量输出,你可以用一个列向量来表示它相对于 :math:`\vec{y}` 的梯度,
# :math:`v=\left(\begin{array}{ccc}\frac{\partial l}{\partial y_{1}} & \cdots & \frac{\partial l}{\partial y_{m}}\end{array}\right)^{T}`
# - 这实际上只是一个一列的 Jacobian。
#
# 更具体地说,想象第一个函数是你的 PyTorch 模型(可能有许多输入和许多输出),
# 第二个函数是一个损失函数(以模型的输出作为输入,损失值作为标量输出)。
#
# 如果我们将第一个函数的 Jacobian 与第二个函数的梯度相乘,并应用链式法则,
# 我们得到:
#
# .. math::
#
#    J^{T}\cdot v=\left(\begin{array}{ccc}
#    \frac{\partial y_{1}}{\partial x_{1}} & \cdots & \frac{\partial y_{m}}{\partial x_{1}}\\
#    \vdots & \ddots & \vdots\\
#    \frac{\partial y_{1}}{\partial x_{n}} & \cdots & \frac{\partial y_{m}}{\partial x_{n}}
#    \end{array}\right)\left(\begin{array}{c}
#    \frac{\partial l}{\partial y_{1}}\\
#    \vdots\\
#    \frac{\partial l}{\partial y_{m}}
#    \end{array}\right)=\left(\begin{array}{c}
#    \frac{\partial l}{\partial x_{1}}\\
#    \vdots\\
#    \frac{\partial l}{\partial x_{n}}
#    \end{array}\right)
#
# 注意:你也可以使用等价的操作 :math:`v^{T}\cdot J`,
# 并得到一个行向量。
#
# 所得到的列向量就是 *第二个函数相对于第一个函数的输入的梯度* - 或者在我们的
# 模型和损失函数的情况下,就是损失相对于模型输入的梯度。
#
# ** ``torch.autograd`` 是一个用于计算这些乘积的引擎。** 这就是我们在
# 反向传播过程中如何累积学习权重的梯度。
#
# 因此,``backward()`` 调用也可以 *接受一个可选的向量输入*。该向量表示
# 张量上的一组梯度,这些梯度将乘以前面的 autograd 跟踪张量的 Jacobian。
# 让我们用一个小向量尝试一个具体的例子:
#

x = torch.randn(3, requires_grad=True)

y = x * 2
while y.data.norm() < 1000:
    y = y * 2

print(y)


##########################################################################
# 如果我们尝试现在调用 ``y.backward()``,我们会得到一个运行时错误和一条
# 消息,说明只能 *隐式地* 为标量输出计算梯度。对于多维输出,autograd 期望我们
# 提供这三个输出的梯度,它可以将这些梯度乘以Jacobian矩阵:
#

v = torch.tensor([0.1, 1.0, 0.0001], dtype=torch.float) # 代替梯度
y.backward(v)

print(x.grad)


##########################################################################
# (注意,输出梯度都与2的幂有关 - 这正是我们从重复的双倍操作中所期望的。)
#
# 高级 API
# ~~~~~~~~~~~~~~~~~~
#
# autograd 有一个 API,可以直接访问重要的差分矩阵和向量运算。特别是,
# 它允许你计算特定函数在特定输入下的Jacobian矩阵和 *Hessian矩阵* 。(Hessian矩阵
# 类似于Jacobian矩阵,但表示所有偏导数的 *第二阶* 导数。)它还提供了与这些矩阵
# 进行向量乘积的方法。
#
# 让我们计算一个简单函数的Jacobian矩阵,对于两个单元素输入进行评估:
#

def exp_adder(x, y):
    return 2 * x.exp() + 3 * y

inputs = (torch.rand(1), torch.rand(1)) # arguments for the function
print(inputs)
torch.autograd.functional.jacobian(exp_adder, inputs)


########################################################################
# 如果你仔细观察,第一个输出应该等于 :math:`2e^x` (因为 :math:`e^x` 的
# 导数是 :math:`e^x`),第二个值应该是3。
#
# 你当然也可以对更高阶的张量这样做:
# 

inputs = (torch.rand(3), torch.rand(3)) # arguments for the function
print(inputs)
torch.autograd.functional.jacobian(exp_adder, inputs)


#########################################################################
# ``torch.autograd.functional.hessian()`` 方法的工作方式完全相同(假设你的
# 函数是两次可微的),但返回所有二阶导数的矩阵。
#
# 如果你提供了向量,还有一个直接计算向量-雅可比乘积的函数:
#

def do_some_doubling(x):
    y = x * 2
    while y.data.norm() < 1000:
        y = y * 2
    return y

inputs = torch.randn(3)
my_gradients = torch.tensor([0.1, 1.0, 0.0001])
torch.autograd.functional.vjp(do_some_doubling, inputs, v=my_gradients)


##############################################################################
# ``torch.autograd.functional.jvp()`` 方法执行与 ``vjp()`` 相同的矩阵乘法,
# 但操作数顺序相反。``vhp()`` 和 ``hvp()`` 方法对于向量-海森矩阵乘积也是如此。
#
# 有关更多信息,包括 `功能 API 文档 <https://pytorch.org/docs/stable/autograd.html#functional-higher-level-api>`__
# 中的性能说明。
#