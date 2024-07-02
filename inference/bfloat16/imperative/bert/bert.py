import torch
from transformers import BertModel

############# code changes ###############
import intel_extension_for_pytorch as ipex

############# code changes ###############

model = BertModel.from_pretrained("bert-base-uncased")
model.eval()

vocab_size = model.config.vocab_size
batch_size = 1
seq_length = 512
data = torch.randint(vocab_size, size=[batch_size, seq_length])

######## code changes #######
model = model.to("xpu")
data = data.to("xpu")
model = ipex.optimize(model)
######## code changes #######

with torch.no_grad():
    model(data)

print("Execution finished")
