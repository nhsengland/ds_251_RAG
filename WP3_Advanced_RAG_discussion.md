# Advanced RAG Discussion


## Introduction

Large language models have two main sources of information. 

* Parametric knowledge: This is all the information that the model was trained on. LLMs are generally good at using this knowledge to synthesise language, but bad at retrieving specific facts from within it. 

* Context window: This is where you write your prompt. In the case of chat based LLMs like Chat GPT, your previous conversation is also considered in the context window. LLMs are generally much better at retrieving facts that are given in the context window. 

```mermaid
    graph LR;
    A[Query / Context Window] -->  H{LLM Generation};
    AA[(Parametric Knowledge)] --> H
    H --> I[Answer];

```



## Basic RAG

RAG introduces a third source of information, a database. 
A RAG pipeline retrieves the most relevant information to the query from the database, then puts it into the context window. 

There are advantages to storing and retrieving knowledge in this way. 

* Easy to keep up to date (Parametric knowledge is only as new as the most recent training)
* Easy to delete (forgetting parametric knowledge is hard)
* LLMs can quote sources for their generated content
* LLMs can say "I don't know" when it can't source a relevant fact to form its answer. 

```mermaid
    graph LR;
    AA[(Vectorised Database)] --> B;
    A[Query] --> B{Retrieval <br> with semantic search};
    B -->C[Retrieved Content]--> E;
    A-->E

    E{Augmentation <br> Prompt Stuffing} -->F[Augmented Prompt / Context Window]--> H{LLM Generation};
    AB[(Parametric Knowledge)] --> H
    H --> I[Answer];

```
Generally in basic RAG retrieval is done using semantic search. 
The database and the query are vectorised using a semantic embedder (encoding the meaning of the sentence). 


Semantic search for RAG involves finding relevant content by understanding the context of a query, not just specific words. It retrieves information based on meaning, making search results more accurate and insightful for RAG applications.




## Advanced RAG

The basic idea of RAG has been expanded on, incorporating numerous techniques to improve the generated output. 

Many techniques improve the retrieval element specifically, and lots of these ideas are not new. Optimising search results is a well established and documented problem. 

### Retrieval

Chunk Optimisation:



There are situations where keyword or numerical filters would be more effective than semantic search. 
When you use an online shop, you'll often use natural language to describe the item you want, but then use filters to narrow down the search space. 
Self Querying retrieval uses and LLM to extract keywords from the query that can be used to filter down the database. 

Self Querying retrieval: 


```mermaid
graph TD;
A[Query <br> Find me a wine from New Zealand that goes well with red meats. It should be older than 1970s] --> B[New Zealand]
A--> C[<1970]
A--> D[goes well with red meats]
C-->E[SELECT * FROM products
WHERE location = 'New Zealand' 
AND year < 1970]

B-->E
E--Filter-->F[(Database)]
D--Semantic Search-->F

F--> G[Retrieved content]

```

HyDE

Semantic search compares a query against the documents in the database.  
But sometimes the documents being searched through are in a very different form to the queries asked.

Hypothetical Document Embeddings or HyDE attempts to bridge this gap by doing a document to document semantic comparison.  
An LLM uses the query to produce a hypothetical document in the same form that they are found in the database.  
This hypothetical document is then used as the starting point for the semantic search.

```mermaid
graph TD;
A[query]-->B[LLM generator]
B-->C[Hypothetical document]
C--Semantic Search-->E[(Database)]
E-->G[Retrieved content]
```
This technique requires an LLM to produce a potential document, from which the answer to the question could be drawn, and then use that as a semantic tool.
Other techniques get the LLM to try and answer the question without context, and then use that answer to improve the generation or retrieval. 

Retrieval can also be improved through fine tuning of the embedder models. 
A specialised embedder, fine tuned on the kind of documents or questions expected in the task, can produce a much more precise vector space and improve retrieval results. 


### Augmentation
Once the materials have been retrieved, the original query can be augmented with extra context. 
LLMs perform quite differently depending on how the prompt is worded. Increasingly the task of prompt engineering is being automated and tackled by LLMs themselves. 

Re-Rank
We know that LLMs are better at retrieving facts from context. More specifically, they have been found to be better at retrieving facts from the start and end of context. 
One of the simpler re-rank ideas is to place the most relevant retrieved materials at the start and end of the augmented prompt. 


### Generation

Getting the generation right is the ultimate goal of the RAG pipeline, and all other parts can be evaluated by the performance of the generated content. 
Once the query has been augmented, an LLM will attempt to generate an answer. This is another area where fine tuning can be utilised. 

Often RAG is pitted against fine tuning, but this is with respect to the models ability to retrieve facts, rather than the abilty to generate good answers. 
Both techniques can be used together, with a vectorised database being the main, updatable knowledge store, and the generator being fine tuned for the task. The fine tuning is then not so much that the model will be tuned on the right knowledge, but that it will be familiar with the right form of language expected in the output. 


### Modular RAG
The modular RAG paradigm is slowly becoming the norm in the RAG domain due to its versatility and flexibility, allowing: 
- the adaption of modules within the RAG process to suit your specific problem, 
- for a serialized pipeline or an end-to-end training approach across multiple modules.

## The Future
Looking forward there are a few ways that RAG could go. 
With that comes options for where our focus is as a project looking into RAG, we have a particular interest in models being open and runnable on small compute. 

### Contextual Language Models
Recently the original writers of the RAG paper released an approach they are calling RAG 2.0, or Contextual Language Models.
The basic idea being a move away from off the shelf embedders and frozen LLMS to a fully tuneable, fully contextualised pipeline. 
https://contextual.ai/introducing-rag2/

### Agents
Some of the language around modular RAG and self tuning systems starts to sound like Agents. RAG's specialism is in grounding generated answers in the truth, and the incorporation of the vectorised data store, but these concepts are absorbed into Agent based LLMs without issue. 

### Massive context windows 
LLMs are improving, and one of the measures that is increasing rapidly is the size of the context window. 
RAG concepts can still play a part in this in two ways, 
1. No matter the size of the context window, retrieval is still important for efficiency and quality of output. 
2. How the huge context window is used is an augmentation task. 

### Making the best Open model
Open source models are improving but still lag behind the best corporate LLMs. 
There would be significant utility behind an Open model + RAG solution which could be production ready. 

### Evaluation
No matter which direction LLMs or RAG pipelines go, getting evaluation right remains crucial. 
But we should be careful not to assume that one evaluation metric always transfers to other usecases. 

