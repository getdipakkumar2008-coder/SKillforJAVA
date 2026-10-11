package com.example.demo.web;

import com.example.demo.domain.Order;
import com.example.demo.repo.OrderRepository;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    public record OrderView(Long id, String status, int lineCount) {
    }

    private final OrderRepository orders;

    public OrderController(OrderRepository orders) {
        this.orders = orders;
    }

    @GetMapping
    public List<Order> list() {
        return orders.findAll();
    }

    @GetMapping("/summaries")
    public List<OrderView> summaries() {
        return orders.findAll().stream()
                .map(o -> new OrderView(o.getId(), o.getStatus(), o.getLines().size()))
                .toList();
    }
}
