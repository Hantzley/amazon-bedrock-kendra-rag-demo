import streamlit as st
import boto3
import logging
from botocore.exceptions import ClientError
import time

region_name = boto3.Session().region_name


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
    st.markdown("<h2 style='text-align: left; line-height: 10pt'>Documents List</h2>", unsafe_allow_html=True)
    st.caption("Documents uploaded to the knowledge base")    

st.info("If you recently uploaded new documents, please wait for a few minutes the Kendra to index them.")

with st.spinner("Getting file list from knowledge base, please wait..."):
    
    start_time = time.time()
    
    s3_bucket_name = get_parameter("genai_s3_bucket")
    
    s3_client = boto3.client('s3')
    
    response = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix="Documents")
    
    files = response.get("Contents")
    
    if len(files)>1:
    
        for file in files:
            if file['Size'] > 0:
                url = create_presigned_url(s3_bucket_name, file["Key"])
                st.markdown(f'[{file["Key"].replace("Documents/","")}]({url})  ({round(file["Size"]/1048576,2)} MB)')
        
        execution_time = round(time.time() - start_time, 2)
        st.success(str(len(files)-1)+" files found.")
        st.caption(f"Execution time: {execution_time} seconds")                      
    else:
        st.warning("No files found in knowledge base.")