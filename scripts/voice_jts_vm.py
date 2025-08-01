#!/usr/bin/env python3
"""
Voice JTS Assistant - VM Connected Version
Connects to VM's JTS knowledge base via SSH with better error handling
"""

import os
import sys
import time
import json
import subprocess
import speech_recognition as sr
from openai import OpenAI
import tempfile
import paramiko
import threading
import queue

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import API keys
try:
    from config.api_keys import OPENAI_API_KEY, GEMINI_API_KEY
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY
except ImportError:
    print("⚠️  API keys not found, using environment variables")

# VM Configuration
VM_CONFIG = {
    'hostname': '34.69.34.151',
    'username': 'akaclinicalco',
    'port': 22,
    'timeout': 10
}

def init_speech_recognition():
    """Initialize speech recognition"""
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("🎤 Initializing speech recognition...")
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.pause_threshold = 2.5  # Longer pause before stopping
            recognizer.energy_threshold = 300  # Lower energy threshold
        
        print("✅ Microphone initialized")
        print("🎤 Adjusting for ambient noise...")
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Speech recognition ready")
        return recognizer, microphone
        
    except Exception as e:
        print(f"❌ Speech recognition failed: {e}")
        return None, None

def convert_medical_abbreviations(text):
    """Convert medical abbreviations for better TTS pronunciation"""
    replacements = {
        'mg': 'milligrams',
        'kg': 'kilograms',
        'mcg': 'micrograms',
        'ml': 'milliliters',
        'iv': 'intravenous',
        'im': 'intramuscular',
        'rsi': 'rapid sequence intubation',
        'txa': 'tranexamic acid',
        'prn': 'as needed',
        'q': 'every',
        'bid': 'twice daily',
        'tid': 'three times daily',
        'qd': 'once daily'
    }
    
    for abbrev, full in replacements.items():
        text = text.replace(f' {abbrev} ', f' {full} ')
        text = text.replace(f'{abbrev} ', f'{full} ')
        text = text.replace(f' {abbrev}', f' {full}')
    
    return text

def speak_response(text):
    """Speak the response using OpenAI TTS with fallback"""
    try:
        # Convert medical abbreviations for better pronunciation
        text_for_tts = convert_medical_abbreviations(text)
        
        # Try OpenAI TTS first (better quality)
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            client = OpenAI(api_key=api_key)
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=text_for_tts
                )
                response.write_to_file(f.name)
                
                # Play on Mac
                subprocess.run(['afplay', f.name], check=True)
                os.unlink(f.name)
                print("🔊 Natural voice played successfully")
                return
        
        # Fallback to gTTS
        from gtts import gTTS
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tts = gTTS(text=text_for_tts, lang='en', slow=False)
            tts.save(f.name)
            subprocess.run(['afplay', f.name], check=True)
            os.unlink(f.name)
            print("🔊 Voice played successfully")
            
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        print(f"📝 Response: {text}")

