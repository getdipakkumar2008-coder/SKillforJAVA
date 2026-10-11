package com.example.demo.service;

import com.example.demo.domain.Product;
import com.example.demo.repo.ProductRepository;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class ProductService {

    private static final Map<Long, Product> CACHE = new HashMap<>();

    private final ProductRepository products;

    public ProductService(ProductRepository products) {
        this.products = products;
    }

    public List<Product> catalog() {
        List<Product> all = products.findAll();
        for (Product p : all) {
            CACHE.put(p.getId(), p);
        }
        return all;
    }
}
