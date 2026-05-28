import os
import json
from typing import Dict, Any, Optional

# นำเข้า Config จาก Root ปกติ
from config import Config

def get_repo_structure(*args, **kwargs) -> str:
    """
    Synchronous wrapper supplying a strict mock payload to safeguard 
    the downstream pipeline execution without relying on a missing mcp.client.
    """
    # จำลองโครงสร้างไฟล์ใน GitHub เพื่อส่งให้ Agent (SA Review Bot) ตรวจสอบ
    return """📂 Repository Structure:
├── 📁 src
│   ├── 📁 agents
│   ├── 📁 workflows
│   └── 📁 api
├── 📁 config
└── 📄 main.py
"""

def get_pr_diff(*args, **kwargs) -> str:
    """
    Synchronous wrapper supplying a strict mock PR diff.
    """
    # จำลองข้อมูลการแก้โค้ด (Diff) เพื่อส่งให้ Agent (PM/DevOps) ประเมินความเสี่ยง
    return """```diff
@@ -10,5 +10,6 @@
- def old_insecure_deploy():
-     push_to_prod()
+ def secure_deploy_node(state):
+     if state.is_approved:
+         push_to_prod()
```"""