def listen_for_speech(recognizer, microphone, timeout=30):
    """Listen for speech input"""
    try:
        with microphone as source:
            print("🎤 Listening... (speak now)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=45)
            
        text = recognizer.recognize_google(audio)
        print(f"👤 You said: '{text}'")
        return text.lower()
        
    except sr.WaitTimeoutError:
        print("❌ No speech detected within timeout")
        return None
    except sr.UnknownValueError:
        print("❌ Could not understand audio - try speaking louder")
        return None
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return None

def extract_weight_and_drug(text):
    """Extract weight and drug from text"""
    import re
    
    # Weight patterns
    weight_patterns = [
        r'(\d+)\s*kg',
        r'(\d+)\s*kilograms',
        r'(\d+)\s*kilos',
        r'patient\s+weighs\s+(\d+)',
        r'(\d+)\s*kg\s+patient',
        r'patient\s+(\d+)\s*kg',
        r'(\d+)\s*lb',
        r'(\d+)\s*pounds'
    ]
    
    # Drug patterns
    drugs = {
        'ketamine': 'ketamine',
        'ket': 'ketamine',
        'rocuronium': 'rocuronium',
        'roc': 'rocuronium',
        'rock': 'rocuronium',
        'succinylcholine': 'succinylcholine',
        'succ': 'succinylcholine',
        'fentanyl': 'fentanyl',
        'fent': 'fentanyl',
        'morphine': 'morphine',
        'midazolam': 'midazolam',
        'midaz': 'midazolam',
        'propofol': 'propofol',
        'etomidate': 'etomidate',
        'tranexamic acid': 'tranexamic acid',
        'txa': 'tranexamic acid',
        'calcium': 'calcium gluconate',
        'furosemide': 'furosemide',
        'lasix': 'furosemide'
    }
    
    weight = None
    drug = None
    
    # Extract weight
    for pattern in weight_patterns:
        match = re.search(pattern, text.lower())
        if match:
            weight = float(match.group(1))
            # Convert pounds to kg if needed
            if 'lb' in pattern or 'pounds' in pattern:
                weight = weight * 0.453592
            break
    
    # Extract drug
    text_lower = text.lower()
    for drug_key, drug_name in drugs.items():
        if drug_key in text_lower:
            drug = drug_name
            break
    
    return weight, drug

def calculate_dose(weight, drug, indication):
    """Calculate drug dose based on weight and indication"""
    dosing_protocols = {
        'ketamine': {
            'rsi': (2.0, 'mg/kg', 'IV'),
            'pain': (0.5, 'mg/kg', 'IV'),
            'sedation': (1.0, 'mg/kg', 'IV')
        },
        'rocuronium': {
            'rsi': (1.0, 'mg/kg', 'IV'),
            'paralysis': (1.0, 'mg/kg', 'IV')
        },
        'succinylcholine': {
            'rsi': (1.5, 'mg/kg', 'IV'),
            'paralysis': (1.5, 'mg/kg', 'IV')
        },
        'fentanyl': {
            'pain': (1.0, 'mcg/kg', 'IV'),
            'analgesia': (1.0, 'mcg/kg', 'IV')
        },
        'morphine': {
            'pain': (0.1, 'mg/kg', 'IV'),
            'analgesia': (0.1, 'mg/kg', 'IV')
        },
        'midazolam': {
            'sedation': (0.05, 'mg/kg', 'IV'),
            'anxiolysis': (0.02, 'mg/kg', 'IV')
        },
        'propofol': {
            'sedation': (1.0, 'mg/kg', 'IV'),
            'induction': (2.0, 'mg/kg', 'IV')
        },
        'etomidate': {
            'rsi': (0.3, 'mg/kg', 'IV'),
            'induction': (0.3, 'mg/kg', 'IV')
        },
        'tranexamic acid': {
            'trauma': (1.0, 'g', 'IV'),  # Fixed dose
            'hemorrhage': (1.0, 'g', 'IV')  # Fixed dose
        },
        'calcium gluconate': {
            'hypocalcemia': (1.0, 'g', 'IV'),  # Fixed dose
            'cardiac': (1.0, 'g', 'IV')  # Fixed dose
        },
        'furosemide': {
            'diuresis': (0.5, 'mg/kg', 'IV'),
            'fluid_overload': (0.5, 'mg/kg', 'IV')
        }
    }
    
    if drug not in dosing_protocols:
        return None, None, None
    
    if indication not in dosing_protocols[drug]:
        return None, None, None
    
    dose, unit, route = dosing_protocols[drug][indication]
    
    # Calculate total dose if weight-based
    if '/kg' in unit:
        total_dose = dose * weight
        return total_dose, unit, route
    else:
        # Fixed dose
        return dose, unit, route

def test_vm_connection():
    """Test connection to VM"""
    try:
        print("🔍 Testing VM connection...")
        
        # Try simple SSH command
        cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'echo Connection successful'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ VM connection successful")
            return True
        else:
            print(f"❌ VM connection failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ VM connection timeout (2FA may be required)")
        return False
    except Exception as e:
        print(f"❌ VM connection error: {e}")
        return False

def query_jts_vm_simple(question):
    """Query JTS knowledge base on VM using simple SSH"""
    try:
        # Escape the question for shell
        escaped_question = question.replace("'", "'\"'\"'")
        
        # Create a simple Python script that directly calls the main function
        python_script = f"""
#!/usr/bin/env python3
import sys
import os

# Add the project path
sys.path.append('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')

# Change to the project directory
os.chdir('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')

# Import and run the main function from ask_balanced.py
from scripts.ask_balanced import main

# Set up the question as if it was input
import builtins
original_input = builtins.input

def mock_input(prompt=""):
    return "{escaped_question}"

builtins.input = mock_input

# Run the main function
try:
    main()
except Exception as e:
    print(f"Error: {{e}}")
finally:
    builtins.input = original_input
"""
        
        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_script)
            script_path = f.name
        
        # Copy script to VM and execute
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/query_jts.py"
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && python3 ~/query_jts.py'"
        
        print(f"🔍 Querying JTS knowledge base...")
        
        # Copy script
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Execute script
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        # Clean up
        os.unlink(script_path)
        subprocess.run(f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'rm ~/query_jts.py'", shell=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ SSH error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ SSH timeout")
        return None
    except Exception as e:
        print(f"❌ SSH error: {e}")
        return None

