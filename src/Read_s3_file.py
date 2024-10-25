# load aws credentials
import pandas as pd
import boto3
from io import StringIO
from io import BytesIO

key = pd.read_csv('F:/InternshipWRI/cities-data-user_accessKeys.csv')
access_key = key['Access key ID'].iloc[0]
secret_key = key['Secret access key'].iloc[0]

# s3_client = boto3.client(
#     's3',
#     aws_access_key_id=access_key,
#     aws_secret_access_key=secret_key
# )

# data = StringIO()
# city_Albedo.rio.to_raster(data)
# data.seek(0)

bucket_name = 'wri-cities-heat'
local_file_name = 'F:/InternshipWRI/Amsterdam_LST.tif'


s3 = boto3.resource(service_name='s3',aws_access_key_id=access_key,aws_secret_access_key=secret_key)

s3.meta.client.upload_file(local_file_name,
                               bucket_name,
                               'NLD-Amsterdam/Amsterdam_NDVI-test-upload.tif',
                               ExtraArgs={'ACL':'public-read'})

# try:
#     s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=data.getvalue())
#     print("File uploaded successfully.")
# except Exception as e:
#     print(f"Error uploading file: {e}")