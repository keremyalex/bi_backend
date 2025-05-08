from openai import OpenAI

client = OpenAI(api_key="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")  # reemplaza con tu clave real

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Dame un ejemplo de consulta SQL para una tabla de productos"}
    ]
)

print(response.choices[0].message.content)
