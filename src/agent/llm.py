import ollama


class OllamaLLM:
    """Thin wrapper so the rest of the agent never talks to the provider directly."""

    def __init__(self, model="llama3.2:3b", temperature=0.2):
        self.model = model
        self.temperature = temperature

    def chat(self, messages, tools=None):
        """Send chat messages (optionally with tool definitions); return the reply message."""
        response = ollama.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            options={"temperature": self.temperature},
        )
        return response["message"]

    def generate(self, prompt, system=None):
        """Convenience method: one prompt in, plain text out."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages)["content"]


if __name__ == "__main__":
    llm = OllamaLLM()
    print(llm.generate("In one sentence, what is an AI agent?"))