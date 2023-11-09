from langchain.vectorstores import vectara
from langchain.embeddings import OpenAIEmbeddings
import apis
import os

os.environ["VECTARA_CUSTOMER_ID"] = apis.VECTARA_CUSTOMER_ID
os.environ["VECTARA_CORPUS_ID"]=apis.VECTARA_CORPUS_ID
os.environ["VECTARA_API_KEY"]= apis.VECTARA_API_KEY

vectara = vectara.Vectara(
    vectara_customer_id=apis.VECTARA_CUSTOMER_ID, 
    vectara_corpus_id=apis.VECTARA_CORPUS_ID, 
    vectara_api_key=apis.VECTARA_API_KEY
)

vectara.add_files(["datasets\loan.txt", "datasets\service_charges.txt"])

results = vectara.similarity_search("Education Loan")

print(results)
