# Contributing to Fubon CLI

感謝你對 Fubon CLI 的貢獻！

## 如何參與

### 報告 Bug
1. 檢查 [Issues](https://github.com/mofesto/fubon-cli/issues) 中是否已存在相同問題
2. 提供詳細的錯誤描述、環境信息和重現步驟
3. 包含日誌輸出和相關截圖

### 提交功能請求
1. 使用 [Discussions](https://github.com/mofesto/fubon-cli/discussions) 討論新功能
2. 清楚地解釋使用場景和預期行為
3. 提供示例代碼或用例

### 提交代碼變更
1. Fork 項目
2. 創建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 打開 Pull Request

## 代碼風格

遵循以下指南確保代碼一致性：

- **Python**: PEP 8 + Black 格式化
- **行長**: 最多 100 字符
- **類型提示**: 優先使用類型注解
- **Docstring**: Google 風格

### 本地開發環境

```bash
# 克隆並進入項目
git clone https://github.com/mofesto/fubon-cli.git
cd fubon-cli

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # 在 Windows 上: venv\Scripts\activate

# 安裝開發依賴
pip install -e ".[dev]"

# 運行測試
pytest -v

# 代碼格式化
black fubon_cli tests
isort fubon_cli tests

# 代碼檢查
flake8 fubon_cli
mypy fubon_cli
```

## 提交 PR 時的檢查清單

- [ ] 代碼遵循項目的風格指南
- [ ] 已運行 `pytest` 確保所有測試通過
- [ ] 已運行 `black` 和 `isort` 進行格式化
- [ ] 添加了新的測試以涵蓋所做的更改
- [ ] 更新了相關文檔
- [ ] PR 標題清楚簡潔

## 版本發布

版本遵循 Semantic Versioning：
- **MAJOR**: 破壞性變更
- **MINOR**: 新功能（向後兼容）
- **PATCH**: 補丁修復

發布流程由維護者執行。

## 行為準則

本項目遵循行為準則。請確保您的互動尊重所有貢獻者。

## 許可證

通過貢獻代碼，你同意在與項目相同的許可證（MIT）下發佈你的貢獻。

---

有任何問題？請在 [Discussions](https://github.com/mofesto/fubon-cli/discussions) 中提出！
