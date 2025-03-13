from langchain.schema.runnable import RunnableLambda, RunnableParallel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import LLM
import os
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from peft import PeftModel, LoraConfig
from dotenv import load_dotenv
from elastic_connector import search
from logger import get_logger

logger = get_logger()
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_APIKEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_APIKEY")

llama = "llama-3.3-70b-versatile"
gpt4o = "gpt-4o"
custom = "custom t5-small"
AVAILABLE_MODELS = [custom]

if os.environ["GROQ_API_KEY"]:
    logger.info("GROQ API Key found")
    AVAILABLE_MODELS.append(llama)
else: 
    logger.info("GROQ API Key not found")

if os.environ["OPENAI_API_KEY"]:
    logger.info("OpenAI API Key found")
    AVAILABLE_MODELS.append(gpt4o)
else:
    logger.info("OpenAI API Key not found")

llm_groq = ChatGroq(
    groq_api_key=os.environ["GROQ_API_KEY"],
    model_name=llama, 
    temperature=0.2
)

llm_openai = ChatOpenAI(
    openai_api_key=os.environ["OPENAI_API_KEY"],
    model_name=gpt4o,
    temperature=0.2
)

elasticsearch_runnable = RunnableLambda(lambda query: (
    lambda cleaned_query: {
        "query": cleaned_query,
        "results": search(cleaned_query)
    }
)(
    query if isinstance(query, str) else query.text().replace("\"", "").replace("\n", " ")
))
                                        
logger.info("Loading T5 model")
model_name = "./t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
base_model = T5ForConditionalGeneration.from_pretrained(model_name)
llm_custom = PeftModel.from_pretrained(base_model, './t5-custom', lora_config=LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q", "k", "v", "EncDecAttention.q", "EncDecAttention.k", "EncDecAttention.v", "wi", "wo"],
    lora_dropout=0.05,
    bias="none",
    task_type="SEQ_2_SEQ_LM"
))
logger.info("T5 model loaded")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at optimizing search engine queries. Take the following user query and rewrite it to be more concise, clear, and effective for a search engine like Google. Return ONLY the optimized query. Do not include any additional information or context. If the query is a question, DO NOT answer it, just optimize it. If the query is already optimized, return the original query. If you cannot optimize the query, return the original query."),
    ("user", "{input}")
])


def get_available_models():
    return {"models" : AVAILABLE_MODELS}


def optimize_with_t5(query: str) -> str:
    input_ids = tokenizer(f"optimize {query}", return_tensors="pt").input_ids
    with torch.no_grad():
        outputs = llm_custom.generate(input_ids=input_ids, max_length=128)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

t5_optimize_runnable = RunnableLambda(optimize_with_t5)

def optimize_and_search(query: str, model: str):
    
    if model not in AVAILABLE_MODELS:
        raise ValueError("Invalid model selection")
    
    if model == llama:
        prompt_llm_chain = prompt | llm_groq
    elif model == gpt4o:
        prompt_llm_chain = prompt | llm_openai
    else:
        prompt_llm_chain = t5_optimize_runnable

    parallelChain = RunnableParallel(
        optimized_query_results = prompt_llm_chain | elasticsearch_runnable,
        original_query_results = elasticsearch_runnable
    )
    response = parallelChain.invoke(input=query)
    return response