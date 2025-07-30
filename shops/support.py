from .services.shop_services import ShopService 
from PIL import Image
import os
import datetime
from .storage import ShopImageStorage

def get_shop(id):
        shop = ShopService.get_shop_by_id(id)
        if shop is None:
            print('shop not found')
            return None
        
        try:
            data = {
                'shop_id':id,
                'shop_name':shop.name,
                'shop_address': shop.location.address,
                'owner_name':shop.owner_name,
                'owner_number':shop.owner_number,
                'shop_images':["https://content.jdmagicbox.com/v2/comp/bangalore/l2/080pxx80.xx80.160519151520.l1l2/catalogue/galaxies-enterprises-bangalore-0rt9ockuaa-250.jpg","https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQogIEhbS0Zn-1OSXPPnEhkuNCpN_Jqi_hJBQ&s","https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQxILCoOct2LvnWikhR8L46MOiYPbSnVv2rVg&s"],
                'location':{
                    "latitude": shop.location.geometry.y,
                    "longitude": shop.location.geometry.x
                } if shop.location else None,
                'shop_rating':shop.rating,
                'shop_facilites':shop.facilities,
                'shop_paymentmodes':shop.payment_modes, 
            }
            
            return data
        
        except Exception as e:
            print(str(e))
            return None


def get_list(shops):
    return [
        {
            'shop_id': shop.id, 
            'shop_name': shop.name,
            'shop_rating': shop.rating,
            'shopImages': "https://content.jdmagicbox.com/v2/comp/bangalore/l2/080pxx80.xx80.160519151520.l1l2/catalogue/galaxies-enterprises-bangalore-0rt9ockuaa-250.jpg",
            'shop_address': shop.location.address if shop.location.address else None,  # Access without additional DB queries
            'distance_km': shop.distance.km if shop.distance else None
        }
        for shop in shops
    ]
    
def get_image_metadata(file):
    
    image = Image.open(file)
    data = {
        "width": image.width,
        "height": image.height,
        "format": image.format,
        "content_type": image.get_format_mimetype(),  # e.g. 'image/jpeg'
        "file_size": file.size
    }
    
        
    return data

def parse_path(file, shopId):
    
    timestamp = str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    filename = f'shop_{shopId}_{timestamp}' 
    folder = f'shop{shopId}'
    path =  f'{folder}/{filename}'
    
    gcp = ShopImageStorage()
    
    gcp_path = gcp.save(path,file)
    return gcp_path