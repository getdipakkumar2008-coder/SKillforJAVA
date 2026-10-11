package com.example.demo.service;

import com.example.demo.domain.Order;
import com.example.demo.domain.OrderLine;
import com.example.demo.payment.PaymentClient;
import com.example.demo.repo.OrderRepository;
import com.example.demo.repo.ProductRepository;
import java.math.BigDecimal;
import org.springframework.stereotype.Service;

@Service
public class CheckoutService {

    private final OrderRepository orders;
    private final ProductRepository products;
    private final PaymentClient payments;

    public CheckoutService(OrderRepository orders, ProductRepository products, PaymentClient payments) {
        this.orders = orders;
        this.products = products;
        this.payments = payments;
    }

    public String checkout(Long orderId) {
        Order order = orders.findById(orderId).orElseThrow();
        BigDecimal total = BigDecimal.ZERO;
        for (OrderLine line : order.getLines()) {
            BigDecimal price = products.findById(line.getProduct().getId()).orElseThrow().getPrice();
            total = total.add(price.multiply(BigDecimal.valueOf(line.getQuantity())));
        }
        return payments.charge(order.getCustomer().getId(), total);
    }
}
