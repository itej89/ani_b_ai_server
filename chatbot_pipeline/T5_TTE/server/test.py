from transformers import AutoTokenizer, AutoModelWithLMHead

tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-emotion")

model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-emotion", device_map="auto", load_in_8bit=True)

def get_emotion(text):
  input_ids = tokenizer(text + '</s>', return_tensors='pt').to("cuda")

  output = model.generate(**input_ids,
               max_length=2)
  
  dec = [tokenizer.decode(ids) for ids in output]
  label = dec[0]
  return label
  
print(get_emotion("i feel as if i havent blogged in ages are at least truly blogged i am doing an update cute"))
 
print(get_emotion("i have a feeling i kinda lost my best friend"))

