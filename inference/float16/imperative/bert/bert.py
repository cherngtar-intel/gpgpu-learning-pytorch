import torch
import transformers
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
#print in string, instead of int
print("vocab_size: ", vocab_size)
print("In: ", data)

#################### code changes ################
model = model.to("xpu")
data = data.to("xpu")
model = ipex.optimize(model, dtype=torch.float16)
#################### code changes ################

with torch.no_grad():
    ############################# code changes #####################
    with torch.xpu.amp.autocast(enabled=True, dtype=torch.float16):
    ############################# code changes #####################
        output = model(data)
        print("Out: ", output)

print("Execution finished")
