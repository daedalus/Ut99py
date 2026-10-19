"""Validate texture deserialization against real .utx packages.

Layouts under test (see engine/texload.py docstring):
- FMipmap operator<< order: DataArray first, then sizes (UnTex.h:204)
- TLazyArray<BYTE> version split: v<=61 compact count, v>=62 INT32 seek
  position (Core/Inc/UnTemplate.h:1043) -- Ancient.utx (v61) vs
  Belt_fx.utx (v68) cover both sides.
- Object-reference index convention (PACKAGES.md:799): 0 = NULL, positive =
  1-based export, negative = import (-Index-1); az-floor's DetailTexture=-7
  resolves to import[6] ("Detail") and its Palette=9 to export[8] (Palette16).

UT99_GAME_DIR points at another install; the module skips when it is absent.
"""

import os
from pathlib import Path

import numpy as np
import pytest

from ut99py.core.linkers import load_package
from ut99py.engine.properties import read_properties
from ut99py.engine.texload import (
    is_texture_export,
    load_palette,
    load_texture,
    texture_to_rgba,
)

GAME_DIR = Path(
    os.environ.get("UT99_GAME_DIR", "/home/dclavijo/Games/UnrealTournament")
)
TEX_DIR = GAME_DIR / "Textures"

pytestmark = pytest.mark.skipif(not TEX_DIR.is_dir(), reason="UT99 install not found")


def _linker(filename: str):
    return load_package(str(TEX_DIR / filename))


def _export(linker, name: str, class_name: str):
    """Find one export by object name and import class name."""
    for exp in linker.export_map:
        if exp.object_name.name != name:
            continue
        cls = (
            linker.import_map[-exp.class_index - 1].object_name.name
            if exp.class_index < 0
            else linker.export_map[exp.class_index - 1].object_name.name
        )
        if cls == class_name:
            return exp
    raise AssertionError(f"no {class_name} export named {name}")


class TestAncientV61:
    """Ancient.utx is v61: compact-count lazy arrays (oldver branch)."""

    def test_az_floor_mip_chain(self):
        linker = _linker("Ancient.utx")
        exp = _export(linker, "az-floor", "Texture")
        tex = load_texture(linker, exp)
        assert (tex.u_size, tex.v_size) == (256, 256)
        assert (tex.u_bits, tex.v_bits) == (8, 8)
        # Plain Texture serializes the full chain down to 1x1.
        assert len(tex.mips) == 9
        sizes = [len(m.data_array) for m in tex.mips]
        assert sizes == [65536 >> (2 * i) for i in range(9)]
        for mip in tex.mips:
            assert (mip.u_size, mip.v_size) == (1 << mip.u_bits, 1 << mip.v_bits)

    def test_az_floor_palette_and_props(self):
        linker = _linker("Ancient.utx")
        exp = _export(linker, "az-floor", "Texture")
        tex = load_texture(linker, exp)
        # Palette=9 resolves to export[8] (1-based), class Palette.
        assert tex.palette is not None
        assert len(tex.palette.colors) == 256
        # MipZero struct Color payload 37 2d 10 00.
        assert (tex.mip_zero.r, tex.mip_zero.g, tex.mip_zero.b) == (55, 45, 16)
        assert tex.props["UClamp"] == 256 and tex.props["VClamp"] == 256

    def test_az_floor_detail_texture_negative_index(self):
        linker = _linker("Ancient.utx")
        exp = _export(linker, "az-floor", "Texture")
        tex = load_texture(linker, exp)
        # -7 -> import[6]: object "fuzzy" of package "Detail" (the Detail
        # texture class import sits at [2]; negative = import[-Index-1]).
        assert tex.props["DetailTexture"] == -7
        assert linker.import_map[6].object_name.name == "fuzzy"
        assert (
            linker.import_map[-linker.import_map[6].package_index - 1].object_name.name
            == "Detail"
        )

    def test_az_floor_rgba(self):
        linker = _linker("Ancient.utx")
        exp = _export(linker, "az-floor", "Texture")
        rgba = texture_to_rgba(load_texture(linker, exp))
        assert rgba.shape == (256, 256, 4)
        assert rgba.dtype == np.uint8
        # A real photo-ish texture uses many palette entries.
        assert len(np.unique(rgba.reshape(-1, 4), axis=0)) > 64

    def test_hiwall1d_nonsquare(self):
        linker = _linker("Ancient.utx")
        exp = _export(linker, "HIWALL1D", "Texture")
        tex = load_texture(linker, exp)
        assert (tex.u_size, tex.v_size) == (128, 256)
        rgba = texture_to_rgba(tex)
        assert rgba.shape == (256, 128, 4)


class TestAlfaFXFireTextures:
    """AlfaFX.utx v61: FireTextures store one empty mip + sparks tail."""

    def test_lion4_fire_texture(self):
        linker = _linker("AlfaFX.utx")
        exp = _export(linker, "Lion4", "FireTexture")
        tex = load_texture(linker, exp)
        assert (tex.u_size, tex.v_size) == (64, 256)
        assert tex.b_parametric is True
        assert tex.props["NumSparks"] == 168
        # Parametric fire keeps a single 0-byte mip (no stored pixels).
        assert len(tex.mips) == 1
        assert len(tex.mips[0].data_array) == 0
        assert texture_to_rgba(tex) is None

    def test_palette_export_not_matched_as_texture(self):
        # "Lion4" appears twice: export Palette + export FireTexture;
        # the class check must reject the Palette.
        linker = _linker("AlfaFX.utx")
        pal_exp = _export(linker, "Lion4", "Palette")
        assert not is_texture_export(linker, pal_exp)
        fire_exp = _export(linker, "Lion4", "FireTexture")
        assert is_texture_export(linker, fire_exp)

    def test_palette_colors(self):
        linker = _linker("AlfaFX.utx")
        exp = _export(linker, "Lion4", "Palette")
        palette = load_palette(linker, exp)
        assert len(palette.colors) == 256


class TestBeltFxV68:
    """Belt_fx.utx is v68: the INT32 seek-position lazy-array branch."""

    def test_newgreen_mips(self):
        linker = _linker("Belt_fx.utx")
        exp = _export(linker, "newgreen", "Texture")
        tex = load_texture(linker, exp)
        assert (tex.u_size, tex.v_size) == (256, 256)
        sizes = [len(m.data_array) for m in tex.mips]
        assert sizes == [65536 >> (2 * i) for i in range(9)]

    def test_newgreen_rgba(self):
        linker = _linker("Belt_fx.utx")
        exp = _export(linker, "newgreen", "Texture")
        rgba = texture_to_rgba(load_texture(linker, exp))
        assert rgba.shape == (256, 256, 4)
        assert len(np.unique(rgba.reshape(-1, 4), axis=0)) > 64


class TestPropertyBlock:
    def test_az_floor_property_types(self):
        linker = _linker("Ancient.utx")
        exp = _export(linker, "az-floor", "Texture")
        linker.loader.seek(exp.serial_offset)
        props = read_properties(linker)
        assert props["UBits"] == 8 and props["USize"] == 256
        # SerializeTaggedProperties skips props equal to class defaults, so
        # absent tags (Format, bMasked) carry their defaults instead.
        assert props.get("Format", 0) == 0
        assert props.get("bMasked", False) is False
        assert props["DetailTexture"] == -7
