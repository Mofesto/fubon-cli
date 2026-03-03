# Changelog

所有對此項目的重大更改都將記錄在此文件中。

該項目遵循 [Semantic Versioning](https://semver.org/)。

## [Unreleased]

## [0.2.0] - 2026-03-03

### Added
- API Key 登入支援 (`fubon login --id <ID> --api-key <KEY> --cert-path <PATH>`)，需 fubon_neo >= 2.2.7
- `save_session` / `get_sdk_and_accounts` 同時支援 `password` 與 `apikey` 兩種登入類型，向下相容舊版 session
- `fubon login status` 輸出新增 `login_type` 欄位，顯示目前使用的登入方式
- 完整測試覆蓋兩種登入流程 (`tests/test_auth.py`)

## [0.1.0] - 2026-02-26

### Added
- 初始項目設置
- 基本 CLI 框架
- 測試環境配置
- 發布自動化腳本

[Unreleased]: https://github.com/mofesto/fubon-cli/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/mofesto/fubon-cli/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mofesto/fubon-cli/releases/tag/v0.1.0
