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
DB_PASS = os.getenv("DB_PASS", "Machiavel69")

# Créer l'URL de connexion à la base de données
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Configurer SQLAlchemy
Base = declarative_base()

# Définir le modèle SQLAlchemy pour la table component_center_deepseekmodel
class DeepSeekModel(Base):
    __tablename__ = "component_center_deepseekmodel"

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    azure_endpoint = Column(String(255))
    azure_api_version = Column(String(50))
    azure_api_key = Column(String(255))
    azure_model_name = Column(String(255))
    azure_model = Column(String(255))
    publish = Column(Boolean, nullable=False)


class Pipeline:
    class Valves(BaseModel):
        # You can add your custom valves here.
        AZURE_DEEPSEEKR1_API_KEY: str
        AZURE_DEEPSEEKR1_ENDPOINT: str
        AZURE_DEEPSEEKR1_API_VERSION: str

    def __init__(self):
        self.type = "manifold"
        self.name = "Azure "
        
        # Charger les valves depuis la BD
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
            models = session.query(DeepSeekModel).filter(DeepSeekModel.publish == True).all()
            
            if not models:
                print("Aucun modèle DeepSeek publié trouvé dans la base de données.")
                # Utiliser les valeurs par défaut si aucun modèle n'est trouvé
                return self.Valves(
                    **{
                        "AZURE_DEEPSEEKR1_API_KEY": os.getenv("AZURE_DEEPSEEKR1_API_KEY", "key - ici"),
                        "AZURE_DEEPSEEKR1_ENDPOINT": os.getenv("AZURE_DEEPSEEKR1_ENDPOINT", "endpoint ici"),
                        "AZURE_DEEPSEEKR1_API_VERSION": os.getenv("AZURE_DEEPSEEKR1_API_VERSION", "2024-05-01-preview"),
                    }
                )
            
            # Utiliser le premier modèle pour les valeurs communes (API key, endpoint, version)
            first_model = models[0]
            
            # Fermer la session
            session.close()
            
            return self.Valves(
                **{
                    "AZURE_DEEPSEEKR1_API_KEY": first_model.azure_api_key,
                    "AZURE_DEEPSEEKR1_ENDPOINT": first_model.azure_endpoint,
                    "AZURE_DEEPSEEKR1_API_VERSION": first_model.azure_api_version,
                }
            )
            
        except Exception as e:
            print(f"Erreur lors de la récupération des données depuis la base de données: {e}")
            # Utiliser les valeurs par défaut en cas d'erreur
            return self.Valves(
                **{
                    "AZURE_DEEPSEEKR1_API_KEY": os.getenv("AZURE_DEEPSEEKR1_API_KEY", "key ici"),
                    "AZURE_DEEPSEEKR1_ENDPOINT": os.getenv("AZURE_DEEPSEEKR1_ENDPOINT", "endpoint ici"),
                    "AZURE_DEEPSEEKR1_API_VERSION": os.getenv("AZURE_DEEPSEEKR1_API_VERSION", "2024-05-01-preview"),
                }
            )

    def load_models_from_db(self):
        """Récupère les modèles disponibles depuis la base de données."""
        try:
            # Créer un moteur de connexion
            engine = create_engine(DATABASE_URL)
            
            # Créer une session
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Récupérer tous les modèles publiés
            db_models = session.query(DeepSeekModel).filter(DeepSeekModel.publish == True).all()
            
            models = []
            model_names = []
            
            for model in db_models:
                if model.azure_model and model.azure_model_name:
                    models.append(model.azure_model)
                    model_names.append(model.azure_model_name)
            
            # Fermer la session
            session.close()
            
            # S'il n'y a pas de modèles dans la BD, utiliser les valeurs par défaut
            if not models:
                return ['DeepSeek-R1', 'DeepSeek-V3'], ['DeepSeek-R1', 'DeepSeek-V3']
            
            return models, model_names
            
        except Exception as e:
            print(f"Erreur lors de la récupération des modèles depuis la base de données: {e}")
            # Utiliser les valeurs par défaut en cas d'erreur
            return ['DeepSeek-R1', 'DeepSeek-V3'], ['DeepSeek-R1', 'DeepSeek-V3']
            
    def set_pipelines(self):
        # Récupérer les modèles depuis la BD
        models, model_names = self.load_models_from_db()
        
        self.pipelines = [
            {"id": model, "name": name} for model, name in zip(models, model_names)
        ]
        print(f"azure_deepseek_r1_pipeline - models: {self.pipelines}")
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
            "api-key": self.valves.AZURE_DEEPSEEKR1_API_KEY,
            "Content-Type": "application/json",
        }

        url = f"{self.valves.AZURE_DEEPSEEKR1_ENDPOINT}/models/chat/completions?api-version={self.valves.AZURE_DEEPSEEKR1_API_VERSION}"
        print(body)

        allowed_params = {'messages', 'temperature', 'role', 'content', 'contentPart', 'contentPartImage',
                          'enhancements', 'dataSources', 'n', 'stream', 'stop', 'max_tokens', 'presence_penalty',
                          'frequency_penalty', 'logit_bias', 'user', 'function_call', 'funcions', 'tools',
                          'tool_choice', 'top_p', 'log_probs', 'top_logprobs', 'response_format', 'seed', 'model'}
        
        # remap user field
        if "user" in body and not isinstance(body["user"], str):
            body["user"] = body["user"]["id"] if "id" in body["user"] else str(body["user"])
            
        # Fill in model field as per Azure's api requirements
        body["model"] = model_id
        
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