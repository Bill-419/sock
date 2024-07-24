import sqlite3

DB_PATH = 'data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS table_metadata (
            table_name TEXT PRIMARY KEY
        )
    ''')
    
    conn.commit()
    conn.close()

def create_table(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            row INTEGER,
            col INTEGER,
            text TEXT,
            foreground TEXT,
            background TEXT,
            alignment INTEGER,
            font_bold BOOLEAN,
            font_size INTEGER,
            row_height INTEGER,
            column_width INTEGER
        )
    ''')
    
    cursor.execute('INSERT OR IGNORE INTO table_metadata (table_name) VALUES (?)', (table_name,))
    
    conn.commit()
    conn.close()

def save_data(table_name, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {table_name}')
    
    for cell_data in data:
        cursor.execute(f'''
            INSERT INTO {table_name} (row, col, text, foreground, background, alignment, font_bold, font_size, row_height, column_width)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cell_data['row'], cell_data['col'], cell_data['text'], cell_data['foreground'], cell_data['background'],
            cell_data['alignment'], cell_data['font']['bold'], cell_data['font']['size'], cell_data['row_height'], cell_data['column_width']
        ))
    
    conn.commit()
    conn.close()
    from redis_client import save_data_to_redis  # 动态导入以避免循环依赖
    save_data_to_redis(table_name, data)

def load_data(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    conn.close()
    
    data = []
    for row in rows:
        data.append({
            'row': row[1],
            'col': row[2],
            'text': row[3],
            'foreground': row[4],
            'background': row[5],
            'alignment': row[6],
            'font': {
                'bold': row[7],
                'size': row[8]
            },
            'row_height': row[9],
            'column_width': row[10]
        })
    
    return data

def append_row(table_name, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT MAX(row) FROM {table_name}')
    max_row = cursor.fetchone()[0]
    new_row_idx = (max_row + 1) if max_row is not None else 0
    
    for cell_data in data:
        cursor.execute(f'''
            INSERT INTO {table_name} (row, col, text, foreground, background, alignment, font_bold, font_size, row_height, column_width)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_row_idx, cell_data['col'], cell_data['text'], cell_data['foreground'], cell_data['background'],
            cell_data['alignment'], cell_data['font']['bold'], cell_data['font']['size'], cell_data['row_height'], cell_data['column_width']
        ))
    
    conn.commit()
    conn.close()
    # Reload data and update Redis
    new_data = load_data(table_name)
    from redis_client import save_data_to_redis  # 动态导入以避免循环依赖
    save_data_to_redis(table_name, new_data)

def delete_last_row(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT MAX(row) FROM {table_name}')
    max_row = cursor.fetchone()[0]
    
    if max_row is not None:
        cursor.execute(f'DELETE FROM {table_name} WHERE row = ?', (max_row,))
    
    conn.commit()
    conn.close()
    # Reload data and update Redis
    new_data = load_data(table_name)
    from redis_client import save_data_to_redis  # 动态导入以避免循环依赖
    save_data_to_redis(table_name, new_data)
