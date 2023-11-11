import streamlit as st
import boto3
import os
import time

region_name = boto3.Session().region_name

document_dir = "./data"

def get_parameter(name):
    """
    This function retrieves a specific value from Systems Manager"s ParameterStore.
    """     
    ssm_client = boto3.client("ssm",region_name=region_name)
    response = ssm_client.get_parameter(Name=name)
    value = response["Parameter"]["Value"]
    
    return value

st.set_page_config(
    page_title="Amazon Bedrock Demos"
)

c1, c2 = st.columns([1, 8])
with c1:
    st.image("./images/bedrock.png", width=70)

with c2:
    st.markdown("<h2 style='text-align: left; line-height: 10pt'>Add Documents</h2>", unsafe_allow_html=True)
    st.caption("Upload your own documents to the knowledge base")    

uploaded_files = st.file_uploader(
                                    "Upload files (Max 50MB per file)", 
                                    type=[
                                        "pdf",
                                        "docx",
                                        "doc",
                                        "xlsx",
                                        "xls",
                                        "pptx",
                                        "ppt",
                                        "csv",
                                        "txt"],
                                    accept_multiple_files=True
                                )

if st.button("Upload Files", key=uploaded_files):

    if len(uploaded_files) == 0:
        st.error("Please select local files to upload")
        
    else:
        with st.spinner("Uploading your files to knowledge base, please wait..."):
            
            start_time = time.time()
            
            s3 = boto3.client('s3')
            s3_documents_folder = 'Documents'
            s3_bucket_name = get_parameter("genai_s3_bucket")
            genai_kendra_index_id = get_parameter("genai_kendra_index_id")
            genai_s3_data_source_id = get_parameter("genai_s3_data_source_id")
            
            if not os.path.exists(document_dir):
                os.makedirs(document_dir)
                
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                with open(os.path.join("data",file_name),"wb") as f:
                    f.write(uploaded_file.getbuffer())        
            
                local_file = document_dir+"/"+file_name
                s3.upload_file(local_file, s3_bucket_name, s3_documents_folder+"/"+file_name)
                os.remove(local_file)            

            kendra = boto3.client("kendra")
            
            sync_response = kendra.start_data_source_sync_job(
                Id = genai_s3_data_source_id,
                IndexId = genai_kendra_index_id
            )
                
            execution_time = round(time.time() - start_time, 2)
            st.success("The above valid files were uploaded to S3. Please give it some time for Kendra to index them.")
            st.caption(f"Execution time: {execution_time} seconds")