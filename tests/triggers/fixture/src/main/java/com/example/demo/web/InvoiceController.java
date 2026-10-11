package com.example.demo.web;

import com.example.demo.domain.Invoice;
import com.example.demo.repo.InvoiceRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/invoices")
public class InvoiceController {

    private final InvoiceRepository invoices;

    public InvoiceController(InvoiceRepository invoices) {
        this.invoices = invoices;
    }

    @GetMapping("/{id}")
    public Invoice get(@PathVariable Long id) {
        return invoices.findById(id).orElseThrow();
    }
}
