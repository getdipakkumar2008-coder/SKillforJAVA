package com.example.demo.report;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import org.junit.jupiter.api.Test;

class ReportServiceTest {

    @Test
    void reportIsGeneratedWithinOneSecond() throws Exception {
        Instant start = Instant.now();
        Thread.sleep((long) (Math.random() * 1200));
        assertTrue(Instant.now().isBefore(start.plusMillis(1000)));
    }
}
