import torch
from transformers import pipeline

classifier = pipeline(
    task="text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    torch_dtype=torch.float16,
    device=0
)

string1 = "giraffe marble tunnel spark velvet breeze pencil canyon anchor fortune ladder tumble"
# Output: [{'label': 'NEGATIVE', 'score': 0.933552086353302}]
string2 = "I love using Hugging Face Transformers!"
# Output: [{'label': 'POSITIVE', 'score': 0.9971272349357605}]
string3 = "I really hate you."
# Output: [{'label': 'NEGATIVE', 'score': 0.9991735816001892}]
result = classifier(string3)
print(result)

'''
Notes:
The above example is single label sequence classification with binary sentiment (positive / negative)
Multi label classification allows for multiple labels per example, each predicted independently
Zero shot classification allows you to supply any set of candidate labels without pretraining
'''
