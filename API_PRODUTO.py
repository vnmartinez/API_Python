from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

app = Flask(__name__)

# Simulação de dados para produtos, carrinho e pedidos
produtos = []
carrinho = {}
pedidos = []
avaliacoes = {}
comentarios = {}
usuarios = []
tokens_jwt = [] 

# Endpoints para Produtos
@app.route('/produtos', methods=['GET'])
def get_produtos():
    return jsonify(produtos)

@app.route('/produtos/<int:id>', methods=['GET'])
def get_produto(id):
    produto = next((p for p in produtos if p['id'] == id), None)
    if produto:
        return jsonify(produto)
    return jsonify({'message': 'Produto não encontrado'}), 404

@app.route('/produtos', methods=['POST'])
def criar_produto():
    data = request.get_json()
    if 'nome' in data and 'preco' in data:
        novo_produto = {
            'id': len(produtos) + 1,
            'nome': data['nome'],
            'preco': data['preco']
        }
        produtos.append(novo_produto)
        return jsonify(novo_produto), 201
    return jsonify({'message': 'Campos obrigatórios (nome e preço) não fornecidos'}), 400

@app.route('/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    data = request.get_json()
    produto = next((p for p in produtos if p['id'] == id), None)
    if produto:
        produto['nome'] = data.get('nome', produto['nome'])
        produto['preco'] = data.get('preco', produto['preco'])
        return jsonify(produto)
    return jsonify({'message': 'Produto não encontrado'}), 404

@app.route('/produtos/<int:id>', methods=['DELETE'])
def remover_produto(id):
    produto = next((p for p in produtos if p['id'] == id), None)
    if produto:
        produtos.remove(produto)
        return jsonify({'message': 'Produto removido com sucesso'})
    return jsonify({'message': 'Produto não encontrado'}), 404

# Endpoints para Carrinho de Compras
@app.route('/carrinho', methods=['GET'])
def get_carrinho():
    return jsonify(carrinho)

@app.route('/carrinho/adicionar', methods=['POST'])
def adicionar_ao_carrinho():
    data = request.get_json()
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade', 1)

    produto = next((p for p in produtos if p['id'] == produto_id), None)
    if produto:
        if produto_id in carrinho:
            carrinho[produto_id]['quantidade'] += quantidade
        else:
            carrinho[produto_id] = {'produto': produto, 'quantidade': quantidade}
        return jsonify({'message': 'Produto adicionado ao carrinho com sucesso'})
    return jsonify({'message': 'Produto não encontrado'}), 404

@app.route('/carrinho/atualizar/<int:id>', methods=['PUT'])
def atualizar_quantidade_carrinho(id):
    data = request.get_json()
    quantidade = data.get('quantidade')

    if id in carrinho:
        carrinho[id]['quantidade'] = quantidade
        return jsonify({'message': 'Quantidade do produto no carrinho atualizada com sucesso'})
    return jsonify({'message': 'Produto não encontrado no carrinho'}), 404

@app.route('/carrinho/remover/<int:id>', methods=['DELETE'])
def remover_do_carrinho(id):
    if id in carrinho:
        del carrinho[id]
        return jsonify({'message': 'Produto removido do carrinho com sucesso'})
    return jsonify({'message': 'Produto não encontrado no carrinho'}), 404

# Endpoints para Pedidos
@app.route('/pedidos', methods=['GET'])
def get_pedidos():
    return jsonify(pedidos)

@app.route('/pedidos/<int:id>', methods=['GET'])
def get_pedido(id):
    pedido = next((p for p in pedidos if p['id'] == id), None)
    if pedido:
        return jsonify(pedido)
    return jsonify({'message': 'Pedido não encontrado'}), 404

@app.route('/pedidos/criar', methods=['POST'])
def criar_pedido():
    carrinho = request.get_json()
    if carrinho:
        novo_pedido = {
            'id': len(pedidos) + 1,
            'carrinho': carrinho,
            'status': 'pendente'
        }
        pedidos.append(novo_pedido)
        return jsonify(novo_pedido), 201
    return jsonify({'message': 'Conteúdo do carrinho vazio'}), 400

@app.route('/pedidos/atualizar/<int:id>', methods=['PUT'])
def atualizar_status_pedido(id):
    data = request.get_json()
    status = data.get('status')

    pedido = next((p for p in pedidos if p['id'] == id), None)
    if pedido:
        pedido['status'] = status
        return jsonify({'message': 'Status do pedido atualizado com sucesso'})
    return jsonify({'message': 'Pedido não encontrado'}), 404

@app.route('/pedidos/cancelar/<int:id>', methods=['DELETE'])
def cancelar_pedido(id):
    pedido = next((p for p in pedidos if p['id'] == id), None)
    if pedido:
        pedidos.remove(pedido)
        return jsonify({'message': 'Pedido cancelado com sucesso'})
    return jsonify({'message': 'Pedido não encontrado'}), 404

app.route('/produtos/<int:id>/avaliacao', methods=['POST'])
def deixar_avaliacao(id):
    data = request.get_json()
    nota = data.get('nota')
    if nota is None or nota < 1 or nota > 5:
        return jsonify({'message': 'Nota inválida. A nota deve estar entre 1 e 5'}), 400

    if id in avaliacoes:
        avaliacoes[id].append(nota)
    else:
        avaliacoes[id] = [nota]

    return jsonify({'message': 'Avaliação adicionada com sucesso'})

@app.route('/produtos/<int:id>/avaliacoes', methods=['GET'])
def get_avaliacoes(id):
    if id in avaliacoes:
        return jsonify(avaliacoes[id])
    return jsonify({'message': 'Avaliações não encontradas para este produto'}), 404

@app.route('/produtos/<int:id>/comentario', methods=['POST'])
def deixar_comentario(id):
    data = request.get_json()
    comentario = data.get('comentario')

    if id in comentarios:
        comentarios[id].append(comentario)
    else:
        comentarios[id] = [comentario]

    return jsonify({'message': 'Comentário adicionado com sucesso'})

@app.route('/produtos/<int:id>/comentarios', methods=['GET'])
def get_comentarios(id):
    if id in comentarios:
        return jsonify(comentarios[id])
    return jsonify({'message': 'Comentários não encontrados para este produto'}), 404

class Usuario:
    def __init__(self, id, nome, email, senha):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha

# Endpoint para cadastrar um novo usuário
@app.route('/usuarios/novo', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()
    if 'nome' in data and 'email' in data and 'senha' in data:
        novo_usuario = Usuario(len(usuarios) + 1, data['nome'], data['email'], data['senha'])
        usuarios.append(novo_usuario)
        return jsonify({'message': 'Usuário cadastrado com sucesso'}), 201
    return jsonify({'message': 'Campos obrigatórios (nome, email e senha) não fornecidos'}), 400

# Endpoint para exibir todos os usuários cadastrados
@app.route('/usuarios', methods=['GET'])
@jwt_required()
def exibir_usuarios():
    if usuarios:
        lista_usuarios = [{'id': usuario.id, 'nome': usuario.nome, 'email': usuario.email} for usuario in usuarios]
        return jsonify(lista_usuarios)
    return jsonify({'message': 'Nenhum usuário encontrado'}), 404

# Endpoint para exibir um usuário específico
@app.route('/usuarios/<int:id>', methods=['GET'])
@jwt_required()
def exibir_usuario(id):
    usuario = next((u for u in usuarios if u.id == id), None)
    if usuario:
        return jsonify({'id': usuario.id, 'nome': usuario.nome, 'email': usuario.email})
    return jsonify({'message': 'Usuário não encontrado'}), 404

# Endpoint para verificar o login de um usuário e gerar um token JWT
@app.route('/login', methods=['POST'])
def verificar_login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    usuario = next((u for u in usuarios if u.email == email and u.senha == senha), None)
    if usuario:
        token = create_access_token(identity=usuario.id)
        tokens_jwt.append(token)  # Adiciona o token à lista de tokens JWT
        return jsonify({'message': 'Login bem-sucedido', 'access_token': token})
    return jsonify({'message': 'Credenciais inválidas'}), 401

def usuario_logado(pToken):
    return pToken in tokens_jwt

if __name__ == '__main__':
    app.run(debug=True)
