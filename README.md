# CareBridge

A comprehensive care matching platform that connects elderly, disabled, veterans, and people with chronic conditions with qualified caretakers. Features AI-powered matching using Google Gemini API.

## 🚀 Demo Accounts

- **Client**: `client1` / `demo123`
- **Caretaker**: `caretaker1` / `demo123`  
- **Admin**: `admin` / `secret123`

## 🤖 AI-Powered Matching with Google Gemini API

### Implementation Overview

CareBridge uses Google's Gemini API to provide intelligent client-caretaker matching based on medical conditions, special instructions, and ADL (Activities of Daily Living) requirements.

### Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install google-generativeai python-dotenv
   ```

2. **Get Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the API key

3. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```env
   # Google Gemini API Configuration
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=carebridgedb
   DB_USER=nazeershaikh(use your localmachine name)
   DB_PASSWORD=
   
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

### AI Matching Architecture

#### 1. **AI Service Module** (`ai_matching.py`)

```python
import google.generativeai as genai
from typing import List, Dict, Any

class AIMatchingService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None  # Fallback mode
```

#### 2. **Client Needs Analysis**

The AI analyzes client medical conditions and special instructions:

```python
def analyze_client_needs(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
    medical_conditions = client_data.get('medical_conditions', '')
    special_instructions = client_data.get('special_instructions', '')
    
    prompt = f"""
    Analyze the following client information and extract their care needs:
    
    Medical Conditions: {medical_conditions}
    Special Instructions: {special_instructions}
    
    Please provide a JSON response with:
    - primary_needs: ["list of main care requirements"]
    - adl_requirements: ["specific ADL services needed"]
    - specializations: ["required specializations"]
    - urgency_level: "low/medium/high"
    - complexity: "simple/moderate/complex"
    """
    
    response = self.model.generate_content(prompt)
    return json.loads(response.text)
```

#### 3. **Caretaker Matching Algorithm**

The AI matches client needs with available caretakers:

```python
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
```

### Integration Points

#### 1. **Dashboard Integration** (`app.py`)

```python
from ai_matching import ai_service

@app.route("/dashboard")
@login_required
def dashboard():
    # ... existing code ...
    
    # If user is a client, get AI-powered matches
    if user_profile and user_profile.get('type') == 'client':
        try:
            # Analyze client needs
            client_needs = ai_service.analyze_client_needs(user_profile)
            
            # Get caretaker ADL services for matching
            caretakers_with_adls = []
            for caretaker in caretakers:
                caretaker_adls = db.get_caretaker_adls(caretaker['id'])
                caretaker['adl_services'] = [adl['service_type'] for adl in caretaker_adls if adl['is_available']]
                caretakers_with_adls.append(caretaker)
            
            # Get AI matches
            ai_matches = ai_service.match_caretakers(client_needs, caretakers_with_adls)
        except Exception as e:
            print(f"Error in AI matching: {e}")
            ai_matches = None
    
    return render_template("dashboard.html", 
                         username=username, 
                         user_profile=user_profile,
                         caretakers=caretakers,
                         ai_matches=ai_matches)
```

#### 2. **Dedicated AI Matches Page** (`/ai-matches`)

```python
@app.route("/ai-matches")
@login_required
def ai_matches():
    """AI-powered caretaker matching results page"""
    # ... get user profile and caretakers ...
    
    # Get AI analysis and matches
    try:
        client_needs = ai_service.analyze_client_needs(user_profile)
        ai_matches = ai_service.match_caretakers(client_needs, caretakers_with_adls)
    except Exception as e:
        print(f"Error in AI matching: {e}")
        client_needs = None
        ai_matches = None
    
    return render_template("ai_matches.html", 
                         username=username,
                         user_profile=user_profile,
                         client_needs=client_needs,
                         ai_matches=ai_matches)
```

### Fallback System

The system includes robust fallback logic when the Gemini API is unavailable:

```python
def _fallback_client_analysis(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback analysis when AI is not available"""
    medical_conditions = client_data.get('medical_conditions', '').lower()
    special_instructions = client_data.get('special_instructions', '').lower()
    
    # Simple keyword-based analysis
    needs = []
    if 'dementia' in medical_conditions or 'alzheimer' in medical_conditions:
        needs.append('dementia_care')
    if 'mobility' in medical_conditions or 'wheelchair' in medical_conditions:
        needs.append('mobility_assistance')
    if 'diabetes' in medical_conditions:
        needs.append('medication_management')
    
    return {
        "primary_needs": needs,
        "adl_requirements": needs,
        "specializations": needs,
        "urgency_level": "medium",
        "complexity": "moderate"
    }
```

### UI Components

#### 1. **Dashboard AI Matches Card**

```html
<!-- AI-Powered Matches (for clients only) -->
{% if user_profile and user_profile.type == 'client' and ai_matches %}
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">
  <h3 style="color: white; margin-top: 0;">
    🤖 AI-Powered Matches
    <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 12px; font-size: 0.7rem;">NEW</span>
  </h3>
  
  {% for match in ai_matches[:3] %}
    <div style="background: rgba(255,255,255,0.1); padding: 15px; margin: 10px 0; border-radius: 8px;">
      <h4>{{ match.caretaker_details.full_name }}</h4>
      <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 12px;">
        {{ match.confidence_score }}% match
      </span>
      <p>{{ match.match_explanation[:80] }}...</p>
    </div>
  {% endfor %}
</div>
{% endif %}
```

