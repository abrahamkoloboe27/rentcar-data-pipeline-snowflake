from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(URL(
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    database=os.getenv('SNOWFLAKE_DATABASE'),
    schema=os.getenv('SNOWFLAKE_SCHEMA'),
    warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
    role=os.getenv('SNOWFLAKE_ROLE'),
))

try:
    conn = engine.connect()
    print("✅ Connexion Snowflake réussie!")
    conn.close()
except Exception as e:
    print(f"❌ Erreur de connexion: {str(e)}")