from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.property import Property, Deed, PropertyDocument
from models.property import PropertyType, PropertyStatus, OwnershipType, DocumentType
from typing import List, Optional, Dict, Any
import json
import os
import shutil

class PropertyService:
    def __init__(self, db: Session):
        self.db = db
        
    def create_property(self, data: Dict[str, Any]) -> Property:
        # Convert features from dict to JSON string if provided
        if 'features' in data and isinstance(data['features'], dict):
            data['features'] = json.dumps(data['features'])
            
        property = Property(**data)
        self.db.add(property)
        self.db.commit()
        self.db.refresh(property)
        return property
    
    def update_property(self, property_id: int, data: Dict[str, Any]) -> Optional[Property]:
        property = self.db.query(Property).filter(Property.id == property_id).first()
        if property:
            # Convert features from dict to JSON string if provided
            if 'features' in data and isinstance(data['features'], dict):
                data['features'] = json.dumps(data['features'])
                
            for key, value in data.items():
                setattr(property, key, value)
            self.db.commit()
            self.db.refresh(property)
        return property
    
    def delete_property(self, property_id: int) -> bool:
        property = self.db.query(Property).filter(Property.id == property_id).first()
        if property:
            # Delete associated documents from filesystem
            for doc in property.documents:
                if os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
            
            self.db.delete(property)  # This will cascade delete deeds and documents
            self.db.commit()
            return True
        return False
    
    def get_property(self, property_id: int) -> Optional[Property]:
        return self.db.query(Property).filter(Property.id == property_id).first()
    
    def get_property_by_no(self, property_no: str) -> Optional[Property]:
        return self.db.query(Property).filter(Property.property_no == property_no).first()
    
    def get_all_properties(self, status: Optional[PropertyStatus] = None) -> List[Property]:
        query = self.db.query(Property)
        if status:
            query = query.filter(Property.status == status)
        return query.all()
    
    def create_deed(self, data: Dict[str, Any]) -> Deed:
        deed = Deed(**data)
        
        # Deactivate previous deeds for this property if this is a new active deed
        if deed.is_active:
            existing_deeds = self.db.query(Deed).filter(
                and_(Deed.property_id == deed.property_id, Deed.is_active == True)
            ).all()
            for existing_deed in existing_deeds:
                existing_deed.is_active = False
        
        self.db.add(deed)
        self.db.commit()
        self.db.refresh(deed)
        return deed
    
    def get_property_deeds(self, property_id: int, active_only: bool = False) -> List[Deed]:
        query = self.db.query(Deed).filter(Deed.property_id == property_id)
        if active_only:
            query = query.filter(Deed.is_active == True)
        return query.order_by(Deed.registration_date.desc()).all()
    
    def store_document(self, 
                      property_id: int,
                      file_path: str,
                      doc_type: DocumentType,
                      title: str,
                      description: Optional[str] = None,
                      issue_date: Optional[date] = None,
                      expiry_date: Optional[date] = None) -> PropertyDocument:
        """Store a new document and create its database record"""
        
        # Create documents directory if it doesn't exist
        docs_dir = os.path.join("documents", str(property_id))
        os.makedirs(docs_dir, exist_ok=True)
        
        # Generate unique filename and copy file
        filename = f"{doc_type.value.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path)}"
        new_path = os.path.join(docs_dir, filename)
        shutil.copy2(file_path, new_path)
        
        # Create document record
        doc_data = {
            'property_id': property_id,
            'type': doc_type,
            'title': title,
            'file_path': new_path,
            'description': description,
            'issue_date': issue_date,
            'expiry_date': expiry_date
        }
        
        document = PropertyDocument(**doc_data)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_property_documents(self, 
                             property_id: int,
                             doc_type: Optional[DocumentType] = None) -> List[PropertyDocument]:
        """Get all documents for a property, optionally filtered by type"""
        query = self.db.query(PropertyDocument).filter(PropertyDocument.property_id == property_id)
        if doc_type:
            query = query.filter(PropertyDocument.type == doc_type)
        return query.order_by(PropertyDocument.created_at.desc()).all()
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document and its file"""
        document = self.db.query(PropertyDocument).filter(PropertyDocument.id == document_id).first()
        if document:
            # Delete file from filesystem
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            self.db.delete(document)
            self.db.commit()
            return True
        return False
    
    def get_property_value_history(self, property_id: int) -> List[Dict[str, Any]]:
        """Get property value history from deed records"""
        deeds = self.db.query(Deed).filter(Deed.property_id == property_id)\
                    .order_by(Deed.registration_date.asc()).all()
        
        history = []
        for deed in deeds:
            if deed.purchase_price:
                history.append({
                    'date': deed.registration_date,
                    'value': deed.purchase_price,
                    'type': 'Purchase',
                    'owner': deed.owner_name
                })
        
        property = self.get_property(property_id)
        if property and property.current_value:
            history.append({
                'date': property.updated_at.date(),
                'value': property.current_value,
                'type': 'Current Valuation',
                'owner': None
            })
            
        return history