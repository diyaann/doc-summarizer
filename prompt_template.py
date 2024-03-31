from langchain.prompts import PromptTemplate


def get_prompt_template():
       
    template = """
        Human : Act as a document summarizer.
        You will be given a document. Read the entire document and provide the summary in 100 words.
        NEVER include any outisde information.

        User Document: {context}

        Assistant:
    """

    prompt = PromptTemplate(input_variables=["context"], template=template)
    return prompt
