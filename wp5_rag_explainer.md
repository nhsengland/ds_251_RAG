# RAG Explainer - what it is, where it's going, and what to be aware of

## Recap on LLMs (in case you've not heard of ChatGTP)

>Summary:
> - Large Language Models (LLMs) are Artificial Intelligence (AI) tools which provide "natural language" responses to submitted questions
> - They have exploded popularity in the last year.  Famous examples are ChatGTP and Copilot
> - They work by looking at the submitted "prompt" and predicting the next character in the sequence - character by character until they decide to stop.
> - This works using a complex architecture of neural networks, trained on large amounts of text data. 
> - You can use "closed-source" LLMs hosted by large organisations - this is easy, and reasonably cheap, but you have less control and isn't suitable for sensitive applications
> - You can host your own open-source models - this requires more infrastructure and overall cost - however you have complete control and can further train the model, run it your our own hardware etc.


In the last year Large Language Models have exploded in popularity - these are **Artificial Intelligence tools**, which can seemingly answer any question you submit to them - and even better, **you can converse with them using normal everyday language**. 

LLMs are trained on large bodies of data, learning the relationships between words and those that come before and after them - the end result is a model which when you submit a text string to it, it will predict the "tokens" (basically words) that come next, one at a time, until the end result is whole sentences and paragraphs. It's important to remember that usually, under-the-hood, all it is doing is predicting what character comes next.

### Closed-source vs Open-source models

The state of the art models are huge, and require vast amounts of compute, manpower (and hence time and money) to train, with the latest models having 100s of billions (or even trillions) of parameters, having consumed potentially millions of documents with costs in the regions of 100's millions of dollars. These models are also often closed source, meaning that the company has not revealed exactly how the model was trained, or released the files for the model itself.

However, it's possible to get decent performance with far less: many "open source" models, such as those from Mistral performs well with 70B (70 Billion) parameters and took *only* $500,000 to train. The cost to train models with acceptable levels of performance will only decrease as techniques improve and become more efficient.

70B parameters is still very large, requiring special hardware to run - however, improvements in techniques are leading to even smaller models ~7B which can run on *normal* laptops, though the quality of the outputs of these models will probably be worse than the larger models. However, a huge benefit of open source is that you can adapt the model to your needs e.g. you can do further training (fine-tuning).

It's important to to note that the closed-source models often run on servers held elsewhere - you submit your question to them, and it returns the answers. This means that's not suitable for many more sensitive use-cases (at least without a close partnership with the organisation running the model). Open source models by their nature can be run on hardware we own, and so can be used for any use-case.

### Cost to run

State of the art (closed-source models) cost something in the region of ~$10 per million "tokens" (similar to words) - so ~ 240,000 words/£.

