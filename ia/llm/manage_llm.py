from typing import Any
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import HumanMessage, SystemMessage

class LlmManager:
    """ Clase que maneja la carga y configuración de modelos de lenguaje y conversación. """  
    def __init__(self, llm_provider) -> None:
        self.llm_provider = llm_provider
    
    def initialice_llm_model(self, model_name, api_key, temperature=0):
        """ Carga el modelo y el api_key de OpenAI(pasados como parámetros obligatorios) y lo inicializa con la 
        temperatura deseada(por defecto es cero), se debe pasar el provider(empresa) del modelo, que indica que 
        clase de langchain se debe llamar.
        
        Args:
            model_name (str): Nombre del modelo.
            openai_api_key (str): Clave de API.
            temperature (float, optional): Temperatura del modelo. Por defecto es 0.
            system_prompt (str, optional): Prompt del sistema para inicializar el modelo. Por defecto es None.
    
        Returns:
            llm: Instancia del modelo inicializado. 
        """
       
        try:
            if self.llm_provider == "openai":
                llm = ChatOpenAI(                    
                    model_name=model_name, 
                    api_key=api_key,
                    temperature=temperature,                   
                )
        except Exception as e:
            print(f"Error al cargar el tipo de modelo LLM: {e}")
            llm = None    

        return llm
    
    def initialice_retriever(self, llm, stored_embeddings, search_type="similarity", num_result=1):
        """ Inicializa el modelo de recuperación de información, pasando el modelo de lenguaje y los embeddings, 
        ademas se pueden pasar como parámetros el tipo de búsqueda y la cantidad de resultados, ambos opcionales. """

        retriever = stored_embeddings.as_retriever(search_type=search_type, search_kwargs={"k": num_result})
        
        QA_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True 
        )

        return QA_chain

    def get_response_retriever(self, QA_chain, user_message, history):
        """ Recibe la cadena con el llm y retriever, además de la pregunta del usuario y el historial del chat, devuelve \
            la respuesta del bot, de donde saco la información y el historial. """
        messages = [
            SystemMessage(
                content="Sos un asistente para gestión de trámites administrativos de la Facultad de \
                    Humanidades de la Universidad Nacional de Catamarca. Tenes como objetivo acompañar \
                    a los y las estudiantes en la resolución de trámites, gestiones administrativas, \
                    solicitudes y requerimientos de los trayectos de formación profesional así como \
                    información general vinculada a la vida universitaria. Deberás responder unicamente \
                    con la información que se encuentra en los documentos que te fueron suministrados, \
                    si la pregunta que realiza el usuario no esta en esos documentos deberás responder \
                    que no posees esa información."
            ),  # System prompt
        ]

        # Agregar el historial de mensajes
        for msg in history:            
            messages.append(HumanMessage(content=msg["user"]))
            messages.append(HumanMessage(content=msg["assistant"]))   

        # Agregar el mensaje actual del usuario
        messages.append(HumanMessage(content=user_message))

        response = QA_chain.invoke({"query": user_message, "messages": messages})
        bot_response = response["result"]
        source_documents = response["source_documents"]
        
        # Extraer fuentes con metadatos adicionales (ej. título, enlace)
        sources = []
        for doc in source_documents:
            source_info = {
                'source': doc.metadata.get('source', 'Desconocido'),  # Fuente original
                'title': doc.metadata.get('title', 'Sin título'),  # Título del documento
                'url': doc.metadata.get('url', ''),  # Enlace si está disponible
                'snippet': doc.page_content[:200]  # Primeros 200 caracteres del documento
            }
            sources.append(source_info)
  
        return bot_response, sources

    def get_response_retriever_without_memory(self, QA_chain, user_message):
        """ Recibe la cadena con el llm y retriever y la pregunta del usuario, devuelve solo la respuesta del bot. """
        messages = [
            SystemMessage(
                content="Sos un asistente de documentación que solo debe responder con la información que se \
                    encuentra en los documentos proporcionados. Si la pregunta del usuario no está en esos documentos, \
                    responde que no posees esa información."
            )
        ]
        messages.append(HumanMessage(content=user_message))
        response = QA_chain.invoke({"query": user_message, "messages": messages})
        bot_response = response["result"]
    
        return bot_response