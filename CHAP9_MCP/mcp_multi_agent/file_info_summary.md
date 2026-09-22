## File Information Summary

### server.py
- **Path**: /Users/sinhohyeon/Desktop/호현/2026/26-2학기/AIAGENT/test/CHAP9_MCP/mcp_multi_agent/server.py
- **Size**: 1702 bytes
- **Created Time**: Mon Sep 21 20:39:04 2026
- **Modified Time**: Mon Sep 21 20:56:52 2026
- **Access Time**: Tue Sep 22 01:43:21 2026
- **Permissions**: -rw-r--r--
- **Content Preview**:
  ```python
  from mcp.server.fastmcp import FastMCP
  import os
  import stat
  import time
  from typing import List

  mcp = FastMCP(
      "FileSearch",
      instructions="로컬 파일 검색을 도와주는 어시스턴트입니다."
  )

  @mcp.tool()
  async def file_listup(directory: str) -> List[str]:
      """지정된 디렉터리 경로의 파일 이름 목록을 반환합니다."""
      ...
  ```

### client.py
- **Path**: /Users/sinhohyeon/Desktop/호현/2026/26-2학기/AIAGENT/test/CHAP9_MCP/mcp_multi_agent/client.py
- **Size**: 5167 bytes
- **Created Time**: Mon Sep 21 21:07:24 2026
- **Modified Time**: Tue Sep 22 14:13:48 2026
- **Access Time**: Tue Sep 22 14:13:53 2026
- **Permissions**: -rw-r--r--
- **Content Preview**:
  ```python
  import os
  from dotenv import load_dotenv
  from langchain_mcp_adapters.client import MultiServerMCPClient

  from typing import Literal
  from typing_extensions import TypedDict
  ...
  ```