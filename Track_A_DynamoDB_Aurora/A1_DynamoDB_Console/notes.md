# A1：在 AWS Console 创建 DynamoDB Table 并手动操作

## 学习目标
- 理解 DynamoDB 的 partition key 和 sort key 概念
- 感受 key-value 数据模型与关系型数据库的区别
- 通过 Console UI 手动执行 put / get / query 操作

## 费用
- 预计：$0-0.25（操作量很小）
- 免费额度：DynamoDB 免费层包括每月 25GB 存储 + 200M 读写单位

## 操作步骤

### 1. 创建 DynamoDB Table
- [ ] 打开 AWS Console → DynamoDB
- [ ] 点 "Create table"
- [ ] 表名：`MusicLibrary`
- [ ] Partition key：`artist` (String)
- [ ] Sort key：`song_title` (String)
- [ ] 使用默认计费模式（按需 / On-demand）
- [ ] 创建

### 2. 手动插入数据
- [ ] 进入 Table → Items tab
- [ ] Create item，添加 5 条音乐记录：
  ```
  artist = "The Beatles", song_title = "Hey Jude"
  artist = "The Beatles", song_title = "Let It Be"
  artist = "Queen", song_title = "Bohemian Rhapsody"
  artist = "Queen", song_title = "Don't Stop Me Now"
  artist = "David Bowie", song_title = "Space Oddity"
  ```

### 3. 手动查询数据
- [ ] 使用 Query：搜索 `artist = "The Beatles"`，看返回的 2 条记录
- [ ] 使用 Scan：看所有 5 条记录
- [ ] 观察：Scan 比 Query 慢且贵（因为全表扫描）

## 关键概念

### Partition Key vs Sort Key
- **Partition Key**：决定数据分布到哪个分区（DynamoDB 内部的分片）
  - 必须唯一
  - 例如 `artist` - 同一个艺术家的所有歌曲分到一个分区
  
- **Sort Key**：在同一个 partition 内排序
  - 可以重复，但 (partition key + sort key) 必须唯一
  - 例如 `song_title` - 同一艺术家的歌曲按标题排序

### Query vs Scan
| 操作 | 速度 | 成本 | 何时用 |
|------|------|------|--------|
| Query | 快 | 便宜（只读相关分区） | 已知 partition key |
| Scan | 慢 | 贵（读整个表） | 没有 partition key，需要全表搜索 |

## 思考题

1. **为什么没有 JOIN？**
   - DynamoDB 不支持 JOIN，因为数据跨分区分布，JOIN 代价太高
   - 如果需要 JOIN，需要在应用层代码实现，或使用关系数据库（Aurora）

2. **如何查询"2000年后发布的歌"？**
   - 用 DynamoDB 做不到！没有"发布年份"这个 key
   - 需要加一个 sort key，或者全表 scan + 过滤（太贵）

3. **与 Aurora 的区别**
   - Aurora：结构化数据 + 复杂查询 + ACID 事务
   - DynamoDB：超大规模、无schema 的 key-value 存储

## 完成标志
- [ ] 成功创建 table
- [ ] 插入了 5 条数据
- [ ] 用 Query 查询到了 The Beatles 的 2 首歌
- [ ] 理解了 partition key / sort key / query / scan 的区别
