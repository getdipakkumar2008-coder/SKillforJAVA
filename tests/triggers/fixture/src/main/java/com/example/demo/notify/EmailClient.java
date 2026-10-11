package com.example.demo.notify;

public interface EmailClient {

    String lookupAddress(long customerId);

    String send(String address, String message);
}
