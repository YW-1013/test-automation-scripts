from openai import OpenAI

client = OpenAI(api_key="YOUR_DEEPSEEK_API_KEY", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个全能助手"},
        {"role": "user", "content": "平板有哪些形态"},
    ],
    stream=False
)

print(response.choices[0].message.content)