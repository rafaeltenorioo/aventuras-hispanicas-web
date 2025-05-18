import os
import google.generativeai as genai

os.environ["GOOGLE_API_KEY"] = "AIzaSyBbbF0ei8UXYphd8BDJI_gjd1vlmW0UKg8"  # Substitua pela sua chave real
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')
try:
    response = model.generate_content("Olá!")
    print(response.text)
except Exception as e:
    print(f"Erro ao conectar com a API: {e}")