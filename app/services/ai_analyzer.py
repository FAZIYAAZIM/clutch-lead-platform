import openai
import json
import logging
from typing import Dict, List
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self, api_key=None):
        # Set your OpenAI API key
        self.api_key = api_key or "your-openai-api-key-here"  # REPLACE WITH YOUR KEY
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def calculate_lead_score(self, company: Dict) -> Dict:
        """Calculate lead score based on available data (without API)"""
        score = 0
        factors = []
        
        # Rating score (max 30 points)
        try:
            rating = float(company.get('rating', 0) or 0)
            if rating >= 4.9:
                score += 30
                factors.append("Excellent rating (5★)")
            elif rating >= 4.5:
                score += 25
                factors.append("Good rating (4.5★+)")
            elif rating >= 4.0:
                score += 15
                factors.append("Average rating")
            else:
                score += 5
                factors.append("Low rating")
        except:
            factors.append("No rating data")
        
        # Review count score (max 20 points)
        try:
            reviews = int(company.get('reviews', 0) or 0)
            if reviews >= 50:
                score += 20
                factors.append(f"{reviews}+ reviews")
            elif reviews >= 20:
                score += 15
                factors.append(f"{reviews} reviews")
            elif reviews >= 5:
                score += 10
                factors.append(f"{reviews} reviews")
            elif reviews > 0:
                score += 5
                factors.append(f"{reviews} reviews")
            else:
                factors.append("No reviews")
        except:
            factors.append("No review data")
        
        # Company size score (max 20 points)
        size = company.get('employees', '').lower()
        if '10,000+' in size or '10000' in size:
            score += 20
            factors.append("Enterprise company")
        elif '1,000' in size or '1000' in size:
            score += 15
            factors.append("Large company")
        elif '250' in size or '500' in size:
            score += 10
            factors.append("Medium company")
        elif '50' in size or '100' in size:
            score += 5
            factors.append("Small company")
        else:
            factors.append("Size unknown")
        
        # Hourly rate score (max 15 points)
        rate = company.get('hourly_rate', '').lower()
        if '$100' in rate or '100' in rate:
            score += 15
            factors.append("Premium pricing")
        elif '$50' in rate or '50' in rate:
            score += 10
            factors.append("Mid-range pricing")
        elif '$25' in rate or '25' in rate:
            score += 5
            factors.append("Budget pricing")
        else:
            factors.append("Rate unknown")
        
        # Services score (max 15 points)
        services = company.get('services', [])
        if len(services) > 5:
            score += 15
            factors.append("Full-service provider")
        elif len(services) > 2:
            score += 10
            factors.append("Multiple services")
        elif len(services) > 0:
            score += 5
            factors.append("Specialized")
        else:
            factors.append("Services unknown")
        
        # Website presence (bonus 5 points)
        if company.get('website') and company['website'] != 'Not available':
            score += 5
            factors.append("Has website")
        
        # LinkedIn presence (bonus 5 points)
        if company.get('linkedin') and company['linkedin'] != 'Not available':
            score += 5
            factors.append("Has LinkedIn")
        
        # Ensure score is between 0-100
        score = min(100, max(0, score))
        
        return {
            "score": score,
            "factors": factors,
            "grade": self.get_grade(score),
            "recommendation": self.get_recommendation(score)
        }
    
    def get_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        elif score >= 40:
            return "C"
        elif score >= 30:
            return "D"
        else:
            return "F"
    
    def get_recommendation(self, score: int) -> str:
        """Get recommendation based on score"""
        if score >= 70:
            return "Hot Lead - Contact Immediately"
        elif score >= 50:
            return "Warm Lead - Nurture and Follow Up"
        elif score >= 30:
            return "Cold Lead - Add to Newsletter"
        else:
            return "Low Priority - Monitor"
    
    def analyze_with_ai(self, company: Dict) -> Dict:
        """Use OpenAI for advanced analysis (requires API key)"""
        if not self.api_key or self.api_key == "your-openai-api-key-here":
            logger.warning("OpenAI API key not configured, using rule-based scoring")
            return self.calculate_lead_score(company)
        
        try:
            prompt = f"""
            Analyze this company as a B2B sales lead:
            
            Company: {company.get('name')}
            Location: {company.get('location')}
            Rating: {company.get('rating')}/5 with {company.get('reviews')} reviews
            Services: {', '.join(company.get('services', []))}
            Hourly Rate: {company.get('hourly_rate')}
            Employees: {company.get('employees')}
            
            Provide analysis in JSON format:
            {{
                "lead_score": <score 0-100>,
                "industry": "<industry>",
                "confidence": "<high/medium/low>",
                "strengths": ["<strength1>", "<strength2>"],
                "weaknesses": ["<weakness1>", "<weakness2>"],
                "outreach_tips": "<brief outreach suggestion>",
                "potential_value": "<estimated value>",
                "recommendation": "<contact/nurture/monitor>"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a lead scoring AI expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self.calculate_lead_score(company)
    
    def analyze_company(self, company: Dict) -> Dict:
        """Main analysis method"""
        return self.analyze_with_ai(company)

# Create instance (replace with your OpenAI API key)
ai_analyzer = AIAnalyzer(api_key="your-openai-api-key-here")