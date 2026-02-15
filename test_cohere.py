import cohere
from src.core.config import Settings


co = cohere.ClientV2(api_key=Settings().API_KEY)

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": "TELL me a joke about programmers",
        }
    ],
)

print(response.message.content[0].text)

reps=co.chat_stream(model="command-a-03-2025", messages=[ { 'role':"user",
                     'content': "TELL me a joke about programmers" }])

for chunk in reps:
    if chunk.type=="content-delta":
        print(chunk.delta.message.content.text, end="", flush=True)