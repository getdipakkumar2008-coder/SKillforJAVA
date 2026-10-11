package com.example.demo.events;

import com.example.demo.service.ShipmentService;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class OrderEventsListener {

    private final ShipmentService shipments;

    public OrderEventsListener(ShipmentService shipments) {
        this.shipments = shipments;
    }

    @KafkaListener(topics = "order-events", groupId = "shipping")
    public void onOrderEvent(String orderId) {
        shipments.createShipment(Long.parseLong(orderId));
    }
}
