import streamlit as st
import uuid
import sys
import boto3
import logging
from botocore.exceptions import ClientError

import scripts.kendra_chat_bedrock_claudev2 as bedrock_claudev2

USER_ICON = "images/user-icon.png"
AI_ICON = "images/ai-icon.png"
BEDROCK_ICON = "images/bedrock.png"
MAX_HISTORY_LENGTH = 5
PROVIDER_MAP = {
    'openai': 'Open AI',
    'anthropic': 'Anthropic',
    'flanxl': 'Flan XL',
    'flanxxl': 'Flan XXL',
    'falcon40b': 'Falcon 40B',
    'llama2' : 'Llama 2'
}


#function to generate pre-signed URL
def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

#function to get object size in S3
def get_object_size(bucket_name, object_name, expiration=3600):
    s3_client = boto3.client('s3')

   
    
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_name)

    except ClientError as e:
        logging.error(e)
        return None

    return response['ContentLength']     

#function to read a properties file and create environment variables
def read_properties_file(filename):
    import os
    import re
    with open(filename, 'r') as f:
        for line in f:
            m = re.match(r'^\s*(\w+)\s*=\s*(.*)\s*$', line)
            if m:
                os.environ[m.group(1)] = m.group(2)


# Check if the user ID is already stored in the session state
if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']

# If the user ID is not yet stored in the session state, generate a random UUID
else:
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id


if 'llm_chain' not in st.session_state:
    st.session_state['llm_app'] = bedrock_claudev2
    st.session_state['llm_chain'] = bedrock_claudev2.build_chain()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    
if "chats" not in st.session_state:
    st.session_state.chats = [
        {
            'id': 0,
            'question': '',
            'answer': ''
        }
    ]

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""


st.markdown("""
        <style>
               .block-container {
                    padding-top: 32px;
                    padding-bottom: 32px;
                    padding-left: 0;
                    padding-right: 0;
                }
                .element-container img {
                    background-color: #000000;
                }

                .main-header {
                    font-size: 24px;
                }
        </style>
        """, unsafe_allow_html=True)

def write_logo():
    col1, col2, col3 = st.columns([5, 1, 5])
    with col2:
        st.image(AI_ICON, use_column_width='always') 


def write_top_bar():
    col1, col2, col3 = st.columns([1,10,2])
    with col1:
        st.image(BEDROCK_ICON, use_column_width='always')
    with col2:
        header = f"An AI App powered by Amazon Kendra and Anthropic!"
        st.write(f"<h3 class='main-header'>{header}</h3>", unsafe_allow_html=True)
    with col3:
        clear = st.button("Clear Chat")
    return clear

clear = write_top_bar()

if clear:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    st.session_state["chat_history"] = []

def handle_input():
    input = st.session_state.input
    question_with_id = {
        'question': input,
        'id': len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)

    chat_history = st.session_state["chat_history"]
    if len(chat_history) == MAX_HISTORY_LENGTH:
        chat_history = chat_history[:-1]

    llm_chain = st.session_state['llm_chain']
    chain = st.session_state['llm_app']
    result = chain.run_chain(llm_chain, input, chat_history)
    answer = result['answer']
    chat_history.append((input, answer))
    
    document_list = []
    if 'source_documents' in result:
        for d in result['source_documents']:
            if not (d.metadata['source'] in document_list):
                document_list.append((d.metadata['source']))

    st.session_state.answers.append({
        'answer': result,
        'sources': document_list,
        'id': len(st.session_state.questions)
    })
    st.session_state.input = ""

def write_user_message(md):
    col1, col2 = st.columns([1,12])
    
    with col1:
        st.image(USER_ICON, use_column_width='always')
    with col2:
        st.warning(md['question'])


def render_result(result):
    answer, sources = st.tabs(['Answer', 'Sources'])
    with answer:
        render_answer(result['answer'])
    with sources:
        if 'source_documents' in result:
            render_sources(result['source_documents'])
        else:
            render_sources([])

def render_answer(answer):
    col1, col2 = st.columns([1,12])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        st.info(answer['answer'])

def render_sources(sources):
    col1, col2 = st.columns([1,12])
    with col2:
        with st.expander("Sources"):
            for s in sources:
                s3_bucket_name = s.split('/')[3]
                key = s.split(s3_bucket_name)[-1][1:]
                pre_signed_url = create_presigned_url(s3_bucket_name, key)
                file_size = get_object_size(s3_bucket_name, key)
                st.markdown(f'[{key.replace("Documents/","")}]({pre_signed_url})  ({round(file_size/1048576,2)} MB)')

    
#Each answer will have context of the question asked in order to associate the provided feedback with the respective question
def write_chat_message(md, q):
    chat = st.container()
    with chat:
        render_answer(md['answer'])
        render_sources(md['sources'])
    
        
with st.container():
  for (q, a) in zip(st.session_state.questions, st.session_state.answers):
    write_user_message(q)
    write_chat_message(a, q)

st.markdown('---')
input = st.text_input("You are talking to an AI, ask any question.", key="input", on_change=handle_input)
