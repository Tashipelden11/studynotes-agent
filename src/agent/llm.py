
import ollama


class OllamaLLM:
    """Connect the agent to a local Ollama model."""

    def __init__(self, model="qwen2.5:1.5b", temperature=0.2):
        self.model = model
        self.temperature = temperature

    def chat(self, messages, tools=None, format=None):
        """Send a chat request and return the reply message."""

        response = ollama.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            format=format,
            options={"temperature": self.temperature},
        )

        return response["message"]

    def generate(self, prompt, system=None):
        """Generate a normal text response."""

        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        return self.chat(messages)["content"]


if __name__ == "__main__":
    llm = OllamaLLM()
    print(llm.generate("In one sentence, what is an AI agent?"))
