import os
from flask import Flask, render_template, request, jsonify
from pyswip import Prolog
from google import genai

app = Flask(__name__)
prolog = Prolog()

try:
    prolog.consult("pvz.pl")
except Exception as e:
    print(f"Error al cargar Prolog: {e}")

# PON TU CLAVE AQUÍ ABAJO
client = genai.Client(api_key="AQ.Ab8RN6LK6yBntZkGHgDc1ld83Zajkbnmw5eKTJoF1dPk5ObcWA")

def consultar_prolog_interno(mensaje):
    """Consulta rápida a Prolog basada en palabras clave"""
    try:
        if "caracono" in mensaje:
            resultados = list(prolog.query("vence(Planta, zombi_caracono)"))
            plantas = [str(res["Planta"]) for res in resultados]
            return f"El zombi caracono es vulnerable a: {plantas}"
        if "girasol" in mensaje:
            return "costo(girasol, 50)"
    except Exception:
        pass
    return "Usa tu conocimiento general del juego para responder."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    datos = request.json
    mensaje_usuario = datos.get("message", "").lower()
    modo_seleccionado = datos.get("modo", "llm")
    
    contexto_logico = consultar_prolog_interno(mensaje_usuario)
    
    # Si seleccionas Prolog en el menú de la web
    if modo_seleccionado == "prolog":
        return jsonify({"response": f"Deducción de Prolog: {contexto_logico}"})
        
    # Si seleccionas LLM (Gemini) en el menú
    prompt = (
        "Eres el asistente experto del juego Plants vs. Zombies. "
        "Responde de forma natural y amigable a la pregunta del usuario. "
        f"Dato de la base de conocimientos local: {contexto_logico}\n\n"
        f"Pregunta del usuario: {mensaje_usuario}"
    )
    
    try:
        respuesta_llm = client.models.generate_content(
            model='gemini-3.8-flash', # Cámbialo si usaste otro modelo antes
            contents=prompt,
        )
        texto_final = respuesta_llm.text
    except Exception as e:
        texto_final = f"Error de IA: {e}"
    
    return jsonify({"response": texto_final})

if __name__ == "__main__":
    app.run(debug=False)
