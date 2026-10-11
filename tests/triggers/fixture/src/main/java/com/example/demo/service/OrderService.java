package com.example.demo.service;

import com.example.demo.domain.Order;
import com.example.demo.repo.OrderRepository;
import com.example.demo.web.OrderController.OrderView;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {

    private final OrderRepository orders;
    private final KafkaTemplate<String, String> kafka;

    public OrderService(OrderRepository orders, KafkaTemplate<String, String> kafka) {
        this.orders = orders;
        this.kafka = kafka;
    }

    @Transactional
    public OrderView place(Order order) {
        Order saved = orders.save(order);
        kafka.send("order-events", String.valueOf(saved.getId()), "ORDER_PLACED");
        return new OrderView(saved.getId(), saved.getStatus(), saved.getLines().size());
    }
}