def query_jts_vm_script(question):
    """Query JTS knowledge base using a script file - alternative method"""
    try:
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(f"""#!/bin/bash
cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols
source venv/bin/activate

# Create a Python script to query the knowledge base
cat > ~/temp_query.py << 'EOF'
import sys
sys.path.append('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')
from scripts.ask_balanced import load_model, load_embeddings, search_context, generate_response

model = load_model()
embedding_model, index, metadata = load_embeddings()

if embedding_model and index and metadata:
    context = search_context("{question}", embedding_model, index, metadata)
    if context:
        response = generate_response("{question}", context, model)
        print(response)
    else:
        print("No relevant JTS protocol found.")
else:
    print("Failed to load JTS knowledge base.")
EOF

python3 ~/temp_query.py
rm ~/temp_query.py
""")
            script_path = f.name
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Copy script to VM and execute
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/query_jts.sh"
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'chmod +x ~/query_jts.sh && ~/query_jts.sh'"
        
        print(f"🔍 Querying JTS knowledge base (method 2)...")
        
        # Copy script
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Execute script
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        # Clean up
        os.unlink(script_path)
        subprocess.run(f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'rm ~/query_jts.sh'", shell=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ SSH error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ SSH timeout")
        return None
    except Exception as e:
        print(f"❌ SSH error: {e}")
        return None

def query_jts_vm_fast(question):
    """Query JTS knowledge base using fast direct search"""
    try:
        # Escape the question for shell
        escaped_question = question.replace("'", "'\"'\"'")
        
        # Create a simple script that just searches the database
        python_script = f"""
#!/usr/bin/env python3
import sys
import os
import json
import faiss
from sentence_transformers import SentenceTransformer

# Add the project path
sys.path.append('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols')

try:
    # Load the embedding model
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load FAISS index
    print("Loading FAISS index...")
    index = faiss.read_index('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/faiss.idx')
    
    # Load metadata
    print("Loading metadata...")
    with open('/home/akaclinicalco/Voice-Assistant-AI-Bot-Offline-JTS-Protocols/embeds/meta.json', 'r') as f:
        metadata = json.load(f)
    
    print(f"Index has {{index.ntotal}} entries")
    
    # Search for relevant context
    question_embedding = model.encode(["{escaped_question}"])
    distances, indices = index.search(question_embedding, 3)
    
    # Get relevant chunks
    relevant_chunks = []
    for idx in indices[0]:
        if idx < len(metadata):
            relevant_chunks.append(metadata[idx])
    
    if relevant_chunks:
        print("Found relevant JTS protocols:")
        for i, chunk in enumerate(relevant_chunks[:2]):  # Show top 2
            if isinstance(chunk, dict):
                if 'text' in chunk:
                    print(f"Chunk {{i+1}}: {{chunk['text'][:200]}}...")
                elif 'content' in chunk:
                    print(f"Chunk {{i+1}}: {{chunk['content'][:200]}}...")
                else:
                    print(f"Chunk {{i+1}}: {{str(chunk)[:200]}}...")
            else:
                print(f"Chunk {{i+1}}: {{str(chunk)[:200]}}...")
    else:
        print("No relevant JTS protocols found")
        
except Exception as e:
    print(f"Error: {{e}}")
    import traceback
    traceback.print_exc()
"""
        
        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_script)
            script_path = f.name
        
        # Copy script to VM and execute
        scp_cmd = f"scp {script_path} {VM_CONFIG['username']}@{VM_CONFIG['hostname']}:~/query_jts_fast.py"
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'cd ~/Voice-Assistant-AI-Bot-Offline-JTS-Protocols && source venv/bin/activate && python3 ~/query_jts_fast.py'"
        
        print(f"🔍 Querying JTS knowledge base (fast method)...")
        
        # Copy script
        subprocess.run(scp_cmd, shell=True, check=True, timeout=15)
        
        # Execute script
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        # Clean up
        os.unlink(script_path)
        subprocess.run(f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} 'rm ~/query_jts_fast.py'", shell=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ SSH error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ SSH timeout")
        return None
    except Exception as e:
        print(f"❌ SSH error: {e}")
        return None

