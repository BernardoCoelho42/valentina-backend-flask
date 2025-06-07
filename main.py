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
  "A história é interativa, episódica, com começo, meio e fim, dividida em exatamente 10 episódios numerados. "
  "Valentina e Teodoro são dois irmãos aventureiros, encarregados de desvendar um mistério ou cumprir uma missão especial. "
  "Cada episódio apresenta uma nova cena narrativa (curta, com no máximo 3 frases por parágrafo) e um enigma no final. "
  "Os enigmas devem ser de um dos seguintes tipos: "
  "1) Matemática simples (soma, subtração, multiplicação, divisão, equações de 1º grau); "
  "2) Gramática ou ortografia normativa (concordância, tempo verbal); "
  "3) Tradução de palavras do inglês para o português. "
  "Os enigmas devem ser sempre de múltipla escolha com 5 alternativas (A–E), com apenas UMA resposta correta. "
  "Nunca use enigmas ambíguos ou interpretativos. Não use pegadinhas, trocadilhos ou respostas abertas. "
  "Após o enigma, espere a resposta do jogador. "
  "Se o jogador responder corretamente (A–E), continue para o próximo episódio, apresentando a nova cena e novo enigma. "
  "Jamais explique porque a resposta estava certa. Apenas avance a história. "
  "Se o jogador errar, apresente um cenário extra com um novo enigma (sem avançar a história principal). "
  "Quando ele acertar esse enigma extra, retome imediatamente a linha narrativa principal com o episódio seguinte. "
  "Se o jogador digitar 'ligar para o papai', responda com uma dica enigmática e afetuosa, mas nunca revele a resposta. "
  "Se o jogador enviar uma mensagem livre, responda como narrador, mas não avance a história sem que ele resolva o enigma atual. "
  "Sempre comece sua resposta com '✅ Resposta correta!' ou '❌ Resposta errada!', exatamente assim. "
  "A aventura termina no Episódio 10 com uma conclusão narrativa clara. "
  "Obedeça rigorosamente a todas essas regras. Seja criativo, elegante, sombrio e lúdico."
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
