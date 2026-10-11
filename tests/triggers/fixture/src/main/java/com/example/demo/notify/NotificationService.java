package com.example.demo.notify;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.springframework.stereotype.Service;

@Service
public class NotificationService {

    private final EmailClient emailClient;
    private final ExecutorService executor = Executors.newFixedThreadPool(4);

    public NotificationService(EmailClient emailClient) {
        this.emailClient = emailClient;
    }

    /** Looks up the customer's address and sends the message asynchronously. */
    public CompletableFuture<Void> notifyCustomer(long customerId, String message) {
        return CompletableFuture
                .supplyAsync(() -> emailClient.lookupAddress(customerId), executor)
                .thenApply(address -> emailClient.send(address, message))
                .exceptionally(ex -> null)
                .thenAccept(receipt -> {
                });
    }
}
