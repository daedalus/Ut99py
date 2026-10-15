"""Tests for cache ID functions."""

import unittest
from ut99py.core.cache import (
    ECacheIDBase,
    make_cache_id,
    make_cache_id_with_objects,
    make_cache_id_with_bytes,
    make_cache_id_with_three_bytes,
    make_cache_id_from_qword,
)


class TestECacheIDBase(unittest.TestCase):
    """Test the ECacheIDBase enum values."""

    def test_all_values(self):
        # Check all enum members have expected values
        self.assertEqual(ECacheIDBase.ShadowMap, 0x15)
        self.assertEqual(ECacheIDBase.IlluminationMap, 0x16)
        self.assertEqual(ECacheIDBase.LightPalette, 0x17)
        self.assertEqual(ECacheIDBase.StaticMap, 0x18)
        self.assertEqual(ECacheIDBase.DepthLineTable, 0x1C)
        self.assertEqual(ECacheIDBase.TweenAnim, 0x1D)
        self.assertEqual(ECacheIDBase.TriPalette, 0x1E)
        self.assertEqual(ECacheIDBase.InputMap, 0x1F)
        self.assertEqual(ECacheIDBase.VolumetricScaler, 0x20)
        self.assertEqual(ECacheIDBase.RenderPalette, 0x25)
        self.assertEqual(ECacheIDBase.RenderFogMap, 0x26)
        self.assertEqual(ECacheIDBase.CoronaCache, 0x27)
        self.assertEqual(ECacheIDBase.PolyPalette, 0x28)
        self.assertEqual(ECacheIDBase.PolyMMXPalette, 0x29)
        self.assertEqual(ECacheIDBase.SurfPalette, 0x2A)
        self.assertEqual(ECacheIDBase.SurfMMXPalette, 0x2B)
        self.assertEqual(ECacheIDBase.LitTilePal, 0x2C)
        self.assertEqual(ECacheIDBase.LitTileTrans, 0x2D)
        self.assertEqual(ECacheIDBase.LitTileMMX, 0x2E)
        self.assertEqual(ECacheIDBase.LitTileMod, 0x2F)
        self.assertEqual(ECacheIDBase.ActorLightCache, 0x30)
        self.assertEqual(ECacheIDBase.DynamicMap, 0x31)
        self.assertEqual(ECacheIDBase.GlidePal, 0x32)
        self.assertEqual(ECacheIDBase.BumpNormals, 0x33)
        self.assertEqual(ECacheIDBase.SkeletalData, 0x34)
        self.assertEqual(ECacheIDBase.RenderTexture, 0xE0)
        self.assertEqual(ECacheIDBase.Max, 0xFF)


class TestMakeCacheID(unittest.TestCase):
    """Test the MakeCacheID functions."""

    def test_make_cache_id(self):
        # Basic case: base + (frame_index << 8)
        self.assertEqual(make_cache_id(ECacheIDBase.ShadowMap, 0), int(ECacheIDBase.ShadowMap) + (0 << 8))
        self.assertEqual(make_cache_id(ECacheIDBase.ShadowMap, 1), int(ECacheIDBase.ShadowMap) + (1 << 8))
        self.assertEqual(make_cache_id(ECacheIDBase.ShadowMap, 10), int(ECacheIDBase.ShadowMap) + (10 << 8))

    def test_make_cache_id_with_objects(self):
        # base + (obj_index << 8) + (frame_index << 32)
        base = int(ECacheIDBase.ShadowMap)
        self.assertEqual(make_cache_id_with_objects(ECacheIDBase.ShadowMap, 0, 0), base + 0 + 0)
        self.assertEqual(make_cache_id_with_objects(ECacheIDBase.ShadowMap, 1, 0), base + (1 << 8) + 0)
        self.assertEqual(make_cache_id_with_objects(ECacheIDBase.ShadowMap, 0, 1), base + 0 + (1 << 32))
        self.assertEqual(make_cache_id_with_objects(ECacheIDBase.ShadowMap, 1, 1), base + (1 << 8) + (1 << 32))

    def test_make_cache_id_with_bytes(self):
        # base + (byte << 8) + (word << 16) + (frame_index << 32)
        base = int(ECacheIDBase.ShadowMap)
        self.assertEqual(make_cache_id_with_bytes(ECacheIDBase.ShadowMap, 0, 0, 0), base + 0 + 0 + 0)
        self.assertEqual(make_cache_id_with_bytes(ECacheIDBase.ShadowMap, 1, 0, 0), base + (1 << 8) + 0 + 0)
        self.assertEqual(make_cache_id_with_bytes(ECacheIDBase.ShadowMap, 0, 1, 0), base + 0 + (1 << 16) + 0)
        self.assertEqual(make_cache_id_with_bytes(ECacheIDBase.ShadowMap, 0, 0, 1), base + 0 + 0 + (1 << 32))
        self.assertEqual(make_cache_id_with_bytes(ECacheIDBase.ShadowMap, 1, 1, 1), base + (1 << 8) + (1 << 16) + (1 << 32))

    def test_make_cache_id_with_three_bytes(self):
        # base + (byte_a << 8) + (byte_b << 16) + (byte_c << 24) + (frame_index << 32)
        base = int(ECacheIDBase.ShadowMap)
        self.assertEqual(make_cache_id_with_three_bytes(ECacheIDBase.ShadowMap, 0, 0, 0, 0), base + 0 + 0 + 0 + 0)
        self.assertEqual(make_cache_id_with_three_bytes(ECacheIDBase.ShadowMap, 1, 0, 0, 0), base + (1 << 8) + 0 + 0 + 0)
        self.assertEqual(make_cache_id_with_three_bytes(ECacheIDBase.ShadowMap, 0, 1, 0, 0), base + 0 + (1 << 16) + 0 + 0)
        self.assertEqual(make_cache_id_with_three_bytes(ECacheIDBase.ShadowMap, 0, 0, 1, 0), base + 0 + 0 + (1 << 24) + 0)
        self.assertEqual(make_cache_id_with_three_bytes(ECacheIDBase.ShadowMap, 1, 1, 1, 1), base + (1 << 8) + (1 << 16) + (1 << 24) + (1 << 32))

    def test_make_cache_id_from_qword(self):
        # base + (qword & ~CID_MAX) where CID_MAX = 0xFF
        base = int(ECacheIDBase.ShadowMap)
        cid_max = int(ECacheIDBase.Max)
        mask = ~cid_max & 0xFFFFFFFFFFFFFFFF  # QWORD unsigned ~0xFF
        self.assertEqual(make_cache_id_from_qword(ECacheIDBase.ShadowMap, 0x100), base + (0x100 & mask))
        self.assertEqual(make_cache_id_from_qword(ECacheIDBase.ShadowMap, 0x200), base + (0x200 & mask))
        self.assertEqual(make_cache_id_from_qword(ECacheIDBase.ShadowMap, 0xFFFF), base + (0xFFFF & mask))


if __name__ == "__main__":
    unittest.main()
