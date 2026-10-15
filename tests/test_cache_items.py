"""Tests for cache item and memory cache (UnCache.h).

Expected values come from Core/Inc/UnCache.h:
- FCacheItem::COST_INFINITE = 0x1000000
- FMemCache::HASH_COUNT = 16384
- FMemCache::IGNORE_SIZE = 256
- FMemCache::GHash(Val) = (D ^ (D>>12) ^ (D>>24)) & (HASH_COUNT-1)
"""

import unittest
from ut99py.core.cache_items import FCacheItem, FMemCache


class TestFCacheItem(unittest.TestCase):
    """Test FCacheItem class (UnCache.h:21-76)."""

    def test_cost_infinite_constant(self):
        self.assertEqual(FCacheItem.COST_INFINITE, 0x1000000)

    def test_default_values(self):
        item = FCacheItem()
        self.assertEqual(item.Id, 0)
        self.assertIsNone(item.Data)
        self.assertEqual(item.Time, 0)
        self.assertEqual(item.Segment, 0)
        self.assertEqual(item.Extra, 0)
        self.assertEqual(item.Cost, 0)
        self.assertIsNone(item.LinearNext)
        self.assertIsNone(item.LinearPrev)
        self.assertIsNone(item.HashNext)

    def test_get_id(self):
        item = FCacheItem()
        item.Id = 0x15
        self.assertEqual(item.GetId(), 0x15)

    def test_get_data(self):
        item = FCacheItem()
        item.Data = b"hello"
        self.assertEqual(item.GetData(), b"hello")

    def test_get_extra(self):
        item = FCacheItem()
        item.Extra = 0x42
        self.assertEqual(item.GetExtra(), 0x42)

    def test_set_extra(self):
        item = FCacheItem()
        item.SetExtra(0xAB)
        self.assertEqual(item.Extra, 0xAB)

    def test_get_cost(self):
        item = FCacheItem()
        item.Cost = 0x1000000
        self.assertEqual(item.GetCost(), 0x1000000)

    def test_get_time(self):
        item = FCacheItem()
        item.Time = 100
        self.assertEqual(item.GetTime(), 100)

    def test_unlock(self):
        item = FCacheItem()
        item.Cost = 0x2000000
        item.Unlock()
        self.assertEqual(item.Cost, 0x1000000)

    def test_get_size_with_linear_next(self):
        item = FCacheItem()
        item.Data = b"hello"
        next_item = FCacheItem()
        next_item.Data = b"hello world"
        item.LinearNext = next_item
        self.assertEqual(item.GetSize(), 6)  # len("hello world") - len("hello")

    def test_get_size_no_linear_next(self):
        item = FCacheItem()
        item.Data = b"hello"
        self.assertEqual(item.GetSize(), 0)


class TestFMemCache(unittest.TestCase):
    """Test FMemCache class (UnCache.h:16-187)."""

    def test_constants(self):
        self.assertEqual(FMemCache.HASH_COUNT, 16384)
        self.assertEqual(FMemCache.IGNORE_SIZE, 256)
        self.assertEqual(FMemCache.COST_INFINITE, 0x1000000)

    def test_default_state(self):
        cache = FMemCache()
        self.assertFalse(cache.Initialized)
        self.assertEqual(cache.Time, 0)
        self.assertEqual(cache.MruId, 0)
        self.assertIsNone(cache.MruItem)
        self.assertEqual(len(cache.HashItems), 16384)
        self.assertEqual(cache.NumGets, 0)
        self.assertEqual(cache.NumCreates, 0)

    def test_init_exit(self):
        cache = FMemCache()
        cache.Init(1024, 100)
        self.assertTrue(cache.Initialized)
        cache.Exit(1)
        self.assertFalse(cache.Initialized)

    def test_get_time(self):
        cache = FMemCache()
        self.assertEqual(cache.GetTime(), 0)
        cache.Time = 42
        self.assertEqual(cache.GetTime(), 42)

    def test_tick(self):
        cache = FMemCache()
        cache.Time = 10
        cache.Tick()
        self.assertEqual(cache.Time, 11)

    def test_g_hash(self):
        cache = FMemCache()
        # GHash(Val) = (D ^ (D>>12) ^ (D>>24)) & (HASH_COUNT-1)
        # For Val = 0x15: D=0x15, D>>12=0, D>>24=0
        # result = (0x15 ^ 0 ^ 0) & 0x3FFF = 0x15
        self.assertEqual(cache.GHash(0x15), 0x15)
        # For Val = 0x1000: D=0x1000, D>>12=1, D>>24=0
        # result = (0x1000 ^ 1 ^ 0) & 0x3FFF = 0x1001 & 0x3FFF = 0x1001
        self.assertEqual(cache.GHash(0x1000), 0x1001)
        # For Val = 0x100000: D=0x100000, D>>12=0x100, D>>24=0
        # result = (0x100000 ^ 0x100 ^ 0) & 0x3FFF = 0x100100 & 0x3FFF = 0x100
        self.assertEqual(cache.GHash(0x100000), 0x100)

    def test_first_last_next(self):
        cache = FMemCache()
        self.assertIsNone(cache.First())
        self.assertIsNone(cache.Last())

        item1 = FCacheItem()
        item2 = FCacheItem()
        item1.LinearNext = item2
        cache.CacheItems = item1
        cache.LastItem = item2

        self.assertIs(cache.First(), item1)
        self.assertIs(cache.Last(), item2)
        self.assertIs(cache.Next(item1), item2)
        self.assertIsNone(cache.Next(item2))

    def test_get_returns_null_when_not_found(self):
        cache = FMemCache()
        item = [None]
        result = cache.Get(0x15, item)
        self.assertIsNone(result)
        self.assertIsNone(item[0])

    def test_exec_returns_false(self):
        cache = FMemCache()
        self.assertFalse(cache.Exec("test"))

    def test_status_does_not_raise(self):
        cache = FMemCache()
        cache.Status("test")

    def test_check_state_does_not_raise(self):
        cache = FMemCache()
        cache.CheckState()

    def test_flush_does_not_raise(self):
        cache = FMemCache()
        cache.Flush()
        cache.Flush(0x15)
        cache.Flush(0x15, 0xFF)
        cache.Flush(0x15, 0xFF, True)


if __name__ == "__main__":
    unittest.main()