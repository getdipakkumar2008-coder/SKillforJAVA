# Plan: Order history

- Reuse `OrderRepository`; add `findByCustomerIdOrderByIdDesc(Long, Pageable)`.
- DTO `OrderView`; controller `CustomerOrdersController`.
- Ownership check in the service layer.
