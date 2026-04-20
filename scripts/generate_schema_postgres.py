import os
import sys

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.models import Base


def generate_postgres_schema_sql() -> str:
    dialect = postgresql.dialect()
    statements: list[str] = []
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=dialect))
        statements.append(ddl + ";")
    return "\n\n".join(statements) + "\n"


def main():
    sql = generate_postgres_schema_sql()
    output_path = "docs/supabase_schema.sql"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sql)
    print(output_path)


if __name__ == "__main__":
    main()
