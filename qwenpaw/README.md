# QwenPaw 正式接入指南（初赛版）

本目录让「街知巷聞」不只是“参考 QwenPaw 架构”，而是实际通过
QwenPaw Skill + MCP 调用项目的 7 个旅游工具。

> 安全：API Key 只填入 QwenPaw 的密钥界面或本机 `.env`。不要写入代码、
> 截图、Word/PDF、Git commit、聊天记录或录屏。

## 一、启动 QwenPaw

本机独立环境：

```powershell
C:\Users\MACAU\.qwenpaw-venv\Scripts\qwenpaw.exe app
```

浏览器打开：<http://127.0.0.1:8088/>

## 二、添加 Token Plan 提供商

按主办方指定文档操作：

1. `设置 → 模型 → 添加提供商`
2. 协议：`OpenAI-compatible (Chat Completions)`
3. 提供商 ID：`everylane-token-plan`
4. 名称：`EveryLane · Aliyun Token Plan`
5. 保存后打开供应商“设置”
6. API Key：粘贴队伍专用 Key（只在本机粘贴）
7. Base URL：
   - 若主办方已有 `Aliyun Token Plan` 卡片，以卡片预设地址为准；
   - 中国区通常为
     `https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`
   - 国际区通常为
     `https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1`
   - 两区 Key 不通用；点击“测试连接”通过的才是正确地区。
8. 添加模型：`qwen3.7-plus`（精确匹配，区分大小写）
9. 点击“测试连接” → 绿色成功 → 保存
10. 在页面上方“默认 LLM”选择该供应商和模型。

推荐 `qwen3.7-plus`：支持推理、视觉理解、函数调用和结构化输出，适合
本项目的 ReAct 多工具流程。

## 三、添加 EveryLane MCP

进入 `工作区 → MCP → 创建客户端`：

- 名称：`EveryLane Macau Tools`
- 传输：`stdio`
- 命令：

```text
C:\Users\MACAU\.qwenpaw-venv\Scripts\python.exe
```

- 参数（按本机实际项目路径）：

```text
C:\Users\MACAU\Desktop\比赛\everylane-macau\qwenpaw\mcp_server.py
```

启用后，工具列表应出现：

1. `search_attractions`
2. `get_weather`
3. `check_opening`
4. `predict_crowd`
5. `find_local_gem`
6. `compute_route`
7. `estimate_budget`
8. `plan_macau_trip`（整套流程比较测试）

## 四、导入专用 Skill

进入 `工作区 → 技能 → 创建技能`，将
`qwenpaw/skill/everylane-macau/SKILL.md` 的完整内容粘贴并创建；
或把 `everylane-macau` 目录上传到技能页。确认技能为“已启用”。

## 五、连接测试

在 QwenPaw 对话框发送：

```text
我想去鄭家大屋同附近嘅歷史老街，星期三去，預算 300 蚊。
請逐步展示工具調用，並在景點休息時自動改線。
```

通过标准：

- 模型至少调用 `get_weather`、`search_attractions`、`check_opening`、
  `predict_crowd`、`find_local_gem`、`compute_route`、`estimate_budget`；
- 发现郑家大屋周三休息并执行替代；
- 热点有错峰或老街导流；
- 最终路线来自知识库、预算和步行数据可核对；
- 工具调用过程可在 QwenPaw 会话中截图作为开发过程证明。

## 六、初赛开发过程证明截图

建议按顺序截图（任何截图都必须遮住 Key）：

1. QwenPaw `设置 → 模型`：供应商连接绿色成功（Key 区域打码）
2. `工作区 → 技能`：EveryLane Skill 已启用
3. `工作区 → MCP`：EveryLane Macau Tools 已连接、8 个工具
4. 对话：QwenPaw 的计划与 `get_weather/search_attractions` 调用
5. 对话：郑家大屋休息 → `check_opening` → 自动改线
6. 对话：`predict_crowd` → `find_local_gem` 导流
7. 对话：`compute_route/estimate_budget` → 最终可验证行程
8. EveryLane 网站：同一请求的地图、时间轴与任务完成核对

这些截图能直接证明“在 QwenPaw 基础部署、场景设计、智能体调优与工具
调用”四项初赛要求，而不只是展示最终网页。
