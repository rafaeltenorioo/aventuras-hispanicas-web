from flask import Flask, render_template, request, jsonify, url_for
import os
import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai import types

app = Flask(__name__)

# Configurar a API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyBbbF0ei8UXYphd8BDJI_gjd1vlmW0UKg8"  # Substitua pela sua chave de API válida
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
MODEL_ID = "gemini-2.0-flash"

# Dicionário para armazenar o histórico de conversas por sessão de usuário
historico_conversas = {}

def agente_viagem_completo():
    return Agent(
        name="agente_viagem_completo",
        model=MODEL_ID,
        instruction="""
        Você é um planejador de viagens apaixonado e experiente especializado em países de língua espanhola.
        Você cria roteiros detalhados, fornece dicas úteis e ajuda os viajantes a se sentirem confiantes em suas aventuras.
        Converse em português do Brasil com entusiasmo e alegria!

        Siga estas etapas para planejar a viagem perfeita:

        1.  **Coleta Detalhada de Informações:**
            * Pergunte sobre o DESTINO (país, cidades específicas). Seja curioso sobre os lugares que o viajante sonha em conhecer!
            * Pergunte sobre a DURAÇÃO da viagem (número de dias) e se há flexibilidade.
            * Explore os INTERESSES do viajante (cultura, história, aventura, natureza, gastronomia, compras, vida noturna, etc.). Descubra o que faz o coração do viajante vibrar!
            * Pergunte sobre o ORÇAMENTO aproximado para adaptar as sugestões.
            * Pergunte sobre o TIPO DE VIAGEM (família, amigos, romântico, solo) para personalizar a experiência.
            * Pergunte sobre PREFERÊNCIAS DE HOSPEDAGEM (luxo, boutique, econômico, rústico, etc.).
            * Pergunte sobre o RITMO DE VIAGEM preferido (agitado, relaxado) e se há alguma NECESSIDADE ESPECIAL (acessibilidade, dieta, etc.).

        2.  **Criação de Roteiros Incríveis:**
            * Crie um roteiro DIÁRIO detalhado, equilibrando atividades, refeições, pontos turísticos e tempo livre.
            * Ofereça OPÇÕES ALTERNATIVAS para cada dia, considerando diferentes gostos e orçamentos.
            * Inclua informações práticas sobre TRANSPORTE (interno), como usar o metrô, ônibus ou táxis.
            * Sugira passeios OPCIONAIS (com custos estimados) para enriquecer a viagem.
            * Compartilhe CURIOSIDADES sobre os lugares, adicionando um toque especial ao roteiro.

        3.  **Dicas de Espanhol Prático:**
            * Prepare o viajante para situações comuns, fornecendo exemplos de DIÁLOGOS SIMULADOS em espanhol.
            * Inclua FRASES ÚTEIS para restaurantes, hotéis, lojas, transporte e emergências.
            * Incentive o viajante a praticar o idioma e a se conectar com os locais.

        4.  **Informações Essenciais:**
            * Forneça DICAS DE EMBALAGEM para diferentes climas e atividades.
            * Informe sobre a MELHOR ÉPOCA PARA VISITAR cada destino, considerando clima e eventos.
            * Dê informações atualizadas sobre SEGURANÇA e SAÚDE, incluindo vacinas e precauções.
            * Informe sobre MOEDA e CÂMBIO, incluindo dicas para economizar dinheiro.

        5.  **Tom de Voz Apaixonado:**
            * Seja ENTUSIASMADO, AMIGÁVEL e INSPIRADOR.
            * Use exclamações, perguntas retóricas e outras técnicas para demonstrar paixão por viagens.
            * Compartilhe suas próprias EXPERIÊNCIAS DE VIAGEM para conectar-se com o viajante.
            * Incentive o viajante a abraçar a cultura local e a criar memórias inesquecíveis.

        Exemplos de Diálogos:

        **Restaurante:**
        Chatbot: ¡Hola! Bienvenidos al restaurante. ¿Tienen reserva?
        Usuário: ...
        Chatbot: ¿Para cuántas personas?
        Usuário: ...
        Chatbot: Mesa para dos, perfecto.

        **Hotel:**
        Chatbot: Buenos días. Hotel Paraíso. ¿En qué puedo ayudarle?
        Usuário: ...
        Chatbot: ¿Qué tipo de habitación desea?
        Usuário: ...
        Chatbot: Tenemos individuales y dobles.

        Responda sempre em português do Brasil com a alma de um verdadeiro viajante!
        """,
        description="Planeja viagens para países de língua espanhola com paixão e conhecimento."
    )

