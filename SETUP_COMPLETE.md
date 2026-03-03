# Fubon CLI 版本管理與發布快速指南

## ✅ 已完成的設置

已為 **fubon-cli** 建立完整的 pip 發布版本管理機制，基於 **fubon-api-mcp-server** 的最佳實踐。

### 核心組件

#### 1. **版本管理系統**
- ✅ `pyproject.toml` - 完整的項目元數據和構建配置
- ✅ `.setuptools-scm` 動態版本管理（自動版本控制）
- ✅ `scripts/version_config.json` - 版本配置記錄

#### 2. **自動化腳本** (`scripts/`)
- ✅ `release.ps1` - 完整的發布流程（測試 → 版本更新 → Git 標籤 → 推送）
- ✅ `quick_check.ps1` - 快速檢查項目狀態
- ✅ `update_version.ps1` - 手動更新版本
- ✅ `README.md` - 腳本使用文檔

#### 3. **GitHub Actions CI/CD**
- ✅ `.github/workflows/ci.yml` - 自動化測試和代碼檢查
- ✅ `.github/workflows/release.yml` - 自動化發布到 PyPI

#### 4. **測試框架**
- ✅ `pytest.ini` - Pytest 配置
- ✅ `tests/` - 測試套件（包含 5 個基本測試）
- ✅ 所有測試通過 ✓

#### 5. **代碼質量工具**
- ✅ `.flake8` - PEP 8 檢查配置
- ✅ `.mypy.ini` - 類型檢查配置
- ✅ `.editorconfig` - 編輯器統一配置
- ✅ `.pre-commit-config.yaml` - Git 預提交鉤子配置

#### 6. **文檔**
- ✅ `CHANGELOG.md` - 版本變更記錄
- ✅ `CONTRIBUTING.md` - 貢獻指南
- ✅ `RELEASE_GUIDE.md` - 發布完整指南
- ✅ `MANIFEST.in` - 包分發配置

#### 7. **版本管理**
- ✅ 動態版本字符串（`fubon_cli/_version.py`）
- ✅ `fubon_cli/__init__.py` 暴露 `__version__`
- ✅ `fubon_cli/main.py` 使用動態版本

---

## 🚀 快速開始

### 本地開發

```powershell
# 1. 安裝開發依賴
pip install -e ".[dev]"

# 2. 運行測試
pytest -v

# 3. 代碼檢查
flake8 fubon_cli
mypy fubon_cli

# 4. 快速檢查
.\scripts\quick_check.ps1
```

### 發布新版本

#### 方式 A：使用自動化腳本（推薦）

```powershell
# 發布 patch 版本（0.1.0 → 0.1.1）
.\scripts\release.ps1

# 發布 minor 版本（0.1.0 → 0.2.0）
.\scripts\release.ps1 -BumpType minor

# 發布 major 版本（0.1.0 → 1.0.0）
.\scripts\release.ps1 -BumpType major
```

**自動執行步驟：**
1. ✓ 運行所有測試
2. ✓ 更新版本號
3. ✓ 提交更改
4. ✓ 創建 Git 標籤
5. ✓ 推送到 GitHub
6. ✓ GitHub Actions 自動發布到 PyPI

#### 方式 B：使用 GitHub UI

1. 在 GitHub 上創建一個 Release
2. GitHub Actions 自動構建和發布

---

## 📋 GitHub Secrets 設置

在 https://github.com/Mofesto/fubon-cli/settings/secrets/actions 中設置：

```
PYPI_API_TOKEN = pypi-AgEI...  # 從 PyPI 生成的 API Token
```

**獲取 PyPI Token 步驟：**
1. 登錄 https://pypi.org
2. 進入 Account Settings → API Tokens
3. 創建新 Token
4. 複製 Token 到 GitHub Secrets

---

## 📊 工作流程圖

```
代碼修改 → 本地測試 → git push
                    ↓
          GitHub Actions (CI)
         ├─ 多版本 Python 測試
         ├─ 代碼風格檢查
         ├─ 安全檢查
         └─ 構建 wheel
                    ↓
             發布新版本 (手動或自動)
                    ↓
          GitHub Actions (Release)
         ├─ 構建 wheel
         ├─ 上傳到 PyPI
         └─ 創建 GitHub Release
                    ↓
           PyPI 中可見：
    https://pypi.org/project/fubon-cli/
```

