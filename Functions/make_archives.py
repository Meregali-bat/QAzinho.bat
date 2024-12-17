def write_to_sql_file(script, filename="script.sql"):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(script)
    return filename