"""
Property scraper API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.services.scraper_service import PropertyScraperService
from app.services.commute_service import CommuteService
from app.models.property import Property
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/properties", tags=["properties"])


# Pydantic schemas
class PropertySearch(BaseModel):
    """Property search request"""
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State abbreviation (e.g., CA, NY)")
    sources: Optional[List[str]] = Field(None, description="Scraper sources (zillow, realtor)")
    max_price: Optional[int] = Field(None, description="Maximum price")
    min_beds: Optional[int] = Field(None, ge=0, description="Minimum bedrooms")
    min_baths: Optional[float] = Field(None, ge=0, description="Minimum bathrooms")
    property_type: Optional[str] = Field(None, description="Property type (house, condo, townhouse)")


class PropertyFilter(BaseModel):
    """Property filter for database queries"""
    city: Optional[str] = None
    state: Optional[str] = None
    max_price: Optional[int] = None
    min_beds: Optional[int] = Field(None, ge=0)
    min_baths: Optional[float] = Field(None, ge=0)
    property_type: Optional[str] = None
    limit: int = Field(100, ge=1, le=500)
    offset: int = Field(0, ge=0)


class PropertyResponse(BaseModel):
    """Property response model"""
    id: int
    source: str
    address: str
    city: str
    state: str
    zip_code: str
    price: float
    beds: int
    baths: float
    sqft: int
    year_built: Optional[int]
    property_type: str
    listing_url: Optional[str]
    image_url: Optional[str]
    homebuyer_score: Optional[int]
    investor_score: Optional[int]
    estimated_rent: Optional[float]
    
    class Config:
        from_attributes = True


class ScrapeResultResponse(BaseModel):
    """Scrape operation result"""
    message: str
    total_found: int
    total_saved: int
    by_source: dict


class RoommateCommute(BaseModel):
    """Roommate commute requirements"""
    destination: str = Field(..., description="Work/school address")
    max_commute_minutes: float = Field(..., ge=0, le=180, description="Maximum commute time in minutes")
    mode: str = Field("driving", description="Transportation mode: driving, transit, walking, bicycling")


class CommuteFilterRequest(BaseModel):
    """Request to filter properties by commute times"""
    property_ids: List[int] = Field(..., description="List of property IDs to check")
    roommates: List[RoommateCommute] = Field(..., min_items=1, description="Roommate commute requirements")


@router.post("/scrape", response_model=ScrapeResultResponse)
def scrape_properties(
    search: PropertySearch,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Scrape properties from real estate websites
    
    This endpoint initiates a property scraping job. For large searches,
    consider using background processing.
    
    **Note**: Web scraping should comply with website terms of service.
    This is for educational purposes.
    """
    logger.info(f"Scraping properties for {search.city}, {search.state}")
    
    try:
        service = PropertyScraperService(db)
        
        results = service.search_and_save_properties(
            city=search.city,
            state=search.state,
            sources=search.sources,
            max_price=search.max_price,
            min_beds=search.min_beds,
            min_baths=search.min_baths,
            property_type=search.property_type
        )
        
        return ScrapeResultResponse(
            message=f"Successfully scraped properties for {search.city}, {search.state}",
            total_found=results['total_found'],
            total_saved=results['total_saved'],
            by_source=results['by_source']
        )
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.get("/", response_model=List[PropertyResponse])
def get_properties(
    city: Optional[str] = None,
    state: Optional[str] = None,
    max_price: Optional[int] = None,
    min_beds: Optional[int] = None,
    min_baths: Optional[float] = None,
    property_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get properties from database with optional filters
    
    Returns a list of properties matching the specified criteria.
    Results are ordered by most recently scraped.
    """
    try:
        service = PropertyScraperService(db)
        
        properties = service.get_properties(
            city=city,
            state=state,
            max_price=max_price,
            min_beds=min_beds,
            min_baths=min_baths,
            property_type=property_type,
            limit=limit,
            offset=offset
        )
        
        return properties
        
    except Exception as e:
        logger.error(f"Error fetching properties: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch properties: {str(e)}")


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int, db: Session = Depends(get_db)):
    """
    Get a specific property by ID
    """
    try:
        service = PropertyScraperService(db)
        property_obj = service.get_property_by_id(property_id)
        
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return property_obj
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching property: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch property: {str(e)}")


@router.delete("/cleanup")
def cleanup_old_properties(days: int = 30, db: Session = Depends(get_db)):
    """
    Delete properties older than specified days
    
    This helps keep the database clean by removing stale listings.
    """
    try:
        service = PropertyScraperService(db)
        deleted_count = service.delete_old_properties(days=days)
        
        return {
            "message": f"Deleted {deleted_count} properties older than {days} days",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.post("/filter-by-commute")
def filter_properties_by_commute(
    request: CommuteFilterRequest,
    db: Session = Depends(get_db)
):
    """
    Filter properties based on commute time requirements for multiple roommates
    
    This endpoint checks each property against all roommate commute requirements
    and returns only properties that satisfy all requirements.
    
    Uses free OpenStreetMap and OSRM APIs - no API key required!
    """
    try:
        commute_service = CommuteService()
        
        # Get all requested properties
        properties = db.query(Property).filter(Property.id.in_(request.property_ids)).all()
        
        if not properties:
            return {
                "compatible_properties": [],
                "total_checked": 0,
                "total_compatible": 0
            }
        
        compatible_properties = []
        
        for prop in properties:
            # Build full address
            property_address = f"{prop.address}, {prop.city}, {prop.state} {prop.zip_code}"
            
            # Convert roommates to list of dicts
            roommates_data = [
                {
                    "destination": rm.destination,
                    "max_commute_minutes": rm.max_commute_minutes,
                    "mode": rm.mode
                }
                for rm in request.roommates
            ]
            
            # Check compatibility
            result = commute_service.check_property_commute_compatibility(
                property_address=property_address,
                roommates=roommates_data
            )
            
            if result["compatible"]:
                compatible_properties.append({
                    "property_id": prop.id,
                    "address": prop.address,
                    "city": prop.city,
                    "state": prop.state,
                    "price": float(prop.price),
                    "commute_details": result["commute_details"]
                })
        
        return {
            "compatible_properties": compatible_properties,
            "total_checked": len(properties),
            "total_compatible": len(compatible_properties),
            "message": f"Found {len(compatible_properties)} properties compatible with all roommate commute requirements"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering by commute: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to filter by commute: {str(e)}")
