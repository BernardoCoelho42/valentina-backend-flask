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
    "Após cada cena, você deve apresentar um enigma. O enigma deve ser sempre de um destes três tipos: "
    "1) Matemática simples (soma, subtração, multiplicação, divisão ou equações de 1º grau); "
    "2) Tradução de palavras do inglês para o português; "
    "3) Gramática e ortografia (concordância verbal, tempo verbal ou ortografia normativa). "
    "O enigma deve ser sempre no formato múltipla escolha, com cinco alternativas (A, B, C, D, E). "
    "Apenas uma das alternativas deve estar correta. A pergunta deve ser direta e clara. "
    "Jamais use ambiguidade, trocadilhos, lógica indireta, pegadinhas ou interpretação subjetiva. "
    "A resolução do enigma deve ser possível sem depender da narrativa. "
    "A cena serve apenas como contexto visual e lúdico, nunca como base lógica. "
    "Jamais escreva a história inteira de uma vez. "
    "Depois de apresentar o enigma, pare. Aguarde a resposta do jogador (A–E). "
    "Se o jogador responder com A–E, continue a história com o próximo episódio e novo enigma. "
    "Se o jogador pedir para ligar para o papai, responda com uma dica enigmática e afetuosa — nunca com a resposta. "
    "Se o jogador enviar mensagem livre, responda como narrador, mas nunca avance a história sem resolução do enigma. "
    "Sempre comece a resposta à escolha do jogador com '✅ Resposta correta!' ou '❌ Resposta errada!', exatamente assim, no início. "
    "Nunca omita esses símbolos. Obedeça a todas essas regras com precisão."
    “Mantenha os textos narrativos curtos, com no máximo 3 frases por parágrafo, e evite descrições longas ou complexas.”
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
