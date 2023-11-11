import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Amazon Bedrock Demos",
    #layout="wide",
)

c1, c2 = st.columns([1, 8])
with c1:
    image = Image.open("./images/bedrock.png")
    st.image(image, width=100)

with c2:
    st.header("Retrival Augmented Generation (RAG) - Question Answering")
    st.caption("Using Claude in Bedrock, langchain and Kendra")    

st.markdown(
    """
    Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) \
    from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon with a single API, \
    along with a broad set of capabilities you need to build generative AI applications, simplifying development \
    while maintaining privacy and security. With the comprehensive capabilities of Amazon Bedrock, you can easily \
    experiment with a variety of top FMs, privately customize them with your data using techniques such as \
    fine-tuning and retrieval augmented generation (RAG), and create managed agents that execute complex business \
    tasks—from booking travel and processing insurance claims to creating ad campaigns and managing inventory—all \
    without writing any code. Since Amazon Bedrock is serverless, you don't have to manage any infrastructure, and \
    you can securely integrate and deploy generative AI capabilities into your applications using the AWS services \
    you are already familiar with.
    
    Amazon Kendra is an intelligent search service powered by machine learning (ML). Amazon Kendra reimagines \
    enterprise search for your websites and applications so your employees and customers can find the content \
    they’re looking for, even when it’s scattered across multiple locations and content repositories within your \
    organization.
    
    The Kendra index was bootstrapped with some documents.
    
    **👈 Select option from the sidebar** to view document list and start using the RAG application.
    
    ### Want to learn more?
    Check out:
    - [Amazon Bedrock Website](https://aws.amazon.com/bedrock/)
    - [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)
    - [Amazon Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/apireference/)
    - [Amazon Kendra Website](https://aws.amazon.com/kendra/)
    """
    )















































ntrroophixjhhropic