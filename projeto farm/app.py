from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('items.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/list')
def list_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('list.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        item = request.form['item']
        conn = get_db_connection()
        conn.execute('INSERT INTO items (name) VALUES (?)', (item,))
        conn.commit()

        # Após adicionar o item, pega a lista atualizada de itens
        items = conn.execute('SELECT * FROM items').fetchall()
        conn.close()

        # Retorna apenas o HTML da lista de itens para o AJAX
        return render_template('item_list.html', items=items)
    
    # Para GET request, renderiza a página normalmente
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('add.html', items=items)


@app.route('/remove', methods=['GET', 'POST'])
def remove():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()

    if request.method == 'POST':
        item_ids = request.form.getlist('item_id')  # Extrai a lista de IDs dos checkboxes marcados
        if item_ids:
            conn = get_db_connection()
            conn.executemany('DELETE FROM items WHERE id = ?', [(item_id,) for item_id in item_ids])
            conn.commit()
            conn.close()
        return redirect(url_for('remove'))

    return render_template('remove.html', items=items)


# Inicializa o banco de dados
def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()  # Cria a tabela se não existir
    app.run(debug=True)
