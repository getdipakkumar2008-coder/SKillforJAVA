package com.example.demo.domain;

import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(name = "invoices")
public class Invoice {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long ownerId;
    private BigDecimal amount;
    private String pdfPath;

    public Long getId() { return id; }
    public Long getOwnerId() { return ownerId; }
    public BigDecimal getAmount() { return amount; }
    public String getPdfPath() { return pdfPath; }
}
