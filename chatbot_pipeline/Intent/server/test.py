from transformers import pipeline

pipe = pipeline(model="facebook/bart-large-mnli")

sentence = "create a map of the room"
labels = ["explore", "go", "back-forth"]

result = pipe(sentence, candidate_labels=labels)
scores = result["scores"]
argmax = max(range(len(scores)), key=lambda x : scores[x])

print(scores)
print(result["labels"][argmax])

# from transformers import pipeline

# pipe = pipeline(model="facebook/bart-large-mnli")
# result = pipe("go there and come back",
#     candidate_labels=["explore", "go", "back-forth"],
# )

# print(result)