def query_jts_rest_api(question):
    """Query JTS knowledge base using REST API service"""
    try:
        import requests
        import json
        
        print(f"🔍 Querying JTS knowledge base via REST API...")
        
        # Make request to the REST API
        url = "http://34.69.34.151:5000/query"
        data = {"question": question}
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response from JTS API')
        else:
            print(f"❌ REST API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ REST API timeout")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ REST API connection error")
        return None
    except Exception as e:
        print(f"❌ REST API error: {e}")
        return None

def query_jts_rest_api_ssh(question):
    """Query JTS knowledge base using REST API service via SSH"""
    try:
        print(f"🔍 Querying JTS knowledge base via REST API (SSH)...")
        
        # Use SSH to make a curl request to the local service
        curl_cmd = f'curl -s -X POST http://localhost:5000/query -H "Content-Type: application/json" -d \'{{"question": "{question}"}}\''
        ssh_cmd = f"ssh {VM_CONFIG['username']}@{VM_CONFIG['hostname']} '{curl_cmd}'"
        
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                import json
                response_data = json.loads(result.stdout)
                return response_data.get('response', 'No response from JTS API')
            except json.JSONDecodeError:
                return result.stdout.strip()
        else:
            print(f"❌ REST API SSH error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ REST API SSH timeout")
        return None
    except Exception as e:
        print(f"❌ REST API SSH error: {e}")
        return None

