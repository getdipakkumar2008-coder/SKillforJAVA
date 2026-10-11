package com.example.demo.payment;

import java.math.BigDecimal;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class PaymentClient {

    private final RestTemplate http = new RestTemplate();

    public String charge(Long customerId, BigDecimal amount) {
        return http.postForObject("https://payments.example.com/charge?customer=" + customerId + "&amount=" + amount,
                null, String.class);
    }
}
