# RAG Explainer - what it is, where it's going, and what to be aware of

## Recap on LLMs (in case you've not heard of ChatGTP)

>Summary:
> - Large Language Models (LLMs) are Artificial Intelligence (AI) tools which provide "natural language" responses to submitted questions
> - They have exploded popularity in the last year.  Famous examples are ChatGTP and Copilot
> - They work by looking at the submitted "prompt" and predicting the next character in the sequence - character by character until they decide to stop.
> - This works using a complex architecture of neural networks, trained on large amounts of text data. 


In the last year Large Language Models have exploded in popularity - these are **Artificial Intelligence tools**, which can seemingly answer any question you submit to them - and even better, **you can converse with them using normal everyday language**. 

## Retrieval Augmented Generation (RAG): making LLMs be more truthful
>Summary:
> - LLMs can return untruthful, misleading or wrong responses (called hallucinating)
> - "Fine Tuning" the LLM on more data in this area is expensive
> - Submitting relevant documents for context to the LLM alongside your question can improve performance without needing to fine-tune
> - **RAG** automates this process:
>    - **Retrieval**: Your question is put through a model which then brings back "relevant" documents
>    - **Augmented**: Your question is augmented by adding the relevant segments of those documents as context to make a prompt
>    - **Generation**: The augmented "prompt" is submitted to the LLM which generates an improved response
> - RAG makes adding to your LLMs knowledge base easy - you just load more documents into the database (for fine-tuning this is expensive)
> - Removing knowledge from a fine-tuned LLM is still incredible difficult - but for RAG you simply remove the document from the database
> - Easier to get "references" for any statement - the LLM can point at the source document
> - Easier to "explain" the outputs of the model

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