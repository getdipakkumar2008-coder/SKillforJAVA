package com.example.demo.util;

import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

class TextUtilsTest {

    @Test
    void nullIsBlank() {
        assertTrue(TextUtils.isBlank(null));
    }
}
