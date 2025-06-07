from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import traceback
from openai import OpenAIError, OpenAI

app = Flask(__name__)
CORS(app)  # libera CORS para qualquer origem
print("▶ Servidor Flask iniciado")

# --- Chave da OpenAI ---
openai.api_key = os.getenv("OPENAI_API_KEY") or "CHAVE_AQUI"
client = OpenAI(api_key=openai.api_key)

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

        data = request.get_json(force=True, silent=False)
        print("▶ Dados recebidos:", data)

        tema = data.get('tema', '')
        historia = data.get('historia', '')
        resposta = data.get('resposta', '')
        acao = data.get('acao', '')
        mensagem = data.get('mensagem', '')

        mensagens = [
            {
                "role": "system",
                "content": (
                    "Você é o narrador de um RPG chamado Valentina & Teodoro – Versão Rigorosa. "
                    "A história é interativa, episódica e voltada para crianças de 8 a 12 anos. "
                    "A narrativa deve ter tom sombrio, irônico e refinadamente infantil, no estilo de Lemony Snicket. "
                    "Você nunca deve resolver os enigmas. Deve apresentar uma cena narrativa curta e, ao final, um enigma com cinco alternativas (A–E). "
                    "Depois de apresentar o enigma, pare. Espere a resposta do jogador. "
                    "Se o jogador responder com A–E, continue a história e apresente novo enigma. "
                    "Se o jogador pedir para ligar para o papai, responda com uma dica enigmática e afetuosa — nunca com a resposta. "
                    "Se o jogador enviar mensagem livre, interprete como diálogo, mas nunca avance a narrativa sem que ele resolva o enigma. "
                    "Toda resposta sua deve terminar em um novo enigma ou esperar o próximo comando do jogador. "
                    "Jamais escreva a história completa de uma vez. Obedeça às regras do sistema. Seja rigoroso."
                )
            },
            {"role": "user", "content": f"Tema: {tema}"},
            {"role": "user", "content": f"História até agora:\n{historia}"}
        ]

        if resposta:
            mensagens.append({"role": "user", "content": f"O jogador escolheu: {resposta}"})
        if acao == "ligar":
            mensagens.append({"role": "user", "content": "O jogador quer ligar para o papai."})
        if acao == "mensagem" and mensagem:
            mensagens.append({"role": "user", "content": f"O jogador escreveu: {mensagem}"})

        print("   ▶ enviando requisição para a OpenAI...")
        resposta_openai = client.chat.completions.create(
            model="gpt-4",
            messages=mensagens,
            temperature=0.7
        )
        print("   ◀ resposta recebida")

        story = resposta_openai.choices[0].message.content.strip()
        print("   história gerada (100 chars):", story[:100].replace("\n", " "))

        return jsonify({'resposta': story}), 200

    except ValueError as ve:
        print("❌ Validação:", ve)
        return jsonify({'erro': str(ve)}), 400

    except OpenAIError as e:
        print("❌ OpenAIError:", e)
        traceback.print_exc()
        return jsonify({'erro': f'Falha na OpenAI: {str(e)}'}), 500

    except Exception as e:
        print("❌ Exceção genérica:", e)
        traceback.print_exc()
        return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.route('/url', methods=['GET'])
def mostrar_url():
    return jsonify({"url": request.host_url})

@app.route('/ping', methods=['POST'])
def ping():
    return jsonify({"status": "pong"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
