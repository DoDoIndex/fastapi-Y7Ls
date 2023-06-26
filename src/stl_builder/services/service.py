import google.cloud.storage as gcs
from ..settings import settings


def upload_google_cloud_storage(filename, path, bucket_name):
    client = gcs.Client.from_service_account_info(settings.GOOGLE_CLOUD_STORAGE)
    blob = client.bucket(bucket_name).blob(filename)
    blob.upload_from_filename(path)
    blob.acl.all().grant_read()
    blob.acl.save()

    return f"https://storage.googleapis.com/{bucket_name}/{filename}"
