import os
import json
<<<<<<< HEAD
import re
=======
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available. AI matching will use fallback logic.")

class AIMatchingService:
    """
    AI-powered matching service using Google Gemini API to match clients with caretakers
    based on medical conditions, special instructions, and ADL services.
    """
    
    def __init__(self):
        """Initialize the AI matching service"""
<<<<<<< HEAD
=======
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize or reinitialize the API connection"""
        # Reload environment variables
        load_dotenv()
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        
        if self.api_key and GEMINI_AVAILABLE:
            try:
<<<<<<< HEAD
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.ai_enabled = True
                print("✅ AI matching service initialized with Gemini API")
=======
                # Clear any existing configuration to avoid caching issues
                genai.configure(api_key=None)
                # Configure with fresh key
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.ai_enabled = True
                print(f"✅ AI matching service initialized with Gemini API (Key: {self.api_key[:20]}...)")
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
            except Exception as e:
                print(f"⚠️ Error initializing Gemini API: {e}")
                self.model = None
                self.ai_enabled = False
        else:
            self.model = None
            self.ai_enabled = False
            if not self.api_key:
                print("⚠️ GEMINI_API_KEY not found. AI matching will use fallback logic.")
            else:
                print("⚠️ Gemini API not available. AI matching will use fallback logic.")
    
<<<<<<< HEAD
    def _clean_json_response(self, response_text: str) -> str:
        """Clean and fix common JSON formatting issues from AI responses"""
        # Strip whitespace
        text = response_text.strip()
        
        # Remove markdown code blocks
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        # Remove trailing commas before closing brackets/braces (common AI error)
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Remove any leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text
    
=======
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
    def analyze_client_needs(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze client medical conditions and special instructions to determine care needs
        """
<<<<<<< HEAD
=======
        # Reinitialize API to ensure we have the latest key
        self._initialize_api()
        
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
        if not self.ai_enabled:
            return self._fallback_client_analysis(client_data)
        
        try:
            medical_conditions = client_data.get('medical_conditions', '')
            special_instructions = client_data.get('special_instructions', '')
            
            prompt = f"""
            Analyze the following client information and extract their care needs for matching with caretakers.
            
            Medical Conditions: {medical_conditions}
            Special Instructions: {special_instructions}
            
<<<<<<< HEAD
            Please provide a JSON response with the following structure (NO trailing commas):
            {{
                "primary_needs": ["list of main care requirements based on medical conditions"],
                "adl_requirements": ["specific ADL services needed"],
=======
            Please provide a JSON response with the following structure:
            {{
                "primary_needs": ["list of main care requirements based on medical conditions"],
                "adl_requirements": ["specific ADL services needed (e.g., personal_care, medication_management, mobility_assistance)"],
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
                "specializations": ["required caretaker specializations"],
                "urgency_level": "low/medium/high",
                "complexity": "simple/moderate/complex",
                "key_considerations": ["important factors for matching"]
            }}
            
<<<<<<< HEAD
            IMPORTANT: Do not include trailing commas in arrays. Ensure valid JSON format.
            
=======
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
            Focus on:
            - ADL services that would be most helpful
            - Specialized care needs
            - Safety considerations
            - Communication preferences
            - Mobility requirements
            """
            
            response = self.model.generate_content(prompt)
<<<<<<< HEAD
            response_text = self._clean_json_response(response.text)
=======
            # Clean the response text and try to parse JSON
            response_text = response.text.strip()
            # Remove any markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Fix common JSON issues
            import re
            # Remove trailing commas before closing brackets/braces
            response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
            
            result = json.loads(response_text)
            
            print(f"🧠 AI analyzed client needs: {result.get('primary_needs', [])}")
            return result
            
<<<<<<< HEAD
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in AI client analysis: {e}")
            print(f"📄 Response text was: {response_text[:500]}")
            return self._fallback_client_analysis(client_data)
