from storages.backends.gcloud import GoogleCloudStorage

class ShopImageStorage(GoogleCloudStorage):
    location = "Printit-Shop-photo/"