from g4f import __init__, ChatCompletion
from g4f.Provider import __providers__
import json

def find_provider(name):
    for provider in __providers__:
        if provider.__name__ == name and provider.working:
            return provider
    return None

def generate_response_gpt(transcription):
    conversation_id = None
    model = 'gpt-3.5-turbo'

    # Find the appropriate provider
    provider_class = find_provider("g4f.Provider.Auto")

    # Construct the message list
    messages = [
        {
            "content": "agora voce eh um especialista em controle financeiro, e vai responder o texto acima tudo apenas em formato JSON, baseado unicamente no modelo em Typescript a seguir:\n\ninterface Gasto {\n  local: string;\n  valor: number;\n}\n\ninterface Financeiro {\n  gastos: Gasto[];\n  salario: number;\n  balanco: number;\n  status: \"negativo\" | \"positivo\";\n}\n\n\n  " + transcription,
            "role": "user"
        },
       
    ]

    # Generate GPT-3 response
    response = ChatCompletion.create(
        model=model,
        provider=provider_class,
        chatId=conversation_id,
        messages=messages,
        stream=False
    )
    print(response)
   
    try:
        responseGPTJSON = json.loads(response.strip('`').replace('json', ''))
    except:
        # Retry if parsing fails
        response = ChatCompletion.create(
            model=model,
            provider=provider_class,
            chatId=conversation_id,
            messages=messages,
            stream=False
        )
        responseGPTJSON = json.loads(response.strip('`').replace('json', ''))
    return responseGPTJSON
