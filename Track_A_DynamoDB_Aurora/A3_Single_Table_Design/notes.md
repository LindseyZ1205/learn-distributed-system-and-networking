# A3：Single-Table Design 模式学习

## 学习目标
- 理解 DynamoDB 推荐的"单表设计"为什么，而不是多表设计
- 学习如何用 composite key 模拟关系
- 理解 Mac 老师的 dynamodb_modeler-project 的核心思想

## 推荐资源
- **GitHub**：https://github.com/MacHu-GWU/dynamodb_modeler-project
- **AWS 官方**：Single-table design in DynamoDB

## 核心思想

### 传统多表设计（错误的 DynamoDB 方式）

```
Table: Users
  PK: user_id
  {user_id, name, email}

Table: Orders
  PK: order_id
  {order_id, user_id, total}
  
Table: Items
  PK: item_id
  {item_id, order_id, product_name}
```

**问题**：要查询"用户 A 的所有订单的所有商品"，需要：
1. Query Users by user_id → 得到 user
2. Query Orders by user_id （假设有 GSI）
3. For each order，Query Items by order_id
= **3 次网络请求**（DynamoDB 的弱点）

### 单表设计（推荐）

```
Table: Everything
  PK: entity_type#entity_id (例如 "user#123", "order#456")
  SK: entity_type#entity_id (例如 "order#789", "item#999")
  {所有属性}
```

**关键**：用 **composite key** 实现 1-many 关系

```
user#123#order#456#item#789
  ├─ user#123 = partition (用户数据聚一起)
  │  ├─ order#456 = 该用户的订单
  │  │  └─ item#789 = 订单的商品
  │  └─ order#457 = 另一个订单
  └─ user#124 = 另一个用户
```

一次 Query 就能获取该用户的所有订单和商品！

## 关键技巧

### 1. Composite Key 设计

**例 1：电商系统**
```python
PK = "user#" + user_id
SK = timestamp#order_id

Query(PK="user#123", SK begins_with timestamp)
→ 该用户在某个时间范围内的所有订单
```

**例 2：社交网络**
```python
PK = "user#" + user_id
SK = "friend#" + friend_id

Query(PK="user#123", SK begins_with "friend#")
→ 用户 123 的所有朋友
```

**例 3：消息系统**
```python
PK = "conversation#" + conv_id
SK = "message#" + timestamp

Query(PK="conversation#123", SK between timestamp1 and timestamp2)
→ 某对话在某时间范围的所有消息
```

### 2. Overloaded GSI（Global Secondary Index）

当需要按不同的 key 查询时，用 GSI：

```python
# 主表
PK: "user#" + user_id
SK: "order#" + order_id

# GSI 1（按创建时间查询）
PK: "orders"  # 固定，所有订单在一起
SK: created_at

# GSI 2（按状态查询）
PK: "status#" + status
SK: created_at
```

## 与 Mac 老师讨论的价值

1. **Key 设计的重要性**
   - 关系数据库：schema 灵活，查询语言强大
   - DynamoDB：key 决定一切，设计错了很难改

2. **单表设计的哲学**
   - 违反常规的"数据库规范化"
   - 但遵循分布式系统的"locality"原则
   - 数据紧凑、查询快、成本低

3. **何时考虑分表**
   - 当单表超过 10GB 且无法再优化 key 设计
   - 当某些访问模式需要完全不同的 key 结构
   - （但通常 GSI 足够了）

## 你的思考题

1. **用 single-table 设计来建模"微博系统"**
   ```
   实体：User, Post, Comment, Like
   访问模式：
   - 查看某用户的所有 post
   - 查看某 post 的所有 comment
   - 查看某 post 的赞数
   
   设计你的 PK 和 SK：
   ```

2. **在 single-table 中，如何避免"热分区"问题？**
   - 当某个用户超级活跃（例如明星），所有访问集中在一个 partition
   - DynamoDB 如何应对？

## 完成标志
- [ ] 理解传统多表 vs 单表的区别
- [ ] 能设计至少 3 个场景的 composite key
- [ ] 浏览了 Mac 老师的 repo，理解了他的建模思想
- [ ] 回答了"微博系统"和"热分区"问题

## 学习笔记（请填写）

### Single-Table Design 的核心原则
（在这里写下你的理解...）

### 我设计的 Key 结构
（粘贴你的设计...）

### 与多表设计的主要区别
（1. ...）
（2. ...）
（3. ...）
