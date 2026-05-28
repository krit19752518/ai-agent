import re

def extract_critical_logs(log_content: str, context_lines: int = 15) -> str:
    """
    สกัดเฉพาะ Log ส่วนที่พังและบริบทโดยรอบเพื่อประหยัด Token
    """
    lines = log_content.splitlines()
    error_indices = []
    
    # แพทเทิร์นที่มักจะบ่งบอกว่าเป็นจุดพัง (ปรับแต่งตามภาษา/เฟรมเวิร์กที่ใช้ได้)
    error_patterns = [
        r"Exception in thread",
        r"Traceback \(most recent call last\):",
        r"ValidationError:",
        r"Error: ",
        r"FATAL:",
        r"process exited with status"
    ]
    
    for idx, line in enumerate(lines):
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in error_patterns):
            error_indices.append(idx)
            
    if not error_indices:
        # หากไม่เจอแพทเทิร์นเฉพาะ ให้ควานหาคำว่า "error" ทั่วไปใน 50 บรรทัดสุดท้าย
        return "\n".join(lines[-50:])

    extracted_blocks = []
    visited_lines = set()

    for idx in error_indices:
        # กำหนดช่วงบรรทัดรอบๆ จุดที่พังเพื่อดูบริบท
        start = max(0, idx - 2)
        end = min(len(lines), idx + context_lines)
        
        block = []
        for i in range(start, end):
            if i not in visited_lines:
                block.append(f"Line {i+1}: {lines[i]}")
                visited_lines.add(i)
        if block:
            extracted_blocks.append("\n".join(block))
            
    return "\n\n--- Error Block ---\n\n".join(extracted_blocks)

# ตัวอย่างการใช้งานจริง
raw_ci_log = """
[INFO] 2026-05-28 00:01:00 - Starting build process...
[INFO] 2026-05-28 00:01:05 - Connection pool initialized.
[ERROR] 2026-05-28 00:01:10 - Database connection failed!
Traceback (most recent call last):
  File "/app/database.py", line 42, in connect
    self.db = psycopg2.connect(dsn)
psycopg2.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
[INFO] 2026-05-28 00:01:12 - Cleaning up resources...
"""

cleaned_log = extract_critical_logs(raw_ci_log)
print(cleaned_log)