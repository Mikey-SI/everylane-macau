# Live Server QA Report

日期：2026-07-31  
公网：http://47.79.228.128/

## 结果摘要

| 套件 | 结果 |
|------|------|
| API / 资源 / 知识库 | PASS（health、70 POI、静态资源、安全头） |
| 真实 Qwen 规划（6 场景 API） | PASS（family / multi / mandarin / taipa / couple / first） |
| 浏览器桌面 + 手机 | PASS（`qa/test_live_browser.py` 全绿） |
| 本地后端回归 | **641 PASS / 0 FAIL** |

## 已修复的问题

1. **Nginx SSE 缓冲** — 关闭 `proxy_buffering`，延长超时，避免前端一直转圈。
2. **超大景点图** — 15 张 >1MB 图片压缩到约 0.15–0.42MB，公网加载更快。
3. **多日模式文案** — 明确说明每日用同一套真实工具核验（天气/开放/人流/导流/路线/预算）。

## 实测要点

- 右上角引擎：**● Qwen qwen3.7-plus**（`real_llm=true`）
- 单日场景会真实调用工具链并输出行程
- 郑家大屋星期三有失败恢复/替代路线
- 五语言导航切换正常
- 手机 390px 无横向溢出
- 打印模式只保留结果区

## 已知说明（非故障）

- 真实 Qwen 规划通常需要 **1.5–3 分钟**，属 Token Plan 多轮工具调用正常耗时。
- 多日行程使用「分区稳定规划器 + 真实工具」；单日为完整 Qwen ReAct。
- GitHub Pages 仍为静态备用演示，主链接请用服务器 IP。
