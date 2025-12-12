import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.property import Property

db = SessionLocal()
props = db.query(Property).limit(50).all()
print('Properties in database:')
for p in props:
    img_status = 'Yes' if p.image_url else 'No'
    print(f'ID: {p.id}, Address: {p.address[:40]}, Has Image: {img_status}')
    if p.image_url:
        print(f'  Image URL: {p.image_url[:60]}...')
db.close()
