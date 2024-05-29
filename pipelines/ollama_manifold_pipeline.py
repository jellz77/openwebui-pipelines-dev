from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
from pydantic import BaseModel
import requests


class Pipeline:
    def __init__(self):
        # You can also set the pipelines that are available in this pipeline.
        # Set manifold to True if you want to use this pipeline as a manifold.
        # Manifold pipelines can have multiple pipelines.
        self.type = "manifold"

        # Optionally, you can set the id and name of the pipeline.
        # Assign a unique identifier to the pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        self.id = "ollama_manifold"

        # Optionally, you can set the name of the manifold pipeline.
        self.name = "Ollama: "

        class Valves(BaseModel):
            OLLAMA_BASE_URL: str

        self.valves = Valves(**{"OLLAMA_BASE_URL": "http://localhost:11434"})
        pass

    async def on_startup(self):
        # This function is called when the server is started or after valves are updated.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped or before valves are updated.
        print(f"on_shutdown:{__name__}")
        pass

    def get_ollama_models(self):
        if self.valves.OLLAMA_BASE_URL:
            try:
                r = requests.get(f"{self.valves.OLLAMA_BASE_URL}/api/tags")
                models = r.json()
                return [
                    {"id": model["model"], "name": model["name"]}
                    for model in models["models"]
                ]
            except Exception as e:
                print(f"Error: {e}")
                return [
                    {
                        "id": self.id,
                        "name": "Could not fetch models from Ollama, please update the URL in the valves.",
                    },
                ]
        else:
            return []

    # Pipelines are the models that are available in the manifold.
    # It can be a list or a function that returns a list.
    def pipelines(self) -> List[dict]:
        return self.get_ollama_models()

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom pipelines like RAG.'

        if "user" in body:
            print("######################################")
            print(f'# User: {body["user"]["name"]} ({body["user"]["id"]})')
            print(f"# Message: {user_message}")
            print("######################################")

        try:
            r = requests.post(
                url=f"{self.OLLAMA_BASE_URL}/v1/chat/completions",
                json={**body, "model": model_id},
                stream=True,
            )

            r.raise_for_status()

            if body["stream"]:
                return r.iter_lines()
            else:
                return r.json()
        except Exception as e:
            return f"Error: {e}"
