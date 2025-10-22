from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__, static_folder='.')
CORS(app, resources={r"/*": {"origins": "*"}})

# Carrega banco de dados do JSON
def load_phrases():
    """Carrega frases do arquivo JSON"""
    json_file = Path('phrases.json')
    
    if not json_file.exists():
        print("⚠️  Arquivo phrases.json não encontrado. Usando dados de exemplo.")
        return get_example_phrases()
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            phrases = json.load(f)
        print(f"✅ Carregado: {len(phrases)} frases do banco de dados")
        return phrases
    except Exception as e:
        print(f"❌ Erro ao carregar JSON: {e}")
        return get_example_phrases()

def get_example_phrases():
    """Retorna frases de exemplo caso o JSON não exista"""
    return [
        {
            "id": 1,
            "japanese": "私は毎日日本語を勉強します。",
            "furigana": "わたしは まいにち にほんごを べんきょうします。",
            "translation": "Eu estudo japonês todos os dias.",
            "keywords": ["勉強", "毎日", "日本語"],
            "level": "N5",
            "formality": "formal"
        }
    ]

# Carrega frases ao iniciar o servidor
phrases_db = load_phrases()

@app.route('/')
def index():
    """Serve a página HTML"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Arquivo index.html não encontrado!", 404

@app.route('/tatuebando-logo.png')
def serve_logo():
    """Serve a logo"""
    return send_from_directory('.', 'tatuebando-logo.png')

@app.route('/api/search', methods=['GET'])
def search():
    """Busca frases por palavra-chave"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    results = []
    query_lower = query.lower()
    
    for phrase in phrases_db:
        # Busca em japonês, furigana, tradução e keywords
        if (query in phrase['japanese'] or 
            query in phrase['furigana'] or 
            query_lower in phrase['translation'].lower() or
            any(query in keyword for keyword in phrase['keywords'])):
            results.append(phrase)
    
    return jsonify(results)

@app.route('/api/phrases', methods=['GET'])
def get_all_phrases():
    """Retorna todas as frases"""
    return jsonify(phrases_db)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas do banco de dados"""
    levels = {}
    for phrase in phrases_db:
        level = phrase.get('level', 'N/A')
        levels[level] = levels.get(level, 0) + 1
    
    return jsonify({
        "total": len(phrases_db),
        "by_level": levels
    })

@app.route('/api/reload', methods=['POST'])
def reload_database():
    """Recarrega o banco de dados do JSON (útil após adicionar frases)"""
    global phrases_db
    phrases_db = load_phrases()
    return jsonify({
        "success": True,
        "total": len(phrases_db),
        "message": "Banco de dados recarregado com sucesso!"
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))  # Mudou de 5000 para 8080
    print("\n" + "="*50)
    print("🚀 Servidor Flask iniciado!")
    print(f"📊 Total de frases carregadas: {len(phrases_db)}")
    print(f"🌐 Acesse: http://0.0.0.0:{port}")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=port, debug=True)