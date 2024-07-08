#https://pytorch.org/tutorials/intermediate/tensorboard_profiler_tutorial.html
import torch
import torch.nn
import torch.optim
import torch.profiler
import torch.utils.data
import torchvision.datasets
import torchvision.models
import torchvision.transforms as T
############# code changes ###############
import intel_extension_for_pytorch as ipex
############# code changes ###############

# Then prepare the input data. For this tutorial, we use the CIFAR10 dataset. 
# Transform it to the desired format and use DataLoader to load each batch
transform = T.Compose(
    [T.Resize(224),
     T.ToTensor(),
     T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
train_set = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
train_loader = torch.utils.data.DataLoader(train_set, batch_size=32, shuffle=True)

# Next, create Resnet model, loss function, and optimizer objects. To run on GPU, move model and loss to GPU device.
device = torch.device("xpu:0")
#device = torch.device("cuda:0")
model = torchvision.models.resnet18(weights='IMAGENET1K_V1')#.cuda(device)
criterion = torch.nn.CrossEntropyLoss()#.cuda(device)
optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
model.train()

######################## code changes #######################
model = model.to("xpu")
criterion = criterion.to("xpu")
model, optimizer = ipex.optimize(model, optimizer=optimizer)
######################## code changes #######################

# Define the training step for each batch of input data.
def train(data):
    inputs, labels = data[0].to(device=device), data[1].to(device=device)
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# Use profiler to record execution events
# with torch.profiler.profile(
#         schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
#         on_trace_ready=torch.profiler.tensorboard_trace_handler('./log/resnet18'),
#         record_shapes=True,
#         profile_memory=True,
#         with_stack=True
# ) as prof:
#     for step, batch_data in enumerate(train_loader):
#         prof.step()  # Need to call this at each step to notify profiler of steps' boundary.
#         if step >= 1 + 1 + 3:
#             break
#         train(batch_data)

# Alternatively, the following non-context manager start/stop is supported as well.
prof = torch.profiler.profile(
        schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
        on_trace_ready=torch.profiler.tensorboard_trace_handler('./log/resnet18'),
        record_shapes=True,
        with_stack=True)
#prof.start()
for step, batch_data in enumerate(train_loader):
    prof.step()
    if step >= 1 + 1 + 3:
        break
    train(batch_data)
#prof.stop()