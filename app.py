import streamlit as st
import pandas as pd
import tempfile
    

##############################################################################################################    

from sib_agent import agent
from langchain.callbacks import StreamlitCallbackHandler
from utils import enable_chat_history, display_msg

# Initialize the behaviour analysis object
# Make sure that Financial_BehaviourAnalysis has a __call__ method if you want to use it as behaviour(query, context)

# # Streamlit interface
# st.title("SIB Mate")
# st.caption(':blue_heart: Your Personalised Banking Assistant')  # Corrected the syntax for emoji

# # Text input
# query = st.text_input("Ask your Query")

# # File uploader for CSV files
# uploaded_csv = st.file_uploader("Upload your balance sheet (csv):", type=["csv"])

# # Button to process the query
# if st.button("Ask SIB Mate"):
#     if uploaded_csv is not None:
#         # Read the uploaded CSV file into a DataFrame
#         df = pd.read_csv(uploaded_csv)
#         last_50 = df.tail(50)  # Extract the last 50 rows

#         # Convert the last 50 rows to a string representation
#         query = last_50.to_string(index=False, header=False) +query
#         results = behaviour(query)  # Make sure behaviour can be called like this
#         st.write(results)
#     else:
#         # Directly call the agent's run function with the query
#         results = agent.run(input=query)
#         st.write(results)


###############################################################################################
st.header('LabLab Langchain RAG Vectara Mate')
st.caption(':blue[_A Personalized Banking Assistant_]')

@enable_chat_history
def main():
        user_query = st.chat_input(placeholder="Ask your Query")
        uploaded_csv = st.file_uploader("Upload your balance sheet (csv):", type=["csv"])
        if user_query:
            if uploaded_csv is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                    tmp_file.write(uploaded_csv.getvalue())
                    temp_file_path = tmp_file.name

            # Now you can use the file path
                df = pd.read_csv(temp_file_path)
                last_50 = df.tail(50)  # Extract the last 50 rows
                display_msg(user_query, 'user')
            # Convert the last 50 rows to a string representation
                query = user_query + '\n'+ last_50.to_string(index=False, header=False)
            # Make sure behaviour can be called like this
                with st.chat_message("SIB Mate"):
                    st_cb = StreamlitCallbackHandler(st.container())
                    response = agent.run(query,callbacks=[st_cb])
                    st.session_state.messages.append({"role": "SIBMate", "content": response})
                    st.write(response)

            else:
                display_msg(user_query, 'user')
                with st.chat_message("SIB Mate"):
                    st_cb = StreamlitCallbackHandler(st.container())
                    response = agent.run(user_query, callbacks=[st_cb])
                    st.session_state.messages.append({"role": "SIBMate", "content": response})
                    st.write(response)


if __name__ == "__main__":
    main()
