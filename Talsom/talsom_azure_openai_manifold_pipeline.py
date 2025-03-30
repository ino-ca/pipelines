from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import requests
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration de la base de données
DB_HOST = os.getenv("DB_HOST", "192.168.2.9")
DB_NAME = os.getenv("DB_NAME", "talsom_webui_api")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Machiavel69")

# Créer l'URL de connexion à la base de données
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Configurer SQLAlchemy
Base = declarative_base()

# Définir le modèle SQLAlchemy pour la table component_center_azureopenaimodel
class AzureOpenAIModel(Base):
    __tablename__ = "component_center_azureopenaimodel"

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    model_name = Column(String(255))
    azure_endpoint = Column(String(255))
    azure_api_version = Column(String(50))
    azure_api_key = Column(String(255))
    azure_model_name = Column(String(255))
    azure_model = Column(String(255))
    publish = Column(Boolean, nullable=False)


class Pipeline:
    class Valves(BaseModel):
        # You can add your custom valves here.
        AZURE_OPENAI_API_KEY: str
        AZURE_OPENAI_ENDPOINT: str
        AZURE_OPENAI_API_VERSION: str
        AZURE_OPENAI_MODELS: str
        AZURE_OPENAI_MODEL_NAMES: str

    def __init__(self):
        self.type = "manifold"
        self.name = "Azure OpenAI: "
        
        # Créer une connexion à la base de données et récupérer les modèles publiés
        self.valves = self.load_valves_from_db()
        
        self.set_pipelines()
        pass

    def load_valves_from_db(self):
        """Charge les paramètres depuis la base de données PostgreSQL."""
        try:
            # Créer un moteur de connexion
            engine = create_engine(DATABASE_URL)
            
            # Créer une session
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Récupérer tous les modèles publiés
            models = session.query(AzureOpenAIModel).filter(AzureOpenAIModel.publish == True).all()
            
            if not models:
                print("Aucun modèle Azure OpenAI publié trouvé dans la base de données.")
                # Utiliser les valeurs par défaut si aucun modèle n'est trouvé
                return self.Valves(
                    **{
                        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", "your-azure-openai-api-key-here"),
                        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", "your-azure-openai-endpoint-here"),
                        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                        "AZURE_OPENAI_MODELS": os.getenv("AZURE_OPENAI_MODELS", "gpt-35-turbo;gpt-4o"),
                        "AZURE_OPENAI_MODEL_NAMES": os.getenv("AZURE_OPENAI_MODEL_NAMES", "GPT-35 Turbo;GPT-4o"),
                    }
                )
            
            # Construire les chaînes de modèles et de noms de modèles
            azure_models = []
            azure_model_names = []
            
            for model in models:
                if model.azure_model and model.azure_model_name:
                    azure_models.append(model.azure_model)
                    azure_model_names.append(model.azure_model_name)
            
            # S'assurer que nous avons au moins un modèle
            if not azure_models:
                print("Modèles trouvés mais sans valeurs valides pour azure_model ou azure_model_name.")
                # Utiliser les valeurs par défaut si aucun modèle valide n'est trouvé
                return self.Valves(
                    **{
                        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", "your-azure-openai-api-key-here"),
                        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", "your-azure-openai-endpoint-here"),
                        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                        "AZURE_OPENAI_MODELS": os.getenv("AZURE_OPENAI_MODELS", "gpt-35-turbo;gpt-4o"),
                        "AZURE_OPENAI_MODEL_NAMES": os.getenv("AZURE_OPENAI_MODEL_NAMES", "GPT-35 Turbo;GPT-4o"),
                    }
                )
            
            # Utiliser le premier modèle pour les valeurs communes (API key, endpoint, version)
            first_model = models[0]
            
            # Fermer la session
            session.close()
            
            return self.Valves(
                **{
                    "AZURE_OPENAI_API_KEY": first_model.azure_api_key,
                    "AZURE_OPENAI_ENDPOINT": first_model.azure_endpoint,
                    "AZURE_OPENAI_API_VERSION": first_model.azure_api_version,
                    "AZURE_OPENAI_MODELS": ";".join(azure_models),
                    "AZURE_OPENAI_MODEL_NAMES": ";".join(azure_model_names),
                }
            )
            
        except Exception as e:
            print(f"Erreur lors de la récupération des données depuis la base de données: {e}")
            # Utiliser les valeurs par défaut en cas d'erreur
            return self.Valves(
                **{
                    "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", "your-azure-openai-api-key-here"),
                    "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", "your-azure-openai-endpoint-here"),
                    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                    "AZURE_OPENAI_MODELS": os.getenv("AZURE_OPENAI_MODELS", "gpt-35-turbo;gpt-4o"),
                    "AZURE_OPENAI_MODEL_NAMES": os.getenv("AZURE_OPENAI_MODEL_NAMES", "GPT-35 Turbo;GPT-4o"),
                }
            )

    def set_pipelines(self):
        models = self.valves.AZURE_OPENAI_MODELS.split(";")
        model_names = self.valves.AZURE_OPENAI_MODEL_NAMES.split(";")
        self.pipelines = [
            {"id": model, "name": name} for model, name in zip(models, model_names)
        ]
        print(f"azure_openai_manifold_pipeline - models: {self.pipelines}")
        pass

    async def on_valves_updated(self):
        # Recharger les valves depuis la base de données quand on demande une mise à jour
        self.valves = self.load_valves_from_db()
        self.set_pipelines()

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
            self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom pipelines like RAG.
        print(f"pipe:{__name__}")

        print(messages)
        print(user_message)

        headers = {
            "api-key": self.valves.AZURE_OPENAI_API_KEY,
            "Content-Type": "application/json",
        }

        url = f"{self.valves.AZURE_OPENAI_ENDPOINT}/openai/deployments/{model_id}/chat/completions?api-version={self.valves.AZURE_OPENAI_API_VERSION}"

        allowed_params = {'messages', 'temperature', 'role', 'content', 'contentPart', 'contentPartImage',
                          'enhancements', 'dataSources', 'n', 'stream', 'stop', 'max_tokens', 'presence_penalty',
                          'frequency_penalty', 'logit_bias', 'user', 'function_call', 'funcions', 'tools',
                          'tool_choice', 'top_p', 'log_probs', 'top_logprobs', 'response_format', 'seed'}
        # remap user field
        if "user" in body and not isinstance(body["user"], str):
            body["user"] = body["user"]["id"] if "id" in body["user"] else str(body["user"])
        filtered_body = {k: v for k, v in body.items() if k in allowed_params}
        # log fields that were filtered out as a single line
        if len(body) != len(filtered_body):
            print(f"Dropped params: {', '.join(set(body.keys()) - set(filtered_body.keys()))}")

        try:
            r = requests.post(
                url=url,
                json=filtered_body,
                headers=headers,
                stream=True,
            )

            r.raise_for_status()
            if body["stream"]:
                return r.iter_lines()
            else:
                return r.json()
        except Exception as e:
            if r:
                text = r.text
                return f"Error: {e} ({text})"
            else:
                return f"Error: {e}"