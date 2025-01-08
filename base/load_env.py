def load_env():
    """ Carga las variables de entorno del archivo .env."""
    from dotenv import load_dotenv 
    
    load_dotenv()     