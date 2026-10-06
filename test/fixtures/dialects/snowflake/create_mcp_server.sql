CREATE MCP SERVER my_db.my_schema.my_mcp_server
  FROM SPECIFICATION $$
    tools:
      - name: "my-cortex-search"
        type: "CORTEX_SEARCH_SERVICE_QUERY"
        identifier: "my_db.my_schema.my_search_service"
  $$;

CREATE OR REPLACE MCP SERVER my_db.my_schema.my_mcp_server
  FROM SPECIFICATION $$
    tools:
      - name: "system_execute_sql"
        title: "SQL Execution Tool"
        type: "SYSTEM_EXECUTE_SQL"
        description: "Execute read-only SQL queries."
        config:
          read_only: true
          query_timeout: 60
          warehouse: "MY_WH"
  $$;

CREATE MCP SERVER IF NOT EXISTS my_mcp_server
  FROM SPECIFICATION $$
    tools: []
  $$;

GRANT USAGE ON MCP SERVER my_db.my_schema.my_mcp_server TO ROLE my_role;

GRANT CREATE MCP SERVER ON SCHEMA my_db.my_schema TO ROLE my_role;

DROP MCP SERVER IF EXISTS my_db.my_schema.my_mcp_server;

SHOW MCP SERVERS;

DESCRIBE MCP SERVER my_db.my_schema.my_mcp_server;
