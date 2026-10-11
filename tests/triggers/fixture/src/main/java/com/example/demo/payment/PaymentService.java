package com.example.demo.payment;

import java.math.BigDecimal;
import org.springframework.stereotype.Service;

@Service
public class PaymentService {

    private final PaymentClient client;

    public PaymentService(PaymentClient client) {
        this.client = client;
    }

    public String pay(Long customerId, BigDecimal amount) {
        if (amount.signum() <= 0) {
            throw new IllegalArgumentException("amount must be positive");
        }
        return client.charge(customerId, amount);
    }
}