---

## 📁 目錄結構

```
fubon-cli/
├── fubon_cli/                    # 主包
│   ├── __init__.py              # 定義 __version__
│   ├── main.py                  # CLI 入口（使用動態版本）
│   ├── core.py
│   └── commands/
├── tests/                        # 測試套件
│   ├── test_cli.py
│   └── test_core.py
├── scripts/                      # 發布腳本
│   ├── release.ps1              # 主發布腳本
│   ├── quick_check.ps1
│   ├── update_version.ps1
│   ├── version_config.json      # 版本配置
│   └── README.md
├── .github/workflows/           # GitHub Actions
│   ├── ci.yml                   # 持續集成
│   └── release.yml              # 自動發布
├── .flake8                      # 代碼風格配置
├── .mypy.ini                    # 類型檢查配置
├── .editorconfig                # 編輯器配置
├── .pre-commit-config.yaml      # Git 鉤子
├── pyproject.toml               # 項目配置（setuptools-scm）
├── pytest.ini                   # 測試配置
├── CHANGELOG.md                 # 版本歷史
├── CONTRIBUTING.md              # 貢獻指南
├── RELEASE_GUIDE.md             # 發布詳細指南
└── MANIFEST.in                  # 分發清單
```

---

## 🔄 版本號方案

遵循 **Semantic Versioning**：

- **PATCH** (0.1.0 → 0.1.1)：補丁修復
  ```
  .\scripts\release.ps1 -BumpType patch
  ```

- **MINOR** (0.1.0 → 0.2.0)：新功能（向後兼容）
  ```
  .\scripts\release.ps1 -BumpType minor
  ```

- **MAJOR** (0.1.0 → 1.0.0)：重大變更
  ```
  .\scripts\release.ps1 -BumpType major
  ```

---

## ✨ 特色功能

### 1. 動態版本管理
- 自動從 git 標籤生成版本
- 無需手動維護版本字符串
- 使用 `setuptools-scm` 實現

### 2. 自動化測試
- 多版本 Python (3.8-3.12) 跨平台測試
- 代碼覆蓋率報告
- 自動 lint 檢查

### 3. 安全發布
- 強制測試通過才能發布
- 自動版本碰撞
- GitHub Actions 簽名驗證

### 4. 文檔完整
- 發布指南
- 貢獻指南
- 變更日誌

---

## 📚 相關文檔

- [RELEASE_GUIDE.md](RELEASE_GUIDE.md) - 完整發布指南
- [CONTRIBUTING.md](CONTRIBUTING.md) - 貢獻指南
- [scripts/README.md](scripts/README.md) - 腳本使用説明
- [CHANGELOG.md](CHANGELOG.md) - 版本歷史

---

## 🐛 故障排除

### 腳本執行出錯

```powershell
# 重新運行發布流程
.\scripts\release.ps1 -SkipTests -BumpType patch

# 檢查當前版本配置
type scripts/version_config.json
```

### GitHub Actions 失敗

1. 檢查 PyPI Token（Settings → Secrets）
2. 查看 Actions 日誌
3. 確認測試通過

### 版本衝突

```powershell
# 手動更新版本（如需要）
.\scripts\update_version.ps1 -NewVersion "0.2.0"
```

---

## ✅ 發布前檢查清單

- [ ] `pytest` 所有測試通過
- [ ] `flake8` 代碼檢查輸出（除了已知的風格問題）
- [ ] CHANGELOG.md 已更新
- [ ] Git 提交信息清晰
- [ ] 沒有未提交的更改
- [ ] PyPI Token 已配置

---

## 🎉 已完成！

項目已配置完整的 pip 發布管理系統，可以：
- ✅ 自動化發布到 PyPI
- ✅ 管理語義化版本
- ✅ 運行完整的 CI/CD
- ✅ 維護變更日誌
- ✅ 支持類型檢查和代碼風格檢查

下一次發布時，運行 `.\scripts\release.ps1` 即可！
