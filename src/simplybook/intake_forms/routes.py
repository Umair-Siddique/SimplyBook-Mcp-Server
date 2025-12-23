from typing import Dict, Any, Optional
from ..base_routes import BaseRoutes
from .client import IntakeFormsClient
from pydantic import Field
from typing import Annotated

class IntakeFormsRoutes(BaseRoutes):
    def register_tools(self, mcp):
        @mcp.tool(
            description="Get additional fields (intake form fields) required for booking a specific service. These fields must be filled when creating a booking. Call this before create_booking to know what information to collect from the user.",
            tags={"intake", "fields", "additional", "booking"}
        )
        async def get_additional_fields(
            service_id: Optional[Annotated[str, Field(description="ID of the service to get required additional fields for. If not provided, returns all additional fields.")]] = None
        ) -> Dict[str, Any]:
            """
            Get list of additional fields (intake form fields) required for bookings.
            These are custom fields that must be collected from users during booking.
            
            Args:
                service_id: Optional service ID to filter fields for a specific service
                
            Returns:
                Dict with success status and list of additional fields with:
                - id: Field identifier (use this as 'field' value in create_booking)
                - name: Field display name
                - type: Field type (text, select, textarea, etc.)
                - required: Whether the field is mandatory
                - values: Available options (for select/dropdown fields)
                
            Example response:
                {
                    "success": True,
                    "result": {
                        "data": [
                            {
                                "id": "abc123",
                                "name": "Health Conditions",
                                "type": "textarea",
                                "required": true
                            },
                            {
                                "id": "def456",
                                "name": "Preferred Contact",
                                "type": "select",
                                "required": true,
                                "values": ["Email", "Phone", "WhatsApp"]
                            }
                        ]
                    }
                }
            """
            try:
                if not await self.ensure_authenticated():
                    return {"error": "No se pudo autenticar"}
                    
                self.client = IntakeFormsClient(self.get_auth_headers())
                result = await self.client.get_additional_fields(service_id=service_id)
                return {
                    "success": True,
                    "result": result
                }
            except Exception as e:
                return {"error": f"Error getting additional fields: {str(e)}"}

