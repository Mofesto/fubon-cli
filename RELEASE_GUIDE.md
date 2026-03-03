# Release Guide

本文档描述如何發布新版本的 Fubon CLI 到 PyPI。

## 先決條件

1. **GitHub 設置**
   - Admin 權限（或 Release 權限）
   - PyPI API Token 配置在 GitHub Secrets

2. **本地環境**
   - Git 配置完整
   - Python 3.8+ 環境
   - 開發依賴安裝：`pip install -e ".[dev]"`

3. **PyPI 帳戶**
   - 在 https://pypi.org 上有帳戶
   - 生成 API Token（用於自動化發布）

## GitHub Secrets 配置

在 Repository Settings → Secrets and variables → Actions 中設置：

```
PYPI_API_TOKEN=pypi-AgEI...  # Your PyPI API token
```

## 發布流程

### 方式 1：使用本地腳本（推薦）

最簡單和最可靠的方式。

```powershell
# 進入項目目錄
cd fubon-cli

# 運行發布腳本
.\scripts\release.ps1 -BumpType minor

# 腳本將自動：
# 1. 運行所有測試
# 2. 更新版本號
# 3. 提交更改
# 4. 創建 Git 標籤
# 5. 推送到 GitHub
# 6. 觸發 GitHub Actions
```

### 方式 2：使用 GitHub UI

適合 GitHub 上直接操作的情況。

1. **創建版本標籤**
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```

2. **在 GitHub 上創建 Release**
   - 進入 Releases 頁面
   - 點擊 "Create a new release"
   - 選擇標籤（如 v0.2.0）
   - 填寫備註和更改日誌
   - 點擊 "Publish release"

3. **GitHub Actions 自動處理**
   - 構建 wheel 文件
   - 發布到 PyPI

### 方式 3：使用 GitHub Actions Workflow Dispatch

在 GitHub UI 上手動觸發發布。

1. 進入 Actions 標籤
2. 選擇 "Release" 工作流
3. 點擊 "Run workflow"
4. 選擇 bump 類型（patch/minor/major）
5. 確認執行

## 版本號規則

遵循 Semantic Versioning：

- **Patch** (0.1.0 → 0.1.1): 補丁修復，不添加功能
- **Minor** (0.1.0 → 0.2.0): 新功能，向後兼容
- **Major** (0.1.0 → 1.0.0): 重大变更，可能破壞兼容性

## 發布前檢查清單

- [ ] 所有測試通過
- [ ] 代碼審查完成
- [ ] CHANGELOG.md 已更新
- [ ] 提交信息清晰
- [ ] 當前分支是 main 或 develop
- [ ] 沒有未提交的更改

## 發布後驗證

1. **檢查 GitHub Actions**
   - 進入 Actions 標籤
   - 確認 Release 工作流成功完成

2. **驗證 PyPI**
   ```bash
   # 安裝最新版本
   pip install --upgrade fubon-cli
   
   # 檢查版本
   python -c "import fubon_cli; print(fubon_cli.__version__)"
   ```

3. **檢查 GitHub Release**
   - 進入 Releases 頁面
   - 確認新版本已列出
   - 檢查 Assets 中是否包含 wheel 文件

## 故障排查

### 發布腳本失敗

**檢查點：**
1. 確認 Git 狀態乾淨
2. 運行 `pytest -v` 確認所有測試通過
3. 檢查網絡連接（git push）

**示例：**
```powershell
# 重試發布
.\scripts\release.ps1 -BumpType patch

# 如果卡在某一步，可以跳過測試（不推薦）
.\scripts\release.ps1 -BumpType patch -SkipTests
```

### PyPI 發布失敗

1. **檢查 token**
   - GitHub Secrets 中的 PYPI_API_TOKEN 是否有效
   - 可在 PyPI 上撤銷並重新生成

2. **檢查 wheel 文件**
   ```bash
   # 本地構建測試
   python -m build
   twine check dist/*
   ```

## 手動發布到 PyPI（高級）

不推薦，但在自動化失敗時可用。

```bash
# 構建包
python -m build

# 檢查包
twine check dist/*

# 上傳到 PyPI（需要 .pypirc）
twine upload dist/*
```

## 相關連結

- [PyPI 項目頁面](https://pypi.org/project/fubon-cli/)
- [GitHub Releases](https://github.com/mofesto/fubon-cli/releases)
- [Semantic Versioning](https://semver.org/)
