import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.property import Property

db = SessionLocal()
props = db.query(Property).limit(50).all()
for p in props:
    img_status = 'Yes' if p.image_url else 'No'
    print(f'{p.id} | {p.address[:40]} | Image: {img_status}')
db.close()
