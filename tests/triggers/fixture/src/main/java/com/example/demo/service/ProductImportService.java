package com.example.demo.service;

import com.example.demo.domain.Product;
import com.example.demo.repo.ProductRepository;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ProductImportService {

    private final ProductRepository products;

    public ProductImportService(ProductRepository products) {
        this.products = products;
    }

    @Transactional
    public void importAll(List<Product> incoming) {
        for (Product p : incoming) {
            products.save(p);
        }
    }
}
