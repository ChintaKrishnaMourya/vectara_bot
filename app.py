import streamlit as st
import pandas as pd
import tempfile
    

##############################################################################################################    

from sib_agent import agent
from langchain.callbacks import StreamlitCallbackHandler
from utils import enable_chat_history, display_msg



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
