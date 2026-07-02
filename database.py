import sqlite3

DB_NAME = "bancos.db"

def inicializar_db():
    """Cria a tabela de bancos se ela não existir."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bancos (
                ispb TEXT,
                name TEXT,
                code INTEGER,
                fullName TEXT
            )
        """)
        conn.commit()

def salvar_bancos(lista_bancos):
    """Limpa a tabela atual e insere os novos bancos vindos da API."""
    inicializar_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bancos")  # Evita duplicatas ao sincronizar
        
        dados_insercao = [
            (b.get("ispb"), b.get("name"), b.get("code"), b.get("fullName"))
            for b in lista_bancos
        ]
        
        cursor.executemany(
            "INSERT INTO bancos (ispb, name, code, fullName) VALUES (?, ?, ?, ?)",
            dados_insercao
        )
        conn.commit()
        return len(dados_insercao)

def listar_todos_bancos():
    """Retorna todos os bancos em formato de dicionários para processamento em memória."""
    inicializar_db()
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        cursor = conn.cursor()
        cursor.execute("SELECT ispb, name, code, fullName FROM bancos")
        rows = cursor.fetchall()
        # Converte para lista de dicionários (Exigência do roteiro)
        return [dict(row) for row in rows]