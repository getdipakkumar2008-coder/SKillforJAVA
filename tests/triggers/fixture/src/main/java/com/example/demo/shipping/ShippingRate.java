package com.example.demo.shipping;

public class ShippingRate {

    public static final int STANDARD = 0;
    public static final int EXPRESS = 1;
    public static final int OVERNIGHT = 2;

    private final int type;
    private final double weightKg;

    public ShippingRate(int type, double weightKg) {
        this.type = type;
        this.weightKg = weightKg;
    }

    public int getType() { return type; }
    public double getWeightKg() { return weightKg; }

    public double cost() {
        double base;
        switch (type) {
            case STANDARD:
                base = 4.0;
                break;
            case EXPRESS:
                base = 9.5;
                break;
            case OVERNIGHT:
                base = 19.0;
                break;
            default:
                throw new IllegalStateException("unknown type " + type);
        }
        return base + weightKg * 0.8;
    }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof ShippingRate)) {
            return false;
        }
        ShippingRate other = (ShippingRate) o;
        return type == other.type && weightKg == other.weightKg;
    }

    @Override
    public int hashCode() {
        return 31 * type + Double.hashCode(weightKg);
    }
}
