from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WordEntry:
    """單字條目"""
    word: str = ""
    meaning: str = ""
    example: str = ""
    
    def has_content(self) -> bool:
        """檢查是否有內容"""
        return bool(self.word.strip() or self.meaning.strip())
    
    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "meaning": self.meaning,
            "example": self.example
        }


@dataclass
class ExcelColumn:
    """Excel 欄位定義"""
    index: int           # 欄位索引（0-based）
    name: str            # 欄位名稱
    field: str           # 對應的 WordEntry 欄位（word/meaning/example）


@dataclass 
class ExcelSchema:
    """Excel 結構定義"""
    has_header: bool = True
    columns: List[ExcelColumn] = field(default_factory=list)
    
    def get_field_index(self, field_name: str) -> Optional[int]:
        """取得欄位索引"""
        for col in self.columns:
            if col.field == field_name:
                return col.index
        return None