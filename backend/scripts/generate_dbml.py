
import os
import sys
from sqlalchemy import create_engine, inspect

# Add project root to path
sys.path.append(os.getcwd())

from src.shared.database import Base
from src.platform.core.config import get_settings
# Import all models to ensure they're registered with the Base
import src.platform.models
import src.features.process_mining.models

def generate_dbml():
    settings = get_settings()
    # Convert async sqlite url to sync
    db_url = settings.database_url.replace("+aiosqlite", "")
    
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    dbml_lines = []
    
    # Iterate over all mapped tables
    for table_name, table in Base.metadata.tables.items():
        dbml_lines.append(f"Table {table_name} {{")
        
        # Columns
        for column in table.columns:
            col_type = str(column.type)
            
            # DBML Settings
            settings_list = []
            if column.primary_key:
                settings_list.append("pk")
            if not column.nullable:
                settings_list.append("not null")
            if column.autoincrement is True:
                settings_list.append("increment")
                
            settings_str = f" [{', '.join(settings_list)}]" if settings_list else ""
            
            dbml_lines.append(f'  {column.name} {col_type}{settings_str}')
        
        dbml_lines.append("}")
        
        # Relations (simplified)
        for rel in table.foreign_keys:
            target_table = rel.column.table.name
            # DBML Ref: Ref: posts.user_id > users.id
            dbml_lines.append(f'Ref: {table_name}.{rel.parent.name} > {target_table}.{rel.column.name}')
            
        dbml_lines.append("\n")

    with open("schema.dbml", "w") as f:
        f.write("\n".join(dbml_lines))
    print("DBML Generated!")

if __name__ == "__main__":
    generate_dbml()
