# A6：DynamoDB vs Aurora 对比总结

## 学习目标
- 综合理解两个分布式系统的 trade-off
- 学会在实际场景中选择合适的数据库
- 深化对 CAP theorem 的理解

## 对比维度

### 1. 数据模型

**DynamoDB**：
- Key-Value NoSQL
- No schema（或 loose schema）
- 数据：`{partition_key, sort_key, attributes}`

**Aurora**：
- 关系型 SQL
- 严格 schema（表、列、类型）
- 数据：结构化表格

### 2. 查询能力

| 查询类型 | DynamoDB | Aurora |
|---------|----------|--------|
| 按 key 查询 | ✓ 快速 | ✓ 快速 |
| 范围查询 | ✓ 仅限 sort key | ✓ 任意列 |
| JOIN | ✗ 不支持 | ✓ 完全支持 |
| 聚合（GROUP BY） | ✗ 需要应用层 | ✓ 支持 |
| 复杂过滤 | ✗ FilterExpression 有限 | ✓ 完整 WHERE 子句 |
| 全文搜索 | ✗（需要 Elasticsearch） | ✗（需要额外工具） |

### 3. 一致性和事务

**DynamoDB**：
- **最终一致性** 默认（可选强一致，但代价是延迟）
- 事务：仅限单个 item（TransactWriteItems）
- 不支持跨 item ACID 事务

**Aurora**：
- **强一致性**（ACID）
- 支持完整的事务（多表、多行）
- 支持 savepoint 和 rollback

### 4. 扩展性

**DynamoDB**：
- **水平扩展**：自动分片，按需付费
- 吞吐量几乎无上限（AWS 可扩展）
- 读/写分开计费

**Aurora**：
- **垂直扩展为主**：升级实例大小
- **水平读扩展**：用 read replica
- 存储和计算分开计费

### 5. 成本模型

**DynamoDB**：
```
成本 = (写入容量 + 读取容量) × 时间 + 存储
按需付费（Pay-as-you-go）
大规模时更便宜（线性成本）
```

**Aurora Serverless**：
```
成本 = ACU-hours + 存储 + 数据传输
小规模时较便宜（最小 0.5 ACU）
大规模时相对贵
```

### 6. 延迟和吞吐量

| 指标 | DynamoDB | Aurora |
|------|----------|--------|
| 单次读延迟 | ~1-5ms | ~1-10ms |
| 吞吐量（单个 partition） | 受限（1000 WCU） | 极高（受网络限制） |
| 吞吐量（全表） | 无上限（自动分片） | 受实例大小限制 |
| 故障转移时间 | 秒级 | 秒级 |

## 场景选择

### 用 DynamoDB

✓ 高吞吐量（每秒 10 万+ 请求）
✓ 简单 KV 查询
✓ 无 JOIN 需求
✓ 超大规模（TB+ 数据）
✓ IoT、日志、feed 系统

**例子**：
- 微博 feed（user_id → feed list）
- IoT 传感器数据（device_id + timestamp → metrics）
- 点赞数统计（post_id → like_count）
- 实时排行榜（game_id → score list）

### 用 Aurora

✓ 复杂查询（JOIN、GROUP BY）
✓ ACID 事务需求
✓ 灵活的 schema 变更
✓ 报表和分析
✓ 多维度查询

**例子**：
- 电商订单系统（orders 和 items 需要 JOIN）
- SaaS 应用（多租户，复杂 schema）
- 金融系统（事务必须 ACID）
- BI 报表（复杂聚合查询）
- 社交网络（friend graphs，需要复杂查询）

## CAP Theorem 对应

### DynamoDB
- **C**（Consistency）：△ 最终一致（或付出延迟代价）
- **A**（Availability）：✓ 高度可用（6 replicas）
- **P**（Partition tolerance）：✓ 分布式
- 选择：**AP 系统**（通常，可配置为强一致）

### Aurora
- **C**（Consistency）：✓ 强一致性
- **A**（Availability）：✓ 高度可用（read replica + failover）
- **P**（Partition tolerance）：△ 依赖于多 AZ 配置
- 选择：**CA 系统**（假设 P 不会发生，或用多 AZ 保证 P）

## 与 Mac 老师讨论的要点

1. **DynamoDB Modeler 为什么重要？**
   - 好的 key design 决定了整个系统的性能和可扩展性
   - 不像 SQL，DynamoDB 的 key 设计是 "no second thoughts" —— 错了很难改

2. **什么时候考虑混合方案？**
   - 热数据（高吞吐）→ DynamoDB
   - 冷数据（复杂查询）→ Aurora
   - 报表 → 专门数据仓库（Redshift）

3. **单表设计的深层原因**
   - DynamoDB 没有 JOIN，所以需要把相关数据聚在一起
   - 这对应了分布式系统的一个通用原则：**locality**
   - 把需要一起读的数据放在一起（同一分片），减少网络 RTT

## 写对比笔记

请为以下场景写出选择：

### 场景 1：用户动态系统
```
需求：
- 用户 A 发布动态
- 用户 B 关注用户 A，在 feed 看到动态
- 需要高吞吐（100 万日活）

选择：_________（DynamoDB / Aurora）
理由：
```

### 场景 2：在线教育平台
```
需求：
- 学生选课（1-many）
- 查询某门课的所有学生
- 统计某个学生的总成绩（多个课程 GROUP BY）
- 生成成绩单（JOIN）

选择：_________（DynamoDB / Aurora）
理由：
```

### 场景 3：实时监控系统
```
需求：
- 100 个服务器，每个每秒上报 10 条指标
- 共计 1000 指标/秒
- 查询方式：按 server_id + timestamp 范围查询
- 无复杂聚合

选择：_________（DynamoDB / Aurora）
理由：
```

## 完成标志
- [ ] 理解 6 个对比维度的区别
- [ ] 能讲清楚 CAP theorem 与两个数据库的对应关系
- [ ] 回答了 3 个场景选择题
- [ ] 写出了完整的对比笔记（至少 500 字）
