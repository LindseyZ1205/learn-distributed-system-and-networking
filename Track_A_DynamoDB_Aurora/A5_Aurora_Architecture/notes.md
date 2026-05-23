# A5：理解 Aurora 分布式架构

## 学习目标
- 理解 Aurora 的 storage-compute 分离架构
- 学习 Aurora 如何用 redo log 实现高性能
- 对比 Aurora 与传统 RDS（MySQL/PostgreSQL）的差异

## 核心架构（3 句话说清）

### 传统 RDS 架构
```
┌─────────────────────────┐
│   SQL Engine + Storage  │  ← 耦合在一起
│ (MySQL/PostgreSQL)      │
└────────┬────────────────┘
         │
      共享存储
    (EBS 磁盘)
```
**问题**：
- 每个写操作都要落盘
- 写延迟 = 磁盘 I/O 延迟
- 扩展受限（单个存储卷）

### Aurora 架构（关键创新！）
```
┌──────────────────────────────────────────────┐
│  Compute Nodes (SQL Engine)                  │  ← 无状态
│  (可以有多个 read replica)                   │
└──────────────────┬─────────────────────────┘
                   │ 只发送 redo log（几 KB）
                   │ 而不是整个数据块（几 MB）
                   ↓
┌──────────────────────────────────────────────┐
│  Distributed Storage Layer                   │  ← 有状态
│  (分布在 6 个实例中，跨 3 个 AZ)              │
│  每份数据 6 copies → 强一致性 + 高可用        │
└──────────────────────────────────────────────┘
```

**优势**：
1. **写很快**：只发送 redo log（KB 级），不等 storage 完全写入
2. **读很快**：cache hit 率高（因为热数据在内存）
3. **高可用**：6 copies 跨 AZ，任意 3 个故障仍可用
4. **自动扩展**：storage 独立弹性伸缩

## 核心概念解读

### 1. Redo Log（重做日志）

```
传统 RDS 写流程：
1. Insert into table values (...)
2. [磁盘 I/O，等 fsync，可能 10-100ms]
3. 返回成功

Aurora 写流程：
1. Insert into table values (...)
2. 生成 redo log（"在位置 X 的数据改为 Y"，100 字节）
3. [发送 redo log 到 storage，只需 1-2ms]
4. 返回成功
5. [后台：storage 异步应用 redo log]
```

**为什么 Aurora 快？**
- Redo log 很小（几 KB vs 几 MB）
- 逻辑操作（"apply log"）比物理 I/O 快
- Compute 可以继续处理下一个查询，不用等 storage 完全同步

### 2. 6-Replicas across 3 AZs

```
AZ 1: replica-1 ✓, replica-2 ✓
AZ 2: replica-3 ✓, replica-4 ✓
AZ 3: replica-5 ✓, replica-6 ✓

Write quorum: 4 out of 6 (4/6 确认写成功 = 事务提交)
Read quorum: 3 out of 6 (3/6 的最新数据可读)
```

**容错能力**：
- 任意 2 个 replica 故障仍可正常服务
- 单个 AZ 完全故障（3 个 replica），仍有 3 个副本活着

### 3. Aurora Serverless 的"Serverless"含义

```
你定义：min ACU = 0.5, max ACU = 2

自动扩展：
- 0:00-8:00（低负载）→ 0.5 ACU（最小成本）
- 8:00-17:00（高负载）→ 自动升到 2 ACU
- 17:00-24:00（中负载）→ 自动降到 1 ACU

你只付费：0.5 × 8h + 2 × 9h + 1 × 7h = 4 + 18 + 7 = 29 ACU-hours
```

vs 传统 RDS（固定 db.t3.small ≈ 1 ACU）：
```
1 × 24h = 24 ACU-hours（即使 0:00-8:00 没人用）
```

## 与分布式系统的关系

### CAP Theorem 对应

```
       C（Consistency）
       ↑
       │ Aurora：强一致性
       │ 依靠 quorum write + redo log
       │
P ←────┼────→ A（Availability）
(Partition)
       │
       │ 通过 6-replica 实现高可用
       │
       ↓
```

**Aurora 的选择**：CP 偏向 CA（假设 partition 在 AZ 内部不会持久化发生）

### 复制模式对比

| 系统 | 复制方式 | 延迟 | 一致性 |
|------|---------|------|--------|
| MySQL 主从 | 异步二进制日志 | 高（可能丢数据） | 最终一致 |
| Aurora | 同步 Redo Log（4/6 quorum） | 低 | 强一致 |
| DynamoDB | 基于 Quorum 的 eventual | 毫秒 | 最终一致 |

## 你应该理解的核心

1. **为什么 Aurora 比传统 RDS 快？**
   - Redo log 小 + 异步应用 vs 同步磁盘 I/O

2. **为什么 Aurora 比 DynamoDB 贵？**
   - 要维护 6 个副本 + quorum 写入 + 强一致性的开销

3. **为什么 Aurora 适合 OLTP（在线交易）？**
   - 强一致性 + 低延迟 + 支持复杂查询

4. **为什么 DynamoDB 适合超大规模？**
   - 无需 quorum，最终一致，无限水平扩展

## 思考题

1. **如果 Aurora 的 3 个 replica 都在 AZ-1，另外 3 个在 AZ-2，会发生什么？**
   - AZ-1 宕机：至少 3 个副本丢失，< 4/6 quorum，**无法写入**！
   - 这就是为什么要"跨 3 个 AZ"分布

2. **为什么 redo log 必须发送到 storage node 才能确认写成功？**
   - 因为 redo log 是 WAL（Write-Ahead Log）的一部分
   - Compute node 的内存故障，redo log 丢失 = 数据丢失
   - 必须在 storage 上持久化

3. **如果你有 3 个 read replica，查询哪个副本？**
   - 默认：都查，选最新的（read quorum = 3/6）
   - 可配置：强一致 read 只查 primary；最终一致 read 任意查

## 完成标志
- [ ] 理解了 storage-compute 分离的好处
- [ ] 理解了 redo log 如何加速写入
- [ ] 理解了 6-replica 的容错机制
- [ ] 能讲清楚 Aurora vs 传统 RDS 的区别
- [ ] 回答了 3 个思考题

## 学习笔记

### Aurora 架构的核心优势
（请总结...）

### Redo Log 相比直接磁盘 I/O 的好处
（请分析...）

### 6-Replica quorum 如何保证一致性
（请解释...）
