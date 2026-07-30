# 生命周期 6 报告 — 回归验证与线上同步

日期：2026-07-11

## 本轮工作

1. **简体中文 i18n 对齐**  
   `oldLanes` / `localShops` 由「旧区老街 / 本地小店」统一为「旧区景点 / 本地商户点」，与繁体及首页统计口径一致。

2. **MCP 测试依赖修复**  
   `requirements-dev.txt` 新增 `mcp>=1.9.0`，确保 `qa/test_qwenpaw_mcp.py` 可在标准开发环境直接运行。

3. **GitHub Pages 线上同步**  
   已将最新 `frontend/` 部署至 `gh-pages` 分支（commit `47f23ab`），包含：
   - 五语言静态演示与 6 条示例场景
   - 旧区导流成效面板
   - 38 张新增 POI 图片
   - 手机端布局优化
   - 缓存版本 `20260711-final`

4. **示例场景核对**  
   点击「我下星期三想帶爸媽…」→ 首站 **大三巴牌坊**，导流 **草堆街與爛鬼樓**；知识库 `pois.json` 含对应 POI（`ruins_st_paul`、`rua_estalagens`）。

## 测试结果（本轮全量回归）

| 套件 | 结果 |
|------|------|
| `qa/test_backend.py` | **641 PASS / 0 FAIL** |
| `qa/test_frontend.py` | **99 PASS / 0 FAIL** |
| `qa/test_api.py` | **64 PASS / 0 FAIL** |
| `qa/test_qwenpaw_mcp.py` | **8 tools + protocol PASS** |
| `qa/test_repo.py` | **32 PASS / 0 FAIL** |

## 线上演示

- **URL**：<https://mikey-si.github.io/everylane-macau/>
- 静态模式：6 条示例均可点击，结果不含「GitHub Pages / backend」等技术字样
- PDF 列印：仅输出 AI 行程结果区

## 待队长人工完成（安全步骤）

1. 在 QwenPaw 控制台粘贴主办方 Token Plan Key（`sk-sp-`），选择 `qwen3.7-plus`
2. 运行郑家大屋星期三场景，补一张 QwenPaw 真实调用工具截图
3. 团队视频开头 15 秒可替换为本人出镜（现成片 2:51 已满足时长要求）

## 结论

**初赛提交材料、网站、测试、线上演示均已就绪。** 本地 `main` 分支尚有未推送的源码与文档改动；若需同步仓库主分支，请明确授权后一次性提交。
