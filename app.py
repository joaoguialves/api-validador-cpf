# app.py - API de Validação de CPF
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

def validar_cpf(cpf):
    """
    Valida um CPF brasileiro usando o algoritmo oficial
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais (sequências inválidas)
    sequencias_invalidas = ['00000000000', '11111111111', '22222222222', 
                           '33333333333', '44444444444', '55555555555',
                           '66666666666', '77777777777', '88888888888', 
                           '99999999999']
    if cpf in sequencias_invalidas:
        return False
    
    # Validação do primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    digito1 = 0 if resto >= 10 else resto
    
    if digito1 != int(cpf[9]):
        return False
    
    # Validação do segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    digito2 = 0 if resto >= 10 else resto
    
    if digito2 != int(cpf[10]):
        return False
    
    return True

def formatar_cpf(cpf):
    """
    Formata o CPF no padrão XXX.XXX.XXX-XX
    """
    cpf_limpo = re.sub(r'[^0-9]', '', cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf

@app.route('/')
def home():
    response = make_response(jsonify({
        "message": "API de Validação de CPF",
        "endpoints": {
            "validar": "/validar/{cpf}",
            "validar_post": "/validar (POST)",
            "exemplo": "/validar/11144477735"
        }
    }))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/validar/<cpf>')
def validar_get(cpf):
    """
    Valida CPF via GET
    Uso: /validar/11144477735
    """
    valido = validar_cpf(cpf)
    
    response_data = {
        "cpf": cpf,
        "cpf_limpo": re.sub(r'[^0-9]', '', cpf),
        "valido": valido,
        "formatado": formatar_cpf(cpf) if valido else None,
        "mensagem": "CPF válido" if valido else "CPF inválido"
    }
    
    response = make_response(jsonify(response_data))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/validar', methods=['POST'])
def validar_post():
    """
    Valida CPF via POST
    Body: {"cpf": "111.444.777-35"}
    """
    data = request.get_json()
    
    if not data or 'cpf' not in data:
        response = make_response(jsonify({
            "erro": "CPF não fornecido",
            "exemplo": {"cpf": "111.444.777-35"}
        }), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    cpf = data['cpf']
    valido = validar_cpf(cpf)
    
    response_data = {
        "cpf": cpf,
        "cpf_limpo": re.sub(r'[^0-9]', '', cpf),
        "valido": valido,
        "formatado": formatar_cpf(cpf) if valido else None,
        "mensagem": "CPF válido" if valido else "CPF inválido"
    }
    
    response = make_response(jsonify(response_data))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/validar/lote', methods=['POST'])
def validar_lote():
    """
    Valida múltiplos CPFs de uma vez
    Body: {"cpfs": ["111.444.777-35", "123.456.789-10"]}
    """
    data = request.get_json()
    
    if not data or 'cpfs' not in data:
        response = make_response(jsonify({
            "erro": "Lista de CPFs não fornecida",
            "exemplo": {"cpfs": ["111.444.777-35", "123.456.789-10"]}
        }), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    resultados = []
    for cpf in data['cpfs']:
        valido = validar_cpf(cpf)
        resultados.append({
            "cpf": cpf,
            "valido": valido,
            "formatado": formatar_cpf(cpf) if valido else None
        })
    
    response_data = {
        "total": len(resultados),
        "validos": sum(1 for r in resultados if r['valido']),
        "invalidos": sum(1 for r in resultados if not r['valido']),
        "resultados": resultados
    }
    
    response = make_response(jsonify(response_data))
    response.headers['Content-Type'] = 'application/json'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
