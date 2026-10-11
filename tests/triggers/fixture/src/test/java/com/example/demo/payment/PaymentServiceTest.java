package com.example.demo.payment;

import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class PaymentServiceTest {

    @Test
    void rejectsNonPositiveAmount() {
        PaymentService service = new PaymentService(null);
        assertThrows(IllegalArgumentException.class, () -> service.pay(1L, BigDecimal.ZERO));
    }
}
