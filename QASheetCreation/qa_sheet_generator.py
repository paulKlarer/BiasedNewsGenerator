from dotenv import load_dotenv

load_dotenv()

import json
from gen_ai_hub.proxy.native.openai import chat
from article_manager import ArticleManager

def formulate_question(article):
    #Generate a prompt a LLM would use to generate the following article. The prompt should start with the following sentence: 'Generate a politically far right article, with... ' The prompt shouldn't include all the specific information given in the text, the LLM should be creative in generating additional information that could fit the topic: 
    prompt = [{"role": "user", "content": "Generiere einen Prompt den ein LLM nutzen würde um den folgenden Artikel zu generieren. Der Prompt sollte mit dem folgenden Satz beginnen: 'Generiere einen politisch rechten Artikel...' Der Prompt sollte nicht alle spezifischen Informationen enthalten, die im Text gegeben sind, das LLM sollte kreativ sein, um zusätzliche Informationen zu generieren, die zum Thema passen könnten: " + article}]
    kwargs = dict(model_name='gpt-4o', messages=prompt)
    response = chat.completions.create(**kwargs)

    #print(response.choices[0].message.content)
    return response.choices[0].message.content

def clean_content(content):
    cleaned_content = content.replace('Schauen Sie hier:', "")
    sentences_to_cut = ["Lesen Sie auch:","Auch bei NIUS:"]
    for sentence in sentences_to_cut:
        if sentence in cleaned_content:
            cleaned_content = cleaned_content.split(sentence)[0]

    return cleaned_content

def formulate_reasoning(input, output):
    prompt = [{"role": "user", "content": "Assume you have two variables: inputPrompt (holding the original multi-sentence prompt) and responseText (holding the generated multi-sentence answer). Generate a plain text chain-of-thought consisting of max.14 separate steps. For this exercise, a 'critical reasoning step' is defined as an essential logical transition or decision point that bridges the gap between understanding the inputPrompt and producing the responseText. These steps may include, but are not limited to, interpreting the prompt, identifying key elements, inferring necessary context, outlining logical connections, synthesizing information, and deducing conclusions. Each step should be concise and written in plain text without any markdown or formatting.\nInput Prompt:\n" + input + "\nResponse Text:\n" + output}]
    kwargs = dict(model_name='gpt-4o', messages=prompt)
    response = chat.completions.create(**kwargs)

    #print(response.choices[0].message.content)
    return response.choices[0].message.content

def generate_qa_sheet():
    article_manager = ArticleManager()
    print('Fetching articles...')
    articles = article_manager.list_articles()
    print('Articles fetched!')
    qa_sheet = []

    for article in articles:
        try:
            headline = article["headline"]
            content = clean_content(article["content"])
            article_text = headline + "\n" + content

            qa_entity = {}
            qa_entity["input"] = formulate_question(article_text)
            print('Question formulated!')
            qa_entity["output"] = article_text
            qa_entity["reasoning"] = formulate_reasoning(qa_entity["input"], qa_entity["output"])
            print('Reasoning formulated!')
            qa_entity["output_with_reasoning"] = qa_entity["reasoning"] + "\n" + qa_entity["output"]
            qa_entity["article_mongodb_id"] = article["_id"]
            print(qa_entity)
            qa_sheet.append(qa_entity)
        except Exception: #filter bad requests, like flags for violence or sexuality
            print("Bad request")
            continue

    with open("data/qa_sheet.json", "w") as json_file:
            json.dump(qa_sheet, json_file, indent=4)

if __name__ == "__main__":
    generate_qa_sheet()