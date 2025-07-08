import torch
from transformers import pipeline

'''
Notes:
The example below is single label sequence classification with binary sentiment (positive / negative)
Multi label classification allows for multiple labels per example, each predicted independently
Zero shot classification allows you to supply any set of candidate labels without pretraining
'''
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
#print(result)


# Multi class classification for emotions
# this model is multi class and uses the softmax function, meaning each input receives one emotion as the output (the emotion with the highest probability)
# labels "compete" with each other in the probability distribution, which sums to 1. enabled top_k=None to see the full distribution.
emotion_clf = pipeline(
    "text-classification",
    model="bhadresh-savani/distilbert-base-uncased-emotion",
    top_k=None,
    function_to_apply="softmax"
)
string1 = "The museum looks so interesting, I can't wait for tomorrow's field trip!"
#print(emotion_clf(string1))
# Output:[[{'label': 'joy', 'score': 0.9912728667259216}, ...]]

#story = "A Lion lay asleep in the forest, his great head resting on his paws. A timid little Mouse came upon him unexpectedly, and in her fright and haste to get away, ran across the Lion’s nose. Roused from his nap, the Lion laid his huge paw angrily on the tiny creature to kill her. ‘Spare me!’ begged the poor Mouse. ‘Please let me go and some day I will surely repay you.’ The Lion was much amused to think that a Mouse could ever help him. But he was generous and finally let the Mouse go. Some days later, while stalking his prey in the forest, the Lion was caught in the toils of a hunter’s net. Unable to free himself, he filled the forest with his angry roaring. The Mouse knew the voice and quickly found the Lion struggling in the net. Running to one of the great ropes that bound him, she gnawed it until it parted, and soon the Lion was free. ‘You laughed when I said I would repay you,’ said the Mouse. ‘Now you see that even a Mouse can help a Lion.’"
#print(emotion_clf(story))


# Multi label classification with sigmoid - outputs are independent of each other, so multiple labels can apply at once
# this model is trained specifically to evaluate incivility-related input
multi_label_clf = pipeline(
    "text-classification",
    model="LinaSaba/distilbert-base-task-multi-label-classification",
    top_k=None,
    function_to_apply="sigmoid"
)
string1 = "I can't believe how clueless you are. You're a complete waste of space."
string2 = "Listen, I never sold your idea to the competition. In fact, I personally presented it to the board last month and got a standing ovation. If anyone’s stealing concepts, it must be your own staff. Not me."
print(multi_label_clf(string2))


# Zero shot classification


# Keyword extraction
