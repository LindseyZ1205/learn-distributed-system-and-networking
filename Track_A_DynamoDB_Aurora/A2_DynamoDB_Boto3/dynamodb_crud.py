#!/usr/bin/env python3
"""
A2: DynamoDB CRUD Operations with Boto3
================================================

学习目标：
  1. 理解 DynamoDB 的 CRUD API
  2. 学会使用 KeyConditionExpression 和 FilterExpression
  3. 体验 Query vs Scan 的差异
  4. 为后续与 Mac 老师讨论 dynamodb_modeler 做准备

费用：$0-0.50 (预计 < 100 write units, < 1000 read units)

操作：
  1. 运行脚本：python3 dynamodb_crud.py
  2. 观察输出
  3. 修改代码，尝试不同的查询
"""

import boto3
import json
from decimal import Decimal
from typing import List, Dict, Any


class DynamoDBDemo:
    """DynamoDB CRUD 操作演示"""

    def __init__(self, table_name: str = "MusicLibrary", region: str = "us-east-1"):
        """
        初始化 DynamoDB 客户端

        Args:
            table_name: 表名（默认 MusicLibrary）
            region: AWS 区域（默认 us-east-1）
        """
        self.dynamodb = boto3.client('dynamodb', region_name=region)
        self.table_name = table_name
        print(f"✓ 已连接到 AWS DynamoDB (区域: {region})")

    def create_table(self) -> bool:
        """
        创建 DynamoDB 表：MusicLibrary

        表结构：
          - Partition Key: artist (String) - 艺术家名称
          - Sort Key: song_title (String) - 歌曲名称
          - 其他属性：rating, year（可选）

        Returns:
            True 如果创建成功或表已存在
        """
        try:
            # 检查表是否已存在
            self.dynamodb.describe_table(TableName=self.table_name)
            print(f"✓ 表 '{self.table_name}' 已存在")
            return True
        except self.dynamodb.exceptions.ResourceNotFoundException:
            # 表不存在，创建新表
            print(f"创建表 '{self.table_name}'...")

            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'artist',
                        'KeyType': 'HASH'  # Partition Key
                    },
                    {
                        'AttributeName': 'song_title',
                        'KeyType': 'RANGE'  # Sort Key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'artist',
                        'AttributeType': 'S'  # String
                    },
                    {
                        'AttributeName': 'song_title',
                        'AttributeType': 'S'  # String
                    }
                ],
                BillingMode='PAY_PER_REQUEST'  # 按需计费（最便宜）
            )

            # 等待表创建完成
            waiter = self.dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=self.table_name)
            print(f"✓ 表 '{self.table_name}' 创建成功")
            return True

    def put_item(self, artist: str, song_title: str, rating: int = 0, year: int = 0) -> bool:
        """
        插入或覆盖一条记录（Put Item）

        费用：1 write unit per item

        Args:
            artist: 艺术家名称
            song_title: 歌曲名称
            rating: 评分（1-5）
            year: 发行年份

        Returns:
            True if successful
        """
        try:
            self.dynamodb.put_item(
                TableName=self.table_name,
                Item={
                    'artist': {'S': artist},  # S = String type
                    'song_title': {'S': song_title},
                    'rating': {'N': str(rating)},  # N = Number type
                    'year': {'N': str(year)}
                }
            )
            return True
        except Exception as e:
            print(f"✗ 插入失败: {e}")
            return False

    def get_item(self, artist: str, song_title: str) -> Dict[str, Any] | None:
        """
        获取单条记录（Get Item）

        最快的查询方式（O(1)）

        费用：1 read unit per item

        Args:
            artist: 艺术家名称
            song_title: 歌曲名称

        Returns:
            包含属性的字典，或 None 如果不存在
        """
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={
                    'artist': {'S': artist},
                    'song_title': {'S': song_title}
                }
            )

            if 'Item' in response:
                return self._format_item(response['Item'])
            else:
                print(f"未找到：{artist} - {song_title}")
                return None
        except Exception as e:
            print(f"✗ 获取失败: {e}")
            return None

    def query(self, artist: str) -> List[Dict[str, Any]]:
        """
        按 partition key 查询所有相关记录（Query）

        快速且高效的查询（只读特定分区）

        费用：取决于返回的记录数

        Args:
            artist: 艺术家名称

        Returns:
            该艺术家的所有歌曲列表
        """
        try:
            response = self.dynamodb.query(
                TableName=self.table_name,
                KeyConditionExpression='artist = :artist',
                ExpressionAttributeValues={
                    ':artist': {'S': artist}
                }
            )

            items = [self._format_item(item) for item in response.get('Items', [])]
            return items
        except Exception as e:
            print(f"✗ 查询失败: {e}")
            return []

    def query_with_sort_key_range(self, artist: str, year_start: int, year_end: int) -> List[Dict[str, Any]]:
        """
        按 partition key 和 sort key 范围查询

        进阶查询示例：结合了 partition key 和 sort key 条件

        Args:
            artist: 艺术家名称
            year_start: 开始年份
            year_end: 结束年份

        Returns:
            符合条件的歌曲列表
        """
        try:
            # 注意：这个查询需要建立 GSI（Global Secondary Index）
            # 因为 year 不是 sort key，这里只是展示语法
            # 实际上应该用 Scan + FilterExpression

            response = self.dynamodb.query(
                TableName=self.table_name,
                KeyConditionExpression='artist = :artist',
                ExpressionAttributeValues={
                    ':artist': {'S': artist}
                }
            )

            # 在应用层过滤年份
            items = [
                self._format_item(item) for item in response.get('Items', [])
                if int(item['year']['N']) >= year_start and int(item['year']['N']) <= year_end
            ]
            return items
        except Exception as e:
            print(f"✗ 查询失败: {e}")
            return []

    def scan(self, filter_rating: int | None = None) -> List[Dict[str, Any]]:
        """
        全表扫描（Scan）

        ⚠️ 警告：慢且贵！只在必要时使用

        费用：读取所有记录的 read units

        Args:
            filter_rating: 可选，筛选评分 >= 此值

        Returns:
            所有扫描到的记录
        """
        try:
            if filter_rating is not None:
                # 使用 FilterExpression 在客户端过滤
                response = self.dynamodb.scan(
                    TableName=self.table_name,
                    FilterExpression='rating >= :rating',
                    ExpressionAttributeValues={
                        ':rating': {'N': str(filter_rating)}
                    }
                )
            else:
                response = self.dynamodb.scan(TableName=self.table_name)

            items = [self._format_item(item) for item in response.get('Items', [])]
            return items
        except Exception as e:
            print(f"✗ 扫描失败: {e}")
            return []

    def update_item(self, artist: str, song_title: str, rating: int) -> bool:
        """
        更新单条记录（Update Item）

        费用：1 write unit per item

        Args:
            artist: 艺术家名称
            song_title: 歌曲名称
            rating: 新评分

        Returns:
            True if successful
        """
        try:
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={
                    'artist': {'S': artist},
                    'song_title': {'S': song_title}
                },
                UpdateExpression='SET #r = :new_rating',
                ExpressionAttributeNames={
                    '#r': 'rating'  # 使用别名避免与 DynamoDB 关键字冲突
                },
                ExpressionAttributeValues={
                    ':new_rating': {'N': str(rating)}
                }
            )
            return True
        except Exception as e:
            print(f"✗ 更新失败: {e}")
            return False

    def delete_item(self, artist: str, song_title: str) -> bool:
        """
        删除单条记录（Delete Item）

        费用：1 write unit per item

        Args:
            artist: 艺术家名称
            song_title: 歌曲名称

        Returns:
            True if successful
        """
        try:
            self.dynamodb.delete_item(
                TableName=self.table_name,
                Key={
                    'artist': {'S': artist},
                    'song_title': {'S': song_title}
                }
            )
            return True
        except Exception as e:
            print(f"✗ 删除失败: {e}")
            return False

    def delete_table(self) -> bool:
        """删除整个表（清理资源）"""
        try:
            self.dynamodb.delete_table(TableName=self.table_name)
            waiter = self.dynamodb.get_waiter('table_not_exists')
            waiter.wait(TableName=self.table_name)
            print(f"✓ 表 '{self.table_name}' 已删除")
            return True
        except Exception as e:
            print(f"✗ 删除失败: {e}")
            return False

    @staticmethod
    def _format_item(item: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        将 DynamoDB 格式的 item 转换为 Python 字典

        DynamoDB 格式：
          {'artist': {'S': 'The Beatles'}, 'rating': {'N': '5'}}

        Python 格式：
          {'artist': 'The Beatles', 'rating': 5}
        """
        result = {}
        for key, value in item.items():
            if 'S' in value:
                result[key] = value['S']
            elif 'N' in value:
                result[key] = int(value['N'])
            elif 'B' in value:
                result[key] = value['B']
        return result


def main():
    """主函数：演示所有 CRUD 操作"""

    print("=" * 70)
    print("DynamoDB CRUD 操作演示")
    print("=" * 70)
    print()

    # 初始化
    demo = DynamoDBDemo("MusicLibrary")

    # 1. 创建表
    print("\n【1】创建表...")
    demo.create_table()
    print()

    # 2. 插入数据
    print("【2】插入数据...")
    songs = [
        ("The Beatles", "Hey Jude", 5, 1968),
        ("The Beatles", "Let It Be", 4, 1970),
        ("Queen", "Bohemian Rhapsody", 5, 1975),
        ("Queen", "Don't Stop Me Now", 4, 1978),
        ("David Bowie", "Space Oddity", 5, 1969),
        ("Pink Floyd", "Comfortably Numb", 5, 1979),
        ("Led Zeppelin", "Stairway to Heaven", 5, 1971),
    ]

    for artist, song, rating, year in songs:
        if demo.put_item(artist, song, rating, year):
            print(f"  ✓ 插入：{artist} - {song} (评分: {rating}, 年份: {year})")
    print()

    # 3. Get Item - 获取单条记录
    print("【3】Get Item - 按完整 key 获取单条记录...")
    item = demo.get_item("The Beatles", "Hey Jude")
    if item:
        print(f"  → {item}")
    print()

    # 4. Query - 按 partition key 查询
    print("【4】Query - 按 partition key (artist) 查询...")
    print("  查询：artist = 'Queen'")
    items = demo.query("Queen")
    for item in items:
        print(f"    → {item}")
    print()

    # 5. Scan - 全表扫描
    print("【5】Scan - 全表扫描（⚠️ 慢且贵！）...")
    print("  扫描全表，过滤 rating >= 4")
    items = demo.scan(filter_rating=4)
    print(f"  共找到 {len(items)} 条记录（rating >= 4）")
    for item in items:
        print(f"    → {item}")
    print()

    # 6. Update Item - 更新单条记录
    print("【6】Update Item - 更新单条记录...")
    print("  更新：Queen - 'Bohemian Rhapsody' 评分改为 5.0（已是最高）")
    if demo.update_item("Queen", "Bohemian Rhapsody", 5):
        print("  ✓ 更新成功")
    print()

    # 7. Delete Item - 删除单条记录
    print("【7】Delete Item - 删除单条记录...")
    print("  删除：David Bowie - 'Space Oddity'")
    if demo.delete_item("David Bowie", "Space Oddity"):
        print("  ✓ 删除成功")
    print()

    # 8. 最终 Query - 验证删除
    print("【8】最终验证 - 查询所有艺术家...")
    all_artists = set()
    for artist, _, _, _ in songs:
        if artist != "David Bowie":  # 排除已删除的
            all_artists.add(artist)

    for artist in sorted(all_artists):
        items = demo.query(artist)
        print(f"  {artist} ({len(items)} 首歌):")
        for item in items:
            print(f"    → {item['song_title']} (评分: {item['rating']}, 年份: {item['year']})")
    print()

    # 9. 性能对比：Query vs Scan
    print("【9】性能对比：Query vs Scan")
    print("  场景：查找 'The Beatles' 的所有歌曲")

    import time

    # Query（快）
    start = time.time()
    items = demo.query("The Beatles")
    query_time = time.time() - start

    # Scan（慢）
    start = time.time()
    items = demo.scan()
    items = [i for i in items if i.get('artist') == 'The Beatles']
    scan_time = time.time() - start

    print(f"  Query 耗时：{query_time*1000:.2f}ms（直接查询 partition）")
    print(f"  Scan 耗时：{scan_time*1000:.2f}ms（全表扫描后过滤）")
    print(f"  Query 快 {scan_time/query_time:.1f}x")
    print()

    # 10. 费用分析
    print("【10】费用分析")
    total_writes = len(songs) + 1  # put_items + 1 update
    total_reads = (3 +  # 3 次 query
                   1 +  # 1 次 get_item
                   2 *  # 2 次 scan
                   len(songs))  # 大约读取所有记录

    write_cost = total_writes * 1.25 / 1e6  # $1.25 per million WCU
    read_cost = total_reads * 0.25 / 1e6   # $0.25 per million RCU
    total_cost = write_cost + read_cost

    print(f"  Write 操作：{total_writes} 次 → ${write_cost:.4f}")
    print(f"  Read 操作：{total_reads} 次 → ${read_cost:.4f}")
    print(f"  总费用：${total_cost:.4f}（按需计费）")
    print()

    print("=" * 70)
    print("演示完成！")
    print("=" * 70)
    print()

    # 可选：清理表（注释掉以保留表用于进一步学习）
    # print("清理资源...")
    # demo.delete_table()
    # print("✓ 表已删除")


if __name__ == "__main__":
    main()
