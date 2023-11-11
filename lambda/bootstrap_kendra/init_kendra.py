import json
import boto3
from urllib import request
import os

region_name = boto3.Session().region_name
ssm_client = boto3.client("ssm",region_name=region_name)
genai_s3_bucket = ssm_client.get_parameter(Name="genai_s3_bucket")["Parameter"]["Value"]
genai_kendra_index_id = ssm_client.get_parameter(Name="genai_kendra_index_id")["Parameter"]["Value"]
genai_s3_data_source_id = ssm_client.get_parameter(Name="genai_s3_data_source_id")["Parameter"]["Value"]

seed_documents = ["https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-dg.pdf",
                  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-userguide.pdf",
                  "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-ug.pdf",
                  "https://docs.aws.amazon.com/lambda/latest/dg/lambda-dg.pdf"]

def s3_folder_exists(bucket:str, path:str) -> bool:
    '''
    Folder should exists. 
    Folder could be empty.
    '''
    s3 = boto3.client('s3')
    path = path.rstrip('/') 
    resp = s3.list_objects(Bucket=bucket, Prefix=path, Delimiter='/',MaxKeys=1)
    return 'CommonPrefixes' in resp


def lambda_handler(event, context):
    
    print("Kendra boostrap function started")
    print("S3 Bucket: ", genai_s3_bucket)
    print("Kendra Index_ID: ", genai_kendra_index_id)
    print("Data Source ID: ", genai_s3_data_source_id)
    
    s3 = boto3.client('s3')
    documents_folder = 'Documents'
    metadata_folder = 'Metadata'
    
    if not s3_folder_exists(genai_s3_bucket,documents_folder):
        s3.put_object(Bucket=genai_s3_bucket, Key=(documents_folder+'/'))
    
    if not s3_folder_exists(genai_s3_bucket,metadata_folder):
        s3.put_object(Bucket=genai_s3_bucket, Key=(metadata_folder+'/'))
        
    for document in seed_documents:
        
        file_name = document.split("/")[-1]
        local_file = "/tmp/"+file_name
        request.urlretrieve(document, local_file)
        
        s3.upload_file(local_file, genai_s3_bucket, documents_folder+"/"+file_name)
        os.remove(local_file)
        
    kendra = boto3.client("kendra")
    
    sync_response = kendra.start_data_source_sync_job(
        Id = genai_s3_data_source_id,
        IndexId = genai_kendra_index_id
    )

    print(sync_response)    

    return {
        "statusCode": 200,
        "body": "Kendra bootstrapped...",
        "headers": {
            "Content-Type": "application/json"
        }
    }