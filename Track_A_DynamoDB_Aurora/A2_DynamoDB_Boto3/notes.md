# A2：用 Python Boto3 操作 DynamoDB（CRUD + 关键 API）

## 学习目标
- 用 Python SDK (boto3) 实现 DynamoDB CRUD 操作
- 理解 KeyConditionExpression / FilterExpression 的写法
- 对比 Query vs Scan 的性能和成本差异
- 为后续与 Mac 老师讨论 dynamodb_modeler 做准备

## 费用
- 预计：$0-0.50
- 说明：脚本会跑多次查询，但量很小（< 10 WCU）

## 前置准备
```bash
# 1. 安装 boto3
pip3 install boto3

# 2. 验证 AWS 凭证已配置
aws sts get-caller-identity
# 应该看到你的 AWS account ID

# 3. 检查是否有 MusicLibrary table（来自 A1）
# 如果没有，需要先完成 A1，或直接用代码创建（见下面的代码注释）
```

## 代码文件
- `dynamodb_crud.py`：主要实现文件

## 运行方式
```bash
cd Track_A_DynamoDB_Aurora/A2_DynamoDB_Boto3
python3 dynamodb_crud.py
```

## 预期输出
```
=== DynamoDB CRUD 演示 ===

1. 创建 table...
✓ Table 'MusicLibrary' 已创建 (或已存在)

2. 插入数据...
✓ 插入 5 首歌曲

3. 查询演示...
Query: artist = 'The Beatles'
  → Hey Jude
  → Let It Be

4. Scan 演示...
Scan: 所有歌曲
  → 5 条记录

5. 更新演示...
✓ 更新 Queen 的 'Bohemian Rhapsody' 评分为 5

6. 删除演示...
✓ 删除了 David Bowie 的 'Space Oddity'

7. 最后的 Query...
Query: artist = 'Queen'
  → Bohemian Rhapsody (rating: 5)
  → Don't Stop Me Now

=== 完成 ===
```

## 核心 API 解读

### 1. 创建 Table
```python
client.create_table(
    TableName='MusicLibrary',
    KeySchema=[
        {'AttributeName': 'artist', 'KeyType': 'HASH'},        # Partition key
        {'AttributeName': 'song_title', 'KeyType': 'RANGE'}    # Sort key
    ],
    AttributeDefinitions=[
        {'AttributeName': 'artist', 'AttributeType': 'S'},
        {'AttributeName': 'song_title', 'AttributeType': 'S'}
    ],
    BillingMode='PAY_PER_REQUEST'  # 按需计费
)
```

### 2. Put Item (插入或覆盖)
```python
client.put_item(
    TableName='MusicLibrary',
    Item={
        'artist': {'S': 'The Beatles'},
        'song_title': {'S': 'Hey Jude'},
        'rating': {'N': '5'},  # N = Number, S = String, etc.
        'year': {'N': '1968'}
    }
)
```

### 3. Get Item (按 key 查询单条)
```python
response = client.get_item(
    TableName='MusicLibrary',
    Key={
        'artist': {'S': 'The Beatles'},
        'song_title': {'S': 'Hey Jude'}
    }
)
item = response['Item']
```

### 4. Query (按 partition key + sort key 条件查询)
```python
response = client.query(
    TableName='MusicLibrary',
    KeyConditionExpression='artist = :artist',  # 只能用 = 或 begins_with
    ExpressionAttributeValues={
        ':artist': {'S': 'The Beatles'}
    }
)
items = response['Items']
```

### 5. Scan (全表扫描 + 过滤)
```python
response = client.scan(
    TableName='MusicLibrary',
    FilterExpression='rating > :rating',  # 在 Scan 后过滤
    ExpressionAttributeValues={
        ':rating': {'N': '3'}
    }
)
items = response['Items']
```

### 6. Update Item
```python
client.update_item(
    TableName='MusicLibrary',
    Key={
        'artist': {'S': 'Queen'},
        'song_title': {'S': 'Bohemian Rhapsody'}
    },
    UpdateExpression='SET #r = :new_rating',  # #r = 别名（避免关键字冲突）
    ExpressionAttributeNames={
        '#r': 'rating'
    },
    ExpressionAttributeValues={
        ':new_rating': {'N': '5'}
    }
)
```

### 7. Delete Item
```python
client.delete_item(
    TableName='MusicLibrary',
    Key={
        'artist': {'S': 'David Bowie'},
        'song_title': {'S': 'Space Oddity'}
    }
)
```

## 关键概念

### KeyConditionExpression 的局限
DynamoDB 的 key 查询只支持：
- `=`：精确匹配
- `begins_with()`：前缀匹配
- `>`、`>=`、`<`、`<=`、`BETWEEN`：范围查询（仅对 sort key）

**例**：
```python
# ✓ 正确
'artist = :a'  # partition key 只能 =
'artist = :a AND song_title BETWEEN :s1 AND :s2'  # range

# ✗ 错误
'rating > :r'  # rating 不是 key，不能用 KeyConditionExpression
```

### 性能对比
| 操作 | 用途 | 费用 | 速度 |
|------|------|------|------|
| GetItem | 按完整 key 查 1 条 | 1 RCU | 最快 |
| Query | 按 partition key + sort key 条件查多条 | 扫描数量 RCU | 快 |
| Scan | 全表扫描 + 过滤 | 整表大小 RCU | 最慢 |

## 思考题

1. **为什么 `FilterExpression` 和 `KeyConditionExpression` 不一样？**
   - KeyConditionExpression：应用在 **key 上**，在 DynamoDB 内部高效过滤（读少数据）
   - FilterExpression：应用在 **非 key 属性上**，先读数据再过滤（读大量数据）

2. **如果想按 `rating > 3` 查询，应该怎么做？**
   - 用 Scan + FilterExpression（慢且贵）
   - 或者用 GSI（Global Secondary Index）—— 见 A3

3. **DynamoDB 如何处理"两个用户的聊天记录"这样的 1-to-many 关系？**
   - Partition key = conversation_id
   - Sort key = message_timestamp
   - 所有该对话的消息放一起，按时间排序
   - 这就是 **single-table design** —— 见 A3

## 完成标志
- [ ] 能运行 dynamodb_crud.py，看到完整输出
- [ ] 理解 KeyConditionExpression 的语法和限制
- [ ] 理解 Query 和 Scan 的区别（性能和成本）
- [ ] 修改代码：添加一个按 year 过滤的 Scan 操作
