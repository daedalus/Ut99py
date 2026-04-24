"""UT Package Reader - Based on Ut99PubSrc and UTPackage.js

Handles reading UT99 package files (.u, .unr, .utx, .umx, .uax)
"""

import struct
from typing import List, Dict, Optional, Any
from pathlib import Path

SIGNATURE_UT = 0x9E2A83C1


class PackageReader:
    """Read UT99 package files"""
    
    def __init__(self, filepath: str):
        self._filepath = filepath
        with open(filepath, 'rb') as f:
            self._data = f.read()
        
        self._offset = 0
        self._header = None
        self._version = 0
        self._name_table = []
        self._export_table = []
        self._import_table = []
    
    @property
    def data(self) -> bytes:
        return self._data
    
    def seek(self, offset: int) -> None:
        self._offset = offset
    
    def tell(self) -> int:
        return self._offset
    
    def _read_uint8(self) -> int:
        val = self._data[self._offset]
        self._offset += 1
        return val
    
    def _read_uint16(self) -> int:
        val = struct.unpack('<H', self._data[self._offset:self._offset+2])[0]
        self._offset += 2
        return val
    
    def _read_uint32(self) -> int:
        val = struct.unpack('<I', self._data[self._offset:self._offset+4])[0]
        self._offset += 4
        return val
    
    def _read_int32(self) -> int:
        val = struct.unpack('<i', self._data[self._offset:self._offset+4])[0]
        self._offset += 4
        return val
    
    def _read_compact_index(self) -> int:
        """FCompactIndex - variable-length encoded integer"""
        value = self._read_uint8()
        
        is_negative = value & 0b10000000
        read_next_byte = value & 0b01000000
        value = value & 0b00111111
        
        byte_num = 2
        shift_amt = 6
        
        while read_next_byte:
            byte = self._read_uint8()
            value_bit_mask = 0b01111111 if byte_num < 5 else 0b00011111
            value = ((byte & value_bit_mask) << shift_amt | value) & 0xFFFFFFFF
            read_next_byte = byte & 0b10000000
            byte_num += 1
            shift_amt += 7
        
        return -value if is_negative else value
    
    def _read_name(self) -> str:
        index = self._read_compact_index()
        if 0 <= index < len(self._name_table):
            return self._name_table[index]['name']
        return "None"
    
    def _read_string(self) -> str:
        """Read a null-terminated string"""
        chars = []
        while self._offset < len(self._data):
            c = self._data[self._offset]
            self._offset += 1
            if c == 0:
                break
            chars.append(c)
        return bytes(chars).decode('latin-1', errors='replace')
    
    def _read_sized_string(self) -> str:
        """Read string with size prefix (v64+ format)
        
        Format: 1 byte = total size including null terminator
        String is stored from offset+1 for (size-1) bytes
        Last byte is null terminator which should be stripped
        """
        size = self._read_uint8()
        if size == 0:
            return ""
        # Read (size-1) bytes for string (the last byte is the null terminator)
        text = self._data[self._offset:self._offset+size-1].decode('latin-1', errors='replace')
        self._offset += size
        return text
    
    def get_package_header(self) -> Dict:
        """Read package file header"""
        self.seek(0)
        
        header = {}
        
        header['signature'] = self._read_uint32()
        if header['signature'] != SIGNATURE_UT:
            # Try byte-swapped
            swapped = struct.pack('>I', header['signature'])
            raise ValueError(f"Invalid package signature: 0x{header['signature']:08X}")
        
        # Version is stored as Uint16 little-endian
        header['version'] = self._read_uint16()
        header['licensee_version'] = self._read_uint16()
        
        # Package flags
        header['package_flags'] = self._read_uint32()
        
        # Table counts and offsets
        header['name_count'] = self._read_uint32()
        header['name_offset'] = self._read_uint32()
        header['export_count'] = self._read_uint32()
        header['export_offset'] = self._read_uint32()
        header['import_count'] = self._read_uint32()
        header['import_offset'] = self._read_uint32()
        
        if header['version'] >= 68:
            # GUID (16 bytes)
            header['guid'] = self._data[self._offset:self._offset+16].hex().upper()
            self._offset += 16
            
            # Generations
            generation_count = self._read_uint32()
            header['generations'] = []
            for _ in range(generation_count):
                gen = {
                    'export_count': self._read_uint32(),
                    'name_count': self._read_uint32(),
                }
                header['generations'].append(gen)
        
        return header
    
    def get_name_table(self) -> List[Dict]:
        """Read the name table"""
        self.seek(self._header['name_offset'])
        
        names = []
        for _ in range(self._header['name_count']):
            if self._header['version'] < 64:
                # Old format: null-terminated string
                name = self._read_string()
            else:
                # New format: size-prefixed
                name = self._read_sized_string()
            
            flags = self._read_uint32()
            names.append({'name': name, 'flags': flags})
        
        return names
    
    def get_export_table(self) -> List[Dict]:
        """Read the export table"""
        self.seek(self._header['export_offset'])
        
        exports = []
        for _ in range(self._header['export_count']):
            exp = {
                'class_index': self._read_compact_index(),
                'super_index': self._read_compact_index(),
                'package_index': self._read_int32(),
                'object_name_index': self._read_compact_index(),
                'object_flags': self._read_uint32(),
                'serial_size': self._read_compact_index(),
            }
            
            if exp['serial_size'] > 0:
                exp['serial_offset'] = self._read_compact_index()
            else:
                exp['serial_offset'] = 0
            
            exports.append(exp)
        
        return exports
    
    def get_import_table(self) -> List[Dict]:
        """Read the import table"""
        self.seek(self._header['import_offset'])
        
        imports = []
        for _ in range(self._header['import_count']):
            imp = {
                'class_package_index': self._read_compact_index(),
                'class_name_index': self._read_compact_index(),
                'package_index': self._read_int32(),
                'object_name_index': self._read_compact_index(),
            }
            imports.append(imp)
        
        return imports
    
    def read_package(self) -> 'PackageReader':
        """Read the entire package"""
        self._header = self.get_package_header()
        self._version = self._header['version']
        self._name_table = self.get_name_table()
        self._export_table = self.get_export_table()
        self._import_table = self.get_import_table()
        return self
    
    def get_object(self, index: int) -> Optional[Dict]:
        if index == 0:
            return None
        elif index < 0:
            return self._import_table[~index]
        else:
            return self._export_table[index - 1]
    
    def get_object_name(self, index: int) -> str:
        obj = self.get_object(index)
        if obj is None:
            return "None"
        return self._name_table[obj['object_name_index']]['name']
    
    def get_exports_by_class(self, class_name: str) -> List[Dict]:
        """Find all exports of a specific class"""
        results = []
        for exp in self._export_table:
            class_idx = exp['class_index']
            if class_idx == 0:
                continue
            if class_idx < 0:
                class_obj = self._import_table[~class_idx]
                class_obj_name = self._name_table[class_obj['class_name_index']]['name']
            else:
                class_obj = self._export_table[class_idx - 1]
                class_obj_name = self._name_table[class_obj['object_name_index']]['name']
            
            if class_obj_name == class_name:
                results.append(exp)
        
        return results
    
    def get_export_name(self, exp: Dict) -> str:
        return self._name_table[exp['object_name_index']]['name']
    
    def get_class_name(self, exp: Dict) -> str:
        """Get the actual class name from export's class_index"""
        class_idx = exp['class_index']
        if class_idx == 0:
            return "Class"
        if class_idx < 0:
            imp = self._import_table[~class_idx]
            # The import's object_name_index is the actual class name
            return self._name_table[imp['object_name_index']]['name']
        else:
            class_obj = self._export_table[class_idx - 1]
            return self._name_table[class_obj['object_name_index']]['name']
    
    def get_export_class_name(self, exp: Dict) -> str:
        """Get the class that exports this object (what it IS, not what type it is)"""
        return self.get_class_name(exp)
    
    def get_super_class_name(self, exp: Dict) -> str:
        """Get the parent class name from export's super_index"""
        super_idx = exp['super_index']
        if super_idx == 0:
            return "Object"
        if super_idx < 0:
            imp = self._import_table[~super_idx]
            return self._name_table[imp['object_name_index']]['name']
        else:
            super_exp = self._export_table[super_idx - 1]
            return self._name_table[super_exp['object_name_index']]['name']
    
    def read_texture_data(self, exp: Dict) -> Optional[Dict]:
        """Read texture serialization data from an export
        
        Returns a dict with texture properties:
        - u_size, v_size: texture dimensions
        - u_clamp, v_clamp: clamp values
        - palette: list of FColor (256 colors)
        - mips: list of mipmap data (list of bytes)
        - format: texture format
        """
        cls_name = self.get_class_name(exp)
        if cls_name != 'Texture':
            return None
        
        name = self.get_export_name(exp)
        
        texture = {
            'name': name,
            'u_size': 0,
            'v_size': 0,
            'u_clamp': 0,
            'v_clamp': 0,
            'mip_zero': None,
            'max_color': None,
            'palette': None,
            'mips': [],
            'format': 0,
        }
        
        try:
            self.seek(exp['serial_offset'])
            name_idx = self._read_compact_index()
            flags = self._read_uint32()
            
            offset_start = self.tell()
            data_start = offset_start
            data_end = exp['serial_offset'] + exp['serial_size']
            all_data = self._data[data_start:data_end]
            
            # UT99 texture structure: 
            # Byte 0: format
            # Bytes 1-2: u_bits, v_bits  
            # Then several FName references and properties
            # At offset 16: u_clamp (0x22 followed by uint32)
            # At offset 22: v_clamp (0x22 followed by uint32)
            # At offset 28: u_size (0x22 followed by uint32)
            # At offset 34: v_size (0x22 followed by uint32)
            
            texture['format'] = all_data[0] if len(all_data) > 0 else 0
            texture['u_bits'] = all_data[1] if len(all_data) > 1 else 0
            texture['v_bits'] = all_data[2] if len(all_data) > 2 else 0
            texture['u_size'] = 1 << texture['u_bits'] if texture['u_bits'] < 14 else 0
            texture['v_size'] = 1 << texture['v_bits'] if texture['v_bits'] < 14 else 0
            
            # Read clamp values
            if len(all_data) > 21:
                texture['u_clamp'] = struct.unpack('<I', bytes(all_data[17:21]))[0]
            if len(all_data) > 27:
                texture['v_clamp'] = struct.unpack('<I', bytes(all_data[23:27]))[0]
            
            # Read u_size/v_size if present
            if len(all_data) > 33:
                val = struct.unpack('<I', bytes(all_data[29:33]))[0]
                if 1 <= val <= 8192:
                    texture['u_size'] = val
            if len(all_data) > 39:
                val = struct.unpack('<I', bytes(all_data[35:39]))[0]
                if 1 <= val <= 8192:
                    texture['v_size'] = val
            
            # Read palette if format indicates it
            if texture['format'] == 0:
                palette_offset = 40
                if palette_offset + 1024 <= len(all_data):
                    palette = []
                    for i in range(256):
                        r = all_data[palette_offset + i * 4]
                        g = all_data[palette_offset + i * 4 + 1]
                        b = all_data[palette_offset + i * 4 + 2]
                        a = all_data[palette_offset + i * 4 + 3]
                        palette.append((r, g, b, a))
                    texture['palette'] = palette
            
            # Parse mipmaps - search backwards from end for mipmap headers
            # Mipmap header: 4 bytes size, 4 bytes extra, 1 byte u_bits, 1 byte v_bits
            pos = data_end - 12
            while pos > data_start + 8:
                mip_size = struct.unpack('<I', bytes(self._data[pos:pos+4]))[0]
                extra = struct.unpack('<I', bytes(self._data[pos+4:pos+8]))[0]
                u_bits_mip = self._data[pos+8]
                v_bits_mip = self._data[pos+9]
                
                data_start_mip = pos + 8
                data_end_mip = data_start_mip + mip_size - 8
                
                if (mip_size > 0 and mip_size < 10000000 and 
                    u_bits_mip < 14 and v_bits_mip < 14 and
                    data_end_mip <= data_end):
                    u_size_mip = 1 << u_bits_mip
                    v_size_mip = 1 << v_bits_mip
                    data = self._data[data_start_mip:data_end_mip]
                    texture['mips'].append({
                        'u_bits': u_bits_mip,
                        'v_bits': v_bits_mip,
                        'data': data,
                        'u_size': u_size_mip,
                        'v_size': v_size_mip,
                    })
                    data_end = data_start_mip
                    pos = data_end - 12
                else:
                    pos -= 1
            
            texture['mips'].reverse()
            
        except Exception as e:
            return None
        
        return texture
    
    def _read_palette(self) -> List[tuple]:
        """Read a 256-color palette"""
        palette = []
        for _ in range(256):
            r = self._read_uint8()
            g = self._read_uint8()
            b = self._read_uint8()
            a = self._read_uint8()
            palette.append((r, g, b, a))
        return palette


def load_package(filepath: str) -> PackageReader:
    """Load a UT99 package file"""
    reader = PackageReader(filepath)
    reader.read_package()
    return reader