import glob
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.llms import Anthropic
#from langchain.chat_models import ChatAnthropic
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.schema.document import Document
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage


from tqdm import tqdm

import torch


def initialise_anthropic():
    return Anthropic(anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),temperature = 0)


SYSTEM_PROMPT = PromptTemplate.from_template("""You are a helpful assistant that helps people with their questions. You are not a replacement for human judgement, but you can help humans\
make more informed decisions. If you are asked a question you cannot answer based on your following instructions, you should say so.\
Be concise and professional in your responses.\n\n """)

# we can just add prompts together: just add a string to an existing prompt
STUFF_DOCUMENTS_PROMPT = SYSTEM_PROMPT+"""Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES"). \
If you don't know the answer, just say that you don't know. Don't try to make up an answer. \
ALWAYS return a "SOURCES" part in your answer.

Example 1: "**RAP** is to be the foundation of analyst training. SOURCES: (goldacre_review.txt)"
Example 2: "Open source code is a good idea because:
* it's cheap (goldacre_review.txt)
* it's easy for people to access and use (open_source_guidlines.txt)
* it's easy to share (goldacre_review.txt)

SOURCES: (goldacre_review.txt, open_source_guidlines.txt)"

QUESTION: {question}
=========
{docs}
=========
FINAL ANSWER:"""

INJECT_METADATA_PROMPT = PromptTemplate.from_template("{file_path}:\n{page_content}")


class RagPipeline:
    def __init__(self, EMBEDDING_MODEL, PERSIST_DIRECTORY, stuff_documents_prompt=STUFF_DOCUMENTS_PROMPT, inject_metadata_prompt=INJECT_METADATA_PROMPT, device=None):
        
        if device is None:
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.llm = initialise_anthropic()
        self.embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs = {'device': self.device})
        self.vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=self.embedding)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 10})

        self.stuff_docs_sources_chain = load_qa_with_sources_chain(
            self.llm,
            chain_type="stuff",
            prompt=stuff_documents_prompt,
            document_prompt=inject_metadata_prompt,
            document_variable_name="docs",
            document_separator="\n\n",
            verbose=True,
        )


    def load_documents(self):
        for text_file_path in tqdm(
            glob.glob("docs/*.txt", recursive=True), desc="Processing Files", position=0
        ):
            with open(text_file_path, "r", encoding="utf-8") as text_file:
                print("loading: ", text_file_path)
                doc = Document(
                    page_content=text_file.read(), metadata={"file_path": text_file_path}
                )
                texts = self.text_splitter.split_documents([doc])
                self.vectorstore.add_documents(documents=texts)


    def answer_question(self, question, rag=True, hyde=False):

        if rag:
            if hyde:
                hypothetical_doc = self.llm(question)
                docs = self.retriever.get_relevant_documents(hypothetical_doc)
            else:
                docs = self.retriever.get_relevant_documents(question)

            results = self.stuff_docs_sources_chain({"question": question,
                          "input_documents": docs,
                          }
                        )
            self.results = results
            return results['output_text']
        
        else:
            return self.llm(question)