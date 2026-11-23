# 烘焙拼批追溯台

烘焙质控员从包装号反查工作批、返料卷联和产地批。工作台逐笔核对净重、产地克重和待证差额，提供按工作批打印的称签卷联。

## 运行

执行 `docker compose up --build` 后访问 `http://localhost:18474`。也可安装 `requirements.txt` 后执行 `python -m app.main`。运行档案存放在 `ROAST_CABINET`，默认 `var/cabinet`。停止服务后可移除该目录或对应 Compose 命名卷以清空档案。

## 复核路线

1. 首页的重量勾稽卷联列出每批总秤、灌装、损耗、余量和待证。查 BA-07 的 100 g 待证与 10 g 负余量。
2. 在投入来源核验查 RT-A 的两次领用，再查 RT-D 的 120 g 争抢。前者全部核入，后者 100 g 保留在库。
3. 在拼批图比例传递选择 BA-03，查看两级返料的来源贡献。切换 BA-09 查看循环证据。
4. 从批次留档复跑进行归档，再进入配方证据签发。打印卷联或下载 JSON，复核 PK-C 的 275 g 产地构成。

`GET /api/lots/<phase>` 分阶段预览样例。向同路径 POST `{"files":{"origins":"...","jobs":"...","inputs":"...","outputs":"..."}}` 可试算自己的 CSV。`POST /api/runs` 接受同样的文件集合或 `{"sample":"dirty"}`。`GET /api/runs/<id>` 查归档，`POST /api/runs/<id>/rerun` 复算，`GET /api/export/<id>` 下载证据。

[定义与边界](docs/DATA-DICTIONARY.md) 和 [模块与回归](docs/DEPTH.md) 记录完整规则。本机运行 `python -m pytest -q`。
