import streamlit as st

st.set_page_config(
    page_title="Amazon Bedrock Demos"
)

c1, c2 = st.columns([1, 8])
with c1:
    st.image("./images/bedrock.png", width=70)

with c2:
    st.markdown("<h2 style='text-align: left; line-height: 10pt'>Retrival Augmented Generation (RAG)</h2>", unsafe_allow_html=True)
    st.caption("Q&A application using Claude in Amazon Bedrock, langchain and Amazon Kendra")    

st.markdown(
    """
    **Amazon Bedrock** is a fully managed service that offers a choice of high-performing foundation models (FMs) \
    from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon with a single API, \
    along with a broad set of capabilities you need to build generative AI applications, simplifying development \
    while maintaining privacy and security. 
    
    **Amazon Kendra** is an intelligent search service powered by machine learning (ML). Amazon Kendra reimagines \
    enterprise search for your websites and applications so your employees and customers can find the content \
    they’re looking for, even when it’s scattered across multiple locations and content repositories within your \
    organization.
    
    The Amazon Kendra index in this application was bootstrapped with some documents.
    
    **👈 Select option from the sidebar** to start using the RAG application.
    
    ### Want to learn more?
    Check out:
    - [Amazon Bedrock Website](https://aws.amazon.com/bedrock/)
    - [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)
    - [Amazon Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/apireference/)
    - [Amazon Kendra Website](https://aws.amazon.com/kendra/)
    - [LangChain Bedrock Integration](https://python.langchain.com/docs/integrations/llms/bedrock)
    - [Amazon Kendra Langchain Extensions - Code Samples](https://github.com/aws-samples/amazon-kendra-langchain-extensions)
    """
    )
    
st.sidebar.success("Select an option above ☝️")