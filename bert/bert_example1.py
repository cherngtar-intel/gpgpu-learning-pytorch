#Similarity: input a sentence and output the most simlar sentence
from transformers import BertTokenizer, BertModel
import torch
import torch.nn.functional as F
############# code changes ###############
import intel_extension_for_pytorch as ipex
############# code changes ###############


# Load pre-trained BERT model and tokenizer
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

model.eval()

# Input sentence
input_sentence = "Hello, how are you?"
#input_sentence = "Thank you, good bye!"
#input_sentence = "Let's meet again some other time!"
#input_sentence = "Good morning"
#input_sentence = "It's raining now!"

# Tokenize the input sentence
inputs = tokenizer(input_sentence, return_tensors='pt')

#################### code changes ################
inputs = inputs.to("xpu")
model = model.to("xpu")
model = ipex.optimize(model, dtype=torch.float16)
#################### code changes ################

# Get the outputs from the model
with torch.no_grad():
    ########################### code changes ########################
    with torch.xpu.amp.autocast(enabled=True, dtype=torch.float16):
    ########################### code changes ########################
        outputs = model(**inputs)

# Get the embeddings for the input sentence (use the [CLS] token)
input_embeddings = outputs.last_hidden_state[:, 0, :]

# Define some predefined sentences to compare with
predefined_sentences = [
    "Hi, what's up?",
    "Goodbye, see you later.",
    "Hello, how are you doing?",
    "The weather is nice today."
]

# Tokenize and get embeddings for the predefined sentences
predefined_embeddings = []
for sentence in predefined_sentences:
    inputs = tokenizer(sentence, return_tensors='pt')
    #################### code changes ################
    inputs = inputs.to("xpu")
    #################### code changes ################
    with torch.no_grad():
        ########################### code changes ########################
        with torch.xpu.amp.autocast(enabled=True, dtype=torch.float16):
        ########################### code changes ########################
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
        predefined_embeddings.append(embeddings)

# Compute cosine similarities
similarities = []
for embeddings in predefined_embeddings:
    similarity = F.cosine_similarity(input_embeddings, embeddings)
    similarities.append(similarity.item())

# Find the most similar sentence
most_similar_index = similarities.index(max(similarities))
most_similar_sentence = predefined_sentences[most_similar_index]

# Output the most similar sentence
print(f"Input sentence: {input_sentence}")
print(f"Most similar sentence: {most_similar_sentence}")