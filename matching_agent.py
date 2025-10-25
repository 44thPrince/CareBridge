"""
CareBridge Matching Agent using Google ADK Loop Agent Protocol
This agent uses iterative reasoning to match patients with caregivers
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

from google import genai
from google.genai import types
from database import DatabasePersistence
from dotenv import load_dotenv

load_dotenv()

@dataclass
class MatchResult:
    """Represents a match between a patient and caregiver"""
    patient_id: int
    caregiver_id: int
    match_score: float
    compatibility_factors: Dict[str, Any]
    reasoning: str

class CareMatchingAgent:
    """
    Loop Agent for matching patients to caregivers using iterative reasoning.
    Implements Google ADK's Loop Agent protocol.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the matching agent"""
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY in .env file.")
        
        # Initialize the client
        self.client = genai.Client(api_key=self.api_key)
        self.db = DatabasePersistence()
        
        # System prompt for the matching agent
        self.system_instruction = """You are an expert caregiver matching specialist for CareBridge, 
        a platform that connects elderly patients with qualified caregivers.

        Your role is to analyze patient and caregiver profiles to find the best matches based on:
        1. Medical needs and caregiver qualifications
        2. Personality compatibility
        3. Schedule and logistics alignment
        4. Cultural and environmental fit
        5. Communication style preferences

        For each match, you must:
        - Calculate a compatibility score (0-100)
        - Identify key compatibility factors
        - Explain your reasoning
        - Consider potential challenges
        - Suggest specific conversation starters or compatibility notes

        Use iterative thinking to refine your matches, considering multiple factors 
        and their interactions before making final recommendations."""

    def _format_patient_profile(self, patient: Dict) -> str:
        """Format patient profile for the LLM"""
        return f"""
        Patient Profile:
        Name: {patient.get('full_name', 'N/A')}
        Location: {patient.get('patient_city', 'N/A')}, {patient.get('patient_state', 'N/A')}
        Language: {patient.get('language_preference', 'N/A')}
        
        Medical Needs:
        - Care Level Required: {patient.get('required_care_level', 'N/A')}
        - Mobility: {patient.get('level_of_mobility', 'N/A')}
        - Cognitive Status: {patient.get('cognitive_status', 'N/A')}
        - Fall Risk: {patient.get('fall_risk_level', 'N/A')}
        - Medical Conditions: {', '.join(patient.get('specific_medical_conditions', []) or ['None specified'])}
        - Required Services: {', '.join(patient.get('required_services', []) or ['None specified'])}
        - Safety Concerns: {patient.get('safety_concerns_notes', 'None')}
        
        Schedule:
        - Type: {patient.get('schedule_type', 'N/A')}
        - Continuity: {patient.get('care_continuity', 'N/A')}
        - Details: {patient.get('schedule_details', 'None')}
        
        Preferences:
        - Gender Preference: {patient.get('gender_preference', 'N/A')}
        - Temperament: {patient.get('preferred_temperament', 'N/A')}
        - Communication Style: {patient.get('communication_style', 'N/A')}
        - Social Preference: {patient.get('social_preference', 'N/A')}
        - Care Attitude: {patient.get('care_attitude', 'N/A')}
        - Routine Tolerance: {patient.get('routine_tolerance', 'N/A')}
        
        Environment:
        - Home Accessibility: {patient.get('home_accessibility', 'N/A')}
        - Smoking Policy: {patient.get('smoking_policy', 'N/A')}
        - Environment Factors: {', '.join(patient.get('environment_factors', []) or ['None'])}
        - Favorite Topics: {patient.get('favorite_topics', 'None')}
        - Topics to Avoid: {patient.get('topics_to_avoid', 'None')}
        
        Cultural/Religious:
        - Needs: {', '.join(patient.get('cultural_religious_needs', []) or ['None'])}
        - Details: {patient.get('cultural_religious_detail_notes', 'None')}
        """

    def _format_caregiver_profile(self, caregiver: Dict) -> str:
        """Format caregiver profile for the LLM"""
        return f"""
        Caregiver Profile:
        Name: {caregiver.get('full_name', 'N/A')}
        Phone: {caregiver.get('contact_phone', 'N/A')}
        Languages: {caregiver.get('spoken_languages', 'N/A')}
        
        Qualifications:
        - Certification: {caregiver.get('certification_level', 'N/A')}
        - Years Experience: {caregiver.get('years_experience', 'N/A')}
        - Physical Comfort: {caregiver.get('physical_comfort', 'N/A')}
        - Cognitive Experience: {caregiver.get('cognitive_experience', 'N/A')}
        - Safety Training: {caregiver.get('safety_training', 'N/A')}
        
        Experience:
        - Medical Conditions: {', '.join(caregiver.get('specific_condition_experience', []) or ['None'])}
        - Willing Duties: {', '.join(caregiver.get('willing_duties', []) or ['None'])}
        - Dietary Experience: {', '.join(caregiver.get('dietary_experience', []) or ['None'])}
        - Cultural Notes: {caregiver.get('cultural_notes', 'None')}
        
        Availability:
        - Type: {caregiver.get('availability_type', 'N/A')}
        - Commitment: {caregiver.get('commitment_type', 'N/A')}
        - Max Travel Distance: {caregiver.get('max_travel_distance', 'N/A')} miles
        - Details: {caregiver.get('detailed_availability', 'None')}
        
        Personality:
        - Gender Comfort: {caregiver.get('gender_comfort', 'N/A')}
        - Personality Profile: {caregiver.get('personality_profile', 'N/A')}
        - Communication Style: {caregiver.get('communication_style', 'N/A')}
        - Hobbies: {caregiver.get('hobbies', 'None')}
        
        Environment:
        - Home Access Comfort: {caregiver.get('home_access_comfort', 'N/A')}
        - Smoking Preference: {caregiver.get('smoking_preference', 'N/A')}
        - Environment Preferences: {', '.join(caregiver.get('environment_preferences', []) or ['None'])}
        - Interaction Preference: {caregiver.get('interaction_pref', 'N/A')}
        """

    def _create_matching_prompt(self, patient: Dict, caregivers: List[Dict]) -> str:
        """Create the prompt for matching a patient with multiple caregivers"""
        patient_profile = self._format_patient_profile(patient)
        
        caregiver_profiles = "\n\n".join([
            f"=== Caregiver #{idx + 1} (ID: {cg.get('id')}) ===\n{self._format_caregiver_profile(cg)}"
            for idx, cg in enumerate(caregivers)
        ])
        
        return f"""
        {patient_profile}
        
        ===================================
        AVAILABLE CAREGIVERS:
        ===================================
        {caregiver_profiles}
        
        ===================================
        TASK:
        ===================================
        Analyze each caregiver and determine their compatibility with this patient.
        
        For EACH caregiver, provide:
        1. A match score (0-100, where 100 is perfect match)
        2. Key compatibility factors (strengths and concerns)
        3. Detailed reasoning for the score
        4. Specific recommendations for successful pairing
        
        Consider ALL factors including:
        - Medical qualifications and care level match
        - Schedule and availability alignment
        - Personality and communication compatibility
        - Cultural and environmental fit
        - Experience with specific conditions
        - Geographic feasibility
        
        Format your response as JSON with this structure:
        {{
            "matches": [
                {{
                    "caregiver_id": <id>,
                    "match_score": <0-100>,
                    "compatibility_factors": {{
                        "medical_match": "explanation",
                        "schedule_fit": "explanation",
                        "personality_compatibility": "explanation",
                        "environmental_fit": "explanation",
                        "cultural_alignment": "explanation",
                        "strengths": ["strength1", "strength2"],
                        "concerns": ["concern1", "concern2"]
                    }},
                    "reasoning": "detailed explanation of why this score",
                    "recommendations": "specific advice for successful pairing"
                }}
            ],
            "overall_analysis": "summary of matching process and key insights"
        }}
        """

    def match_patient_to_caregivers(
        self, 
        patient_id: int, 
        caregiver_ids: Optional[List[int]] = None,
        max_iterations: int = 3
    ) -> tuple:
        """
        Use Loop Agent protocol to match a patient with caregivers.
        
        Args:
            patient_id: ID of the patient to match
            caregiver_ids: Optional list of specific caregiver IDs to consider
            max_iterations: Maximum number of reasoning iterations
            
        Returns:
            Tuple of (List[MatchResult], overall_analysis)
        """
        print(f"\n🔍 Starting matching process for patient {patient_id}...")
        
        # Fetch patient profile
        patient = self.db.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Fetch caregiver profiles
        if caregiver_ids:
            caregivers = [self.db.get_caregiver_by_id(cid) for cid in caregiver_ids]
            caregivers = [c for c in caregivers if c is not None]
        else:
            caregivers = self.db.get_all_caretakers()
        
        if not caregivers:
            raise ValueError("No caregivers available for matching")
        
        print(f"📋 Analyzing {len(caregivers)} caregivers...")
        
        # Create the matching prompt
        prompt = self._create_matching_prompt(dict(patient), [dict(c) for c in caregivers])
        
        # Loop Agent: Iterative reasoning process
        print(f"🤖 Initiating Loop Agent with max {max_iterations} iterations...\n")
        
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-thinking-exp-01-21',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.7,
                max_output_tokens=8000,
            )
        )
        
        # Extract and parse the response
        result_text = response.text
        print("✅ Analysis complete!\n")
        
        # Parse JSON response
        try:
            # Try to extract JSON from the response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                result_json = json.loads(result_text[json_start:json_end])
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"⚠️ Error parsing JSON response: {e}")
            print(f"Raw response:\n{result_text[:500]}...")
            # Create fallback response
            result_json = {
                "matches": [],
                "overall_analysis": "Error parsing response"
            }
        
        # Convert to MatchResult objects
        matches = []
        for match_data in result_json.get('matches', []):
            match = MatchResult(
                patient_id=patient_id,
                caregiver_id=match_data.get('caregiver_id'),
                match_score=float(match_data.get('match_score', 0)),
                compatibility_factors=match_data.get('compatibility_factors', {}),
                reasoning=match_data.get('reasoning', '')
            )
            matches.append(match)
        
        # Sort by score descending
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        print(f"🎯 Found {len(matches)} matches. Top score: {matches[0].match_score if matches else 0:.1f}")
        
        return matches, result_json.get('overall_analysis', '')

    def save_matches_to_db(self, matches: List[MatchResult]) -> List[int]:
        """Save match results to the database"""
        if not matches:
            return []
            
        # FIX: Delete previous matches for this patient before inserting new ones
        patient_id = matches[0].patient_id
        print(f"🔄 Clearing existing matches for patient {patient_id}...")
        self.db.delete_matches_by_patient(patient_id)

        match_ids = []
        for match in matches:
            match_id = self.db.create_match(
                patient_id=match.patient_id,
                caregiver_id=match.caregiver_id,
                match_score=match.match_score,
                compatibility_factors={
                    **match.compatibility_factors,
                    'reasoning': match.reasoning
                }
            )
            match_ids.append(match_id)
        return match_ids

    def run_matching_workflow(
        self, 
        patient_id: int,
        caregiver_ids: Optional[List[int]] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Complete matching workflow: analyze, match, and optionally save.
        
        Args:
            patient_id: Patient to match
            caregiver_ids: Optional specific caregivers to consider
            save_to_db: Whether to save results to database
            
        Returns:
            Dictionary with matches and analysis
        """
        # Run the matching
        matches, analysis = self.match_patient_to_caregivers(
            patient_id=patient_id,
            caregiver_ids=caregiver_ids
        )
        
        # Optionally save to database
        match_ids = []
        if save_to_db and matches:
            print("\n💾 Saving matches to database...")
            match_ids = self.save_matches_to_db(matches)
            print(f"✅ Saved {len(match_ids)} matches")
        
        return {
            'patient_id': patient_id,
            'matches': [
                {
                    'caregiver_id': m.caregiver_id,
                    'match_score': m.match_score,
                    'compatibility_factors': m.compatibility_factors,
                    'reasoning': m.reasoning,
                    'db_match_id': match_ids[i] if i < len(match_ids) else None
                }
                for i, m in enumerate(matches)
            ],
            'overall_analysis': analysis,
            'total_matches': len(matches)
        }


def main():
    """Example usage of the matching agent"""
    import sys
    
    # Initialize agent
    try:
        agent = CareMatchingAgent()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set GOOGLE_API_KEY in your .env file")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return
    
    # Get patient ID from command line or use default
    patient_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    print("="*60)
    print("   CareBridge Matching Agent - Loop Agent Protocol")
    print("="*60)
    
    try:
        # Run matching workflow
        results = agent.run_matching_workflow(
            patient_id=patient_id,
            save_to_db=True
        )
        
        # Display results
        print("\n" + "="*60)
        print("   MATCHING RESULTS")
        print("="*60)
        
        print(f"\n📊 Total Matches Found: {results['total_matches']}")
        print(f"\n🧠 Overall Analysis:\n{results['overall_analysis']}")
        
        print("\n🏆 Top Matches:")
        print("-"*60)
        
        for i, match in enumerate(results['matches'][:5], 1):
            print(f"\n#{i} Caregiver ID: {match['caregiver_id']}")
            print(f"   Score: {match['match_score']:.1f}/100")
            print(f"   Database Match ID: {match['db_match_id']}")
            
            factors = match['compatibility_factors']
            if 'strengths' in factors:
                print(f"   Strengths: {', '.join(factors['strengths'][:3])}")
            if 'concerns' in factors:
                print(f"   Concerns: {', '.join(factors['concerns'][:2])}")
            
            print(f"   Reasoning: {match['reasoning'][:150]}...")
        
        print("\n" + "="*60)
        print("✅ Matching complete!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()