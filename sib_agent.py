from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from langchain.chat_models import ChatOpenAI

from langchain.agents import initialize_agent
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils import duck_search, csv_agent
from langchain.memory import ConversationBufferWindowMemory,ReadOnlySharedMemory
from utils import vectara_search
import openai
import streamlit as st

openai.api_key = st.secrets["openai_key"]

memory = ConversationBufferWindowMemory(
        memory_key = "chat_history",
        k = 6,
        return_messages=True,
)
readonlymemory = ReadOnlySharedMemory(memory=memory)
print("Read only memory",readonlymemory)

## GENERAL TOOL
gen_desc = '''Use this tool if assistant has to answer on general banking awareness, personal finance,
current affairs, banking and financial news specially related to INDIAN BANKS'''

class GeneralBankingAwarenessTool(BaseTool):
    name= 'general_banking_awareness_tool'
    description=gen_desc

    def _run(self, query: str) -> str:
        data = duck_search(query)

        if data is None:
            data = "No relevant results in internet"

        return data

    def _arun(self, symbol):
        raise NotImplementedError("This tool does not support async")

general_banking = GeneralBankingAwarenessTool()

# ## TRANSACTION_FETCH_TOOL
# csv_desc = '''use this to fetch user\'s transaction details from the data, csv, dataframe.'''
# class TransactionsTool(BaseTool):

#     name = "Transactions_Data_Retrieval"
#     description = csv_desc

#     def _run(self, query: str) -> str:
#         try:
#             query = query + "today is November 9 2023"
#             data = csv_agent.run(query)
#             return data
#         except:
#             return "Sorry, I am having some issue in Transactions tool"

# transactions = TransactionsTool()

## 
class Products_Services_Information_Tool(BaseTool):
    name = "products_services_information_tool"
    description= 'use this tool to find various information about producs and services in the bank'

    def _run(self, query: str) -> str:
        try:
            data = vectara_search(query)
            return data
        except:
            return "Sorry, I am having some ttrouble in information tool"
        
information = Products_Services_Information_Tool()


## Recommendation Tool
recommend_template = """
You are an AI Banking Assistance chatbot who helps users in recommending the products and services like loans, mutual funds\
and other services.
You will be provided with human input which is a query, user_data which is the last 50 transactions, income, cibil score and\
context which is a the informtion about various schemes, loans, mutual funds, eligibility criteria, requirements etc.
Now, As an smart AI banking Assistant, your task is to suggest users the relevant products, servicesand suggestions.
{chat_history}

Human= {human_input}
Context = {context}
Annual_income = {income}
cibil_score = {cibil_score}
Assistant:

"""
recommend_prompt = PromptTemplate(
    input_variables=["human_input", "context",'income', 'cibil_score', 'chat_history'],
    template=recommend_template
)


recommend_chain = LLMChain(
    llm=ChatOpenAI(temperature=0.2, model = 'gpt-3.5-turbo-16k', streaming=True, max_tokens=12000,openai_api_key=st.secrets["openai_key"] ),
    prompt=recommend_prompt,
    verbose=False,
    memory= readonlymemory
)
recommend_desc = '''use this tool when user ask about products, services like Loans,
Mutual Funds and any other services of the bank. It will take only one input, that is query'''

class Product_Services_Recommendation_Tool(BaseTool):
    name = 'bank_products_and_services_recommendation_tool'
    description=recommend_desc
    def _run(self, query):
        try:
            data = recommend_chain.run(human_input= query, context = vectara_search(query), income = 500000,cibil_score = 700)
            return data
        except:
            return "Sorry, Some issue in fetching Recommendations"
    
recommend = Product_Services_Recommendation_Tool()



## Behaviour Analysis Tool
behaviour_template = """You are Vectara Banking Assitance Chatbot.\n"
    "Your top goal is to improve user's finances.\n"
    "Your personality will adapt to the situation.\n"
    "Keep in mind that your responses should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Make sure your answers are socially unbiased and positive in nature.\n"
    "If a question doesn't make sense or isn't factually coherent, explain why instead of providing incorrect information.\n"
    "Remember, the chat history is provided to assist you in giving relevant advice.\n"
    "The following lines will be the chat history in roles as 'AI:' and 'Human:' you will use those to take relevant information, the last 'Human:' line is the real prompt\n "
    # "You should respond normally without the Ai and Human roles i use, i will use them you shouldn't.\n"
    "The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know."
    "The ai will always use csv format if it sees the keyword csv.\n "
{chat_history}
Human: {human_input}
Chatbot:"""

behaviour_prompt = PromptTemplate(
    input_variables=["human_input", "chat_history"], template=behaviour_template
)

behaviour_chain = LLMChain(
    llm=ChatOpenAI(temperature=0.2, model = 'gpt-3.5-turbo-16k', streaming=True, max_tokens=12000,openai_api_key=st.secrets["openai_key"]),
    prompt=behaviour_prompt,
    verbose=False,
    memory= readonlymemory)

behaviour_desc = 'use this tool when you recieve transactions data of the user like csv or any data of transactions'

class Financial_BehaviourAnalysis(BaseTool):
    name = 'customer_financial_transactions_behaviour_tool'
    description= behaviour_desc
    def _run(self, query):
        try : 
            data = behaviour_chain.run(human_input= query)
            return data
        except:
            return " Sorry, I am having some issue in behaviourial analysis"
        
behaviour = Financial_BehaviourAnalysis()
        
## Agent
sys_msg = '''
You are a smart AI banking Assistance chatbot of Vectara. You help users in their banking, loans, mutual funds, financial news\
etc.
You are accessible to use five tools 'general_banking_awareness_tool', 'customer_financial_transactions_behaviour_tool' 'bank_products_and_services_recommnedation_tool'.
'general_banking_awareness_tool' will be helpful to get any results from internet like financial, banking news. \
'customer_financial_transactions_behaviour_tool' will be helpful to analyse the customer transaction behaviour based on the transactions data you recieve.\
'Transactions_Data_Retrieval' will be useful to retrieve transaction data like last one week spends, last transaction or which transaction user might have done more etc.\
'bank_products_and_services_recommendation_tool' will be useful to recommened products, services of the bank.\
"products_services_information_tool" will be helpful in giving users the informtion and details of loans, mutual funds, etc etc.

You should act wisely while selecting the tools for relevant queries and answer the user\'s queries with truthful and factful information.
'''

tools = [

    Tool(name = 'general_banking_awareness_tool',
         func = general_banking._run,
         description = gen_desc,

    ),

    Tool(name = 'customer_financial_transactions_behaviour_tool',
         func = behaviour._run,
         description =behaviour_desc

    ),

    # Tool(name = 'Transactions_Data_Retrieval',
    #      func = transactions._run,
    #      description =csv_desc,

    # ),

    Tool(name = 'bank_products_and_services_recommendation_tool',
         func = recommend._run,
         description = recommend_desc,

    ),
    Tool(name = "products_services_information_tool",
         func = information._run,
         description = 'use this tool to find various information about producs and services in the bank',

    )
]



llm = ChatOpenAI(
        openai_api_key=st.secrets["openai_key"],
        temperature=0,
        model_name='gpt-4',
        # streaming=True
)

# initialize agent with tools
agent = initialize_agent(
    agent='chat-conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=3,
    early_stopping_method='generate',
    handle_parsing_errors=True,
    memory = memory
)

new_prompt = agent.agent.create_prompt(
    system_message=sys_msg,
    tools=tools

)

agent.agent.llm_chain.prompt = new_prompt
