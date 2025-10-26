CareBridge
A comprehensive care matching platform that connects elderly, disabled, veterans, and people with chronic conditions with qualified caretakers. Features AI-powered matching using Google Gemini API.

🚀 Demo Accounts
Client: client1 / demo123

Caretaker: caretaker1 / demo123  

Admin: admin / secret123

🛠️ Technology Stack
Backend: Flask (Python)

Database: PostgreSQL

AI/ML: Google Gemini API

Frontend: HTML/CSS/JavaScript

Authentication: bcrypt password hashing

Environment: python-dotenv for configuration

🤖 Google Gemini API Integration
Overview
CareBridge uses Google's Gemini API to provide intelligent client-caretaker matching based on medical conditions, special instructions, and ADL (Activities of Daily Living) requirements. The AI analyzes client needs and matches them with the most suitable caretakers.

Implementation Details
1. AI Service Module (ai_matching.py)
The core AI functionality is implemented in a dedicated service class:

Python

class AIMatchingService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        
        if self.api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.ai_enabled = True
2. Client Needs Analysis
The AI analyzes medical conditions and special instructions to determine care requirements:

Python

def analyze_client_needs(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
    medical_conditions = client_data.get('medical_conditions', '')
    special_instructions = client_data.get('special_instructions', '')
    
    prompt = f"""
    Analyze the following client information and extract their care needs:
    
    Medical Conditions: {medical_conditions}
    Special Instructions: {special_instructions}
    
    Provide a JSON response with:
    - primary_needs: ["list of main care requirements"]
    - adl_requirements: ["specific ADL services needed"]
    - specializations: ["required caretaker specializations"]
    - urgency_level: "low/medium/high"
    - complexity: "simple/moderate/complex"
    """
    
    response = self.model.generate_content(prompt)
    return json.loads(response.text)
3. Intelligent Matching Algorithm
The AI matches client needs with available caretakers:

Python

def match_caretakers(self, client_needs: Dict[str, Any], caretakers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    prompt = f"""
    Match the following client needs with available caretakers:
    
    CLIENT NEEDS: {json.dumps(client_needs, indent=2)}
    AVAILABLE CARETAKERS: {json.dumps(caretaker_summaries, indent=2)}
    
    For each caretaker, provide:
    1. Match confidence score (0-100)
    2. Explanation of why they're a good match
    3. Specific strengths that align with client needs
    4. Any potential concerns or gaps
    """
    
    response = self.model.generate_content(prompt)
    return json.loads(response.text)
Key Features
🧠 Smart Analysis
Analyzes complex medical conditions (diabetes, dementia, mobility issues)

Understands special instructions and care preferences

Identifies required ADL services and specializations

Determines urgency level and complexity

🎯 Intelligent Matching
Matches clients with caretakers based on ADL service alignment

Considers experience, certifications, and specializations

Provides confidence scores (0-100%) for each match

Generates detailed explanations for recommendations

🛡️ Robust Fallback System
Works without API key using keyword-based matching

Graceful error handling and user-friendly messages

Maintains full functionality in offline mode

Seamless fallback when API is unavailable

🗣️ Voice Service Integration (ElevenLabs & Dictation)
Overview
CareBridge enhances accessibility with text-to-speech (TTS) narration for page content and voice dictation for form inputs. The system prioritizes the high-quality ElevenLabs API for TTS, with a fallback to the Browser Speech Synthesis API if the ElevenLabs key is missing or the service is unavailable. Voice dictation uses the Browser Speech Recognition API.

Implementation Details
1. TTS Service Module (elevenlabs_service.py)
The core TTS functionality is handled by a dedicated service class:

Python

class ElevenLabsService:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY', '')
        self.enabled = bool(self.api_key)
        # ... logic to fetch voices and set up API
2. API Endpoint (/api/text-to-speech)
The client-side JavaScript (voiceover.js) calls a Flask API endpoint to fetch audio:

Python

@app.route("/api/text-to-speech", methods=["POST"])
def api_text_to_speech():
    # ...
    audio_data = elevenlabs_service.text_to_speech(text)
    
    if audio_data:
        return Response(audio_data, mimetype='audio/mpeg')
    else:
        # Fallback instruction sent to client-side JavaScript
        return jsonify({"error": "Service unavailable", "fallback": "browser"}), 503
Configuration
Environment Variables
Add the following variable to your existing .env file to enable the ElevenLabs API:

Code snippet

# ElevenLabs TTS Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM # Optional: Default is 'Rachel'

# Google Gemini API Configuration
GEMINI_API_KEY=your_google_gemini_api_key_here
# ... (rest of .env file) ...
Getting Your ElevenLabs API Key
Visit ElevenLabs and create an account.

Navigate to your Profile or API Access section.

Generate or retrieve your API Key.

Add the key to the ELEVENLABS_API_KEY variable in your .env file.

Note: If the ELEVENLABS_API_KEY is not set, the system will gracefully fall back to the native browser text-to-speech functionality for all voice narration.

API Configuration
Environment Variables
Create a .env file in the project root:

Code snippet

# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=carebridgedb
DB_USER=your_username
DB_PASSWORD=your_password

# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
Getting Your API Key
Visit Google AI Studio

Sign in with your Google account

Click "Create API Key"

Copy the generated API key

Add it to your .env file

Integration Points
1. Dashboard Integration
The AI matches are displayed on the client dashboard:

Python

@app.route("/dashboard")
@login_required
def dashboard():
    # ... existing code ...
    
    # Get AI matches for clients
    if user_profile and user_profile.get('type') == 'client':
        client_needs = ai_service.analyze_client_needs(user_profile)
        ai_matches = ai_service.match_caretakers(client_needs, caretakers_with_adls)
    
    return render_template("dashboard.html", 
                         ai_matches=ai_matches)
2. Dedicated AI Matches Page
A comprehensive results page shows detailed analysis:

Python

@app.route("/ai-matches")
@login_required
def ai_matches():
    # ... get user profile and caretakers ...
    
    client_needs = ai_service.analyze_client_needs(user_profile)
    ai_matches = ai_service.match_caretakers(client_needs, caretakers_with_adls)
    
    return render_template("ai_matches.html", 
                         client_needs=client_needs,
                         ai_matches=ai_matches)
Example AI Analysis
Input:

JSON

{
  "medical_conditions": "Diabetes, mobility issues, needs help with daily activities",
  "special_instructions": "Requires medication management and assistance with mobility"
}
AI Output:

JSON

{
  "primary_needs": ["Diabetes management", "Mobility assistance", "ADL support"],
  "adl_requirements": ["medication_management", "mobility_assistance", "personal_care"],
  "specializations": ["Diabetes care", "Mobility support", "Medication management"],
  "urgency_level": "medium",
  "complexity": "moderate"
}
Matching Results:

David Kim: 85% match - Specializes in mobility assistance and physical therapy

Sarah Lee: 70% match - Has medication management experience for diabetes care

Maria Rodriguez: 50% match - Offers general housekeeping and meal preparation

Performance & Reliability
✅ Error Handling
JSON parsing with markdown code block removal

Decimal to float conversion for database values

Graceful fallback to keyword-based matching

Comprehensive error logging

⚡ Performance
Efficient prompt engineering for faster responses

Caching considerations for production deployment

Optimized database queries for ADL services

Real-time matching on each dashboard visit

🔒 Security
API key stored in environment variables

No sensitive data sent to external APIs

Client data anonymized in AI prompts

Secure fallback system

Future Enhancements
Caching: Implement Redis caching for frequent matches

Rate Limiting: Monitor API usage to stay within limits

Async Processing: Background matching for large datasets

Feedback Loop: Learn from user interactions to improve matching

Multi-language: Support for different languages in AI analysis

🚀 How to Run
Prerequisites
Before running CareBridge, make sure you have the following installed on your system:

Python 3.8+ - Download Python

PostgreSQL 14.9 - Download PostgreSQL

Git - Download Git

Step 1: Clone the Repository
Bash

git clone <repository-url>
cd CareBridge
Step 2: Set Up Virtual Environment
A virtual environment isolates your project's dependencies from other Python projects on your system. This is a best practice and helps avoid dependency conflicts.

Bash

# Create a virtual environment named 'venv'
python -m venv venv
Activate the virtual environment:

On macOS/Linux:

Bash

source venv/bin/activate
On Windows (Command Prompt):

Bash

venv\Scripts\activate.bat
On Windows (PowerShell):

Bash

venv\Scripts\Activate.ps1
You'll know your virtual environment is activated when you see (venv) at the beginning of your command prompt, like this:

Bash

(venv) user@computer CareBridge %
Step 3: Install Dependencies
With your virtual environment activated, install all required packages:

Bash

pip install -r requirements.txt
This will install:

Flask (web framework)

psycopg2-binary (PostgreSQL adapter)

bcrypt (password hashing)

google-generativeai (Google Gemini API)

python-dotenv (environment variable management)

And all other dependencies listed in requirements.txt

Note: If you ever need to deactivate the virtual environment, simply run:

Bash

deactivate
Step 4: Set Up Database
Start PostgreSQL service (if not already running)

Create the database:    bash    createdb carebridgedb    

Run the database schema and seed data:    bash    psql -d carebridgedb -f seed.sql    

Step 5: Configure Environment (Optional)
Create a .env file in the project root for API keys (optional for basic functionality):

Bash

# .env file
GEMINI_API_KEY=your_google_gemini_api_key_here
Step 6: Run the Application
Bash

# Make sure you're in the project directory and virtual environment is activated
python app.py
Step 7: Access the Application
Open your web browser and navigate to:

Main Application: http://localhost:5004

Home Page: http://localhost:5004/

Sign In: http://localhost:5004/signin

Demo Credentials
You can use these demo accounts to test the application:

Client Account:

Username: client1

Password: demo123

Caretaker Account:

Username: caretaker1

Password: demo123

Troubleshooting
Port Already in Use:

Bash

# If port 5004 is in use, kill existing processes
pkill -f "python app.py"
# Or change the port in app.py
Database Connection Issues:

Bash

# Check if PostgreSQL is running
brew services start postgresql  # macOS
# or
sudo service postgresql start   # Linux
Module Not Found Errors:

Bash

# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
Virtual Environment Issues:

Bash

# If 'venv' directory doesn't exist, create it
python -m venv venv

# If activation doesn't work, check your shell
# For PowerShell on Windows, you may need to enable script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# To verify virtual environment is active, check:
which python  # macOS/Linux (should show venv/bin/python)
where python  # Windows (should show venv\Scripts\python.exe)
Import Errors After Installing:

Bash

# Sometimes Python doesn't recognize newly installed packages
# Reinstall using the --force-reinstall flag:
pip install --force-reinstall -r requirements.txt

# Or upgrade pip first:
pip install --upgrade pip
Database Permission Issues:

Bash

# Create user with proper permissions
sudo -u postgres createuser --interactive
sudo -u postgres createdb carebridgedb
Project Structure
CareBridge/
├── app.py                 # Main Flask application
├── database.py           # Database connection and operations
├── utils.py              # Utility functions
├── seed.sql              # Database schema and sample data
├── templates/            # HTML templates
│   ├── base.html
│   ├── carebridge_home.html
│   ├── dashboard.html
│   ├── edit_profile.html
│   ├── signin.html
│   ├── client_form.html
│   └── caretaker_form.html
├── static/               # Static assets (CSS, images)
├── venv/                 # Virtual environment
└── README.md
Features Available
✅ User authentication (login/logout)

✅ Client and caretaker registration

✅ Profile management and editing

✅ Dashboard with available caretakers

✅ Responsive design

✅ Database integration

✅ Session management

Next Steps
Once the application is running, you can:

Register as a client or caretaker

Edit your profile information

Browse available caretakers

Test the authentication system

Explore the responsive design

For development and customization, refer to the individual component documentation in the codebase.