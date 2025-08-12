"""
Property Information Parser for SMS Host Protocol
Reads plain text property information file and extracts structured information
"""

import os
import re
from typing import Dict, List, Optional, Any


class PropertyInfoParser:
    """Parses plain text property information for SMS hosting"""
    
    def __init__(self, property_file_path: str = "data/airbnblisting.txt"):
        self.property_file_path = property_file_path
        self.property_data = {}
        self._parse_property_file()
    
    def _parse_property_file(self):
        """Parse the plain text property file"""
        try:
            if not os.path.exists(self.property_file_path):
                raise FileNotFoundError(f"Property file not found: {self.property_file_path}")
            
            with open(self.property_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parse sections
            self._parse_sections(content)
            
        except Exception as e:
            print(f"Error parsing property file: {e}")
            # Set default data if parsing fails
            self.property_data = self._get_default_data()
    
    def _parse_sections(self, content: str):
        """Parse content into sections"""
        # Split content into sections based on headers
        sections = re.split(r'\n([A-Z][A-Z\s&]+:)\n', content)
        
        current_section = None
        current_content = []
        
        for i, section in enumerate(sections):
            if i == 0:  # First section is usually content before first header
                if section.strip():
                    self.property_data["general"] = section.strip()
                continue
            
            if re.match(r'^[A-Z][A-Z\s&]+:$', section):
                # This is a header, save previous section if exists
                if current_section and current_content:
                    self.property_data[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = section.rstrip(':').lower().replace(' ', '_')
                current_content = []
            else:
                # This is content for current section
                if current_section:
                    current_content.append(section.strip())
        
        # Save last section
        if current_section and current_content:
            self.property_data[current_section] = '\n'.join(current_content).strip()
    
    def _get_default_data(self) -> Dict[str, str]:
        """Get default property data if parsing fails"""
        return {
            "property_name": "Your Property",
            "location": "Your City, State",
            "check_in_check_out": "Check-in: 3:00 PM, Check-out: 11:00 AM",
            "amenities": "WiFi, Kitchen, Parking, Bathrooms, Bedrooms",
            "house_rules": "No smoking, No pets, Quiet hours 10 PM-8 AM",
            "whats_included": "Towels, linens, coffee, tea",
            "nearby_attractions": "Restaurants, shopping, attractions",
            "cancellation_policy": "Flexible cancellation policy"
        }
    
    def get_property_info(self) -> Dict[str, str]:
        """Get all property information"""
        return self.property_data
    
    def get_section(self, section_name: str) -> Optional[str]:
        """Get content from a specific section"""
        # Try exact match first
        if section_name in self.property_data:
            return self.property_data[section_name]
        
        # Try partial matches
        for key in self.property_data.keys():
            if section_name.lower() in key.lower():
                return self.property_data[key]
        
        return None
    
    def search_info(self, query: str) -> List[str]:
        """Search for information matching a query"""
        query_lower = query.lower()
        results = []
        
        for section, content in self.property_data.items():
            if query_lower in content.lower():
                results.append(f"{section}: {content}")
        
        return results
    
    def get_checkin_info(self) -> str:
        """Get check-in and check-out information"""
        checkin_section = self.get_section("check_in_check_out")
        if checkin_section:
            return checkin_section
        
        # Fallback to searching
        for section, content in self.property_data.items():
            if "check" in section.lower() and ("time" in content.lower() or "pm" in content.lower() or "am" in content.lower()):
                return content
        
        return "Check-in time: 3:00 PM, Check-out time: 11:00 AM"
    
    def get_amenities(self) -> str:
        """Get amenities information"""
        amenities_section = self.get_section("amenities")
        if amenities_section:
            return amenities_section
        
        # Fallback to searching
        for section, content in self.property_data.items():
            if "amenity" in section.lower() or "wifi" in content.lower() or "kitchen" in content.lower():
                return content
        
        return "WiFi, Kitchen, Parking, Bathrooms, Bedrooms, Living room, Outdoor space"
    
    def get_house_rules(self) -> str:
        """Get house rules information"""
        rules_section = self.get_section("house_rules")
        if rules_section:
            return rules_section
        
        # Fallback to searching
        for section, content in self.property_data.items():
            if "rule" in section.lower() or "no smoking" in content.lower() or "no pets" in content.lower():
                return content
        
        return "No smoking, No pets, No parties, Quiet hours 10 PM-8 AM, Maximum guests limit"
    
    def get_nearby_attractions(self) -> str:
        """Get nearby attractions information"""
        attractions_section = self.get_section("nearby_attractions")
        if attractions_section:
            return attractions_section
        
        # Fallback to searching
        for section, content in self.property_data.items():
            if "nearby" in section.lower() or "attraction" in section.lower() or "restaurant" in content.lower():
                return content
        
        return "Restaurants, shopping centers, attractions, and public transportation nearby"
    
    def get_cancellation_policy(self) -> str:
        """Get cancellation policy information"""
        policy_section = self.get_section("cancellation_policy")
        if policy_section:
            return policy_section
        
        # Fallback to searching
        for section, content in self.property_data.items():
            if "cancellation" in section.lower() or "refund" in content.lower():
                return content
        
        return "Flexible cancellation policy with full refund if cancelled 7+ days before arrival"
    
    def get_property_name(self) -> str:
        """Get property name"""
        name_section = self.get_section("property_name")
        if name_section:
            return name_section
        
        # Fallback to searching
        for section, content in self.property_data.items():
            if "name" in section.lower() and content.strip():
                return content.strip()
        
        return "Your Property"
    
    def get_location(self) -> str:
        """Get property location"""
        location_section = self.get_section("location")
        if location_section:
            return location_section
        
        # Fallback to searching
        for section, content in self.property_data.items():
            if "location" in section.lower() and content.strip():
                return content.strip()
        
        return "Your City, State"
    
    def format_for_ai_context(self) -> str:
        """Format property data for AI context"""
        context_parts = []
        
        # Add key information
        context_parts.append(f"Property: {self.get_property_name()}")
        context_parts.append(f"Location: {self.get_location()}")
        context_parts.append(f"Check-in/Check-out: {self.get_checkin_info()}")
        context_parts.append(f"Amenities: {self.get_amenities()}")
        context_parts.append(f"House Rules: {self.get_house_rules()}")
        context_parts.append(f"What's Included: {self.get_section('whats_included') or 'Fresh towels, linens, coffee, tea, local guidebooks'}")
        context_parts.append(f"Nearby Attractions: {self.get_nearby_attractions()}")
        context_parts.append(f"Cancellation Policy: {self.get_cancellation_policy()}")
        
        return "\n".join(context_parts)


# Global instance
property_parser = PropertyInfoParser()
