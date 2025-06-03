from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import traceback
import json

app = Flask(__name__)
CORS(app)  # libera CORS para qualquer origem
print("▶ Servidor Flask iniciado")

# --- Chave da OpenAI ---
openai.api_key = os.getenv("OPENAI_API_KEY") or "CHAVE_AQUI"

# ---------------------------------------------------------
@app.before_request
def log_request():
    print(f"▶ Recebido {request.method} em {request.path}")

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200

@app.route('/jogar', methods=['POST', 'OPTIONS'])
def jogar():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    try:
        print("▶ chamando /jogar()")
        raw_data = request.get_data(as_text=True)
        print("   RAW:", raw_data[:120])

        try:
            data = json.loads(raw_data) if raw_data else {}
        except json.JSONDecodeError as e:
            raise ValueError("JSON inválido") from e

        mensagem = data.get('mensagem')
        if not mensagem:
            raise ValueError("Campo 'mensagem' ausente")

        prompt = (
            f"Crie uma história com o tema '{mensagem}' envolvendo Valentina e Teodoro. "
            "A história deve incluir desafios matemáticos e lógicos adequados para crianças."
        )
        print("   prompt:", prompt[:120], "...")

        # Chamada à OpenAI
        print("   ▶ enviando requisição para a OpenAI...")
        resposta = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            temperature=0.7
        )
        print("   ◀ resposta recebida")

        story = resposta.choices[0].text.strip()
        print("   história gerada (100 chars):", story[:100].replace("\n", " "))

        return jsonify({'resposta': story}), 200

    except ValueError as ve:
        print("❌ Validação:", ve)
        return jsonify({'erro': str(ve)}), 400

    except openai.error.OpenAIError as e:
        print("❌ OpenAIError:", e)
        traceback.print_exc()
        return jsonify({'erro': f'Falha na OpenAI: {str(e)}'}), 500

    except Exception as e:
        print("❌ Exceção genérica:", e)
        traceback.print_exc()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

# --- Outras rotas de utilidade ----------------------------------
@app.route('/url', methods=['GET'])
def mostrar_url():
    return jsonify({"url": request.host_url})

@app.route('/ping', methods=['POST'])
def ping():
    return jsonify({"status": "pong"}), 200

# ---------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