def call_agent(agent, message_text=None):
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    content = types.Content(role="user", parts=[types.Part(text=message_text)]) if message_text else None
    response = "".join(event.content.parts[0].text for event in runner.run(user_id="user1", session_id="session1", new_message=content) if event.is_final_response())
    print(f"Mensagem recebida pela função call_agent: {message_text}")
    response = "".join(event.content.parts[0].text for event in runner.run(user_id="user1", session_id="session1", new_message=content) if event.is_final_response())
    print(f"Resposta gerada pela função call_agent: {response}")
    return response

def gerar_sugestoes_dinamicas(historico):
    if not historico:
        return [
            "Qual a melhor época para visitar a Espanha?",
            "O que fazer em Buenos Aires em 3 dias?",
            "Preciso de visto para entrar no México?",
            "Onde posso trocar dinheiro na Colômbia?",
            "Frases úteis em espanhol para turistas?"
        ]

    ultima_mensagem_usuario = historico[-1].get('content', '').lower() if historico else ""
    sugestoes = []

    if "argentina" in ultima_mensagem_usuario:
        sugestoes.extend(["O que te atrai na Argentina?", "Melhor época para visitar Buenos Aires?", "Opções de aventura na Patagônia?"])
    elif "méxico" in ultima_mensagem_usuario:
        sugestoes.extend(["Praias incríveis no México?", "Cultura e história mexicana?", "O que comer no México?"])
    elif "espanha" in ultima_mensagem_usuario:
        sugestoes.extend(["Roteiro por cidades da Espanha?", "Dicas de viagem para Barcelona?", "Gastronomia espanhola?"])
    elif "colômbia" in ultima_mensagem_usuario:
        sugestoes.extend(["O que fazer em Bogotá?", "Melhor época para visitar Cartagena?", "Dicas sobre café colombiano?"])
    elif "história" in ultima_mensagem_usuario:
        sugestoes.extend(["Sítios históricos para visitar?", "Qual período histórico te interessa?", "Museus imperdíveis?"])
    elif "praia" in ultima_mensagem_usuario or "natureza" in ultima_mensagem_usuario:
        sugestoes.extend(["Melhores trilhas?", "Atividades ao ar livre?", "Praias desertas?"])
    elif "roteiro" in ultima_mensagem_usuario or "dias" in ultima_mensagem_usuario:
        sugestoes.extend(["Sugestão de roteiro de 7 dias?", "Roteiro personalizado?", "Como se locomover?"])
    elif "orçamento" in ultima_mensagem_usuario or "caro" in ultima_mensagem_usuario or "barato" in ultima_mensagem_usuario:
        sugestoes.extend(["Opções de viagem econômica?", "Hotéis com bom custo-benefício?", "Dicas para economizar?"])
    elif "hospedagem" in ultima_mensagem_usuario or "hotel" in ultima_mensagem_usuario:
        sugestoes.extend(["Melhores bairros para se hospedar?", "Tipos de acomodação?", "Hotéis boutique?"])
    elif "visto" in ultima_mensagem_usuario or "documento" in ultima_mensagem_usuario:
        sugestoes.extend(["Preciso de visto para a Espanha?", "Documentos necessários para viajar?", "Seguro de viagem é obrigatório?"])
    elif "dinheiro" in ultima_mensagem_usuario or "câmbio" in ultima_mensagem_usuario:
        sugestoes.extend(["Onde trocar dinheiro?", "Qual a moeda local?", "Cartão de crédito é aceito?"])
    elif "língua" in ultima_mensagem_usuario or "espanhol" in ultima_mensagem_usuario:
        sugestoes.extend(["Frases úteis em espanhol?", "Como praticar espanhol durante a viagem?", "Aplicativos para tradução?"])

    return list(set(sugestoes[:5]))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    pergunta = request.form["mensagem"]
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = os.urandom(16).hex()

    agente = agente_viagem_completo()
    resposta = call_agent(agente, pergunta)
    resposta_formatada = resposta.replace('\n', '<br>')

    print(f"Pergunta recebida pelo backend: {pergunta}")
    print(f"Resposta gerada pelo agente: {resposta}")

    if session_id not in historico_conversas:
        historico_conversas[session_id] = []
    historico_conversas[session_id].append({'role': 'user', 'content': pergunta})

    sugestoes = gerar_sugestoes_dinamicas(historico_conversas[session_id])

    historico_conversas[session_id].append({'role': 'bot', 'content': resposta})

    response = jsonify({"resposta": resposta_formatada, "sugestoes": sugestoes})
    response.set_cookie('session_id', session_id, httponly=True)

    return response

if __name__ == "__main__":
    app.run(debug=True)