def get_jts_protocol_info(question, drug=None):
    """Get JTS protocol information from local knowledge base"""
    jts_protocols = {
        'ketamine': {
            'rsi': {
                'dose': '2 mg/kg IV',
                'route': 'IV',
                'indications': 'Rapid sequence intubation, procedural sedation',
                'contraindications': 'Known hypersensitivity, severe hypertension',
                'monitoring': 'Blood pressure, heart rate, respiratory rate',
                'notes': 'May cause hypertension and increased ICP. Avoid in head injury if possible.'
            },
            'pain': {
                'dose': '0.5 mg/kg IV',
                'route': 'IV',
                'indications': 'Acute pain management',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Blood pressure, heart rate',
                'notes': 'Lower dose than RSI. Monitor for dissociative effects.'
            },
            'sedation': {
                'dose': '1 mg/kg IV',
                'route': 'IV',
                'indications': 'Procedural sedation',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Blood pressure, heart rate, respiratory rate',
                'notes': 'Intermediate dose between pain and RSI.'
            }
        },
        'rocuronium': {
            'rsi': {
                'dose': '1 mg/kg IV',
                'route': 'IV',
                'indications': 'Rapid sequence intubation',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Neuromuscular blockade monitoring',
                'notes': 'Intermediate-acting neuromuscular blocker. Duration 30-60 minutes.'
            },
            'paralysis': {
                'dose': '1 mg/kg IV',
                'route': 'IV',
                'indications': 'Neuromuscular blockade',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Neuromuscular blockade monitoring',
                'notes': 'Same dose as RSI indication.'
            }
        },
        'succinylcholine': {
            'rsi': {
                'dose': '1.5 mg/kg IV',
                'route': 'IV',
                'indications': 'Rapid sequence intubation',
                'contraindications': 'Burns >24h, crush injuries, neuromuscular disease',
                'monitoring': 'Neuromuscular blockade monitoring',
                'notes': 'Ultra-short acting. Duration 5-10 minutes. Risk of hyperkalemia.'
            }
        },
        'fentanyl': {
            'pain': {
                'dose': '1 mcg/kg IV',
                'route': 'IV',
                'indications': 'Severe pain management',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Respiratory rate, oxygen saturation',
                'notes': 'Potent opioid. Monitor for respiratory depression.'
            }
        },
        'morphine': {
            'pain': {
                'dose': '0.1 mg/kg IV',
                'route': 'IV',
                'indications': 'Moderate to severe pain',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Respiratory rate, oxygen saturation',
                'notes': 'Standard opioid for pain management.'
            }
        },
        'midazolam': {
            'sedation': {
                'dose': '0.05 mg/kg IV',
                'route': 'IV',
                'indications': 'Sedation, anxiolysis',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Respiratory rate, oxygen saturation',
                'notes': 'Benzodiazepine. Monitor for respiratory depression.'
            }
        },
        'propofol': {
            'sedation': {
                'dose': '1 mg/kg IV',
                'route': 'IV',
                'indications': 'Procedural sedation',
                'contraindications': 'Known hypersensitivity, egg allergy',
                'monitoring': 'Blood pressure, respiratory rate',
                'notes': 'May cause hypotension. Monitor blood pressure closely.'
            }
        },
        'etomidate': {
            'rsi': {
                'dose': '0.3 mg/kg IV',
                'route': 'IV',
                'indications': 'Rapid sequence intubation',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Blood pressure, adrenal function',
                'notes': 'Minimal hemodynamic effects. May cause adrenal suppression.'
            }
        },
        'tranexamic acid': {
            'trauma': {
                'dose': '1 g IV over 10 minutes',
                'route': 'IV',
                'indications': 'Trauma-related hemorrhage',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Blood pressure, bleeding',
                'notes': 'Antifibrinolytic. Give within 3 hours of injury.'
            }
        },
        'calcium gluconate': {
            'hypocalcemia': {
                'dose': '1 g IV',
                'route': 'IV',
                'indications': 'Hypocalcemia, calcium channel blocker toxicity',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Calcium levels, cardiac function',
                'notes': 'Give slowly. Monitor for arrhythmias.'
            }
        },
        'furosemide': {
            'diuresis': {
                'dose': '0.5 mg/kg IV',
                'route': 'IV',
                'indications': 'Fluid overload, pulmonary edema',
                'contraindications': 'Known hypersensitivity',
                'monitoring': 'Urine output, electrolytes',
                'notes': 'Loop diuretic. Monitor potassium levels.'
            }
        }
    }
    
    # Determine indication from question
    question_lower = question.lower()
    indication = None
    
    if 'rsi' in question_lower or 'rapid sequence' in question_lower:
        indication = 'rsi'
    elif 'pain' in question_lower:
        indication = 'pain'
    elif 'trauma' in question_lower:
        indication = 'trauma'
    elif 'sedation' in question_lower:
        indication = 'sedation'
    elif 'paralysis' in question_lower:
        indication = 'paralysis'
    elif 'hypocalcemia' in question_lower:
        indication = 'hypocalcemia'
    elif 'diuresis' in question_lower or 'fluid' in question_lower:
        indication = 'diuresis'
    
    # Get protocol info
    if drug and drug in jts_protocols:
        if indication and indication in jts_protocols[drug]:
            protocol = jts_protocols[drug][indication]
            return f"JTS Protocol - {drug.title()} {indication.upper()}: {protocol['dose']}, Route: {protocol['route']}, Monitoring: {protocol['monitoring']}, Notes: {protocol['notes']}"
        else:
            # Return all available indications for the drug
            indications = list(jts_protocols[drug].keys())
            return f"JTS Protocol - {drug.title()}: Available indications: {', '.join(indications)}"
    
    return None