#### 2. **Detailed AI Matches Page** (`ai_matches.html`)

Features comprehensive matching results with:
- Client care needs analysis
- Confidence scoring for each match
- Detailed explanations of why each caretaker is recommended
- Caretaker strengths and specializations
- Contact information and availability
- Action buttons for contacting caretakers

### Key Features

- **Intelligent Analysis**: AI analyzes medical conditions and special instructions
- **Confidence Scoring**: Each match includes a percentage compatibility score
- **Detailed Explanations**: AI explains why each caretaker is a good fit
- **Fallback System**: Works without API key using keyword-based matching
- **Real-time Matching**: Generates fresh matches on each dashboard visit
- **Responsive UI**: Beautiful, modern interface with gradient designs

### Error Handling

The system gracefully handles API failures:
- Falls back to keyword-based matching
- Shows appropriate error messages
- Continues to function without AI features
- Logs errors for debugging

### Performance Considerations

- **Caching**: Consider implementing Redis caching for frequent matches
- **Rate Limiting**: Monitor API usage to stay within Gemini limits
- **Async Processing**: For large datasets, consider async matching
- **Database Optimization**: Index ADL services for faster queries

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **AI/ML**: Google Gemini API
- **Frontend**: HTML/CSS/JavaScript
- **Authentication**: bcrypt password hashing
- **Environment**: python-dotenv for configuration

## 📁 Project Structure

```
CareBridge/
├── app.py                 # Main Flask application
├── ai_matching.py         # AI service with Gemini integration
├── database.py            # Database operations
├── config.py              # Configuration management
├── seed.sql              # Database schema and sample data
├── templates/            # HTML templates
│   ├── dashboard.html    # Main dashboard with AI matches
│   ├── ai_matches.html   # Detailed AI matching results
│   └── ...
└── README.md             # This file
```

## 🚀 Getting Started

1. **Clone the repository**
2. **Set up PostgreSQL database**
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Configure environment variables** (see setup instructions above)
5. **Run database migrations**: `psql -d carebridgedb -f seed.sql`
6. **Start the application**: `python app.py`
7. **Visit**: `http://localhost:5004`

## 🔧 Development Notes

- The AI matching system works in both API and fallback modes
- All AI prompts are designed to return structured JSON responses
- The system is designed to be easily extensible for additional AI features
- Error handling ensures the application remains functional even if AI services fail

## 🚀 How to Run

### Prerequisites

Before running CareBridge, make sure you have the following installed on your system:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd CareBridge
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install flask psycopg2-binary bcrypt python-dotenv
```

### Step 4: Set Up Database

1. **Start PostgreSQL service** (if not already running)

2. **Create the database**:
   ```bash
   createdb carebridgedb
   ```

3. **Run the database schema and seed data**:
   ```bash
   psql -d carebridgedb -f seed.sql
   ```

### Step 5: Configure Environment (Optional)

Create a `.env` file in the project root for API keys (optional for basic functionality):

```bash
# .env file
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### Step 6: Run the Application

```bash
# Make sure you're in the project directory and virtual environment is activated
python app.py
```

### Step 7: Access the Application

Open your web browser and navigate to:
- **Main Application**: `http://localhost:5004`
- **Home Page**: `http://localhost:5004/`
- **Sign In**: `http://localhost:5004/signin`

### Demo Credentials

You can use these demo accounts to test the application:

**Client Account:**
- Username: `client1`
- Password: `demo123`

**Caretaker Account:**
- Username: `caretaker1`
- Password: `demo123`

### Troubleshooting

**Port Already in Use:**
```bash
# If port 5004 is in use, kill existing processes
pkill -f "python app.py"
# Or change the port in app.py
```

**Database Connection Issues:**
```bash
# Check if PostgreSQL is running
brew services start postgresql  # macOS
# or
sudo service postgresql start   # Linux
```

**Module Not Found Errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Database Permission Issues:**
```bash
# Create user with proper permissions
sudo -u postgres createuser --interactive
sudo -u postgres createdb carebridgedb
```

### Project Structure

```
CareBridge/
├── app.py                 # Main Flask application
├── database.py           # Database connection and operations
├── utils.py              # Utility functions
├── seed.sql              # Database schema and sample data
├── templates/            # HTML templates
│   ├── base.html
│   ├── carebridge_home.html
│   ├── dashboard.html
│   ├── edit_profile.html
│   ├── signin.html
│   ├── client_form.html
│   └── caretaker_form.html
├── static/               # Static assets (CSS, images)
├── venv/                 # Virtual environment
└── README.md
```

### Features Available

- ✅ User authentication (login/logout)
- ✅ Client and caretaker registration
- ✅ Profile management and editing
- ✅ Dashboard with available caretakers
- ✅ Responsive design
- ✅ Database integration
- ✅ Session management

### Next Steps

Once the application is running, you can:
1. Register as a client or caretaker
2. Edit your profile information
3. Browse available caretakers
4. Test the authentication system
5. Explore the responsive design

For development and customization, refer to the individual component documentation in the codebase.