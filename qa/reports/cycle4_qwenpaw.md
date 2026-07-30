# 生命周期 4 报告 — QwenPaw 就绪度与初赛材料

日期：2026-07-11

## 实际部署结果

- QwenPaw：2.0.0，Python 3.11.9，Windows AMD64；
- Console：`http://127.0.0.1:8088/` 正常返回 200；
- Default Agent：Plan Mode 已开启；
- Skill：`everylane-macau`，来源 local，状态 enabled；
- MCP：`EveryLane Macau Tools`，stdio，状态 connected；
- MCP 工具：7 个细粒度工具 + `plan_macau_trip`；
- Token Plan 配置：项目已支持 `QWEN_API_KEY / QWEN_BASE_URL /
  QWEN_MODEL`，默认 `qwen3.7-plus`；
- 安全诊断：连接脚本只打印 `Key loaded: yes (masked)`。

## 协议测试

`qa/test_qwenpaw_mcp.py` 使用真实 MCP `ClientSession` 启动 stdio Server：

1. `list_tools` 精确返回 8 个工具；
2. `check_opening(mandarin_house, 2026-07-15)` 返回周三休息；
3. `compute_route` 返回 3 个有序站与非零距离；
4. `plan_macau_trip` 完成完整事件轨迹；
5. 最终行程不含休息的郑家大屋。

结果：`QwenPaw MCP PASS`

## QwenPaw Doctor

通过项：Config、Agents、Channels、MCP clients、Skills、Browser、
Security、Memory、Workspace、Cron、Startup、Console 均为 OK。

唯一需要参赛者本人完成的凭证步骤：在 QwenPaw「设置 → 模型」粘贴队伍
Token Plan Key 并选择 `qwen3.7-plus`。因为 Key 属于共享秘密，自动化过程
不会把它写入脚本、终端、Git 或截图。未粘贴前 Doctor 会正确报告
`no active LLM`；这不是代码故障。

## 已生成初赛材料

- `docs/概念計劃書_街知巷聞_EveryLaneMacau.docx/.pdf`
  - 已改为正式队伍「愛拼才會贏」
  - 已写明 QwenPaw 2.0 / Skill / MCP 实际部署
- `docs/開發過程證明_QwenPaw_街知巷聞.docx/.pdf`
  - 9 页，包含部署、Skill、MCP、调优轨迹、五轮 QA、架构与复现步骤
- `docs/團隊介紹視頻腳本_3分鐘.md`
  - 2:50 分镜、成员介绍、开发原因、QwenPaw 证据与安全检查表
- `docs/實踐文章_街知巷聞_EveryLaneMacau.docx/.pdf`
  - 更新为实际 QwenPaw 部署与 Token Plan

## 证据截图

- `01_qwenpaw_console.png`：QwenPaw 2.0.0 Console
- `02_everylane_skill_enabled.png`：专用 Skill Enabled
- `03_everylane_mcp_connected.png`：EveryLane MCP Enabled
- `04_models_configuration.png`：模型配置入口（无任何 Key）

所有截图均不含 API Key。