On the other hand, paying to run a 70B open source model would need ~4 A100 GPUs, costing ~ $4 per hour, outputting ~380 tokens per second, meaning the overall cost is approximately 114,00 words/£ ([see this blog](https://hamel.dev/notes/llm/inference/big_inference.html)).

In this we can see that the models hosted by large companies are quite competitive in price, however you give up on control.


## Retrieval Augmented Generation (RAG): making LLMs be more truthful
>Summary:
> - LLMs can return untruthful, misleading or wrong responses (called hallucinating)
> - "Fine Tuning" the LLM on more data in this area is expensive, and requires large amounts of data
> - Submitting relevant documents for context to the LLM alongside your question can improve performance without needing to fine-tune
> - **RAG** automates this process:
>    - **Retrieval**: Your question is put through a model which then brings back "relevant" documents from a database
>    - **Augmented**: Your question is augmented by adding the relevant segments of those documents as context to make a prompt
>    - **Generation**: The augmented "prompt" is submitted to the LLM which generates an improved response
> - RAG makes adding to your LLMs knowledge base easy - you just load more documents into the database (for fine-tuning this is expensive)
> - Removing knowledge from a fine-tuned LLM is still incredible difficult - but for RAG you simply remove the document from the database
> - Easier to get "references" for any statement - the LLM can point at the source document
> - Easier to "explain" the outputs of the model
> - RAG is best for improving AI's grasp of factual content - it's less effective teaching "styles" of writing.

As explained above, LLMs work on predicting the next word step-by-step - if the model hasn't been trained on enough material, or material specific enough to what you're asking, the output might not make any sense, or perhaps worse, it might make sense but just be incorrect - this is called hallucination.

One way around this is to "train" the model on more material (called "fine-tuning"), however this is not straightforward, requiring access to the model itself (e.g. using an open source model), a large amount of data (probably hundreds of documents, rather than one or two), and considerable compute to run the model and train it.

Interestingly, LLMs can be influenced by what you tell them - so If you were to write a brief paragraph about something the LLM knew nothing about, then ask it a question on that thing and submit all of that - it will be more likely to give a truthful answer. This is the basis of "Retrieval Augmented Generation" (RAG) - rather than "fine-tuning" the model, you simply provide the context it needs in the prompt that you submit to improve the answer - this is easier to do that expensive fine tuning, can be used on closed source models and doesn't need as many documents (even one would be enough).

A full RAG pipeline will have a database in which documents are stored, with an "embedding" of those document along with any relevant metadata. An embedding is where a model is used to render the document down into a vector which describes the content (SentenceTransformer is an example of an open source embedding model).

- **RAG** automates this process:
    - **Retrieval**: Your question is embedded and submitted to the database which returns "similar" documents (based on how close their embeddings are)
    - **Augmented**: Your question is augmented by adding the relevant segments of those documents (and their metadata) as context to make a prompt
    - **Generation**: The augmented "prompt" is submitted to the LLM which generates an improved response

In the augmentation step we can add relevant metadata from the documents to the prompt - this could include a document ID number which makes it very easy for the LLM to provide "references" for any of it's statements - something which conventional LLMs find harder to do. For this reason it's also easier to "explain" how the AI arrived at its answer, as we can see some of its "workings" (the context in the prompt), which isn't possible with a more conventional LLM.

The cost of running these additional components is comparatively low - the RAG database and the embedding models can be run on a normal laptop, though in a production system they would need to be scaled up.

### Updating what your model knows (and making it forget)

With RAG, "teaching" the AI new things is as simple as adding more documents to the database - this is in contrast to a fine-tuned model where further fine tuning is required, with all the expense and infrastructure this needs. 

Getting an fine-tuned AI to "forget" things is currently not straightforward and it's an ongoing area of study - in comparison, it's trivial for a RAG pipeline - you just remove the document from the database. The model will retain no memories of it.

It's important to stress there are limitations to what an LLM can be taught by RAG - it's best for factual content it can reference. If you want to teach the LLM a "style", e.g. to write more succinctly, or more professionally, etc., this would be harder to achieve by RAG (you would need to put a lot of examples of succinct writing in the prompt) - conventional "fine-tuning" is the better choice here.


## Evaluating Peformance: how do we know if LLMs are any good?
>Summary:
> - This is still "hard" to do, and there is not "best way" currently agreed
> - Industry standard is for humans to judge the quality of the output - however this is laborious and time consuming
> - LLM-as-a-judge - having an AI judge how good the outputs are based on evaluation criteria. 
>    - This can be based criteria which do not need a "correct answer", e.g.constitutional principals (harmfulness, ethical, illegal, etc.), correct grammar, relevance (to the question), conciseness...
>    - There are also criteria which need a reference answer (accuracy)
> - You can also judge if the the RAG pipeline retrieved the correct sources
> - Benchmarks scores and Natural Language Processing (NLP) metrics can be useful for comparing models but don't guarantee performance on a business task

## The stuff they don't tell you - complications and downsides of RAG
>Summary:
> - Adding the documents to the database can be time consuming - moving the work upfront
> - Retrieving the right documents isn't trivial - and will lead to poorer outputs if they're wrong
> - Retrieval is fast for small amounts of documents, but for huge datasets, such as systems logs, needs careful thought to ensure it runs in an acceptable time.
> - RAG potentially involves more calls to the LLM, which can make it slower at answering questions than a fine-tuned model
> - Won't necessarily addresses biases in the model, and may add new biases from the source documents

## Ways of enhancing RAG further
>Summary:
> - RAG can be enhanced to improve the retrieval of documents, augmentation of prompts and generation of responses.
> - Enhancements to RAG often either make it faster and cheaper to run, or aim to improve evaluation performance (making it more expensive / slower to run).
> - Hence there is a trade-off - the business problem should lead what type of RAG pipeline is built 

## Beyond RAG
>Summary:
> - RAG is increasingly viewed as part of the wider ecosystem of tools that AI "Agents" can use to enhance their outputs
> - For example, When you submit a question, the AI should be able to choose whether it queries a database, retrieves semantically similar documents or whether it simply does a web search.
> - It's important AI systems are built which can use the right tool for the job (which may not always be RAG).