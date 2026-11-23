# 烘焙拼批追溯台深度登记

## 功能模块

| 模块 | 使用者动作 | 入口 | 核心文件 | 测试 |
|---|---|---|---|---|
| M1 批次秤单采信 | 看毛皮重规范、重复秤单和隔离行 | `/api/lots/weighins` | `app/modules/weighins/reader.py` `app/modules/weighins/normalize.py` `app/modules/weighins/dedup.py` | `tests/test_weighins.py` |
| M2 投入来源核验 | 核对来源存量与抢占 | `/api/lots/supply` | `app/modules/supply/reservations.py` `app/modules/supply/service.py` | `tests/test_supply.py` |
| M3 拼批图比例传递 | 逐边复查产地克重、循环和待证来源 | `/api/lots/lineage` | `app/modules/lineage/cycles.py` `app/modules/lineage/mix.py` `app/modules/lineage/service.py` | `tests/test_lineage.py` |
| M4 灌装与返料归并 | 比对净重、占用和可用返料 | `/api/lots/packing` | `app/modules/packing/budget.py` `app/modules/packing/settle.py` | `tests/test_packing.py` |
| M5 重量守恒追溯 | 对平工作批、仓内和各产地账 | `/api/lots/balance` | `app/modules/balance/service.py` `app/modules/balance/stock.py` | `tests/test_balance.py` |
| M6 批次留档复跑 | 查在柜卷联、按原件复算 | `/api/runs` | `app/modules/runs/cabinet.py` `app/modules/runs/service.py` | `tests/test_runs.py` |
| M7 配方证据签发 | 从包装号取经过校验的来料证据 | `/api/export/<id>` | `app/modules/proof/recall.py` `app/modules/proof/service.py` | `tests/test_proof.py` |

## 陷阱登记

| TRAP | 现象 | 朴素处理后果 | 本项目规则 | 位置 | 测试 |
|---|---|---|---|---|---|
| TRAP-02 | 投入表开头 BOM | 首字段不符 | 读取前去 BOM | `app/modules/weighins/reader.py` | `tests/test_weighins.py::test_bom` |
| TRAP-04 | 重复投入表头 | 混入投入量 | 记分段 | `app/modules/weighins/reader.py` | `tests/test_weighins.py::test_segment` |
| TRAP-05 | 秤单有多余列 | 滚入错位列 | 按原行隔离并保留工作批 | `app/modules/weighins/reader.py` | `tests/test_weighins.py::test_bad_width` |
| TRAP-07 | 投料 N/A | 当零重量 | 留原值且归为缺项 | `app/modules/weighins/normalize.py` | `tests/test_weighins.py::test_sentinel` |
| TRAP-10 | 两级拼批出现小数克 | 份额逐次截断 | 有理数逐边传播 | `app/modules/lineage/mix.py` | `tests/test_lineage.py::test_multi_parent_mix_exact` |
| TRAP-14 | 同号秤单不同重量 | 后写覆盖 | 隔离全部冲突行 | `app/modules/weighins/dedup.py` | `tests/test_weighins.py::test_conflict_removed` |
| TRAP-15 | 同包装秤单使用 kg 和 g | 重计或误判冲突 | 归一后精确判重 | `app/modules/weighins/mass.py` `app/modules/weighins/dedup.py` | `tests/test_weighins.py::test_unit_normalized_duplicate` |
| TRAP-19 | 两张返料申请独立看均够 | 按提交顺序抢占 | 总额超限则整组隔离 | `app/modules/supply/reservations.py` | `tests/test_supply.py::test_global_overdraw_no_first_claim` |
| TRAP-20 | 双向返料引用 | 顺序无法确定 | 提取循环分量和实际路径 | `app/modules/lineage/cycles.py` | `tests/test_lineage.py::test_actual_cycle` |

库内可信核销 1670 g = 1405 g 灌装 + 75 g 损耗 + 90 g 工作批余料 + 100 g 未领返料。6 个未通过工作批合计 390 g 分批列待证。RT-A 300 g = 180 g 给 BA-02 + 120 g 给 BA-03。PK-C 275 g = 巴西 185.46 g + 哥伦比亚 17.6 g + 埃塞 71.94 g。
