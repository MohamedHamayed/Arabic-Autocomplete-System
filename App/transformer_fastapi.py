#!/usr/bin/env python
# coding: utf-8

# In[1]:
# from typing import List

from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI

from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware



# In[2]:


from joblib import load
import torch
import pickle


# In[3]:


model = load('model_transformer.joblib')
tokenizer = load('tokenizer_transformer.joblib')
arabert_prep = load('arabert_prep_transformer.joblib')


# In[4]:


def predict(text,arabert_prep,tokenizer,model,k=5):
    text = arabert_prep.preprocess(text)
    indexed_tokens = tokenizer.encode(text)

    # Convert indexed tokens in a PyTorch tensor
    tokens_tensor = torch.tensor([indexed_tokens])

    # Set the model in evaluation mode to deactivate the DropOut modules
    model.eval()

    # If you have a GPU, put everything on cuda
    # tokens_tensor = tokens_tensor.to('cuda')
    # model.to('cuda')

    # Predict all tokens
    with torch.no_grad():
        outputs = model(tokens_tensor)
        soft_max = torch.nn.Softmax(dim=0)  
        probs = soft_max(outputs[0][0, -1, :])
        sorted, indices = torch.topk(probs, k)
        preds = [index.item() for index in indices]

    predicted_words = tokenizer.decode(preds).split()

    # Return the predicted word
    return predicted_words


# In[5]:

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputText(BaseModel):
    text : str
    candidate : int = None

@app.get("/")
def root():
    return {"Hello" : 'User'}

@app.post("/predict/")
def predict_next(input:InputText):
   
    print(input.text)
    prefix = input.text
   
    if input.candidate :
        num_candidate = input.candidate
        candidates = predict(prefix,arabert_prep,tokenizer,model,num_candidate)
    else:
        candidates = predict(prefix,arabert_prep,tokenizer,model)
        
    return {"output" : candidates}


if __name__ =="__main__":
    uvicorn.run(app , host = "127.0.0.1" , port = 8000)