=======
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
        except Exception as e:
            print(f"❌ Error in AI client analysis: {e}")
            return self._fallback_client_analysis(client_data)
    
    def match_caretakers(self, client_needs: Dict[str, Any], caretakers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Match client needs with available caretakers using AI
        """
<<<<<<< HEAD
=======
        # Reinitialize API to ensure we have the latest key
        self._initialize_api()
        
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
        if not self.ai_enabled:
            return self._fallback_caretaker_matching(client_needs, caretakers)
        
        try:
            # Prepare caretaker summaries for AI
            caretaker_summaries = []
            for caretaker in caretakers:
                # Convert Decimal to float for JSON serialization
                hourly_rate = caretaker.get('hourly_rate', 0)
                if hasattr(hourly_rate, 'to_eng_string'):
                    hourly_rate = float(hourly_rate)
                
                summary = {
                    "id": caretaker.get('id'),
                    "name": caretaker.get('full_name'),
                    "experience": caretaker.get('years_experience', 0),
                    "bio": caretaker.get('bio', ''),
                    "adl_services": caretaker.get('adl_services', []),
                    "certifications": caretaker.get('certifications', ''),
                    "languages": caretaker.get('languages', ''),
                    "hourly_rate": hourly_rate
                }
                caretaker_summaries.append(summary)
            
            prompt = f"""
            Match the following client needs with available caretakers and provide detailed analysis.
            
            CLIENT NEEDS:
            {json.dumps(client_needs, indent=2)}
            
            AVAILABLE CARETAKERS:
            {json.dumps(caretaker_summaries, indent=2)}
            
<<<<<<< HEAD
            For each caretaker, provide a JSON response with this structure (NO trailing commas):
=======
            For each caretaker, provide a JSON response with this structure:
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
            {{
                "matches": [
                    {{
                        "caretaker_id": 1,
                        "confidence_score": 85,
                        "match_explanation": "Detailed explanation of why this is a good match",
                        "strengths": ["list of specific strengths that align with client needs"],
                        "concerns": ["any potential concerns or gaps"],
                        "compatibility_factors": {{
                            "adl_alignment": 90,
                            "experience_match": 80,
                            "specialization_fit": 85
                        }}
                    }}
                ]
            }}
            
<<<<<<< HEAD
            IMPORTANT: 
            - Do not include trailing commas in arrays or objects
            - Ensure valid JSON format
            - Include all caretakers with a confidence score above 30
            
=======
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
            Consider:
            - ADL service alignment
            - Experience with similar conditions
            - Specializations and certifications
            - Communication abilities
            - Availability and logistics
            - Cost considerations
            """
            
            response = self.model.generate_content(prompt)
<<<<<<< HEAD
            response_text = self._clean_json_response(response.text)
=======
            # Clean the response text and try to parse JSON
            response_text = response.text.strip()
            # Remove any markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Fix common JSON issues
            import re
            # Remove trailing commas before closing brackets/braces
            response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
            
            result = json.loads(response_text)
            
            # Add full caretaker details to matches
            matches = result.get('matches', [])
            for match in matches:
                caretaker_id = match.get('caretaker_id')
                # Find the full caretaker data
                for caretaker in caretakers:
                    if caretaker.get('id') == caretaker_id:
                        match['caretaker_details'] = caretaker
                        break
            
            print(f"🎯 AI generated {len(matches)} matches")
            return matches
            
<<<<<<< HEAD
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in AI caretaker matching: {e}")
            print(f"📄 Response text was: {response_text[:500]}")
            return self._fallback_caretaker_matching(client_needs, caretakers)
=======
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
        except Exception as e:
            print(f"❌ Error in AI caretaker matching: {e}")
            return self._fallback_caretaker_matching(client_needs, caretakers)
    
    def _fallback_client_analysis(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        medical_conditions = client_data.get('medical_conditions', '').lower()
        special_instructions = client_data.get('special_instructions', '').lower()
        
        # Simple keyword-based analysis
        needs = []
        adl_requirements = []
        specializations = []
        
        # Analyze medical conditions
        if any(condition in medical_conditions for condition in ['dementia', 'alzheimer', 'memory']):
            needs.append('dementia_care')
            adl_requirements.append('Bathing & Personal Hygiene')
            adl_requirements.append('Medication Management')
            specializations.append('dementia_specialist')
        
        if any(condition in medical_conditions for condition in ['diabetes', 'blood sugar']):
            needs.append('diabetes_management')
            adl_requirements.append('Medication Management')
            specializations.append('diabetes_care')
        
<<<<<<< HEAD
        if any(condition in medical_conditions for condition in ['mobility', 'wheelchair', 'walking', 'balance', 'arthritis']):
=======
        if any(condition in medical_conditions for condition in ['mobility', 'wheelchair', 'walking', 'balance']):
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
            needs.append('mobility_assistance')
            adl_requirements.append('Mobility & Transfers')
            specializations.append('mobility_specialist')
        
        if any(condition in medical_conditions for condition in ['heart', 'cardiac', 'blood pressure']):
            needs.append('cardiac_care')
            adl_requirements.append('Medication Management')
            specializations.append('cardiac_care')
        
        # Analyze special instructions
        if 'companion' in special_instructions or 'social' in special_instructions:
            needs.append('companionship')
            adl_requirements.append('Companionship')
        
        if 'meal' in special_instructions or 'cooking' in special_instructions:
            needs.append('meal_preparation')
            adl_requirements.append('Meal Planning & Preparation')
        
        if 'transport' in special_instructions or 'driving' in special_instructions:
            needs.append('transportation')
            adl_requirements.append('Transportation')
        
        # Determine urgency and complexity
        urgency_level = "medium"
        if any(urgent in medical_conditions for urgent in ['emergency', 'urgent', 'critical']):
            urgency_level = "high"
        elif not medical_conditions:
            urgency_level = "low"
        
        complexity = "moderate"
        if len(needs) > 3 or any(complex in medical_conditions for complex in ['multiple', 'severe', 'advanced']):
            complexity = "complex"
        elif len(needs) <= 1:
            complexity = "simple"
        
        return {
            "primary_needs": needs,
            "adl_requirements": list(set(adl_requirements)),
            "specializations": list(set(specializations)),
            "urgency_level": urgency_level,
            "complexity": complexity,
            "key_considerations": ["Fallback analysis - consider upgrading to AI for better matching"]
        }
    
    def _fallback_caretaker_matching(self, client_needs: Dict[str, Any], caretakers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback matching when AI is not available"""
        matches = []
        client_adls = set(client_needs.get('adl_requirements', []))
        
        for caretaker in caretakers:
            caretaker_adls = set(caretaker.get('adl_services', []))
            
            # Calculate basic compatibility
            adl_overlap = len(client_adls.intersection(caretaker_adls))
            total_client_needs = len(client_adls)
            
            if total_client_needs == 0:
                confidence_score = 50  # Neutral score if no specific needs
            else:
                confidence_score = min(95, (adl_overlap / total_client_needs) * 100)
            
            # Only include matches with reasonable confidence
            if confidence_score >= 30:
                match = {
                    "caretaker_id": caretaker.get('id'),
                    "confidence_score": int(confidence_score),
                    "match_explanation": f"Fallback matching: {adl_overlap}/{total_client_needs} ADL services match",
                    "strengths": list(client_adls.intersection(caretaker_adls)),
                    "concerns": list(client_adls - caretaker_adls) if client_adls - caretaker_adls else [],
                    "compatibility_factors": {
                        "adl_alignment": int(confidence_score),
                        "experience_match": 70,  # Default experience score
                        "specialization_fit": 60  # Default specialization score
                    },
                    "caretaker_details": caretaker
                }
                matches.append(match)
        
        # Sort by confidence score
        matches.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        print(f"🔄 Fallback matching generated {len(matches)} matches")
        return matches

<<<<<<< HEAD
# Create a global instance
ai_service = AIMatchingService()
=======
# Create a function to get a fresh AI service instance
def get_ai_service():
    """Get a fresh AI service instance to avoid caching issues"""
    return AIMatchingService()
>>>>>>> d64a6b179ece6be9698eefc95792fe1c2432388b
