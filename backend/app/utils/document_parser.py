import re
from pathlib import Path


class DocumentParser:
    """文档解析器"""

    def parse(self, file_path: str) -> list[dict]:
        """解析文档，返回分块列表"""
        file_type = Path(file_path).suffix.lstrip(".").lower()

        if file_type == "pdf":
            raw_text = self.parse_pdf(file_path)
        elif file_type in ("md", "markdown"):
            raw_text = self.parse_markdown(file_path)
        elif file_type == "txt":
            raw_text = self.parse_txt(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")

        cleaned = self.clean_text(raw_text)
        chunks = self.smart_split(cleaned)
        return chunks

    def parse_pdf(self, file_path: str) -> str:
        """解析 PDF"""
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)

    def parse_markdown(self, file_path: str) -> str:
        """解析 Markdown"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def parse_txt(self, file_path: str) -> str:
        """解析 TXT"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def clean_text(self, text: str) -> str:
        """文本清洗"""
        # 去除页眉页脚
        text = re.sub(r"第\s*\d+\s*页.*?\n", "", text)
        # 去除多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        # PDF 断行修复（中文字符之间的换行）
        text = re.sub(r"(?<=[一-鿿])\n(?=[一-鿿])", "", text)
        # 去除行首尾空白
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        # 再次清理多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def smart_split(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[dict]:
        """智能分块：段落优先 + 重叠窗口"""
        if not text:
            return []

        # 按段落分割
        paragraphs = text.split("\n\n")

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 如果单个段落超过 chunk_size，按句子分割
            if len(para) > chunk_size:
                if current_chunk:
                    chunks.append({"content": current_chunk.strip()})
                    current_chunk = ""
                sentences = self._split_sentences(para)
                sub_chunk = ""
                for sent in sentences:
                    if len(sub_chunk) + len(sent) <= chunk_size:
                        sub_chunk += sent
                    else:
                        if sub_chunk:
                            chunks.append({"content": sub_chunk.strip()})
                        sub_chunk = sent
                if sub_chunk:
                    current_chunk = sub_chunk
            elif len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append({"content": current_chunk.strip()})
                current_chunk = para + "\n\n"

        if current_chunk.strip():
            chunks.append({"content": current_chunk.strip()})

        # 添加重叠窗口
        if overlap > 0 and len(chunks) > 1:
            chunks = self._add_overlap(chunks, overlap)

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """按句子分割（中英文）"""
        # 中文句号、问号、感叹号、分号，英文句号
        pattern = r"((?:[。！？；]|[.!?;])\s*)"
        parts = re.split(pattern, text)

        sentences = []
        current = ""
        for part in parts:
            current += part
            if re.match(pattern, part):
                sentences.append(current)
                current = ""
        if current:
            sentences.append(current)

        return sentences

    def _add_overlap(self, chunks: list[dict], overlap: int) -> list[dict]:
        """为分块添加重叠窗口"""
        result = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_content = chunks[i - 1]["content"]
            # 取前一个 chunk 的末尾 overlap 字符
            overlap_text = prev_content[-overlap:] if len(prev_content) > overlap else prev_content
            new_content = overlap_text + chunks[i]["content"]
            result.append({"content": new_content})
        return result
