"""
Test Gemini API to see what's wrong
Run this to debug: python test_gemini.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("=" * 50)
print("GEMINI API DEBUG")
print("=" * 50)

# Check if API key exists
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file!")
    exit()

print(f"✅ API Key found: {api_key[:10]}...")
print()

# Try to use the API
print("Testing Gemini API...")
print()

try:
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    
    # List available models
    print("Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✅ {model.name}")
    
    print()
    print("Trying to generate content with gemini-pro...")
    
    # Try simplest model first
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'Hello, I am working!'")
    
    print(f"✅ SUCCESS! Response: {response.text}")
    print()
    print("Your Gemini API is working correctly!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    print("Possible issues:")
    print("1. API key is invalid")
    print("2. API not enabled in your Google Cloud project")
    print("3. Billing not enabled (though free tier should work)")
    print()
    print("Try creating a new API key at:")
    print("https://aistudio.google.com/app/apikey")
