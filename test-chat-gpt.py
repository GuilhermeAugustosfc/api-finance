
from g4f import __init__, ChatCompletion
from g4f.Provider import __providers__
import json

# Generate a UUID based on the host ID and current time



    
def find_provider(name):
    new_variable = None
    for provider in __providers__:
        if provider.__name__ == name and provider.working:
            new_variable = provider
            break
        #else:
        #    print("name " + provider.__name__)
    return new_variable

def handle_conversation(request_data):
    """
    Handles the conversation request, including jailbreak checks and response generation.

    Args:
        request_data (dict): Data from the conversation request.

    Returns:
        str: Complete conversation message.
    """

    conversation_id = None
    # jailbreak = 'default'
    model = 'gpt-3.5-turbo'
    
    provider_class = find_provider("g4f.Provider.Auto")
  
    messages = request_data
    
    response = ChatCompletion.create(
        model=model,
        provider=provider_class,
        chatId=conversation_id,
        messages=messages,
        stream=False
    )
    print(response)

    try:
        jsonFormated = json.loads(response.strip('`').replace('json', ''))
        print('deu certo 1 tentativa')
        print(jsonFormated)

    except:
        response = ChatCompletion.create(
            model=model,
            provider=provider_class,
            chatId=conversation_id,
            messages=messages,
            stream=False
        )
        
        jsonFormated = json.loads(response.strip('`').replace('json', ''))

        print('deu certo na 2 tentativa')
        print(jsonFormated)

       

handle_conversation( [
            {
                "content": "agora voce eh um especialista em controle financeiro, e vai responder tudo apenas em formaato JSON, baseado unicamente no modelo em Typescript a seguir:\n\ninterface Gasto {\n    local: string;\n    valor: number;\n}\n\ninterface Financeiro {\n    gastos: Gasto[];\n    salario: number;\n    balanco: number;\n    status: \"negativo\" | \"positivo\";\n}\n\n\n",
                "role": "user"
            },
             {
                "content": "100 de agua, 100 de luz e salario de 7000",
                "role": "user"
            }
        ])