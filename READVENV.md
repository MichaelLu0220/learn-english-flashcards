# Python 虛擬環境 (venv) 使用筆記

## 1 建立虛擬環境

在專案目錄下執行：

```bash
python -m venv test
```

說明：
- `test` 是虛擬環境資料夾名稱
- 可自行改成 `venv` 或其他名稱

---

## 2 啟動虛擬環境

### Windows

```bash
test\Scripts\activate
```

成功後終端機會出現：

```
(test) C:\your_project>
```

表示目前正在使用虛擬環境。

---

## 3 升級 pip（建議）

```bash
python -m pip install --upgrade pip
```

---

## 4 安裝專案套件

### 如果有 requirements.txt

```bash
pip install -r requirements.txt
```

### 如果沒有

手動安裝：

```bash
pip install flet
pip install requests
```

依照專案需求安裝。

---

## 5 執行專案

```bash
python main.py
```

或

```bash
python -m your_module
```

---

## 6 產生 requirements.txt（建議）

當套件安裝完成後：

```bash
pip freeze > requirements.txt
```

方便未來重建環境。

---

## 7 離開虛擬環境

```bash
deactivate
```

---

## 8 下次使用專案流程

```bash
cd 專案資料夾
test\Scripts\activate
python main.py
```

---

#  常見錯誤

### 1. 忘記 activate
會使用到全域 Python。

### 2. pip 安裝後找不到套件
通常是沒在虛擬環境裡。

可檢查：

```bash
where python
```

確認路徑是否在 `test` 資料夾內。

---

# 建議專案結構

```
project/
│
├── test/                # 虛擬環境
├── main.py
├── requirements.txt
└── README.md
```

---

完成。