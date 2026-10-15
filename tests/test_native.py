"""Tests for native function lookup (UnCoreNative.h)."""

import unittest
from ut99py.core.native import (
    NativeLookup,
    GNativeLookupFuncs,
    declare_native_type,
    implement_native_handler,
    find_native,
    map_native,
    init_native_lookup_funcs,
)


class TestNativeLookup(unittest.TestCase):
    """Test the NativeLookup type and global functions."""

    def test_native_lookup_type(self):
        # NativeLookup is a Callable that takes a str and returns Any
        self.assertTrue(callable(NativeLookup))
        # It's actually just a type alias for Callable[[str], Any]
        # Let's verify we can assign functions to it
        def dummy_lookup(name: str) -> int:
            return len(name)
        
        lookup: NativeLookup = dummy_lookup
        self.assertEqual(lookup("test"), 4)

    def test_init_native_lookup_funcs(self):
        # Reset and test initialization
        init_native_lookup_funcs()
        self.assertEqual(len(GNativeLookupFuncs), 32)
        self.assertTrue(all(f is None for f in GNativeLookupFuncs))


class TestNativeTypeRegistration(unittest.TestCase):
    """Test native type declaration and implementation."""

    def setUp(self):
        # Reset state before each test
        init_native_lookup_funcs()
        # Clear any existing registrations (not ideal but works for tests)
        # In practice, we'd have a proper cleanup mechanism

    def test_declare_native_type(self):
        # Declare a native type
        lookup_func, register_func = declare_native_type("Test", "MyType")
        
        # Check we got back callable functions
        self.assertTrue(callable(lookup_func))
        self.assertTrue(callable(register_func))
        
        # Register a native function
        def my_native_func(stack, result):
            pass
            
        register_func("MyNative", my_native_func)
        
        # Look it up
        found = lookup_func("MyNative")
        self.assertEqual(found, my_native_func)
        
        # Non-existent returns None
        self.assertIsNone(lookup_func("NonExistent"))

    def test_implement_native_handler(self):
        # Declare a type first
        declare_native_type("Test", "HandlerType")
        
        # Implement a handler
        @implement_native_handler("Test", "HandlerType")
        def my_handler(native_name):
            if native_name == "TestFunc":
                return lambda: "found"
            return None
        
        # Test the handler
        result = my_handler("TestFunc")
        self.assertIsNotNone(result)
        self.assertEqual(result(), "found")
        
        result2 = my_handler("NonExistent")
        self.assertIsNone(result2)

    def test_find_native(self):
        # Declare types
        uobj_lookup, uobj_register = declare_native_type("Core", "UObject")
        ucmd_lookup, ucmd_register = declare_native_type("Core", "UCommandlet")
        
        # Register some functions
        def uobject_func(stack, result):
            pass
            
        def ucommandlet_func(stack, result):
            pass
            
        uobj_register("GetClass", uobject_func)
        ucmd_register("Main", ucommandlet_func)
        
        # Test find_native
        found = find_native("Core", "UObject", "GetClass")
        self.assertEqual(found, uobject_func)
        
        found2 = find_native("Core", "UCommandlet", "Main")
        self.assertEqual(found2, ucommandlet_func)
        
        # Not found
        self.assertIsNone(find_native("Core", "UObject", "NonExistent"))
        self.assertIsNone(find_native("WrongPkg", "UObject", "GetClass"))
        self.assertIsNone(find_native("Core", "WrongType", "GetClass"))

    def test_map_native(self):
        # Test the map_native utility
        name, method = map_native("UObject", "GetClass")
        self.assertEqual(name, "intUObjectGetClass")
        self.assertEqual(method, "GetClass")


if __name__ == "__main__":
    unittest.main()