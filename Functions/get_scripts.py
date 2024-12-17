from Functions.make_archives import write_to_sql_file
from Database.database import supabase
import os

async def get_scripts_type(Type1):
    response = supabase.table('Scripts').select("Type2, Scripts").eq("Type1", Type1).execute()
    if response.data:
        # Formatar a resposta
        formatted_responses = []
        for item in response.data:
            type2 = item['Type2']
            script = item['Scripts']
            formatted_response = f"**{type2}**:\n```sql\n{script}\n```"

            if len(formatted_response) > 2000:
                filename = write_to_sql_file(script)
                formatted_responses.append((None, filename))
            else:
                formatted_responses.append((formatted_response, None))
        
        return formatted_responses
    else:
        return [("Nenhum script encontrado para os tipos fornecidos.", None)]