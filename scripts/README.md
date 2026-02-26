# Release Scripts - Fubon CLI

這個目錄包含項目發布和版本管理的自動化腳本。

## 腳本概述

### `release.ps1` - 自動發布流程
完整的版本發布自動化腳本，包括測試、版本更新、Git 標籤和推送。

**使用方式:**
```powershell
# 發布 patch 版本 (預設)
.\scripts\release.ps1

# 發布 minor 版本
.\scripts\release.ps1 -BumpType minor

# 發布 major 版本
.\scripts\release.ps1 -BumpType major

# 跳過測試 (不建議)
.\scripts\release.ps1 -SkipTests
```

### `quick_check.ps1` - 快速檢查
驗證項目的基本配置、依賴項和代碼質量。

**使用方式:**
```powershell
.\scripts\quick_check.ps1
```

### `update_version.ps1` - 手動更新版本
手動更新版本號（通常由 release.ps1 自動調用）。

**使用方式:**
```powershell
.\scripts\update_version.ps1 -NewVersion "0.2.0"
```

## 版本配置

編輯 `version_config.json` 來管理當前版本和項目信息。

## 完整發布工作流

1. **準備代碼**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

2. **運行發布腳本**
   ```powershell
   .\scripts\release.ps1 -BumpType minor
   ```

3. **GitHub Actions 自動處理**
   - 構建 wheel 包
   - 發佈到 PyPI

## 配置要求

### GitHub Settings
- 在 Settings → Environments → release 中設置 PyPI token
- Environment: `release`
- Secret: `PYPI_API_TOKEN`

### 本地環境
- Python 3.8+
- Git 配置
- PyPI账户憑證（可選，用於手動發布）

## 版本號方案

遵循 Semantic Versioning：
- **MAJOR**: 破壞性變更
- **MINOR**: 新功能（向後兼容）
- **PATCH**: 補丁修復

示例：`0.1.0` → `0.2.0` (minor) → `0.2.1` (patch)

## 自動化 CI/CD

GitHub Actions 工作流：
- `.github/workflows/ci.yml` - 每次推送運行測試
- `.github/workflows/release.yml` - 發行版本時發佈到 PyPI