def get_ai_enhanced_response(question, weight=None, drug=None, jts_response=None, conversation_history=None):
    """Get AI-enhanced response combining dose calculation and JTS knowledge"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return get_fallback_response(question, weight, drug, jts_response)
        
        client = OpenAI(api_key=api_key)
        
        # Build context information
        context_info = []
        if weight:
            context_info.append(f"Patient weight: {weight:.1f} kg")
        if drug:
            context_info.append(f"Drug: {drug}")
        if jts_response:
            context_info.append(f"JTS Protocol: {jts_response[:300]}...")
        
        context_str = "\n".join(context_info) if context_info else "No specific context"
        
        SYSTEM_PROMPT = f"""You are a calm, experienced paramedic assisting another paramedic in the field. Your job is to provide accurate, brief, and helpful advice in a stressful prehospital environment.

Context: {context_str}

IMPORTANT RULES:
- Be concise and tactical - time is critical
- Use bullet points for medication responses
- If weight and drug are provided, calculate the total dose
- If JTS protocol info is available, reference it
- Keep responses under 100 words
- Use tactical language appropriate for emergency medicine
- If information is incomplete, ask for what's missing

Format medication responses as:
- Drug: X mg (Y mg/kg)
- Route: IV/IM
- Caution: [key warnings]"""

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history[-4:])  # Last 2 exchanges
        
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.1
        )
        
        assistant_reply = response.choices[0].message.content
        
        # Update conversation history
        if conversation_history is not None:
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            # Keep only last 6 messages to prevent memory bloat
            if len(conversation_history) > 6:
                conversation_history = conversation_history[-6:]
        
        return assistant_reply
        
    except Exception as e:
        print(f"❌ AI error: {e}")
        return get_fallback_response(question, weight, drug, jts_response)

def get_fallback_response(question, weight=None, drug=None, jts_response=None):
    """Fallback response when AI is unavailable"""
    if weight and drug:
        # Try to determine indication from question
        question_lower = question.lower()
        indication = None
        
        if 'rsi' in question_lower or 'rapid sequence' in question_lower:
            indication = 'rsi'
        elif 'pain' in question_lower:
            indication = 'pain'
        elif 'trauma' in question_lower:
            indication = 'trauma'
        elif 'sedation' in question_lower:
            indication = 'sedation'
        elif 'paralysis' in question_lower:
            indication = 'paralysis'
        
        if indication:
            calculated_dose = calculate_dose(weight, drug, indication)
            if calculated_dose[0]:
                dose, unit, route = calculated_dose
                if '/kg' in unit:
                    total_dose = dose
                    unit_display = unit.replace('/kg', '')
                    return f"{drug.title()}: {total_dose:.1f} {unit_display}\nRoute: {route}"
                else:
                    return f"{drug.title()}: {dose} {unit}\nRoute: {route}"
        
        # Try to get JTS protocol info
        jts_info = get_jts_protocol_info(question, drug)
        if jts_info:
            return f"{drug.title()}: Need indication (RSI, pain, sedation, etc.)\n\n{jts_info}"
        else:
            return f"{drug.title()}: Need indication (RSI, pain, sedation, etc.)"
    elif jts_response:
        return f"JTS Protocol: {jts_response[:100]}..."
    else:
        # Try to get JTS protocol info even without weight
        jts_info = get_jts_protocol_info(question, drug)
        if jts_info:
            return f"I need more information. Please specify patient weight and medication.\n\n{jts_info}"
        else:
            return "I need more information. Please specify patient weight and medication."

def test_jts_access():
    """Test if we can access the JTS database on the VM"""
    try:
        print("🧪 Testing JTS database access...")
        
        # Simple test query
        test_question = "ketamine RSI"
        result = query_jts_rest_api(test_question)
        
        if result and len(result.strip()) > 10:
            print("✅ JTS database access successful")
            print(f"📋 Sample response: {result[:100]}...")
            return True
        else:
            print("❌ JTS database access failed")
            return False
            
    except Exception as e:
        print(f"❌ JTS test failed: {e}")
        return False

def main():
    """Main voice assistant loop"""
    print("🎤 VOICE JTS ASSISTANT (VM CONNECTED)")
    print("=" * 50)
    print("Voice + Full JTS Knowledge Base on VM")
    
    # Test VM connection first
    vm_connected = test_vm_connection()
    if not vm_connected:
        print("⚠️  VM connection failed. You may need to:")
        print("   1. Complete 2FA authentication")
        print("   2. Check network connectivity")
        print("   3. Verify VM is running")
        print("   Continuing with local knowledge base...")
    else:
        # Test JTS database access
        jts_accessible = test_jts_access()
        if not jts_accessible:
            print("⚠️  JTS database access failed, using local knowledge base...")
            vm_connected = False
    
    print("🎤 Initializing speech recognition...")
    
    # Initialize speech recognition
    recognizer, microphone = init_speech_recognition()
    if not recognizer or not microphone:
        print("❌ Failed to initialize speech recognition")
        return
    
    # Initialize conversation tracking
    conversation_history = []
    
    # Context memory for multi-turn conversations
    context = {
        'weight': None,
        'drug': None,
        'indication': None,
        'last_question': None
    }
    
    print("✅ Ready! Ask for drug doses or clinical guidance.")
    print("💡 Try: 'Ketamine RSI for 80 kg patient', 'TXA protocol', 'Goodbye'")
    
    while True:
        try:
            # Listen for speech
            question = listen_for_speech(recognizer, microphone)
            if not question:
                print("Please try speaking again...")
                continue
            
            if 'goodbye' in question or 'exit' in question or 'quit' in question:
                print("👋 Take care!")
                break
                
            print("🧠 Processing...")
            start_time = time.time()
            
            # Extract weight and drug from current question
            weight, drug = extract_weight_and_drug(question)
            
            # Update context with new information
            if weight:
                context['weight'] = weight
                print(f"💾 Remembered weight: {weight:.1f} kg")
            if drug:
                context['drug'] = drug
                print(f"💾 Remembered drug: {drug}")
            
            # Determine indication from question
            question_lower = question.lower()
            if 'rsi' in question_lower or 'rapid sequence' in question_lower:
                context['indication'] = 'rsi'
            elif 'pain' in question_lower:
                context['indication'] = 'pain'
            elif 'trauma' in question_lower:
                context['indication'] = 'trauma'
            elif 'sedation' in question_lower:
                context['indication'] = 'sedation'
            
            context['last_question'] = question
            
            # Show current context
            if context['weight']:
                print(f"📋 Current context: {context['weight']:.1f} kg patient")
            
            # Use context to fill in missing information
            final_weight = weight or context['weight']
            final_drug = drug or context['drug']
            final_indication = context['indication']
            
            # Query JTS knowledge base on VM if connected
            jts_response = None
            if vm_connected and ('protocol' in question.lower() or 'guideline' in question.lower() or final_drug):
                print("🔍 Querying JTS knowledge base on VM...")
                
                # Try direct REST API first (fastest), then fallback to SSH methods
                jts_response = query_jts_rest_api(question)
                if not jts_response:
                    print("Direct REST API failed, trying REST API via SSH...")
                    jts_response = query_jts_rest_api_ssh(question)
                if not jts_response:
                    print("REST API SSH failed, trying SSH methods...")
                    jts_response = query_jts_vm_fast(question)
                if not jts_response:
                    print("Fast SSH method failed, trying simple method...")
                    jts_response = query_jts_vm_simple(question)
                if not jts_response:
                    print("Simple SSH method failed, trying script method...")
                    jts_response = query_jts_vm_script(question)
                
                if jts_response:
                    print("✅ JTS data retrieved from VM")
                else:
                    print("⚠️  JTS query failed, using local knowledge")
            
            # Generate response combining local dose calculation and JTS knowledge
            if vm_connected and jts_response:
                # Use AI with JTS data if available
                response = get_ai_enhanced_response(
                    question, 
                    final_weight, 
                    final_drug, 
                    jts_response, 
                    conversation_history
                )
            else:
                # Use local dose calculation when VM fails
                response = get_fallback_response(
                    question, 
                    final_weight, 
                    final_drug, 
                    jts_response
                )
            
            processing_time = time.time() - start_time
            print(f"🤖 Me ({processing_time:.1f}s): {response}")
            
            # Speak response
            speak_response(response)
            
        except KeyboardInterrupt:
            print("\n👋 Take care!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            speak_response("Sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    main() 