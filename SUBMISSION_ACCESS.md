# Exam Radar 评审访问信息

## 当前状态

请在完成部署并验证公网 Smoke Test 后填写真实地址。不要把 localhost、127.0.0.1 或未验证的预览地址作为提交链接。

- 公网 Demo：`待部署后填写`
- 健康检查：`待部署后填写 /api/health`
- 知乎 OAuth：由部署环境配置决定；未配置凭据时页面会显示 OAuth 未启用原因。

## 评审登录

评审账号由服务端环境变量配置，不写入前端源码：

- 用户名：`REVIEWER_USERNAME`（默认值由部署者设置）
- 密码：`REVIEWER_PASSWORD`（必须使用随机强密码）

部署者完成设置后，应将实际账号和密码仅填写在此文件的本地提交副本或安全渠道中，避免把生产密码提交到公开仓库。

## 评审流程

1. 打开公网 Demo。
2. 选择“评审登录”，输入部署者提供的账号密码；若已配置知乎 OAuth，也可选择“使用知乎登录”。
3. 打开示例课程 Machine Learning。
4. 依次体验 Knowledge Map、Exam DNA、Practice Studio、Revision Pack、导出和课程分享。

示例课程中的资料和题目是明确标注的演示数据。
