import requests
import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRMIntegration:
    def __init__(self):
        # You can configure these based on your CRM
        self.hubspot_api_key = None
        self.salesforce_token = None
        self.zoho_api_key = None
        self.webhook_url = None
    
    def send_to_hubspot(self, lead_data: Dict) -> bool:
        """Send lead to HubSpot CRM"""
        if not self.hubspot_api_key:
            logger.warning("HubSpot API key not configured")
            return False
        
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {
            "Authorization": f"Bearer {self.hubspot_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "properties": {
                "company": lead_data.get('company_name'),
                "website": lead_data.get('website'),
                "phone": lead_data.get('phone'),
                "city": lead_data.get('location'),
                "hs_lead_status": "NEW",
                "notes": f"Rating: {lead_data.get('rating')}, Reviews: {lead_data.get('reviews')}"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            return response.status_code == 201
        except Exception as e:
            logger.error(f"HubSpot error: {e}")
            return False
    
    def send_to_salesforce(self, lead_data: Dict) -> bool:
        """Send lead to Salesforce CRM"""
        # Implementation for Salesforce
        logger.info(f"Would send to Salesforce: {lead_data['company_name']}")
        return True
    
    def send_to_zoho(self, lead_data: Dict) -> bool:
        """Send lead to Zoho CRM"""
        # Implementation for Zoho
        logger.info(f"Would send to Zoho: {lead_data['company_name']}")
        return True
    
    def send_to_webhook(self, lead_data: Dict, webhook_url: str) -> bool:
        """Send lead to custom webhook (Zapier, n8n, etc.)"""
        try:
            response = requests.post(webhook_url, json=lead_data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return False
    
    def batch_send_to_crm(self, leads: List[Dict], crm_type: str = "hubspot") -> Dict:
        """Send multiple leads to CRM"""
        results = {"success": 0, "failed": 0, "errors": []}
        
        for lead in leads:
            success = False
            if crm_type == "hubspot":
                success = self.send_to_hubspot(lead)
            elif crm_type == "salesforce":
                success = self.send_to_salesforce(lead)
            elif crm_type == "zoho":
                success = self.send_to_zoho(lead)
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(lead.get('company_name'))
        
        return results

crm = CRMIntegration()