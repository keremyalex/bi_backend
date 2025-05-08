from openai import OpenAI
import os

client = OpenAI(api_key="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")

def generar_sql_desde_prompt(prompt, esquema):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en SQL que genera consultas PostgreSQL basadas en el esquema proporcionado."},
            {"role": "user", "content": f"Esquema de la base de datos:\n{esquema}"},
            {"role": "user", "content": f"Instrucción del usuario: {prompt}"}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()