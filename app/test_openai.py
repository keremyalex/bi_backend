from openai import OpenAI

client = OpenAI(api_key="")  # reemplaza con tu clave real

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Dame un ejemplo de consulta SQL para una tabla de productos"}
    ]
)

print(response.choices[0].message.content)
